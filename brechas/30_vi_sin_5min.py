"""VI original (añadidos + salida por cualquier EMA) con PROTECCIONES contra las pérdidas grandes:
 - stop duro: todas las posiciones se cierran si el precio va k·ATR en contra de la PRIMERA entrada (se comprueba antes que el TP)
 - máximo de añadidos (0, 1, 3)
 - no operar días de VIX alto (VIX del cierre anterior > percentil p de 2010-2018)
Elección SOLO con 2010-2018; resultado en 2019-2023 y 2024-2026 se mira después."""
import sys, importlib
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import INSTR
from externos import externos
vi = importlib.import_module("22_vi_usuario")

@njit
def correr(A, E20, E50, atr, t_fin, stop_k, max_add, dia_ok, tick, tmax):
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]) or not dia_ok[di]: continue
        d = 0; ents = np.zeros(8); ne = 0; tp = 0.0; t_last = 0; st = 0.0
        for k in range(1, 389):
            o1 = A[di, k - 1, 0]; c1 = A[di, k - 1, 3]; h1 = A[di, k - 1, 1]; l1 = A[di, k - 1, 2]
            o = A[di, k, 0]; h = A[di, k, 1]; l = A[di, k, 2]; c = A[di, k, 3]
            salio = False
            if d != 0:
                px = 0.0; mot = 0
                if stop_k > 0 and ((d > 0 and l <= st) or (d < 0 and h >= st)):
                    px = st
                    if (d > 0 and o < st) or (d < 0 and o > st): px = o
                    mot = 4
                elif (d > 0 and h >= tp + tick) or (d < 0 and l <= tp - tick): px = tp; mot = 1
                elif (d > 0 and (c < E20[di, k] or c < E50[di, k])) or (d < 0 and (c > E20[di, k] or c > E50[di, k])): px = c; mot = 2
                elif k - t_last >= tmax or k == 385: px = c; mot = 3
                if mot > 0:
                    tot = 0.0
                    for j in range(ne): tot += d * (px - ents[j])
                    out.append((di, d, ne, tot, mot)); d = 0; ne = 0; salio = True
            if salio or k >= t_fin: continue
            up = c > E20[di, k] and c > E50[di, k] and E20[di, k] > E50[di, k]
            dn = c < E20[di, k] and c < E50[di, k] and E20[di, k] < E50[di, k]
            s = 0; ntp = 0.0
            if up and max(o, c) < min(o1, c1) and h >= l1: s = 1; ntp = max(o, c)
            elif dn and min(o, c) > max(o1, c1) and l <= h1: s = -1; ntp = min(o, c)
            if s == 0 or abs(ntp - c) < tick: continue
            if d == 0:
                d = s; ents[0] = c; ne = 1; tp = ntp; t_last = k; st = c - d * stop_k * atr[di]
            elif s == d and ne < 1 + max_add:
                ents[ne] = c; ne += 1; tp = ntp; t_last = k
    return out

A, E20, E50, F, atr = vi.dias_con_ema("NQ"); I = INSTR["NQ"]; tick = I["tick"]; atr_hoy = float(np.nanmean(atr[-60:]))
vix = externos(F).VIX.to_numpy(); dev = F <= "2018-12-31"
filas = []
TMAX = [5, 10, 15, 30, 9999]
for tmax in TMAX:
    for stop_k in [0.0, 0.12]:
        for max_add in [0, 3]:
            ok = np.ones(len(A), bool)
            R = pd.DataFrame(correr(A, E20, E50, atr, 120, stop_k, max_add, ok, tick, tmax), columns=["di", "d", "nc", "pts", "mot"])
            f = F[R.di.astype(int)]; esc = atr_hoy / atr[R.di.astype(int)]
            R["usd"] = (R.pts * esc - R.nc * (I["com"] / I["usd"] + np.where(R.mot == 1, 1, 2) * tick)) * I["usd"]
            fila = dict(limite_tiempo="sin límite" if tmax > 1000 else f"{tmax} min", stop_pts_hoy=round(stop_k * atr_hoy), max_add=max_add,
                        pct_TP=(R.mot == 1).mean(), pct_EMA=(R.mot == 2).mean(), pct_stop=(R.mot == 4).mean())
            for tag, a_, b_ in [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]:
                x = R.usd[(f >= a_) & (f <= b_)]
                fila[tag] = x.mean(); fila[tag + " WR"] = (x > 0).mean(); fila[tag + " t"] = x.mean() / x.std() * np.sqrt(len(x))
            w = R.usd[R.usd > 0]; lo = R.usd[R.usd <= 0]
            fila["gan_media"] = w.mean(); fila["perd_media"] = lo.mean(); fila["peor"] = R.usd.min()
            filas.append(fila)
X = pd.DataFrame(filas); X.to_csv("res_30_vi_sin_5min.csv", index=False)
pd.set_option("display.width", 260)
print(X.round(2).to_string(index=False))
