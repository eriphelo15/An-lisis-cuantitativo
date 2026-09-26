"""Estrategias de Tom Hougaard codificadas de forma mecánica y evaluadas sobre NQ, ES e YM (15 años).

Motor 'bracket': con una vela señal se colocan órdenes stop por encima (largo) y por debajo (corto).
Supuestos conservadores sobre barras de 1 minuto:
  * Fill en el nivel (o en el open si la barra abre más allá) + 1 tick de deslizamiento (incluido en costo).
  * En la barra del fill, si también se toca el stop -> stop.
  * Stop y objetivo en la misma barra -> stop.
  * Stop-and-reverse opcional: si el stop coincide con el nivel opuesto, se abre la operación contraria.
  * Salida por tiempo a las 15:55 ET.
Costos por contrato en puntos del instrumento: comisión all-in + 1 tick por lado.
"""
import os, sys
import numpy as np, pandas as pd
from numba import njit

INSTR = {  # tick, $ por punto, comisión RT (USD, all-in Tradeify)
    "NQ": dict(tick=0.25, usd=20.0, com=5.76, parquet="nq15_1m.parquet"),
    "ES": dict(tick=0.25, usd=50.0, com=5.76, parquet="es15_1m.parquet"),
    "YM": dict(tick=1.0, usd=5.0, com=5.76, parquet="ym15_1m.parquet"),
}
PERIODOS = [("DEV", "2010-10-01", "2018-12-31"), ("VAL1", "2019-01-01", "2021-03-12"), ("VAL2", "2021-03-13", "2026-03-13")]


def cargar_dias(sym):
    """Días RTH completos: matriz (n, 390, 4) en puntos reales, más ATR diario (14d) y fechas."""
    f = os.path.join(os.environ.get("NQ_DATA_DIR", "/home/user/data"), INSTR[sym]["parquet"])
    cache = f.replace(".parquet", "_rth.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        return z["A"], z["atr"], pd.DatetimeIndex(z["fechas"]), z["prev_c"]
    df = pd.read_parquet(f, columns=["ts", "open", "high", "low", "close", "seg"])
    hm = df.ts.dt.hour * 100 + df.ts.dt.minute
    df = df[(hm >= 930) & (hm < 1600)].copy()
    df["d"] = df.ts.dt.normalize(); df["k"] = (df.ts.dt.hour * 60 + df.ts.dt.minute) - 570
    A, fechas, segs = [], [], []
    for d, g in df.groupby("d"):
        if len(g) < 385 or g.k.min() != 0:
            continue
        a = np.full((390, 4), np.nan); a[g.k.to_numpy()] = g[["open", "high", "low", "close"]].to_numpy()
        A.append(pd.DataFrame(a).ffill().to_numpy()); fechas.append(d); segs.append(g.seg.iloc[-1])
    A = np.stack(A)
    rng = A[:, :, 1].max(1) - A[:, :, 2].min(1)
    atr = pd.Series(rng).shift().rolling(14).mean().to_numpy()
    prev_c = np.r_[np.nan, A[:-1, 385, 3]]
    same = np.r_[False, np.array(segs[1:]) == np.array(segs[:-1])]
    prev_c[~same] = np.nan
    np.savez(cache, A=A, atr=atr, fechas=np.array(fechas), prev_c=prev_c)
    return A, atr, pd.DatetimeIndex(fechas), prev_c


@njit(cache=True)
def bracket(A, di, hi_lvl, lo_lvl, t0, t_cut, stop_mode, stop_pts, tgt_R, reverse, lados, tick):
    """Un día. hi_lvl/lo_lvl: niveles de disparo. lados: 1 solo largo, -1 solo corto, 0 ambos.
    stop_mode: 0 = lado opuesto del rango, 1 = mitad del rango, 2 = fijo (stop_pts).
    Devuelve arreglo de hasta 2 trades: (pnl_pts, riesgo_pts, dir); pnl sin costos."""
    out = np.zeros((2, 3))
    nt = 0
    j = t0
    usado_l = False; usado_s = False
    mid = 0.5 * (hi_lvl + lo_lvl)
    while j < t_cut and nt < 2:
        o = A[di, j, 0]; h = A[di, j, 1]; l = A[di, j, 2]
        d = 0.0; e = 0.0
        if lados >= 0 and (not usado_l) and h >= hi_lvl:
            d = 1.0; e = max(hi_lvl, o); usado_l = True
        elif lados <= 0 and (not usado_s) and l <= lo_lvl:
            d = -1.0; e = min(lo_lvl, o); usado_s = True
        if d == 0.0:
            j += 1
            continue
        if stop_mode == 0:
            stop = lo_lvl if d > 0 else hi_lvl
        elif stop_mode == 1:
            stop = mid
        else:
            stop = e - d * stop_pts
        riesgo = abs(e - stop)
        if riesgo < tick:
            riesgo = tick
            stop = e - d * tick
        tgt = e + d * tgt_R * riesgo if tgt_R > 0 else (1e12 if d > 0 else -1e12)
        k = j
        salida = A[di, 385, 3]; kk = 385
        while k <= 385:
            ok_ = A[di, k, 0]; hh = A[di, k, 1]; ll = A[di, k, 2]
            hs = (ll <= stop) if d > 0 else (hh >= stop)
            ht = (hh >= tgt) if d > 0 else (ll <= tgt)
            if k == j and d > 0 and ll <= stop:
                hs = True
            if hs:
                px = stop
                if k > j and ((d > 0 and ok_ < stop) or (d < 0 and ok_ > stop)):
                    px = ok_
                salida = px; kk = k
                break
            if ht and k > j:
                salida = tgt; kk = k
                break
            k += 1
        out[nt, 0] = d * (salida - e); out[nt, 1] = riesgo; out[nt, 2] = d
        nt += 1
        salio_por_stop = kk < 385 and ((d > 0 and salida <= stop) or (d < 0 and salida >= stop))
        if not (reverse and salio_por_stop):
            break
        j = kk if stop_mode == 0 else kk + 1
    return out, nt


def barras(A, di, a, b):
    """High/low/open/close de minutos [a, b) del día di."""
    return A[di, a:b, 1].max(), A[di, a:b, 2].min(), A[di, a, 0], A[di, b - 1, 3]


def evaluar(sym, estrategia, variantes, dias_fomc=None):
    A, atr, fechas, prev_c = cargar_dias(sym)
    I = INSTR[sym]; tick = I["tick"]; costo = 0.0 if os.environ.get("BRUTO") == "1" else I["com"] / I["usd"] + 2 * tick
    filas = []
    for v in variantes:
        pnl, R, fe, ok_atr = [], [], [], []
        for di in range(len(A)):
            if np.isnan(atr[di]):
                continue
            s = señal(A, di, estrategia, v, tick, fechas[di], dias_fomc, prev_c[di])
            if s is None:
                continue
            hi_l, lo_l, t0, lados = s
            out, nt = bracket(A, di, hi_l, lo_l, t0, v.get("t_cut", 360), v["stop"], v.get("stop_atr", 0) * atr[di],
                              v["R"], v["rev"], lados, tick)
            for t in range(nt):
                pnl.append(out[t, 0] - costo); R.append((out[t, 0] - costo) / out[t, 1]); fe.append(fechas[di]); ok_atr.append((out[t, 0] - costo) / atr[di])
        if not pnl:
            continue
        p = np.array(pnl); r = np.array(R); a_ = np.array(ok_atr); fe = pd.DatetimeIndex(fe)
        fila = dict(sym=sym, estrategia=estrategia, **{k: v[k] for k in v}, n=len(p), wr=(p > 0).mean(),
                    exp_pts=p.mean(), exp_usd=p.mean() * I["usd"], exp_R=r.mean(), exp_atr=a_.mean() * 100,
                    pf=p[p > 0].sum() / max(-p[p <= 0].sum(), 1e-9), t=a_.mean() / (a_.std() / np.sqrt(len(a_))))
        for tag, x0, x1 in PERIODOS:
            m = (fe >= x0) & (fe <= x1)
            x = a_[m]
            fila[f"{tag}_n"] = int(m.sum()); fila[f"{tag}_atr%"] = x.mean() * 100 if m.any() else np.nan
            fila[f"{tag}_t"] = x.mean() / (x.std() / np.sqrt(len(x))) if m.sum() > 2 else np.nan
            fila[f"{tag}_wr"] = (p[m] > 0).mean() if m.any() else np.nan
        filas.append(fila)
    return pd.DataFrame(filas)


def señal(A, di, est, v, tick, fecha, dias_fomc, prev_c):
    buf = v.get("buf", 2) * tick
    if est == "SRS":          # 2ª vela de 15 min: 09:45-10:00 -> minutos 15..29
        h, l, _, _ = barras(A, di, 15, 30)
        return h + buf, l - buf, 30, 0
    if est == "ASRS":         # 4ª vela de 5 min: 09:45-09:50 -> minutos 15..19 ; 5ª: 20..24
        a = 15 if v.get("barra", 4) == 4 else 20
        h, l, _, _ = barras(A, di, a, a + 5)
        return h + buf, l - buf, a + 5, 0
    if est in ("1BP", "1BN"):  # 1ª vela de 5 min positiva (1BP -> corto bajo su mínimo) / negativa (1BN -> largo)
        h, l, o, c = barras(A, di, 0, 5)
        if est == "1BP" and c > o:
            return 1e12, l - buf, 5, -1
        if est == "1BN" and c < o:
            return h + buf, -1e12, 5, 1
        return None
    if est == "FOMC4":        # 4ª vela de 10 min tras el anuncio
        if dias_fomc is None or fecha.normalize() not in dias_fomc:
            return None
        t_anu = dias_fomc[fecha.normalize()]   # minuto RTH del anuncio (14:00 -> 270)
        a = t_anu + 30
        if a + 10 >= 380:
            return None
        h, l, _, _ = barras(A, di, a, a + 10)
        return h + buf, l - buf, a + 10, 0
    return None
