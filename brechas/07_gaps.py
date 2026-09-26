"""Gaps de apertura (09:30 vs cierre 16:00 de ayer), en unidades de ATR. ¿Se rellenan? Rendimiento de apostar a rellenar
(entrada 09:30, objetivo = cierre de ayer, stop simétrico = mismo tamaño del gap, salida 16:00) vs seguir el gap."""
import numpy as np, pandas as pd
from base import tramos, periodo, SYMS, cargar
from numba import njit

@njit(cache=True)
def jugar(H, L, C, e, tgt, stp, d):
    for t in range(H.shape[0]):
        if (d > 0 and L[t] <= stp) or (d < 0 and H[t] >= stp):
            return (stp - e) * d
        if (d > 0 and H[t] >= tgt) or (d < 0 and L[t] <= tgt):
            return (tgt - e) * d
    return (C[-1] - e) * d

filas = []
for s in SYMS:
    d = cargar(s, ("ts", "open", "high", "low", "close", "adj_close"))
    d["off"] = d.adj_close - d.close
    r = d[(d.m >= 570) & (d.m < 960)]
    g = dict(tuple(r.groupby("fecha")))
    fechas = sorted(g); prev_c = None; rngs = []
    for f in fechas:
        x = g[f]
        if len(x) < 385: prev_c = None; continue
        H = (x.high + x.off).to_numpy(); L = (x.low + x.off).to_numpy(); C = x.adj_close.to_numpy(); o = x.open.iloc[0] + x.off.iloc[0]
        if prev_c is not None and len(rngs) >= 14:
            atr = np.mean(rngs[-14:]); gap = o - prev_c; ga = gap / atr
            if abs(ga) > 0.05:
                dfill = -np.sign(gap)
                pnl = jugar(H, L, C, o, prev_c, o - dfill * abs(gap), dfill)   # 1:1 simétrico
                filas.append(dict(sym=s, fecha=f, gap_atr=ga, R_fill=pnl / abs(gap), ref=x.close.iloc[0]))
        prev_c = C[-1]; rngs.append(H.max() - L.min())
R = pd.DataFrame(filas); R["P"] = periodo(pd.DatetimeIndex(R.fecha))
R["b"] = pd.cut(R.gap_atr.abs(), [0.05, 0.1, 0.2, 0.3, 0.5, 5])
R["dir"] = np.where(R.gap_atr > 0, "arriba", "abajo")
t = R.groupby(["sym", "dir", "b", "P"], observed=True).R_fill.agg(["mean", "count"]).unstack("P")
pd.set_option("display.width", 250); print(t.round(2).to_string())
