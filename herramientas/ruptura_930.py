"""Seguimiento en vivo de la idea del usuario (aprobado el 29-sep-2026): ruptura de la vela de 1 min de las 9:30, solo cortos,
en las acciones del Radar. Es un ESTUDIO para acumular muestra, no un plan de ejecución (el Radar sigue siendo solo selección).

Reglas (las del usuario, `smallcaps/23b_ruptura_930_usuario.py`): niveles = apertura (O) y mínimo (L) de la vela de 1 min de las 9:30;
corto cuando una vela CIERRA bajo L (hasta las 11:00); UN solo intento por acción; sale si una vela cierra sobre O; todo fuera a las 11:30.
1R = entrada → O (mín. 2 %). Coste 0.5 % del precio. Datos: Yahoo 1 min (solo guarda ~30 días: hay que guardarlos cada día).

Uso:
  python3 herramientas/ruptura_930.py guardar --fecha AAAA-MM-DD   → listas/m1/AAAA-MM-DD/TICKER.csv.gz (acciones de esa lista)
  python3 herramientas/ruptura_930.py medir                        → listas/ruptura_930.csv + resumen por nivel del Radar
"""
import argparse, datetime as dt, glob, json, os
import numpy as np
import pandas as pd

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "listas")
COSTE, RIESGO_MIN = 0.005, 0.02


def acciones(fecha):
    L = json.load(open(os.path.join(RAIZ, "datos", f"{fecha}.json")))
    out = []
    for x in L.get("acciones", []) + L.get("descartadas", []):     # formato nuevo (desde el 30-sep): sin letras
        p = x.get("puntuacion") or {}
        out.append(dict(sym=x["sym"], nivel="DESCARTADA" if "motivo" in x else "TESIS " + p.get("tercio", "?").upper(),
                        gap=x.get("gap"), precio=x.get("precio"), grupo="gap ≥ 50 %" if x["gap"] >= 0.5 else "gap 20-50 %",
                        replay=bool(L.get("replay"))))
    for grupo in ("lista", "vigilar"):
        for x in L.get(grupo) or []:
            out.append(dict(sym=x["sym"], nivel=x.get("nivel") or "SIN CLASIFICAR", gap=x.get("gap"), precio=x.get("precio"),
                            grupo="gap ≥ 50 %" if grupo == "lista" else "gap 20-50 %", replay=bool(L.get("replay"))))
    return out


def guardar(fecha):
    import yfinance as yf
    d = dt.date.fromisoformat(fecha)
    carpeta = os.path.join(RAIZ, "m1", fecha)
    os.makedirs(carpeta, exist_ok=True)
    for a in acciones(fecha):
        f = os.path.join(carpeta, f"{a['sym']}.csv.gz")
        if os.path.exists(f):
            continue
        try:
            x = yf.download(a["sym"], start=d, end=d + dt.timedelta(days=1), interval="1m", prepost=False,
                            progress=False, auto_adjust=False)
        except Exception as e:
            print(a["sym"], "ERROR", e); continue
        if x is None or x.empty:
            print(a["sym"], "sin datos de 1 min (Yahoo solo guarda ~30 días)"); continue
        if isinstance(x.columns, pd.MultiIndex):
            x.columns = x.columns.get_level_values(0)
        x.index = x.index.tz_convert("America/New_York")
        x = x[x.index.date == d][["Open", "High", "Low", "Close", "Volume"]]
        x.to_csv(f, compression="gzip")
        print(a["sym"], len(x), "velas")


def uno(x):
    x = x.between_time("09:30", "15:59")
    if len(x) < 10 or x.index[0].strftime("%H:%M") != "09:30":
        return dict(estado="sin vela de 9:30")
    o, l = x.Open.iloc[0], x.Low.iloc[0]
    t = x.index.strftime("%H:%M"); c = x.Close.to_numpy()
    for i in range(1, len(x)):
        if t[i] > "11:00":
            break
        if c[i] < l:
            e, r = c[i], max((o - c[i]) / c[i], RIESGO_MIN)
            for j in range(i + 1, len(x)):
                if c[j] > o or t[j] >= "11:30":
                    return dict(estado="stop" if c[j] > o else "11:30", O=o, L=l, entrada_hora=t[i], entrada=e,
                                salida_hora=t[j], salida=c[j], R=((e - c[j]) / e - COSTE) / r)
    return dict(estado="no rompió", O=o, L=l, R=0.0)


def medir():
    filas = []
    for carpeta in sorted(glob.glob(os.path.join(RAIZ, "m1", "*"))):
        fecha = os.path.basename(carpeta)
        for a in acciones(fecha):
            f = os.path.join(carpeta, f"{a['sym']}.csv.gz")
            if not os.path.exists(f):
                continue
            x = pd.read_csv(f, index_col=0)
            x.index = pd.to_datetime(x.index, utc=True).tz_convert("America/New_York")
            filas.append(dict(fecha=fecha, **a, **uno(x)))
    X = pd.DataFrame(filas)
    X.to_csv(os.path.join(RAIZ, "ruptura_930.csv"), index=False)

    def met(v):
        v = v.dropna(); g, p = v[v > 0], v[v <= 0]
        return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                              PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, dolares_riesgo_20=20 * v.sum()))
    X["clase"] = np.select([X.nivel.isin(["DESCARTADA", "NO", "NUNCA"]),
                            X.nivel.eq("TESIS ALTA") & (X.grupo == "gap ≥ 50 %"),
                            X.nivel.isin(["TESIS MEDIA", "TESIS BAJA"]) & (X.grupo == "gap ≥ 50 %"),
                            X.nivel.isin(["A", "B"]) & (X.grupo == "gap ≥ 50 %"),
                            (X.grupo == "gap ≥ 50 %") & (X.precio >= 1) & (X.nivel == "VIGILAR"),
                            X.grupo == "gap 20-50 %"], ["descartadas / NO / Nunca", "Tesis alta ≥ 50 %", "Tesis media/baja ≥ 50 %", "A/B", "Vigilar ≥ 50 % (≥ $1)", "20-50 %"], "otras (< $1)")
    T = X[X.estado.isin(["stop", "11:30"])].groupby("clase").R.apply(met).unstack()
    pd.set_option("display.width", 200)
    print(f"días: {X.fecha.nunique()} ({X.fecha.min()} → {X.fecha.max()}) · acciones: {len(X)} · "
          f"con operación: {X.estado.isin(['stop', '11:30']).sum()} · no rompió: {(X.estado == 'no rompió').sum()} · "
          f"sin vela 9:30: {(X.estado == 'sin vela de 9:30').sum()}")
    print(T.round(2).to_string())
    return X, T


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("paso", choices=["guardar", "medir"])
    ap.add_argument("--fecha")
    a = ap.parse_args()
    guardar(a.fecha) if a.paso == "guardar" else medir()
