"""Búsqueda de setups A+ con machine learning walk-forward.
Universo: cada 5 min entre 09:35 y 11:30, operación a favor de la tendencia EMA20/EMA50 (1 min), NQ/ES/YM, 2010-2026.
Etiquetas: bracket 1:2 (stop 0.1 ATR, objetivo 0.2 ATR) y 1:1 (stop 0.12 ATR, objetivo 0.12 ATR), salida 15:55. Neto de costos de hoy.
Walk-forward anual: entrena con todos los años anteriores, predice el año siguiente (2014-2026)."""
import numpy as np, pandas as pd, os, importlib, time
from numba import njit
import lightgbm as lgb
from hougaard import INSTR
vi = importlib.import_module("22_vi_usuario")
DATA = "/home/user/data"; RES = os.path.join(os.path.dirname(__file__), "resultados")

def volumen(sym, F):
    df = pd.read_parquet(os.path.join(DATA, INSTR[sym]["parquet"]), columns=["ts", "volume"])
    hm = df.ts.dt.hour * 100 + df.ts.dt.minute
    df = df[(hm >= 930) & (hm < 1600)]
    df["d"] = df.ts.dt.normalize(); df["k"] = (df.ts.dt.hour * 60 + df.ts.dt.minute) - 570
    V = np.zeros((len(F), 390)); idx = {f: i for i, f in enumerate(F)}
    for d, g in df.groupby("d"):
        i = idx.get(d)
        if i is not None: V[i, g.k.to_numpy()] = g.volume.to_numpy()
    return V

@njit(cache=True)
def bracket(A, di, n, d, stop_pts, tgt_pts):
    e = A[di, n, 3]; st = e - d * stop_pts; tg = e + d * tgt_pts
    for k in range(n + 1, 386):
        o = A[di, k, 0]; h = A[di, k, 1]; l = A[di, k, 2]
        if (l <= st) if d > 0 else (h >= st):
            px = st
            if (d > 0 and o < st) or (d < 0 and o > st): px = o
            return d * (px - e)
        if (h >= tg) if d > 0 else (l <= tg):
            return d * (tg - e)
    return d * (A[di, 385, 3] - e)

def universo(sym):
    A, E20, E50, F, atr = vi.dias_con_ema(sym); V = volumen(sym, F)
    I = INSTR[sym]; costo = I["com"] / I["usd"] + 2 * I["tick"]; atr_hoy = np.nanmean(atr[-60:]); c_atr = costo / atr_hoy
    H = A[:, :, 1]; L = A[:, :, 2]; C = A[:, :, 3]; O = A[:, :, 0]
    tp = (H + L + C) / 3; cv = np.cumsum(V, 1); vwap = np.cumsum(tp * V, 1) / np.maximum(cv, 1)
    hi_run = np.maximum.accumulate(H, 1); lo_run = np.minimum.accumulate(L, 1)
    vol5 = np.array([np.convolve(V[i], np.ones(5), "full")[:390] for i in range(len(V))])
    vol5_ref = pd.DataFrame(vol5).shift(1).rolling(20, min_periods=5).mean().to_numpy()
    prev_c = np.r_[np.nan, C[:-1, 385]]; prev_rng = np.r_[np.nan, (H.max(1) - L.min(1))[:-1]]; prev_ret = np.r_[np.nan, (C[:-1, 385] - O[:-1, 0])]
    atr_rel = (pd.Series(atr) / pd.Series(atr).rolling(100, min_periods=40).mean()).to_numpy()
    filas = []
    for n in range(5, 121, 5):
        d = np.sign(E20[:, n] - E50[:, n])
        ok = (d != 0) & ~np.isnan(atr) & ((C[:, n] - E50[:, n]) * d > 0)
        for di in np.flatnonzero(ok):
            a = atr[di]; dd = d[di]
            y12 = bracket(A, di, n, dd, 0.10 * a, 0.20 * a) / (0.10 * a) - c_atr / 0.10
            y11 = bracket(A, di, n, dd, 0.12 * a, 0.12 * a) / (0.12 * a) - c_atr / 0.12
            rng = hi_run[di, n] - lo_run[di, n]
            filas.append((di, n, dd, y12, y11,
                          dd * (C[di, n] - O[di, 0]) / a, dd * (O[di, 0] - prev_c[di]) / a,
                          dd * (C[di, n] - C[di, n - 5]) / a, dd * (C[di, n] - C[di, max(n - 15, 0)]) / a, dd * (C[di, n] - C[di, max(n - 30, 0)]) / a,
                          dd * (C[di, n] - E20[di, n]) / a, dd * (C[di, n] - E50[di, n]) / a, dd * (E20[di, n] - E20[di, n - 5]) / a, dd * (E20[di, n] - E50[di, n]) / a,
                          dd * (C[di, n] - vwap[di, n]) / a, rng / a, ((C[di, n] - lo_run[di, n]) / max(rng, 1e-9)) if dd > 0 else ((hi_run[di, n] - C[di, n]) / max(rng, 1e-9)),
                          vol5[di, n] / vol5_ref[di, n] if vol5_ref[di, n] > 0 else np.nan, atr_rel[di], prev_rng[di] / a, dd * prev_ret[di] / a,
                          (H[di, n - 4:n + 1].max() - L[di, n - 4:n + 1].min()) / a))
    cols = ["di", "n", "d", "y12", "y11", "dia_a_favor", "gap_a_favor", "r5", "r15", "r30", "dist_ema20", "dist_ema50", "pend_ema20", "sep_emas",
            "dist_vwap", "rango_dia", "pos_rango", "vol_rel", "atr_rel", "rango_ayer", "ret_ayer_a_favor", "rango_5min"]
    X = pd.DataFrame(filas, columns=cols); X["f"] = F[X.di.astype(int)]; X["sym"] = sym
    return X, (A, E20, E50, F)

if __name__ == "__main__":
    t0 = time.time(); U = {}; datos = {}
    for sym in ["NQ", "ES", "YM"]:
        U[sym], datos[sym] = universo(sym); print(sym, len(U[sym]), f"{time.time()-t0:.0f}s", flush=True)
    # confirmación entre índices: tendencia y movimiento del día de los otros dos en el mismo minuto
    for sym in U:
        otros = [s for s in U if s != sym]
        for o in otros:
            A, E20, E50, F = datos[o]; idx = {f: i for i, f in enumerate(F)}
            j = U[sym].f.map(idx); n = U[sym].n.astype(int).to_numpy(); dd = U[sym].d.to_numpy()
            ok = j.notna().to_numpy(); jj = j.fillna(0).astype(int).to_numpy()
            tr = np.sign(E20[jj, n] - E50[jj, n]) * dd; mv = np.sign(A[jj, n, 3] - A[jj, 0, 0]) * dd
            U[sym][f"tend_{o}"] = np.where(ok, tr, np.nan); U[sym][f"dia_{o}"] = np.where(ok, mv, np.nan)
        U[sym] = U[sym].rename(columns={f"tend_{o}": f"tend_otro{i}" for i, o in enumerate(otros)} | {f"dia_{o}": f"dia_otro{i}" for i, o in enumerate(otros)})
    X = pd.concat(U.values(), ignore_index=True)
    X["min"] = X.n; X["dow"] = X.f.dt.dayofweek; X["inst"] = X.sym.map({"NQ": 0, "ES": 1, "YM": 2})
    X.to_parquet(os.path.join(DATA, "universo_ml.parquet"))
    print("universo total", len(X), f"{time.time()-t0:.0f}s")
