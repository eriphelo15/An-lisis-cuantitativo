"""Simulador de fondeo con TRADES REALES de una estrategia (en lugar de entradas aleatorias).
Cada día simulado se toma de un día histórico (bootstrap por días) con su secuencia real de trades,
escalada al precio de hoy (puntos * ATR_hoy / ATR_día). Tamaño: riesgo fijo en USD por trade (micros o minis, sin mezclar).
Reglas Tradeify Select 50K (examen) -> Select Flex (fondeada), y Growth 50K."""
import os, sys, importlib
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "estudio_nq"))
from motor_fondeo import actualizar_piso


def biblioteca(desde, hasta, stop_modo=0, Robj=2.0, sym="NQ"):
    """Trades de la estrategia 'pullback VI en tendencia' agrupados por día, escalados al precio de hoy.
    Devuelve (inicio[ndias+1], riesgo_pts[ntr], res_pts[ntr])."""
    cwd = os.getcwd(); os.chdir(os.path.join(os.path.dirname(__file__), "..", "estudio_nq"))
    vi = importlib.import_module("22_vi_usuario"); pb = importlib.import_module("23_pullback_tendencia")
    from hougaard import INSTR
    A, E20, E50, F, atr = vi.dias_con_ema(sym)
    os.chdir(cwd)
    tick = INSTR[sym]["tick"]
    R = pd.DataFrame(np.array(pb.correr(A, E20, E50, atr, 120, stop_modo, Robj, False, tick, True)), columns=["di", "d", "res", "riesgo", "mot"])
    atr_hoy = np.nanmean(atr[-60:])
    esc = atr_hoy / atr[R.di.astype(int)]
    R["riesgo_h"] = R.riesgo * esc; R["res_h"] = R.res * esc
    dias = np.flatnonzero((F >= pd.Timestamp(desde)) & (F <= pd.Timestamp(hasta)) & ~np.isnan(atr))
    R = R[R.di.isin(dias)]
    inicio = np.zeros(len(dias) + 1, np.int64); rs, rr = [], []
    g = dict(tuple(R.groupby("di")))
    for i, d in enumerate(dias):
        if d in g:
            rs.extend(g[d].riesgo_h.tolist()); rr.extend(g[d].res_h.tolist())
        inicio[i + 1] = len(rs)
    return inicio, np.array(rs), np.array(rr)


@njit(cache=True)
def tamano(riesgo_usd, riesgo_pts, max_micro):
    n_mic = int(riesgo_usd / (riesgo_pts * 2.0 + 2.82)); n_mic = min(n_mic, max_micro)
    n_min = int(riesgo_usd / (riesgo_pts * 20.0 + 15.76)); n_min = min(n_min, max_micro // 10)
    if n_min >= 1 and n_min * 10 >= n_mic - 1:
        return float(n_min), 20.0, 15.76
    if n_mic >= 1:
        return float(n_mic), 2.0, 2.82
    return 0.0, 2.0, 2.82


@njit(cache=True)
def dia(ini, rs, rr, d, Rusd, K, G, L, dist, falta, max_micro):
    pnl = 0.0; n = 0
    for t in range(ini[d], ini[d + 1]):
        if n >= K or pnl >= G or pnl <= -L:
            break
        disp = min(L + pnl, dist + pnl - 1.0)
        c, usd, cost = tamano(min(Rusd, disp), rs[t], max_micro)
        if c <= 0:
            break
        res = rr[t]
        if falta > 0:  # en examen: tomar ganancia al llegar al objetivo si el trade lo alcanzaría
            need = (falta - pnl + cost * c) / (c * usd)
            if res >= need and need > 0:
                res = need
        pnl += res * c * usd - cost * c
        n += 1
        if pnl <= -dist:
            return pnl, True
    return pnl, False


@njit(cache=True)
def examen(ini, rs, rr, nsim, target, dd, dll, cons, min_dias, Rusd, K, G, L, max_micro, max_dias, seed):
    nd = len(ini) - 1; ok = np.zeros(nsim, np.bool_); dias = np.zeros(nsim, np.int32)
    for i in range(nsim):
        np.random.seed(seed + i)
        p = 0.0; mx = 0.0; piso = -dd; best = 0.0
        for k in range(max_dias):
            Ld = L if dll <= 0 else min(L, dll)
            Gd = G if cons <= 0 else min(G, cons * target * 0.95)
            falta = target - p if (cons <= 0 or best <= cons * target) else 0.0
            r, q = dia(ini, rs, rr, np.random.randint(nd), Rusd, K, Gd, Ld, p - piso, falta, max_micro)
            p += r; dias[i] = k + 1
            if q or p <= piso or p - piso < 150.0:
                break
            best = max(best, r); mx = max(mx, p); piso = actualizar_piso(mx, dd)
            if p >= target and k + 1 >= min_dias and (cons <= 0 or best <= cons * p):
                ok[i] = True
                break
    return ok, dias


@njit(cache=True)
def fondeada(ini, rs, rr, nsim, tipo, dd, dll, dia_min, saldo_min, cons, pmin, pmax1, pmax4, frac, colchon,
             Rusd, K, G, L, max_micro, horizonte, seed):
    """tipo 0 growth, 1 select flex. Devuelve cobrado neto, n retiros, días de vida."""
    nd = len(ini) - 1
    cob = np.zeros(nsim); nret = np.zeros(nsim, np.int32); viv = np.zeros(nsim, np.int32)
    for i in range(nsim):
        np.random.seed(seed + i)
        p = 0.0; mx = 0.0; piso = -dd; buenos = 0; ciclo = 0.0; mejor = 0.0; k = 0
        for t in range(horizonte):
            Ld = L if (dll <= 0 or p >= 3000.0) else min(L, dll)
            r, q = dia(ini, rs, rr, np.random.randint(nd), Rusd, K, G, Ld, p - piso, 0.0, max_micro)
            p += r; viv[i] = t + 1
            if q or p <= piso or p - piso < 150.0:
                break
            ciclo += r; mejor = max(mejor, r)
            if r >= dia_min:
                buenos += 1
            mx = max(mx, p); piso = actualizar_piso(mx, dd)
            m = 0.0
            if tipo == 0:
                if buenos >= 5 and p >= saldo_min and ciclo > 0 and mejor <= cons * ciclo:
                    tope = pmax1 if k < 3 else pmax4
                    m = tope if (colchon < 0 or p - tope >= colchon) else 0.0
                    m = min(m, p - 100.0)
                    if m < pmin:
                        m = 0.0
            else:
                if buenos >= 5 and p > 0:
                    m = min(pmax1, frac * p)
                    if m < 250.0:
                        m = 0.0
            if m > 0:
                p -= m; cob[i] += 0.9 * m; nret[i] += 1; k += 1; buenos = 0; ciclo = 0.0; mejor = 0.0
    return cob, nret, viv
