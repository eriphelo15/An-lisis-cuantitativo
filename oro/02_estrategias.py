"""Oro (GC): pullback VI (con y sin filtros), VI original (y con salida parcial + stop duro), ORB de COMEX (08:20) y de 09:30.
Ventanas de señal: COMEX 08:21-10:19 y 'NY' 09:31-11:29. ATR = rango medio 08:20-13:30 de los 14 días previos.
Resultados en R (con coste de hoy) y $ por operación con 1 GC a la volatilidad de hoy."""
import numpy as np, pandas as pd
from numba import njit
from base_oro import cargar, idx, PER, TICK, USD_PT, COSTO_PTS
A, E20, E50, F, ref = cargar()
i820, i1330, i1655 = idx(820), idx(1330), idx(1655)
rng = A[:, i820:i1330, 1].max(1) - A[:, i820:i1330, 2].min(1)
atr = pd.Series(rng).shift().rolling(14).mean().to_numpy(); atr_hoy = np.nanmean(atr[-60:])
Pp = np.array([next((t[:3] for t, a, b in PER if a <= str(f.date()) <= b), "") for f in F])

@njit
def pullback(A, E20, E50, atr, t0, t1, tfin, filtros, parcial, tick):
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]): continue
        at = atr[di]; o0 = A[di, t0 - 1, 0]
        for n in range(t0, t1):
            o1 = A[di, n - 1, 0]; c1 = A[di, n - 1, 3]; h1 = A[di, n - 1, 1]; l1 = A[di, n - 1, 2]
            o = A[di, n, 0]; h = A[di, n, 1]; l = A[di, n, 2]; c = A[di, n, 3]; e20 = E20[di, n]; e50 = E50[di, n]
            d = 0
            if e20 > e50 and c > e20 and c > e50 and max(o, c) < min(o1, c1) and h >= l1: d = 1
            elif e20 < e50 and c < e20 and c < e50 and min(o, c) > max(o1, c1) and l <= h1: d = -1
            if d == 0: continue
            st = e50 - d * 2 * tick; rk = d * (c - st)
            if rk < 4 * tick or rk > 0.25 * at: continue
            if filtros and not (d * (c - o0) > 0.158 * at and d * (e20 - E20[di, n - 10]) > 0.074 * at and rk > 0.069 * at): continue
            tg = c + d * 2 * rk; res = 0.0; hecho = False; parte = 0.0; fin = False
            for k in range(n + 1, tfin):
                oo = A[di, k, 0]; hh = A[di, k, 1]; ll = A[di, k, 2]
                sn = c if (parcial and hecho) else st
                if (d > 0 and ll <= sn) or (d < 0 and hh >= sn):
                    px = oo if ((d > 0 and oo < sn) or (d < 0 and oo > sn)) else sn
                    res = parte + (0.5 if hecho else 1.0) * d * (px - c) / rk; fin = True; break
                if parcial and not hecho and ((d > 0 and hh >= c + d * 0.5 * rk) or (d < 0 and ll <= c + d * 0.5 * rk)):
                    hecho = True; parte = 0.25
                if not parcial and ((d > 0 and hh >= tg) or (d < 0 and ll <= tg)): res = 2.0; fin = True; break
            if not fin: res = parte + (0.5 if hecho else 1.0) * d * (A[di, tfin - 1, 3] - c) / rk
            out.append((di, res, rk)); break
    return out

@njit
def vi_original(A, E20, E50, atr, t0, t1, tfin, parcial_stop, tick):
    """parcial_stop = 0: original (TP hueco, EMA, 5 min). >0: mitad en el hueco + BE, stop duro parcial_stop*ATR, resto hasta tfin."""
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]): continue
        k = t0
        while k < t1:
            o1 = A[di, k - 1, 0]; c1 = A[di, k - 1, 3]; h1 = A[di, k - 1, 1]; l1 = A[di, k - 1, 2]
            o = A[di, k, 0]; h = A[di, k, 1]; l = A[di, k, 2]; c = A[di, k, 3]; e20 = E20[di, k]; e50 = E50[di, k]
            d = 0; tp = 0.0
            if e20 > e50 and c > e20 and c > e50 and max(o, c) < min(o1, c1) and h >= l1: d = 1; tp = max(o, c)
            elif e20 < e50 and c < e20 and c < e50 and min(o, c) > max(o1, c1) and l <= h1: d = -1; tp = min(o, c)
            if d == 0 or abs(tp - c) < tick: k += 1; continue
            e = c; res = 0.0; nsal = 1; j = k + 1; hecho = False; parte = 0.0; st = e - d * parcial_stop * atr[di]; fin = False
            while j < tfin:
                oo = A[di, j, 0]; hh = A[di, j, 1]; ll = A[di, j, 2]; cc = A[di, j, 3]
                if parcial_stop == 0:
                    if (d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick): res = d * (tp - e); nsal = 0; fin = True; break
                    if (d > 0 and (cc < E20[di, j] or cc < E50[di, j])) or (d < 0 and (cc > E20[di, j] or cc > E50[di, j])): res = d * (cc - e); fin = True; break
                    if j - k >= 5: res = d * (cc - e); fin = True; break
                else:
                    sn = e if hecho else st
                    if (d > 0 and ll <= sn) or (d < 0 and hh >= sn):
                        px = oo if ((d > 0 and oo < sn) or (d < 0 and oo > sn)) else sn
                        res = parte + (0.5 if hecho else 1.0) * d * (px - e); fin = True; break
                    if not hecho and ((d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick)): hecho = True; parte = 0.5 * d * (tp - e)
                j += 1
            if not fin: res = parte + (0.5 if hecho else 1.0) * d * (A[di, tfin - 1, 3] - e); j = tfin
            out.append((di, res, nsal)); k = j + 1
    return out

@njit
def orb(A, t0, dur, tfin):
    out = []
    for di in range(A.shape[0]):
        hi = A[di, t0:t0 + dur, 1].max(); lo = A[di, t0:t0 + dur, 2].min(); r = hi - lo
        if r <= 0: continue
        for t in range(t0 + dur, tfin):
            h = A[di, t, 1]; l = A[di, t, 2]
            if h >= hi and l <= lo: out.append((di, -r, r)); break
            if h >= hi or l <= lo:
                d = 1 if h >= hi else -1; e = hi if d > 0 else lo; st = lo if d > 0 else hi; res = 0.0; fin = False
                for u in range(t + 1, tfin):
                    if (d > 0 and A[di, u, 2] <= st) or (d < 0 and A[di, u, 1] >= st): res = -r; fin = True; break
                if not fin: res = d * (A[di, tfin - 1, 3] - e)
                out.append((di, res, r)); break
    return out

def resumen(nom, di, R, usd):
    X = pd.DataFrame(dict(P=Pp[di], R=R, usd=usd, f=F[di]))
    m = X.groupby(X.f.dt.to_period("M")).usd.sum()
    s = f"{nom:52s} n={len(X):5d} acierto {100*(X.usd>0).mean():4.1f}% "
    for t in ["DEV", "VAL"]:
        x = X[X.P == t]; s += f"| {t}: {x.R.mean():+.3f}R t={x.R.mean()/x.R.std()*np.sqrt(len(x)):+.1f} ({x.usd.mean():+6.1f}$) "
    return s + f"| meses+ {100*(m>0).mean():.0f}%"

VENT = {"COMEX 08:21-10:19": (idx(821), idx(1020)), "NY 09:31-11:29": (idx(931), idx(1130))}
print("NOTA: el oro subió con fuerza en 2023-26; comprar 08:20 y vender 13:30 cada día =", end=" ")
b = (A[:, i1330, 0] - A[:, i820, 0]); print(" | ".join(f"{t}: {np.nanmean(b[Pp==t]*atr_hoy/atr[Pp==t]):+.1f} pts/día" for t in ["DEV", "VAL"]))
for vn, (t0, t1) in VENT.items():
    for filt, parc, nom in [(True, False, "Pullback VI filtrado (2R)"), (False, False, "Pullback VI sin filtros (2R)"), (True, True, "Pullback VI filtrado, mitad 0.5R+BE+cierre")]:
        o = np.array(pullback(A, E20, E50, atr, t0, t1, i1655, filt, parc, TICK))
        if len(o) == 0: continue
        di = o[:, 0].astype(int); esc = atr_hoy / atr[di]; Rn = o[:, 1] - COSTO_PTS / (o[:, 2] * esc)
        print(resumen(f"[{vn}] {nom}", di, Rn, Rn * o[:, 2] * esc * USD_PT))
    for ps, nom in [(0.0, "VI original (TP hueco, EMA, 5 min)"), (0.12, "VI original, mitad en hueco+BE, stop 0.12 ATR")]:
        o = np.array(vi_original(A, E20, E50, atr, t0, t1, i1655, ps, TICK)); di = o[:, 0].astype(int); esc = atr_hoy / atr[di]
        usd = (o[:, 1] * esc - COSTO_PTS - o[:, 2] * TICK * 0) * USD_PT
        R = usd / (0.12 * atr_hoy * USD_PT)
        print(resumen(f"[{vn}] {nom}", di, R, usd))
for t0, nom in [(i820, "ORB 15 min COMEX 08:20"), (idx(930), "ORB 15 min 09:30")]:
    o = np.array(orb(A, t0, 15, i1330)); di = o[:, 0].astype(int); esc = atr_hoy / atr[di]
    Rn = (o[:, 1] * esc - COSTO_PTS) / (o[:, 2] * esc)
    print(resumen(nom + " (salida 13:30)", di, Rn, Rn * o[:, 2] * esc * USD_PT))
