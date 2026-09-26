"""Bloques candidatos como operaciones reales (NQ), en R con costo de HOY (el costo en R depende del precio; se evalúa como hoy):
 A pullback VI filtrado (día)             -> de estudio_nq (pullback_señales_nq.parquet + filtros fijados en DEV)
 B compra de caída nocturna 00:30 y 05:30 -> 10_noche_dip
 C deriva pre-FOMC: largo 18:00 -> 14:00 del día FOMC, stop 0.5 ATR
 D post-cierre: largo 16:00 -> 16:59, stop 0.1 ATR
Salida: tabla de operaciones (fecha, bloque, R_bruto, riesgo_atr) para combinar y simular fondeo."""
import numpy as np, pandas as pd, importlib
from numba import njit
from base import cargar, periodo, COSTO_PTS
from calendario import FOMC
nd = importlib.import_module("10_noche_dip")

@njit(cache=True)
def largo(H, L, C, e, stop):
    for t in range(H.shape[0]):
        if L[t] <= stop: return stop - e
    return C[-1] - e

def ventana(sym, a, b, k_stop, filtro_fechas=None):
    d = cargar(sym, ("ts", "open", "high", "low", "close", "adj_close"))
    d["off"] = d.adj_close - d.close
    for c in ["open", "high", "low"]: d[c] += d.off
    g = dict(tuple(d.groupby("fecha"))); filas = []; rngs = []
    for f in sorted(g):
        x = g[f]; r = x[(x.m >= 570) & (x.m < 960)]
        if len(rngs) >= 14 and (filtro_fechas is None or f in filtro_fechas):
            w = x[(x.m >= a) & (x.m < b)]
            if len(w) > 0.8 * (b - a) and w.m.iloc[0] <= a + 2:
                atr = np.mean(rngs[-14:]); e = w.open.iloc[0]
                pnl = largo(w.high.to_numpy(), w.low.to_numpy(), w.adj_close.to_numpy(), e, e - k_stop * atr)
                filas.append(dict(fecha=f, R_bruto=pnl / (k_stop * atr), riesgo_atr=k_stop))
        if len(r) >= 385: rngs.append(r.high.max() - r.low.min())
    return pd.DataFrame(filas)

ATR_HOY = 364.0; COSTO = COSTO_PTS["NQ"]
bloques = []
# A
S = pd.read_parquet("/home/user/data/pullback_señales_nq.parquet")
A = S[(S.dist_ema50_R > 0.0689) & (S.pend20_a_favor > 0.074) & (S.mov_apertura_a_favor > 0.1582)].copy()
A = A.sort_values(["f", "min_desde_apertura"]).groupby("f").head(1)          # 1 operación al día
# R bruto = R_neto + costo en R de aquella época; riesgo en ATR = dist_ema50_R
A_R_bruto = A.res / A.rk if "rk" in A else None
bloques.append(pd.DataFrame(dict(fecha=A.f.to_numpy(), bloque="A pullback VI", R_bruto=(A.res / A.rk).to_numpy(), riesgo_atr=A.dist_ema50_R.to_numpy())))
# B
for t in [30, 330]:
    Bn = nd.correr("NQ", t, verbose=False)
    bloques.append(pd.DataFrame(dict(fecha=Bn.fecha, bloque=f"B noche {'00:30' if t == 30 else '05:30'}",
                                     R_bruto=((Bn.pts + COSTO) / Bn.riesgo).to_numpy(), riesgo_atr=0.15)))
# C
C = ventana("NQ", -360, 840, 0.5, set(FOMC)); C["bloque"] = "C pre-FOMC"; bloques.append(C)
# D
Dd = ventana("NQ", 960, 1019, 0.1); Dd["bloque"] = "D post-cierre"; bloques.append(Dd)
T = pd.concat(bloques, ignore_index=True)
T["fecha"] = pd.to_datetime(T.fecha)
T["R"] = T.R_bruto - COSTO / (T.riesgo_atr * ATR_HOY)
T["P"] = periodo(pd.DatetimeIndex(T.fecha))
T.to_csv("res_11_bloques.csv", index=False)
pd.set_option("display.width", 200)
r = T.groupby(["bloque", "P"]).R.agg(["count", "mean", lambda z: z.mean() / z.std() * np.sqrt(len(z)), lambda z: (z > 0).mean()])
r.columns = ["n", "R_medio", "t", "WR"]; print(r.round(3).unstack("P").to_string())
