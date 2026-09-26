"""VI original con los matices del usuario:
 (1) recorrido mínimo al TP: no operar si |TP - cierre| < X puntos (a la escala de volatilidad de hoy);
 (2) añadir: si aparece un NUEVO VI en la misma dirección estando dentro, se abre otra posición al cierre de esa vela
     y el TP de TODAS pasa al borde del nuevo hueco. El reloj de 5 min se reinicia desde la última entrada.
     Salidas (para todas): TP tocado (+1 tick), cierre al otro lado de la EMA20, o 5 min desde la última entrada.
Supuesto: el recorrido mínimo se exige también a los añadidos. Resultados por contrato y por 'grupo' (operación completa)."""
import sys, importlib
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import INSTR
vi = importlib.import_module("22_vi_usuario")

@njit(cache=True)
def correr(A, E20, E50, atr, atr_hoy, t_fin, min_rec, max_add, tick):
    out = []   # (di, n_primera, d, n_contratos, pnl_total_pts, motivo)
    for di in range(A.shape[0]):
        if np.isnan(atr[di]) or atr[di] <= 0: continue
        esc = atr_hoy / atr[di]
        d = 0; ents = np.zeros(8); ne = 0; tp = 0.0; t_last = 0; n0 = 0
        k = 1
        while k < 389:
            o1 = A[di, k - 1, 0]; c1 = A[di, k - 1, 3]; h1 = A[di, k - 1, 1]; l1 = A[di, k - 1, 2]
            o = A[di, k, 0]; h = A[di, k, 1]; l = A[di, k, 2]; c = A[di, k, 3]
            salio = False
            if d != 0:
                px = 0.0; mot = 0
                if (d > 0 and h >= tp + tick) or (d < 0 and l <= tp - tick): px = tp; mot = 1
                elif (d > 0 and c < E20[di, k]) or (d < 0 and c > E20[di, k]): px = c; mot = 2
                elif k - t_last >= 5: px = c; mot = 3
                if mot > 0:
                    tot = 0.0
                    for j in range(ne): tot += d * (px - ents[j])
                    out.append((di, n0, d, ne, tot, mot))
                    d = 0; ne = 0; salio = True
            if not salio and k < t_fin:
                up = c > E20[di, k] and c > E50[di, k] and E20[di, k] > E50[di, k]
                dn = c < E20[di, k] and c < E50[di, k] and E20[di, k] < E50[di, k]
                s = 0; ntp = 0.0
                if up and max(o, c) < min(o1, c1) and h >= l1: s = 1; ntp = max(o, c)
                elif dn and min(o, c) > max(o1, c1) and l <= h1: s = -1; ntp = min(o, c)
                if s != 0 and abs(ntp - c) >= tick and abs(ntp - c) * esc >= min_rec:
                    if d == 0:
                        d = s; ents[0] = c; ne = 1; tp = ntp; t_last = k; n0 = k
                    elif s == d and ne < 1 + max_add:
                        ents[ne] = c; ne += 1; tp = ntp; t_last = k
            k += 1
        if d != 0:
            tot = 0.0
            for j in range(ne): tot += d * (A[di, 388, 3] - ents[j])
            out.append((di, n0, d, ne, tot, 3))
    return out

A, E20, E50, F, atr = vi.dias_con_ema("NQ"); I = INSTR["NQ"]; tick = I["tick"]
atr_hoy = float(np.nanmean(atr[-60:]))
filas = []
for min_rec in [0.0, 3.0, 5.0, 8.0, 12.0]:
    for max_add in [0, 1, 2, 3]:
        R = pd.DataFrame(correr(A, E20, E50, atr, atr_hoy, 120, min_rec, max_add, tick), columns=["di", "n", "d", "nc", "pts", "mot"])
        R["f"] = F[R.di.astype(int)]; esc = atr_hoy / atr[R.di.astype(int)]
        # coste por contrato: comisión + 1 tick (salida TP limit) o 2 ticks (salida a mercado)
        cpc = I["com"] / I["usd"] + np.where(R.mot == 1, 1, 2) * tick
        R["usd"] = (R.pts * esc - R.nc * cpc) * I["usd"]
        fila = dict(min_rec_pts=min_rec, max_añadidos=max_add, grupos=len(R), contratos_medios=R.nc.mean())
        for tag, a, b in [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]:
            x = R[(R.f >= a) & (R.f <= b)]
            fila[f"{tag} acierto"] = (x.usd > 0).mean(); fila[f"{tag} $/grupo"] = x.usd.mean()
            fila[f"{tag} $/contrato"] = x.usd.sum() / x.nc.sum(); fila[f"{tag} t"] = x.usd.mean() / x.usd.std() * np.sqrt(len(x))
        w = R.usd[R.usd > 0]; lo = R.usd[R.usd <= 0]
        fila["gan_media"] = w.mean(); fila["perd_media"] = lo.mean(); fila["peor"] = R.usd.min()
        filas.append(fila); print(min_rec, max_add, flush=True)
X = pd.DataFrame(filas); X.to_csv("res_25_vi_matices.csv", index=False)
pd.set_option("display.width", 260)
print(X.round(2).to_string(index=False))
