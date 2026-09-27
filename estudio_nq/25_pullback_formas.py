"""Misma entrada (pullback VI en tendencia, NQ), distintas 'formas' de salida para subir el winrate:
objetivo corto (0.5R..1.5R) y salida parcial (50% en xR, stop a break-even, resto a 3R o cierre).
Evaluado al COSTO DE HOY, por periodo, con rachas perdedoras."""
import numpy as np, pandas as pd, os, importlib
from numba import njit
from hougaard import INSTR, PERIODOS
vi = importlib.import_module("22_vi_usuario")
RES = os.path.join(os.path.dirname(__file__), "resultados")

@njit(cache=True)
def correr(A, E20, E50, atr, t_fin, R1, parcial, R2, be, tick):
    """parcial=0: una salida en R1. parcial=1: 50% en R1, luego stop a break-even (si be) y el resto a R2 (0 = cierre)."""
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]): continue
        n = 1; libre = 0
        while n < t_fin:
            if n < libre: n += 1; continue
            o1 = A[di, n - 1, 0]; c1 = A[di, n - 1, 3]; o = A[di, n, 0]; h = A[di, n, 1]; l = A[di, n, 2]; c = A[di, n, 3]
            h1 = A[di, n - 1, 1]; l1 = A[di, n - 1, 2]
            up = c > E20[di, n] and c > E50[di, n] and E20[di, n] > E50[di, n]
            dn = c < E20[di, n] and c < E50[di, n] and E20[di, n] < E50[di, n]
            d = 0.0
            if up and max(o, c) < min(o1, c1) and h >= l1: d = 1.0
            elif dn and min(o, c) > max(o1, c1) and l <= h1: d = -1.0
            if d == 0.0: n += 1; continue
            e = c; stop = E50[di, n] - d * 2 * tick; rk = d * (e - stop)
            if rk < 4 * tick or rk > 0.25 * atr[di]: n += 1; continue
            t1 = e + d * R1 * rk
            t2 = (e + d * R2 * rk) if R2 > 0 else (1e12 if d > 0 else -1e12)
            k = n + 1; frac = 1.0; acum = 0.0; st = stop; fase = 0; fin = False
            while k <= 385 and not fin:
                ok_ = A[di, k, 0]; hh = A[di, k, 1]; ll = A[di, k, 2]; cc = A[di, k, 3]
                hs = (ll <= st) if d > 0 else (hh >= st)
                if hs:
                    px = st
                    if (d > 0 and ok_ < st) or (d < 0 and ok_ > st): px = ok_
                    acum += frac * d * (px - e); fin = True; break
                if fase == 0 and ((hh >= t1) if d > 0 else (ll <= t1)):
                    if parcial == 0:
                        acum += d * (t1 - e); fin = True; break
                    acum += 0.5 * d * (t1 - e); frac = 0.5; fase = 1
                    if be: st = e
                if fase == 1 and ((hh >= t2) if d > 0 else (ll <= t2)):
                    acum += frac * d * (t2 - e); fin = True; break
                if k == 385:
                    acum += frac * d * (cc - e); fin = True
                k += 1
            out.append((di, acum, rk, fase))
            libre = k + 1; n = k + 1
    return out

if __name__ == "__main__":
    A, E20, E50, F, atr = vi.dias_con_ema("NQ"); I = INSTR["NQ"]; tick = I["tick"]
    costo_pts = I["com"] / I["usd"] + 2 * tick; atr_hoy = np.nanmean(atr[-60:]); costo_hoy = costo_pts / atr_hoy
    formas = [("objetivo 0.5R", 0.5, 0, 0, False), ("objetivo 0.75R", 0.75, 0, 0, False), ("objetivo 1R", 1.0, 0, 0, False),
              ("objetivo 1.5R", 1.5, 0, 0, False), ("objetivo 2R", 2.0, 0, 0, False), ("objetivo 3R", 3.0, 0, 0, False),
              ("50% en 0.5R + BE + resto 2R", 0.5, 1, 2.0, True), ("50% en 1R + BE + resto 3R", 1.0, 1, 3.0, True),
              ("50% en 1R + BE + resto al cierre", 1.0, 1, 0.0, True), ("50% en 0.5R + BE + resto al cierre", 0.5, 1, 0.0, True)]
    filas = []
    for nom, R1, par, R2, be in formas:
        R = pd.DataFrame(np.array(correr(A, E20, E50, atr, 120, R1, par, R2, be, tick)), columns=["di", "res", "rk", "fase"])
        R["f"] = F[R.di.astype(int)]
        esc = atr_hoy / atr[R.di.astype(int)]
        R["usd"] = (R.res / atr[R.di.astype(int)] - costo_hoy) * atr_hoy * I["usd"]   # 1 NQ a precio de hoy
        p = R.usd.to_numpy()
        s = (p > 0).astype(int); ml = cur = 0
        for v in s: cur = cur + 1 if v == 0 else 0; ml = max(ml, cur)
        eq = np.cumsum(p / 10); dd = (np.maximum.accumulate(eq) - eq).max()   # por MNQ
        yrs = R.groupby(R.f.dt.year).usd.mean()
        fila = dict(forma=nom, winrate=(p > 0).mean(), gan_media_nq=p[p > 0].mean(), perd_media_nq=p[p <= 0].mean(),
                    por_trade_nq=p.mean(), t=p.mean() / (p.std() / np.sqrt(len(p))), años_pos=f"{int((yrs > 0).sum())}/{len(yrs)}",
                    peor_racha=ml, peor_caida_mnq=dd, por_año_mnq=p.sum() / 10 / (len(np.unique(R.di)) / 252 * len(A) / len(np.unique(R.di))))
        for tag, a, b in PERIODOS:
            x = R[(R.f >= a) & (R.f <= b)].usd
            fila[f"{tag}_nq"] = x.mean(); fila[f"{tag}_t"] = x.mean() / (x.std() / np.sqrt(len(x)))
        filas.append(fila)
    T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "pullback_formas.csv"), index=False)
    pd.set_option("display.width", 250); print(T.round(2).to_string(index=False))
