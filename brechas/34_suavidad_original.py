"""VI ORIGINAL (todas las señales en tendencia 09:31-11:29, una posición a la vez) con gestión de salida parcial.
Medidas de tranquilidad: acierto, % meses positivos, peor racha, caída máxima, suavidad (R² de la curva). $ por operación con 1 NQ equivalente
(mitades = 0.5 NQ, p. ej. 5+5 MNQ), a la volatilidad de hoy, costes: comisión 1 NQ + 1 tick por salida a mercado.
 M0 original: TP en el hueco (todo), salida si cierra al otro lado de cualquier EMA, o 5 min. Sin stop.
 M1 mitad en el hueco + BE; antes del parcial: stop en EMA50 -2 ticks (sin regla de 5 min); resto hasta las 15:55
 M2 igual que M1 pero el resto sale a 2R (R = distancia al stop EMA50)
 M3 mitad en el hueco + BE; antes del parcial: reglas originales (EMA / 5 min) para todo; resto hasta las 15:55
 M4 mitad en el hueco + BE; antes del parcial: stop EMA50; resto sale si cierra al otro lado de la EMA20 (trailing) o 15:55
 M5 igual que M1 pero con stop duro de 41 pts (0.12 ATR) en lugar de EMA50"""
import sys, importlib
import numpy as np, pandas as pd
sys.path.insert(0, "../estudio_nq")
vi = importlib.import_module("22_vi_usuario")
A, E20, E50, F, atr = vi.dias_con_ema("NQ"); tick = 0.25; atr_hoy = float(np.nanmean(atr[-60:]))

def dia(di, modo):
    ops = []; k = 1
    while k < 120:
        o1, h1, l1, c1 = A[di, k - 1]; o, h, l, c = A[di, k]; e20, e50 = E20[di, k], E50[di, k]
        d = 0
        if e20 > e50 and c > e20 and c > e50 and max(o, c) < min(o1, c1) and h >= l1: d, tp = 1, max(o, c)
        elif e20 < e50 and c < e20 and c < e50 and min(o, c) > max(o1, c1) and l <= h1: d, tp = -1, min(o, c)
        if d == 0 or abs(tp - c) < tick: k += 1; continue
        e = c; st = e50 - d * 2 * tick if modo != 5 else e - d * 0.12 * atr[di]; rk = abs(e - st)
        if rk < 4 * tick: st = e - d * 4 * tick; rk = 4 * tick
        parte = 0.0; hecho = False; res = None; nsal = 0; j = k + 1
        while j <= 385:
            oo, hh, ll, cc = A[di, j]
            if modo == 0:
                if (d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick): res = d * (tp - e); break
                if (d > 0 and (cc < E20[di, j] or cc < E50[di, j])) or (d < 0 and (cc > E20[di, j] or cc > E50[di, j])): res = d * (cc - e); nsal = 1; break
                if j - k >= 5: res = d * (cc - e); nsal = 1; break
                j += 1; continue
            stop_now = e if hecho else st
            if not hecho and modo == 3:
                if (d > 0 and (cc < E20[di, j] or cc < E50[di, j])) or (d < 0 and (cc > E20[di, j] or cc > E50[di, j])) or j - k >= 5:
                    if not ((d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick)):
                        res = d * (cc - e); nsal = 1; break
            if (modo != 3 or hecho) and ((d > 0 and ll <= stop_now) or (d < 0 and hh >= stop_now)):
                px = oo if ((d > 0 and oo < stop_now) or (d < 0 and oo > stop_now)) else stop_now
                res = parte + (0.5 if hecho else 1) * d * (px - e); nsal = 1; break
            if not hecho and ((d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick)):
                hecho = True; parte = 0.5 * d * (tp - e)
            elif hecho:
                if modo == 2 and ((d > 0 and hh >= e + 2 * d * rk) or (d < 0 and ll <= e + 2 * d * rk)): res = parte + 0.5 * 2 * rk; break
                if modo == 4 and ((d > 0 and cc < E20[di, j]) or (d < 0 and cc > E20[di, j])): res = parte + 0.5 * d * (cc - e); nsal = 1; break
            j += 1
        if res is None: res = parte + (0.5 if hecho else 1) * d * (A[di, 385, 3] - e); nsal = 1
        ops.append((res, nsal)); k = j + 1
    return ops

NOM = {0: "M0 original (TP hueco, EMA, 5 min)", 1: "M1 mitad en hueco+BE, stop EMA50, resto al cierre", 2: "M2 mitad en hueco+BE, stop EMA50, resto 2R",
       3: "M3 mitad en hueco+BE, reglas originales, resto al cierre", 4: "M4 mitad en hueco+BE, stop EMA50, resto trailing EMA20",
       5: "M5 mitad en hueco+BE, stop 41 pts, resto al cierre"}
filas = []
for modo in NOM:
    rows = []
    for di in range(len(A)):
        if np.isnan(atr[di]): continue
        esc = atr_hoy / atr[di]
        for res, nsal in dia(di, modo):
            rows.append((F[di], (res * esc - nsal * tick - tick * 0) * 20 - 5.76))
    X = pd.DataFrame(rows, columns=["f", "usd"])
    m = X.groupby(X.f.dt.to_period("M")).usd.sum(); eq = X.usd.cumsum().to_numpy(); dd = (np.maximum.accumulate(eq) - eq).max()
    racha = mx = 0
    for v in X.usd: racha = racha + 1 if v < 0 else 0; mx = max(mx, racha)
    fila = dict(gestión=NOM[modo], ops=len(X), acierto=(X.usd > 0).mean(), usd_medio=X.usd.mean(), meses_pos=(m > 0).mean(), peor_racha=mx,
                caida_max_usd=dd, suavidad_R2=np.corrcoef(np.arange(len(eq)), eq)[0, 1] ** 2 * np.sign(eq[-1]), peor_op=X.usd.min())
    for tag, a, b in [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]:
        fila[tag] = X.usd[(X.f >= a) & (X.f <= b)].mean()
    filas.append(fila); print(modo, flush=True)
T = pd.DataFrame(filas); T.to_csv("res_34_suavidad_original.csv", index=False)
pd.set_option("display.width", 260); print(T.round(3).to_string(index=False))
