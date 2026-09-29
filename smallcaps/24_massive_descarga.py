"""Ronda 10: descarga de Massive (antes Polygon), plan gratis (5 consultas/min, 1 min desde 29-sep-2024).
La credencial la añade el entorno (cabecera Authorization) → no hace falta clave en el código.
Fases (se puede reanudar; salta lo ya descargado):
  1) referencia de tickers (acciones comunes y ADR, activas y no activas)
  2) barras diarias de TODO el mercado por día (ajustadas por splits) → gappers
  3) velas de 1 min SIN ajustar de cada día de gap (primero gap ≥ 50 %, luego 20-50 %)
Datos en /home/user/data/massive."""
import json, os, re, sys, time
import pandas as pd
import requests

BASE = "https://api.polygon.io"
OUT = "/home/user/data/massive"
PAUSA = 12.5
S = requests.Session()


def llamar(url, params=None):
    for k in range(6):
        try:
            r = S.get(url if url.startswith("http") else BASE + url, params=params, timeout=(15, 60))
            if r.status_code == 429:
                time.sleep(60); continue
            d = r.json()
            time.sleep(PAUSA)
            return d
        except Exception as e:
            print("reintento", url, e, flush=True); time.sleep(30)
    return None                      # fallo de red: NO se guarda nada (antes se guardaba un archivo vacío como si no hubiera datos)


def referencia():
    f = f"{OUT}/tickers.parquet"
    if os.path.exists(f):
        return pd.read_parquet(f)
    filas = []
    for tipo in ["CS", "ADRC"]:
        for activo in ["true", "false"]:
            d = llamar("/v3/reference/tickers", dict(market="stocks", type=tipo, active=activo, limit=1000)) or {}
            while True:
                filas += [dict(ticker=x["ticker"], tipo=tipo, activo=x.get("active"), nombre=x.get("name"),
                               bolsa=x.get("primary_exchange"), baja=x.get("delisted_utc")) for x in d.get("results", [])]
                print("referencia", tipo, activo, len(filas), flush=True)
                if not d.get("next_url"):
                    break
                d = llamar(d["next_url"]) or {}
    T = pd.DataFrame(filas).drop_duplicates()
    T.to_parquet(f)
    return T


def diarios():
    os.makedirs(f"{OUT}/diario", exist_ok=True)
    for dia in pd.bdate_range("2024-09-27", "2026-09-25"):
        f = f"{OUT}/diario/{dia.date()}.parquet"
        if os.path.exists(f):
            continue
        d = llamar(f"/v2/aggs/grouped/locale/us/market/stocks/{dia.date()}", dict(adjusted="true"))
        if d is None:
            continue
        R = pd.DataFrame(d.get("results") or [])
        R.to_parquet(f)
        print("diario", dia.date(), len(R), flush=True)


def gappers(T):
    fs = sorted(f for f in os.listdir(f"{OUT}/diario") if os.path.getsize(f"{OUT}/diario/{f}") > 1000)
    D = pd.concat([pd.read_parquet(f"{OUT}/diario/{f}").assign(fecha=f[:10]) for f in fs])
    D = D.rename(columns={"T": "sym", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "vw": "vwap"})
    D = D.sort_values(["sym", "fecha"])
    D["pc"] = D.groupby("sym").close.shift()
    D["fecha_prev"] = D.groupby("sym").fecha.shift()
    D["gap"] = D.open / D.pc - 1
    D["dv"] = D.volume * D.vwap
    validos = set(T.ticker)
    E = D[(D.fecha >= "2024-10-01") & (D.gap >= 0.20) & (D.gap < 5) & (D.dv >= 1e6) & D.sym.isin(validos)
          & D.sym.str.fullmatch(r"[A-Z]{1,5}")].copy()
    E = E.merge(T[["ticker", "tipo", "nombre"]].drop_duplicates("ticker"), left_on="sym", right_on="ticker", how="left")
    E.to_parquet(f"{OUT}/gappers.parquet")
    return E


def minutos(E):
    os.makedirs(f"{OUT}/m1", exist_ok=True)
    E = E.assign(prio=(E.gap < 0.5).astype(int)).sort_values(["prio", "fecha"])
    n = 0
    for r in E.itertuples():
        f = f"{OUT}/m1/{r.sym}_{r.fecha}.parquet"
        if os.path.exists(f):
            continue
        d = llamar(f"/v2/aggs/ticker/{r.sym}/range/1/minute/{r.fecha}/{r.fecha}", dict(adjusted="false", limit=50000))
        if d is None or d.get("status") not in ("OK", "DELAYED"):
            print("sin respuesta válida, se reintentará luego:", r.sym, r.fecha, (d or {}).get("status"), flush=True)
            continue
        pd.DataFrame(d.get("results") or []).to_parquet(f)
        n += 1
        if n % 20 == 0:
            print("minutos", n, r.fecha, r.sym, "prio", r.prio, flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    T = referencia()
    diarios()
    E = gappers(T)
    print("gappers:", len(E), "gap ≥ 50 %:", (E.gap >= .5).sum(), flush=True)
    minutos(E)
    print("FIN", flush=True)
