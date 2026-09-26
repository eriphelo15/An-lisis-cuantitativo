"""La volatilidad SÍ es predecible (la dirección no). ¿Se puede elegir entre 'romper' y 'desvanecer' el rango inicial
según la expansión de rango esperada?
Estrategia base: rango 09:30-09:45; bracket: largo sobre el máximo / corto bajo el mínimo, stop = otro extremo, salida 16:00.
Su resultado depende de si el día 'se expande'. Predictores (conocidos a las 09:45): rango nocturno/ATR, rango 15min/ATR,
VIX9D/VIX, cambio VIX, día de noticia 08:30 (volumen 08:30 anómalo)."""
import numpy as np, pandas as pd
from base import cargar, periodo, SYMS, COSTO_PTS
from externos import externos
from numba import njit

@njit(cache=True)
def bracket(H, L, C, hi, lo, t0):
    for t in range(t0, H.shape[0]):
        if H[t] >= hi and L[t] <= lo:
            return -1.0  # ambos en la misma barra: pérdida conservadora
        if H[t] >= hi:
            for u in range(t + 1 if L[t] > lo else t, H.shape[0]):
                if L[u] <= lo: return -1.0
            return (C[-1] - hi) / (hi - lo)
        if L[t] <= lo:
            for u in range(t + 1 if H[t] < hi else t, H.shape[0]):
                if H[u] >= hi: return -1.0
            return (lo - C[-1]) / (hi - lo)
    return 0.0

filas = []
for s in SYMS:
    d = cargar(s, ("ts", "high", "low", "close", "adj_close", "volume"))
    d["off"] = d.adj_close - d.close
    g = dict(tuple(d.groupby("fecha")))
    rngs = []; vol830 = []
    for f in sorted(g):
        x = g[f]; r = x[(x.m >= 570) & (x.m < 960)]
        if len(r) < 385: continue
        H = (r.high + r.off).to_numpy(); L = (r.low + r.off).to_numpy(); C = r.adj_close.to_numpy()
        on = x[x.m < 570]
        v830 = x[(x.m >= 510) & (x.m < 515)].volume.sum(); vpre = x[(x.m >= 480) & (x.m < 510)].volume.sum() / 6
        if len(rngs) >= 20:
            atr = np.mean(rngs[-14:]); hi, lo = H[:15].max(), L[:15].min()
            if hi - lo > 0:
                R = bracket(H, L, C, hi, lo, 15)
                costo = COSTO_PTS[s] / (hi - lo)
                filas.append(dict(sym=s, fecha=f, R=R - costo, or_atr=(hi - lo) / atr,
                                  noche_atr=(on.high.max() - on.low.min()) / atr if len(on) else np.nan,
                                  noticia=v830 / max(vpre, 1), rango_dia_atr=(H.max() - L.min()) / atr))
        rngs.append(H.max() - L.min())
D = pd.DataFrame(filas); D["P"] = periodo(pd.DatetimeIndex(D.fecha))
X = externos(pd.DatetimeIndex(D.fecha)); D["ratio9d"] = X.ratio_9d.to_numpy(); D["dvix"] = X.dvix.to_numpy()
D.to_csv("res_09_orb_vol.csv", index=False)
print("Correlación de predictores con rango del día/ATR (¿es predecible la volatilidad?):")
print(D[["or_atr", "noche_atr", "noticia", "ratio9d", "dvix", "rango_dia_atr"]].corr().rango_dia_atr.round(2).to_dict())
print("\nORB bracket (R neto) por terciles de cada predictor (cortes en DEV):")
for v in ["or_atr", "noche_atr", "noticia", "ratio9d", "dvix"]:
    for s in SYMS:
        Z = D[D.sym == s]; q = Z[Z.P == "DEV"][v].quantile([1/3, 2/3]).to_numpy()
        b = np.where(Z[v] <= q[0], "bajo", np.where(Z[v] >= q[1], "alto", "medio"))
        t = Z.groupby([b, Z.P]).R.mean().unstack().round(3)
        print(v, s, t.to_dict("index"))
print("\nbase:", D.groupby(["sym", "P"]).R.mean().unstack().round(3).to_dict("index"))
