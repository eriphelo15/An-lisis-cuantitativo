"""Simulador de trades sobre barras de 1 minuto (numba).

Supuestos conservadores:
  * Entrada a mercado en el OPEN de la barra siguiente a la señal.
  * Si en una misma barra se tocan stop y target -> se asume STOP primero.
  * Stops/targets en puntos relativos al precio de entrada.
  * Salida por tiempo al CLOSE de la barra de salida (hm_exit) o fin de RTH.
  * Costo fijo por trade restado al final (lib.COSTO_MKT_RT_PTS por defecto).
"""
import numpy as np
from numba import njit


@njit(cache=True)
def simulate(o, h, l, c, day_id, hm, sig_idx, direction, stop_pts, tgt_pts, hm_exit, cost):
    n = len(sig_idx)
    pnl = np.full(n, np.nan)
    bars = np.zeros(n, np.int32)
    outcome = np.zeros(n, np.int8)   # 1 target, -1 stop, 0 tiempo
    N = len(o)
    for k in range(n):
        i = sig_idx[k] + 1
        if i >= N or day_id[i] != day_id[sig_idx[k]]:
            continue
        d = direction[k]
        e = o[i]
        sp = stop_pts[k]; tp = tgt_pts[k]
        stop = e - d * sp
        tgt = e + d * tp
        j = i
        res = np.nan
        while j < N and day_id[j] == day_id[i]:
            if d == 1:
                hit_s = l[j] <= stop
                hit_t = h[j] >= tgt
            else:
                hit_s = h[j] >= stop
                hit_t = l[j] <= tgt
            if hit_s:
                # gap a través del stop: se ejecuta al peor de stop/open
                px = stop
                if j > i and ((d == 1 and o[j] < stop) or (d == -1 and o[j] > stop)):
                    px = o[j]
                res = d * (px - e); outcome[k] = -1; break
            if hit_t:
                res = tp; outcome[k] = 1; break
            if hm[j] >= hm_exit[k] or j + 1 >= N or day_id[j + 1] != day_id[i]:
                res = d * (c[j] - e); outcome[k] = 0; break
            j += 1
        pnl[k] = res - cost
        bars[k] = j - i + 1
    return pnl, bars, outcome


@njit(cache=True)
def simulate_limit(o, h, l, c, day_id, hm, sig_idx, direction, limit_px, hm_cancel,
                   stop_pts, tgt_pts, hm_exit, cost):
    """Entrada con orden LIMIT en limit_px, activa desde la barra siguiente a la señal
    hasta hm_cancel. Fill solo si el precio atraviesa el límite en >= 1 tick (conservador).
    """
    n = len(sig_idx)
    pnl = np.full(n, np.nan)
    outcome = np.zeros(n, np.int8)
    N = len(o)
    for k in range(n):
        i = sig_idx[k] + 1
        if i >= N or day_id[i] != day_id[sig_idx[k]]:
            continue
        d = direction[k]; lp = limit_px[k]
        j = i; filled = -1
        while j < N and day_id[j] == day_id[i] and hm[j] <= hm_cancel[k]:
            if (d == 1 and l[j] <= lp - 0.25) or (d == -1 and h[j] >= lp + 0.25):
                filled = j; break
            j += 1
        if filled < 0:
            continue
        e = lp
        if (d == 1 and o[filled] < lp) or (d == -1 and o[filled] > lp):
            e = o[filled]  # abrió mejor que el límite
        stop = e - d * stop_pts[k]; tgt = e + d * tgt_pts[k]
        j = filled; res = np.nan; first = True
        while j < N and day_id[j] == day_id[i]:
            if d == 1:
                hit_s = l[j] <= stop; hit_t = h[j] >= tgt
            else:
                hit_s = h[j] >= stop; hit_t = l[j] <= tgt
            if first:
                # en la barra de fill no sabemos el orden: solo cuenta el stop
                hit_t = False
                first = False
            if hit_s:
                px = stop
                if (d == 1 and o[j] < stop) or (d == -1 and o[j] > stop):
                    px = o[j]
                res = d * (px - e); outcome[k] = -1; break
            if hit_t:
                res = tgt_pts[k]; outcome[k] = 1; break
            if hm[j] >= hm_exit[k] or j + 1 >= N or day_id[j + 1] != day_id[i]:
                res = d * (c[j] - e); outcome[k] = 0; break
            j += 1
        pnl[k] = res - cost
    return pnl, outcome
