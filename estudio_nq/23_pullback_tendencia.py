"""Versión 'dejar correr' de la estrategia del usuario:
entrada = misma que la suya (VI contra-tendencia dentro de tendencia EMA20/50, 1 min, 09:30-11:30, al cierre de la vela);
stop fijo (EMA50, mínimo de la vela del VI, o 0.1 ATR); objetivo 1R/2R/3R, salida por cierre al otro lado de EMA20, o al cierre del día."""
import numpy as np, pandas as pd, os, itertools
from numba import njit
from hougaard import INSTR, PERIODOS
import importlib
vi = importlib.import_module("22_vi_usuario")
RES = os.path.join(os.path.dirname(__file__), "resultados")

@njit(cache=True)
def correr(A, E20, E50, atr, t_fin, stop_modo, R_obj, trail, tick, estricta):
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]):
            continue
        n = 1; libre = 0
        while n < t_fin:
            if n < libre:
                n += 1; continue
            o1 = A[di, n - 1, 0]; c1 = A[di, n - 1, 3]; o = A[di, n, 0]; h = A[di, n, 1]; l = A[di, n, 2]; c = A[di, n, 3]
            h1 = A[di, n - 1, 1]; l1 = A[di, n - 1, 2]
            up = c > E20[di, n] and c > E50[di, n]; dn = c < E20[di, n] and c < E50[di, n]
            if estricta:
                up = up and E20[di, n] > E50[di, n]; dn = dn and E20[di, n] < E50[di, n]
            d = 0.0
            if up and max(o, c) < min(o1, c1) and h >= l1: d = 1.0
            elif dn and min(o, c) > max(o1, c1) and l <= h1: d = -1.0
            if d == 0.0:
                n += 1; continue
            e = c
            if stop_modo == 0: stop = E50[di, n] - d * 2 * tick
            elif stop_modo == 1: stop = (l - 2 * tick) if d > 0 else (h + 2 * tick)
            else: stop = e - d * 0.1 * atr[di]
            riesgo = d * (e - stop)
            if riesgo < 4 * tick or riesgo > 0.25 * atr[di]:
                n += 1; continue
            tgt = e + d * R_obj * riesgo if R_obj > 0 else (1e12 if d > 0 else -1e12)
            k = n + 1; res = 0.0; mot = 0
            while k <= 385:
                ok_ = A[di, k, 0]; hh = A[di, k, 1]; ll = A[di, k, 2]; cc = A[di, k, 3]
                hs = (ll <= stop) if d > 0 else (hh >= stop)
                ht = (hh >= tgt) if d > 0 else (ll <= tgt)
                if hs:
                    px = stop
                    if (d > 0 and ok_ < stop) or (d < 0 and ok_ > stop): px = ok_
                    res = d * (px - e); mot = -1; break
                if ht:
                    res = d * (tgt - e); mot = 1; break
                if trail and ((d > 0 and cc < E20[di, k]) or (d < 0 and cc > E20[di, k])):
                    res = d * (cc - e); mot = 2; break
                if k == 385:
                    res = d * (cc - e); mot = 3
                k += 1
            out.append((di, d, res, riesgo, mot))
            libre = k + 1
            n = k + 1
    return out

if __name__ == "__main__":
    filas = []
    for sym in ["NQ", "ES", "YM"]:
        A, E20, E50, F, atr = vi.dias_con_ema(sym); I = INSTR[sym]; tick = I["tick"]
        costo = I["com"] / I["usd"] + 2 * tick
        for sm, Robj, trail, est in itertools.product([0, 1, 2], [1.0, 2.0, 3.0, 0.0], [False, True], [True]):
            if Robj == 0.0 and not trail:
                pass  # salida al cierre del día
            r = np.array(correr(A, E20, E50, atr, 120, sm, Robj, trail, tick, est))
            if len(r) == 0: continue
            R = pd.DataFrame(r, columns=["di", "d", "res", "riesgo", "mot"])
            R["neto"] = R.res - costo; R["f"] = F[R.di.astype(int)]; R["atr"] = atr[R.di.astype(int)]
            R["neto_atr"] = R.neto / R.atr * 100; R["bruto_atr"] = R.res / R.atr * 100
            w = R.neto[R.neto > 0]; lo = R.neto[R.neto <= 0]
            fila = dict(sym=sym, stop=["EMA50", "vela VI", "0.1 ATR"][sm], objetivo=("%.0fR" % Robj) if Robj > 0 else "sin objetivo",
                        trail_EMA20=trail, trades=len(R), por_dia=len(R) / len(A), wr=(R.neto > 0).mean(), gan_media_usd=w.mean() * I["usd"],
                        perd_media_usd=lo.mean() * I["usd"], pf=w.sum() / max(-lo.sum(), 1e-9), exp_usd=R.neto.mean() * I["usd"],
                        exp_R=(R.neto / R.riesgo).mean(), t=R.neto_atr.mean() / (R.neto_atr.std() / np.sqrt(len(R))))
            for tag, a, b in PERIODOS:
                x = R[(R.f >= a) & (R.f <= b)]
                fila[f"{tag}_usd"] = x.neto.mean() * I["usd"]; fila[f"{tag}_t"] = x.neto_atr.mean() / (x.neto_atr.std() / np.sqrt(len(x)))
                fila[f"{tag}_bruto_t"] = x.bruto_atr.mean() / (x.bruto_atr.std() / np.sqrt(len(x)))
            filas.append(fila)
        print(sym, flush=True)
    T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "pullback_tendencia.csv"), index=False)
    pd.set_option("display.width", 280)
    print(T.round(2).to_string(index=False))
