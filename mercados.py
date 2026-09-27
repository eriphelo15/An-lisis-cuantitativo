"""
MERCADOS — descarga cotizaciones reales (Yahoo Finance, con retraso) para la terminal
bloomberg.html y las guarda en un JSON.

Uso:
  python mercados.py                        # escribe datos_mercados/mercados.json
  python mercados.py --salida _datos        # carpeta de salida
  python mercados.py --cada 900             # repetir cada 15 min (en tu ordenador)

La página lee el JSON desde la rama `mercados-datos` del repositorio (la actualiza el
workflow .github/workflows/mercados.yml) o, si la sirves en local, desde ./mercados.json.
"""

import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

# nombre, símbolo Yahoo, divisa, futuro (opcional), índice de volatilidad (opcional)
INDICES = {
    "americas": [
        ("DOW JONES", "^DJI", "USD", "YM=F", "^VXD"),
        ("S&P 500", "^GSPC", "USD", "ES=F", "^VIX"),
        ("NASDAQ", "^IXIC", "USD", None, "^VXN"),
        ("RUSSELL 2000", "^RUT", "USD", "RTY=F", None),
        ("S&P/TSX Comp", "^GSPTSE", "CAD", None, None),
        ("S&P/BMV IPC", "^MXX", "MXN", None, None),
        ("IBOVESPA", "^BVSP", "BRL", None, None),
    ],
    "emea": [
        ("Euro Stoxx 50", "^STOXX50E", "EUR", None, None),
        ("FTSE 100", "^FTSE", "GBP", None, None),
        ("CAC 40", "^FCHI", "EUR", None, None),
        ("DAX", "^GDAXI", "EUR", None, None),
        ("IBEX 35", "^IBEX", "EUR", None, None),
        ("FTSE MIB", "FTSEMIB.MI", "EUR", None, None),
        ("SWISS MKT", "^SSMI", "CHF", None, None),
    ],
    "asiaPacific": [
        ("NIKKEI", "^N225", "JPY", "NIY=F", None),
        ("HANG SENG", "^HSI", "HKD", None, None),
        ("SHANGHAI COMP", "000001.SS", "CNY", None, None),
        ("S&P/ASX 200", "^AXJO", "AUD", None, None),
        ("KOSPI", "^KS11", "KRW", None, None),
        ("NIFTY 50", "^NSEI", "INR", None, None),
    ],
}
# Divisas que ofrece la página para convertir los valores (unidades por 1 USD).
DIVISAS_PAGINA = ["EUR", "CAD", "MXN"]
# Índices de los que se leen titulares.
NOTICIAS_DE = ["^GSPC", "^IXIC", "^DJI", "^STOXX50E", "^FTSE", "^GDAXI", "^N225", "^HSI"]
DIAS_HISTORIA = 250
MAX_INTRADIA = 80


def fx_ticker(divisa):
    return f"USD{divisa}=X"


def limpio(x, dec=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return round(float(x), dec)


def columna(df, sym, campo):
    try:
        return df[sym][campo].dropna()
    except KeyError:
        return pd.Series(dtype=float)


def descargar(simbolos, **kw):
    return yf.download(sorted(set(simbolos)), group_by="ticker", auto_adjust=False,
                       progress=False, threads=True, **kw)


def ytd_base(cierres):
    """Último cierre del año anterior (base estándar del %YTD)."""
    if cierres.empty:
        return None
    anio = cierres.index[-1].year
    previos = cierres[cierres.index.year < anio]
    return float(previos.iloc[-1]) if not previos.empty else float(cierres.iloc[0])


def sesion_actual(intradia):
    """Barras de la última sesión de un símbolo (en la zona horaria de la descarga)."""
    if intradia.empty:
        return intradia
    ultimo = intradia.index[-1].date()
    return intradia[[d == ultimo for d in intradia.index.date]]


def recoger():
    simbolos = []
    for items in INDICES.values():
        for _, sym, _, fut, vol in items:
            simbolos += [sym] + [s for s in (fut, vol) if s]
    divisas = sorted(({i[2] for items in INDICES.values() for i in items} | set(DIVISAS_PAGINA)) - {"USD"})
    simbolos += [fx_ticker(d) for d in divisas]

    diario = descargar(simbolos, period="2y", interval="1d")
    intradia = descargar(simbolos, period="5d", interval="15m")

    def ultimo_valor(sym):
        """(valor, timestamp UTC) del último precio disponible."""
        d = columna(diario, sym, "Close")
        i = columna(intradia, sym, "Close")
        if not i.empty and (d.empty or i.index[-1].date() >= d.index[-1].date()):
            return float(i.iloc[-1]), i.index[-1]
        if not d.empty:
            return float(d.iloc[-1]), d.index[-1]
        return None, None

    fx = {}
    for d in divisas:
        cierres = columna(diario, fx_ticker(d), "Close")
        valor, _ = ultimo_valor(fx_ticker(d))
        base = ytd_base(cierres)
        fx[d] = {"usd": limpio(valor), "ytdBase": limpio(base)}

    salida = {}
    for region, items in INDICES.items():
        filas = []
        for nombre, sym, divisa, fut, vol in items:
            cierres = columna(diario, sym, "Close")
            if len(cierres) < 30:
                print(f"  sin datos suficientes: {nombre} ({sym})")
                continue
            valor, ts = ultimo_valor(sym)
            sesion = sesion_actual(columna(intradia, sym, "Close"))
            # Si el diario ya trae la sesión de hoy, el cierre previo es el penúltimo.
            hoy = ts.date()
            previos = cierres[[d < hoy for d in cierres.index.date]]
            prev_close = float(previos.iloc[-1]) if not previos.empty else float(cierres.iloc[-2])
            hist = [float(x) for x in previos.iloc[-(DIAS_HISTORIA - 1):]] + [valor]
            intr = [float(x) for x in sesion]
            if len(intr) > MAX_INTRADIA:
                paso = len(intr) / MAX_INTRADIA
                intr = [intr[int(k * paso)] for k in range(MAX_INTRADIA - 1)] + [intr[-1]]

            # Δ AVAT: volumen diario de la sesión frente a la media de 20 días. Si la sesión
            # sigue abierta, la media se escala por la parte de la sesión ya transcurrida.
            avat = None
            vols = columna(diario, sym, "Volume")
            vols_prev = vols[[d < hoy for d in vols.index.date]].iloc[-20:]
            vol_hoy = vols[[d == hoy for d in vols.index.date]]
            if len(vols_prev) and vols_prev.mean() > 0 and len(vol_hoy) and vol_hoy.iloc[-1] > 0:
                intr_all = columna(intradia, sym, "Close")
                barras_dia = pd.Series([d for d in intr_all.index.date if d < hoy]).value_counts()
                tipico = barras_dia.median() if len(barras_dia) else len(sesion)
                fraccion = min(1.0, len(sesion) / tipico) if tipico else 1.0
                avat = (vol_hoy.iloc[-1] / (vols_prev.mean() * fraccion) - 1) * 100

            fila = {
                "id": nombre, "symbol": sym, "currency": divisa,
                "value": limpio(valor), "prevClose": limpio(prev_close),
                "yearOpen": limpio(ytd_base(cierres)),
                "ts": int(ts.timestamp()),
                "hist": [limpio(x) for x in hist], "intraday": [limpio(x) for x in intr],
                "avat": limpio(avat, 2),
            }
            if fut:
                fv, _ = ultimo_valor(fut)
                fila["future"] = {"symbol": fut, "value": limpio(fv)}
            if vol:
                vv, _ = ultimo_valor(vol)
                fila["impliedVol"] = {"symbol": vol, "value": limpio(vv, 2)}
            filas.append(fila)
        salida[region] = filas

    return {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuente": "Yahoo Finance (yfinance), cotizaciones con retraso",
        "fx": fx,
        "regiones": salida,
        "noticias": noticias(),
    }


def noticias():
    vistas, out = set(), []
    for sym in NOTICIAS_DE:
        try:
            items = yf.Ticker(sym).news or []
        except Exception as e:  # noqa: BLE001 — una fuente caída no debe tumbar el resto
            print(f"  noticias {sym}: {e}")
            continue
        for n in items:
            c = n.get("content", n)
            titulo = c.get("title")
            if not titulo or titulo in vistas:
                continue
            vistas.add(titulo)
            url = (c.get("canonicalUrl") or c.get("clickThroughUrl") or {}).get("url") or c.get("link")
            out.append({
                "titulo": titulo,
                "resumen": c.get("summary") or c.get("description") or "",
                "fuente": (c.get("provider") or {}).get("displayName") or c.get("publisher") or "",
                "fecha": c.get("pubDate") or c.get("displayTime"),
                "url": url,
                "indice": sym,
            })
    out.sort(key=lambda n: n["fecha"] or "", reverse=True)
    return out[:40]


def main():
    parser = argparse.ArgumentParser(description="Cotizaciones reales para bloomberg.html",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__)
    parser.add_argument("--salida", default="datos_mercados", help="Carpeta de salida")
    parser.add_argument("--cada", type=int, default=0, help="Repetir cada N segundos (0 = una vez)")
    args = parser.parse_args()

    destino = Path(args.salida)
    destino.mkdir(parents=True, exist_ok=True)
    while True:
        datos = recoger()
        n = sum(len(v) for v in datos["regiones"].values())
        if n < 10:
            raise SystemExit(f"Sólo se obtuvieron {n} índices; no se sobrescribe el JSON.")
        tmp = destino / "mercados.json.tmp"
        tmp.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        tmp.replace(destino / "mercados.json")
        print(f"{datos['generado']}: {n} índices, {len(datos['noticias'])} noticias → {destino / 'mercados.json'}")
        if not args.cada:
            break
        time.sleep(args.cada)


if __name__ == "__main__":
    main()
