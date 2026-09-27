"""VI A FAVOR de la tendencia con orden límite (idea del usuario).
Tendencia alcista: EMA20 > EMA50 y cierre sobre ambas. VI alcista (a favor): cuerpo actual completamente POR ENCIMA del cuerpo anterior,
mechas que se tocan. Al cierre de esa vela se coloca una COMPRA LÍMITE en el hueco (venta: todo al revés). Ventana de señales 09:31-11:29.
Variantes:
  nivel   : 'borde' = parte baja del cuerpo del VI (retroceso corto) | 'medio' = mitad del hueco | 'fondo' = parte alta del cuerpo anterior (hueco completo)
  validez : minutos que la orden sigue viva (5 / 15); se cancela si antes el precio llega al objetivo
  stop    : 'vela' = mínimo de la vela anterior al VI - 2 ticks | 'ema20' = EMA20 al colocar la orden - 2 ticks | 'atr' = 0.05 ATR bajo la entrada
  objetivo: 1R / 2R / 'máximo' = máximo de la vela VI
Relleno conservador: el límite se llena solo si el precio lo cruza 1 tick; si en la misma vela se toca el stop -> pérdida.
Salida: stop, objetivo, cierre al otro lado de cualquier EMA o 15:55. Una posición a la vez. Riesgo mínimo 4 ticks.
Elección SOLO con 2010-2018; comprobación 2019-23 y 2024-26."""
import sys, importlib, itertools
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import INSTR
vi = importlib.import_module("22_vi_usuario")

@njit
def correr(A, E20, E50, atr, t_fin, nivel, validez, stop_m, obj, tick, salida_ema):
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]): continue
        k = 1; libre = 1
        while k < t_fin:
            if k < libre: k += 1; continue
            o1 = A[di, k - 1, 0]; c1 = A[di, k - 1, 3]; h1 = A[di, k - 1, 1]; l1 = A[di, k - 1, 2]
            o = A[di, k, 0]; h = A[di, k, 1]; l = A[di, k, 2]; c = A[di, k, 3]
            up = c > E20[di, k] and c > E50[di, k] and E20[di, k] > E50[di, k]
            dn = c < E20[di, k] and c < E50[di, k] and E20[di, k] < E50[di, k]
            d = 0
            if up and min(o, c) > max(o1, c1) and l <= h1: d = 1
            elif dn and max(o, c) < min(o1, c1) and h >= l1: d = -1
            if d == 0: k += 1; continue
            borde = min(o, c) if d > 0 else max(o, c)
            fondo = max(o1, c1) if d > 0 else min(o1, c1)
            lim = borde if nivel == 0 else ((borde + fondo) / 2 if nivel == 1 else fondo)
            lim = np.round(lim / tick) * tick
            if stop_m == 0: st = (l1 - 2 * tick) if d > 0 else (h1 + 2 * tick)
            elif stop_m == 1: st = E20[di, k] - d * 2 * tick
            else: st = lim - d * 0.05 * atr[di]
            r = d * (lim - st)
            if r < 4 * tick: k += 1; continue
            if obj == 0: tg = lim + d * r
            elif obj == 1: tg = lim + d * 2 * r
            else:
                tg = h if d > 0 else l
                if d * (tg - lim) < 2 * tick: k += 1; continue
            # esperar el relleno
            j = k + 1; lleno = False
            while j <= min(k + validez, 385):
                hh = A[di, j, 1]; ll = A[di, j, 2]
                if (d > 0 and ll <= lim - tick) or (d < 0 and hh >= lim + tick):
                    lleno = True; break
                if (d > 0 and hh >= tg) or (d < 0 and ll <= tg): break
                j += 1
            if not lleno: libre = j + 1; k += 1; continue
            # en la vela de relleno: ¿stop?
            res = 0.0; mot = 0; m = j
            if (d > 0 and A[di, j, 2] <= st) or (d < 0 and A[di, j, 1] >= st):
                res = -r; mot = 4
            else:
                m = j + 1
                while m <= 385:
                    oo = A[di, m, 0]; hh = A[di, m, 1]; ll = A[di, m, 2]; cc = A[di, m, 3]
                    if (d > 0 and ll <= st) or (d < 0 and hh >= st):
                        px = st
                        if (d > 0 and oo < st) or (d < 0 and oo > st): px = oo
                        res = d * (px - lim); mot = 4; break
                    if (d > 0 and hh >= tg) or (d < 0 and ll <= tg): res = d * (tg - lim); mot = 1; break
                    if salida_ema and ((d > 0 and (cc < E20[di, m] or cc < E50[di, m])) or (d < 0 and (cc > E20[di, m] or cc > E50[di, m]))):
                        res = d * (cc - lim); mot = 2; break
                    if m == 385: res = d * (cc - lim); mot = 3
                    m += 1
            out.append((di, d, res, r, mot))
            libre = m + 1; k = m + 1
    return out

A, E20, E50, F, atr = vi.dias_con_ema("NQ"); I = INSTR["NQ"]; tick = I["tick"]; atr_hoy = float(np.nanmean(atr[-60:]))
NIV = ["borde", "medio", "fondo"]; STP = ["vela", "ema20", "0.05 ATR"]; OBJ = ["1R", "2R", "máximo VI"]
filas = []
for nivel, validez, stop_m, obj, sema in itertools.product(range(3), [5, 15], range(3), range(3), [True, False]):
    R = pd.DataFrame(correr(A, E20, E50, atr, 120, nivel, validez, stop_m, obj, tick, sema), columns=["di", "d", "res", "r", "mot"])
    if len(R) < 200: continue
    f = F[R.di.astype(int)]; esc = atr_hoy / atr[R.di.astype(int)]
    costo = I["com"] / I["usd"] + np.where(R.mot == 1, 0, 1) * tick     # entrada límite (sin desliz.), objetivo límite; stop/EMA/tiempo a mercado 1 tick
    R["R"] = (R.res - costo / esc * 0 - costo * (1 / esc) * 0) / R.r   # R bruto (costo se aplica abajo en $)
    R["usd"] = (R.res * esc - costo) * I["usd"]
    R["Rn"] = R.usd / (R.r * esc * I["usd"])
    fila = dict(nivel=NIV[nivel], validez=validez, stop=STP[stop_m], objetivo=OBJ[obj], salida_EMA=sema, n=len(R), por_dia=len(R) / len(A))
    for tag, a, b in [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]:
        x = R[(f >= a) & (f <= b)]
        fila[tag + " R"] = x.Rn.mean(); fila[tag + " WR"] = (x.usd > 0).mean(); fila[tag + " $"] = x.usd.mean()
        fila[tag + " t"] = x.Rn.mean() / x.Rn.std() * np.sqrt(len(x))
    filas.append(fila)
X = pd.DataFrame(filas).sort_values("2010-18 R", ascending=False); X.to_csv("res_31_vi_a_favor.csv", index=False)
pd.set_option("display.width", 280)
c = ["nivel", "validez", "stop", "objetivo", "salida_EMA", "por_dia", "2010-18 R", "2010-18 WR", "2010-18 t", "2019-23 R", "2019-23 t", "2024-26 R", "2024-26 WR", "2024-26 $", "2024-26 t"]
print("TOP 12 elegidas con 2010-18 (y cómo les fue después):"); print(X[c].head(12).round(3).to_string(index=False))
print("\nMedia de TODAS las variantes:", X[["2010-18 R", "2019-23 R", "2024-26 R"]].mean().round(3).to_dict())
print("Variantes positivas en los 3 periodos:", ((X["2010-18 R"] > 0) & (X["2019-23 R"] > 0) & (X["2024-26 R"] > 0)).sum(), "de", len(X))
