"""¿Qué hacer cuando, estando dentro, aparece un SEGUNDO VI en contra (misma dirección de señal)?
 modo 0: ignorarlo (VI original)
 modo 1: añadir y mover el TP de todas al nuevo hueco (lo que hace el usuario)
 modo 2: SALIR de todo al cierre de esa vela (el segundo VI indica que el retroceso es más fuerte)
Salidas normales: TP (+1 tick), cierre al otro lado de la EMA20 (o de cualquiera de las dos EMAs), 5 min desde la última entrada.
Resultados NQ en $ por operación completa con 1 NQ por entrada, a la volatilidad de hoy, con costes."""
import sys, importlib
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import INSTR
vi = importlib.import_module("22_vi_usuario")

@njit(cache=True)
def correr(A, E20, E50, atr, atr_hoy, t_fin, modo, min_rec, tick):
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]) or atr[di] <= 0: continue
        esc = atr_hoy / atr[di]
        d = 0; ents = np.zeros(8); ne = 0; tp = 0.0; t_last = 0
        for k in range(1, 389):
            o1 = A[di, k - 1, 0]; c1 = A[di, k - 1, 3]; h1 = A[di, k - 1, 1]; l1 = A[di, k - 1, 2]
            o = A[di, k, 0]; h = A[di, k, 1]; l = A[di, k, 2]; c = A[di, k, 3]
            salio = False
            if d != 0:
                px = 0.0; mot = 0
                if (d > 0 and h >= tp + tick) or (d < 0 and l <= tp - tick): px = tp; mot = 1
                elif (d > 0 and (c < E20[di, k] or c < E50[di, k])) or (d < 0 and (c > E20[di, k] or c > E50[di, k])): px = c; mot = 2
                elif k - t_last >= 5: px = c; mot = 3
                if mot > 0:
                    tot = 0.0
                    for j in range(ne): tot += d * (px - ents[j])
                    out.append((di, k, d, ne, tot, mot)); d = 0; ne = 0; salio = True
            if salio or k >= t_fin: continue
            up = c > E20[di, k] and c > E50[di, k] and E20[di, k] > E50[di, k]
            dn = c < E20[di, k] and c < E50[di, k] and E20[di, k] < E50[di, k]
            s = 0; ntp = 0.0
            if up and max(o, c) < min(o1, c1) and h >= l1: s = 1; ntp = max(o, c)
            elif dn and min(o, c) > max(o1, c1) and l <= h1: s = -1; ntp = min(o, c)
            if s == 0 or abs(ntp - c) < tick or abs(ntp - c) * esc < min_rec: continue
            if d == 0:
                d = s; ents[0] = c; ne = 1; tp = ntp; t_last = k
            elif s == d:
                if modo == 1 and ne < 4:
                    ents[ne] = c; ne += 1; tp = ntp; t_last = k
                elif modo == 2:
                    tot = 0.0
                    for j in range(ne): tot += d * (c - ents[j])
                    out.append((di, k, d, ne, tot, 4)); d = 0; ne = 0
    return out

A, E20, E50, F, atr = vi.dias_con_ema("NQ"); I = INSTR["NQ"]; tick = I["tick"]; atr_hoy = float(np.nanmean(atr[-60:]))
for min_rec in [0.0, 3.0]:
    print(f"\n=== recorrido mínimo al TP: {min_rec} pts ===")
    for modo, nom in [(0, "ignorar el 2º VI (original)"), (1, "AÑADIR en el 2º VI (usuario)"), (2, "SALIR en el 2º VI")]:
        R = pd.DataFrame(correr(A, E20, E50, atr, atr_hoy, 120, modo, min_rec, tick), columns=["di", "k", "d", "nc", "pts", "mot"])
        R["f"] = F[R.di.astype(int)]; esc = atr_hoy / atr[R.di.astype(int)]
        cpc = I["com"] / I["usd"] + np.where(R.mot == 1, 1, 2) * tick
        R["usd"] = (R.pts * esc - R.nc * cpc) * I["usd"]
        out = []
        for tag, a, b in [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]:
            x = R.usd[(R.f >= a) & (R.f <= b)]
            out.append(f"{tag}: {100*(x>0).mean():4.1f}% {x.mean():+6.1f}$ (t {x.mean()/x.std()*np.sqrt(len(x)):+.1f})")
        w = R.usd[R.usd > 0]; lo = R.usd[R.usd <= 0]
        print(f"  {nom:30s}", " | ".join(out), f"| gan {w.mean():.0f} perd {lo.mean():.0f} peor {R.usd.min():.0f}")
