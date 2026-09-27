"""Hipótesis de la literatura, probadas en NQ/ES/YM 15 años:
 1) Días de dato macro (NFP y CPI; fechas de publicación reales vía ALFRED/FRED) y FOMC:
    - deriva previa al dato (16:00 de ayer -> 08:29), reacción (08:30->09:30), sesión (09:30->16:00),
    - continuación: dirección de la reacción 08:30->09:30 aplicada a 09:30->10:00 y 09:30->16:00.
 2) Momentum intradía (Gao, Han, Li, Zhou, JFE 2018): rendimiento desde el cierre de ayer hasta 10:00 predice 15:30->16:00.
    Más fuerte en días volátiles y de noticias (según el paper).
 3) Rebalanceo de ETFs apalancados: el movimiento del día hasta 15:30 predice 15:30->16:00 (misma dirección); ¿más fuerte desde 2022?"""
import numpy as np, pandas as pd
from base import tramos, periodo, SYMS
from calendario import FOMC
EXT = "/home/user/data/ext"
NFP = pd.to_datetime(open(f"{EXT}/release_PAYEMS.txt").read().split())
CPI = pd.to_datetime(open(f"{EXT}/release_CPIAUCSL.txt").read().split())

def st(x):
    x = x[~np.isnan(x)]
    return f"{x.mean():+6.1f}bp t={x.mean()/x.std()*np.sqrt(len(x)):+4.1f} n={len(x):3d}" if len(x) > 2 else "  -  "

for s in SYMS:
    T = tramos(s).copy(); P = periodo(T.index)
    T["prev16"] = T.t16.shift()
    r = lambda a, b: ((T[b] - T[a]) / T.ref * 1e4).to_numpy()
    print(f"\n==================== {s} ====================")
    for nom, fechas in [("NFP", NFP), ("CPI", CPI), ("FOMC", FOMC)]:
        m = T.index.isin(fechas)
        print(f"-- {nom} (días en datos: {m.sum()})")
        for tn, (a, b) in {"pre 16h->08:30": ("prev16", "t0830"), "reacción 08:30->09:30": ("t0830", "t0930"),
                           "sesión 09:30->16": ("t0930", "t16")}.items():
            x = r(a, b)
            print(f"   {tn:22s}", " | ".join(f"{p}: {st(x[m & (P == p)])}" for p in ["DEV", "VAL1", "VAL2"]))
        reac = np.sign(r("t0830", "t0930"))
        for tn, (a, b) in {"sigue reacción 09:30->10": ("t0930", "t10"), "sigue reacción 09:30->16": ("t0930", "t16")}.items():
            x = reac * r(a, b)
            print(f"   {tn:22s}", " | ".join(f"{p}: {st(x[m & (P == p)])}" for p in ["DEV", "VAL1", "VAL2"]))
    # 2) Gao et al.
    fh = r("prev16", "t10"); lh = r("t1530", "t16"); x = np.sign(fh) * lh
    vol = pd.Series(np.abs(r("t0930", "t16"))).rolling(20).mean().shift().to_numpy()
    alta = np.abs(fh) > np.nanquantile(np.abs(fh[P == "DEV"]), 0.67)
    noticia = T.index.isin(NFP) | T.index.isin(CPI) | T.index.isin(FOMC)
    print("-- Momentum intradía (Gao+): signo(cierre ayer->10:00) x (15:30->16:00)")
    for nom, m in [("todos", np.ones(len(T), bool)), ("1ª media hora grande", alta), ("días de noticia", noticia)]:
        print(f"   {nom:22s}", " | ".join(f"{p}: {st(x[m & (P == p)])}" for p in ["DEV", "VAL1", "VAL2"]))
    # 3) LETF
    d = r("t0930", "t1530"); y = np.sign(d) * lh; grande = np.abs(d) > np.nanquantile(np.abs(d[P == "DEV"]), 0.8)
    print("-- Rebalanceo ETF apalancados: signo(09:30->15:30) x (15:30->16:00)")
    for nom, m in [("todos", np.ones(len(T), bool)), ("día con movimiento grande (top 20%)", grande)]:
        print(f"   {nom:34s}", " | ".join(f"{p}: {st(y[m & (P == p)])}" for p in ["DEV", "VAL1", "VAL2"]))
    yr = pd.Series(y[grande], index=T.index[grande]).groupby(T.index[grande].year).mean().round(1)
    print("   por año (días grandes):", yr.to_dict())
