"""Estrategia candidata del escaneo: 'comprar la caída nocturna'.
Si entre las 18:00 y la hora de entrada la sesión nocturna cae (tercil inferior, corte fijado en DEV), comprar y salir 2 h después.
Stop protector = 0.15 ATR (ATR = rango RTH medio 14 días). Costos: comisión + 1 tick por lado. Horas de entrada probadas: 00:30 y 05:30.
Se mide en R (riesgo = distancia al stop) y en USD por MNQ a precios de hoy."""
import numpy as np, pandas as pd
from numba import njit
from base import cargar, periodo, COSTO_PTS, USD_PT
from externos import externos

@njit(cache=True)
def largo(H, L, C, e, stop, tfin):
    for t in range(H.shape[0]):
        if t >= tfin: return C[tfin - 1] - e if tfin > 0 else 0.0
        if L[t] <= stop: return stop - e
    return C[-1] - e

def correr(sym, t_ent, h=120, k_stop=0.15, verbose=True):
    d = cargar(sym, ("ts", "open", "high", "low", "close", "adj_close"))
    d["off"] = d.adj_close - d.close
    for c in ["open", "high", "low"]: d[c] += d.off
    g = dict(tuple(d.groupby("fecha")))
    filas = []; rngs = []
    for f in sorted(g):
        x = g[f]
        r = x[(x.m >= 570) & (x.m < 960)]
        n18 = x[x.m == -360]; ne = x[x.m == t_ent]
        if len(rngs) >= 14 and len(n18) and len(ne):
            atr = np.mean(rngs[-14:])
            e = ne.open.iloc[0]; mov = (e - n18.open.iloc[0]) / atr
            w = x[(x.m >= t_ent) & (x.m < t_ent + h)]
            if len(w) > h * 0.8:
                stop = e - k_stop * atr
                pnl = largo(w.high.to_numpy(), w.low.to_numpy(), w.adj_close.to_numpy(), e, stop, len(w))
                filas.append(dict(fecha=f, mov=mov, pts=pnl - COSTO_PTS[sym], riesgo=k_stop * atr, atr=atr, real=ne.close.iloc[0]))
        if len(r) >= 385: rngs.append(r.high.max() - r.low.min())
    D = pd.DataFrame(filas); D["P"] = periodo(pd.DatetimeIndex(D.fecha)); D["R"] = D.pts / D.riesgo
    q = D[D.P == "DEV"].mov.quantile(1/3)
    S = D[D.mov <= q].copy()
    atr_hoy = D.atr.iloc[-60:].mean()
    S["usd_mnq_hoy"] = S.R * k_stop * atr_hoy * USD_PT[sym] / 10
    if verbose:
        print(f"{sym} entrada {t_ent} (min rel.), corte caída DEV = {q:.3f} ATR; ATR hoy {atr_hoy:.0f} pts")
        for p in ["DEV", "VAL1", "VAL2"]:
            z = S[S.P == p]
            print(f"  {p}: n={len(z)} WR={100*(z.R>0).mean():.0f}% R medio={z.R.mean():+.3f} t={z.R.mean()/z.R.std()*np.sqrt(len(z)):+.1f}  USD/MNQ hoy={z.usd_mnq_hoy.mean():+.1f}")
        yrs = S.groupby(pd.DatetimeIndex(S.fecha).year).R.mean(); print("  años positivos:", (yrs > 0).sum(), "/", len(yrs))
    return S

if __name__ == "__main__":
    out = []
    for sym in ["NQ", "ES", "YM"]:
        for t in [30, 330]:
            S = correr(sym, t); S["sym"] = sym; S["t"] = t; out.append(S)
    pd.concat(out).to_csv("res_10_noche_dip.csv", index=False)
