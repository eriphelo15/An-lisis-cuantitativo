"""Ronda 15: backtest del lado largo SOBRE LOS FILTRADOS (reglas fijadas en el pre-registro, escrito ANTES de ver resultados).
Entrada E1 = primera apertura regular posterior a la aceptación del documento (`entrada` en universo_U1).
Stop −20 %: si el mínimo de una sesión toca entrada × 0.80 → salida a 0.80 × 0.98; si una sesión abre por debajo del stop → salida a
esa apertura. Salidas S1/S3/S5 = cierre de la 1.ª/3.ª/5.ª sesión. Coste 0.5 %. R = rentabilidad / 0.20.
Precios: barras diarias AJUSTADAS de Massive (incluyen deslistadas) para la rentabilidad.
  python 36_largos_backtest.py base         → R de todo U1 (para HL6 y descriptivos)
  python 36_largos_backtest.py filtrados    → R de los que pasan A+B+C (lee filtrados_r15.csv)"""
import glob, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun

D = "/home/user/data/largos"
STOP, DESL, COSTE = 0.20, 0.02, 0.005
CAL = [str(x)[:10] for x in comun.calendario()]
POS = {d: i for i, d in enumerate(CAL)}


def barras():
    fs = sorted(glob.glob("/home/user/data/massive/diario/*.parquet")) + sorted(glob.glob(f"{D}/diario_aj/*.parquet"))
    vistos, partes = set(), []
    for f in fs:
        d = os.path.basename(f)[:10]
        if d in vistos:
            continue
        vistos.add(d)
        partes.append(pd.read_parquet(f, columns=["T", "o", "h", "l", "c"]).assign(fecha=d))
    B = pd.concat(partes, ignore_index=True)
    return {(t, f): (o, h, l, c) for t, f, o, h, l, c in zip(B["T"], B.fecha, B.o, B.h, B.l, B.c)}


def largo(bar, tk, entrada, n):
    """R del largo E1 con salida al cierre de la n-ésima sesión (n = 1, 3, 5). None si faltan datos."""
    if entrada not in POS:
        return None
    b0 = bar.get((tk, entrada))
    if b0 is None:
        return None
    p0 = b0[0]
    st = p0 * (1 - STOP)
    sal = None
    for k in range(n):
        d = CAL[POS[entrada] + k]
        b = bar.get((tk, d))
        if b is None:                      # sin cotización (halt largo / deslistada): sale al último cierre conocido si lo hay
            return None if k == 0 else sal_ret(sal_prev, p0)
        o, h, l, c = b
        if k > 0 and o <= st:
            return sal_ret(o, p0)
        if l <= st:
            return sal_ret(st * (1 - DESL), p0)
        sal_prev = c
    return sal_ret(sal_prev, p0)


def sal_ret(salida, p0):
    return ((salida - p0) / p0 - COSTE) / STOP


def metricas(v):
    v = pd.Series(v).dropna()
    g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, dolares=20 * v.sum())


if __name__ == "__main__":
    modo = sys.argv[1]
    bar = barras()
    if modo == "base":
        X = pd.read_parquet(f"{D}/universo_U1.parquet")
    else:
        X = pd.read_csv(f"{D}/filtrados_r15.csv")
    for n in (1, 3, 5):
        X[f"R_S{n}"] = [largo(bar, t, e, n) for t, e in zip(X.ticker, X.entrada)]
    X["per"] = np.where(X.entrada <= "2025-09-30", "DEV", "VAL")
    X.to_csv(f"{D}/res_r15_{modo}.csv", index=False)
    print("guardado", len(X), "eventos (sin imprimir resultados: el informe se hace con el script de análisis)")
