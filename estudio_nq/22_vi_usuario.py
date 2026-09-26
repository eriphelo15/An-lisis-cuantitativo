"""Estrategia del usuario: volume imbalance contra-tendencia dentro de tendencia (EMA 20/50, 1 min, 09:30-11:30).
Entrada al cierre de la vela que crea el VI; TP en el hueco; salida a los N minutos o si cierra al otro lado de EMA(s).
Sin stop loss. Comparada contra un nulo: mismas entradas en tendencia SIN imbalance, con el mismo TP en distancia."""
import numpy as np, pandas as pd, os, itertools, sys
from numba import njit
from hougaard import INSTR, PERIODOS
RES = os.path.join(os.path.dirname(__file__), "resultados")
DATA = "/home/user/data"

def dias_con_ema(sym):
    cache = os.path.join(DATA, f"{sym.lower()}15_rth_ema.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True); return z["A"], z["E20"], z["E50"], pd.DatetimeIndex(z["f"]), z["atr"]
    df = pd.read_parquet(os.path.join(DATA, INSTR[sym]["parquet"]), columns=["ts", "open", "high", "low", "close", "adj_close"])
    off = df.adj_close - df.close                      # offset back-adjust (constante por contrato)
    e20 = df.adj_close.ewm(span=20, adjust=False).mean() - off
    e50 = df.adj_close.ewm(span=50, adjust=False).mean() - off
    df["e20"] = e20; df["e50"] = e50
    hm = df.ts.dt.hour * 100 + df.ts.dt.minute
    df = df[(hm >= 930) & (hm < 1600)].copy()
    df["d"] = df.ts.dt.normalize(); df["k"] = (df.ts.dt.hour * 60 + df.ts.dt.minute) - 570
    A, E20, E50, F = [], [], [], []
    for d, g in df.groupby("d"):
        if len(g) < 385 or g.k.min() != 0: continue
        a = np.full((390, 6), np.nan); a[g.k.to_numpy()] = g[["open", "high", "low", "close", "e20", "e50"]].to_numpy()
        a = pd.DataFrame(a).ffill().to_numpy()
        A.append(a[:, :4]); E20.append(a[:, 4]); E50.append(a[:, 5]); F.append(d)
    A = np.stack(A); E20 = np.stack(E20); E50 = np.stack(E50)
    rng = A[:, :, 1].max(1) - A[:, :, 2].min(1); atr = pd.Series(rng).shift().rolling(14).mean().to_numpy()
    np.savez(cache, A=A, E20=E20, E50=E50, f=np.array(F), atr=atr)
    return A, E20, E50, pd.DatetimeIndex(F), atr

@njit(cache=True)
def correr(A, E20, E50, t_fin, tend_estricta, tp_modo, ema_exit, n_min, entrada_open, tick, nulo, seed):
    """tp_modo 0: borde cercano del hueco; 1: relleno completo. ema_exit 0: EMA20, 1: EMA50, 2: ambas.
    nulo=True: en lugar de VI se toma una vela en tendencia al azar (prob. igual) con TP a la misma distancia típica."""
    np.random.seed(seed)
    out = []
    for di in range(A.shape[0]):
        n = 1
        ocupado_hasta = -1
        while n < t_fin:
            if n <= ocupado_hasta:
                n += 1; continue
            o1 = A[di, n - 1, 0]; c1 = A[di, n - 1, 3]; o = A[di, n, 0]; h = A[di, n, 1]; l = A[di, n, 2]; c = A[di, n, 3]
            h1 = A[di, n - 1, 1]; l1 = A[di, n - 1, 2]
            up = c > E20[di, n] and c > E50[di, n]
            dn = c < E20[di, n] and c < E50[di, n]
            if tend_estricta:
                up = up and E20[di, n] > E50[di, n]; dn = dn and E20[di, n] < E50[di, n]
            d = 0.0; tp = 0.0
            # VI bajista (contra tendencia alcista): cuerpo de n por debajo del cuerpo de n-1, mechas solapadas
            vi_baj = max(o, c) < min(o1, c1) and h >= l1
            vi_alc = min(o, c) > max(o1, c1) and l <= h1
            if not nulo:
                if up and vi_baj:
                    d = 1.0; tp = max(o, c) if tp_modo == 0 else min(o1, c1)
                elif dn and vi_alc:
                    d = -1.0; tp = min(o, c) if tp_modo == 0 else max(o1, c1)
            else:
                if (up or dn) and np.random.random() < 0.08:
                    d = 1.0 if up else -1.0
                    dist = abs(max(o, c) - c) if up else abs(c - min(o, c))
                    dist = max(dist, 0.0) + 2 * tick + np.random.random() * 4 * tick
                    tp = c + d * dist
            if d == 0.0 or abs(tp - c) < tick:
                n += 1; continue
            e = A[di, n + 1, 0] if entrada_open else c
            res = 0.0; k = n + 1; fin = min(n + n_min, 389); motivo = 0
            while k <= fin:
                hh = A[di, k, 1]; ll = A[di, k, 2]; cc = A[di, k, 3]
                if (d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick):
                    res = d * (tp - e); motivo = 1; break
                fuera = False
                if ema_exit == 0: fuera = (cc < E20[di, k]) if d > 0 else (cc > E20[di, k])
                elif ema_exit == 1: fuera = (cc < E50[di, k]) if d > 0 else (cc > E50[di, k])
                else: fuera = ((cc < E20[di, k]) and (cc < E50[di, k])) if d > 0 else ((cc > E20[di, k]) and (cc > E50[di, k]))
                if fuera:
                    res = d * (cc - e); motivo = 2; break
                if k == fin:
                    res = d * (cc - e); motivo = 3
                k += 1
            out.append((di, n, d, res, motivo, abs(tp - c)))
            ocupado_hasta = k
            n = k + 1
    return out

if __name__ == "__main__":
    filas = []; det = {}
    for sym in ["NQ", "ES", "YM"]:
        A, E20, E50, F, atr = dias_con_ema(sym)
        I = INSTR[sym]; tick = I["tick"]
        c_mkt = I["com"] / I["usd"] + 2 * tick      # entrada y salida a mercado
        c_tp = I["com"] / I["usd"] + 1 * tick       # salida por TP (limit): solo desliza la entrada
        for tend, tpm, ex, nm, eo, nulo in itertools.product([False, True], [0, 1], [0, 1, 2], [5], [False, True], [False, True]):
            r = np.array(correr(A, E20, E50, 120, tend, tpm, ex, nm, eo, tick, nulo, 7))
            if len(r) == 0: continue
            R = pd.DataFrame(r, columns=["di", "n", "d", "res", "motivo", "dist"])
            R["neto"] = R.res - np.where(R.motivo == 1, c_tp, c_mkt)
            R["fecha"] = F[R.di.astype(int)]; R["atr"] = atr[R.di.astype(int)]
            w = R.neto[R.neto > 0]; lo = R.neto[R.neto <= 0]
            fila = dict(sym=sym, tend_estricta=tend, tp="relleno" if tpm else "borde", ema_exit=["EMA20", "EMA50", "ambas"][ex],
                        entrada="open sig." if eo else "cierre", modo="NULO (sin VI)" if nulo else "VI usuario",
                        trades=len(R), por_dia=len(R) / len(A), p_tp_5min=(R.motivo == 1).mean(), wr_neto=(R.neto > 0).mean(),
                        gan_media=w.mean(), perd_media=lo.mean(), peor=R.neto.min(), pf=w.sum() / max(-lo.sum(), 1e-9),
                        exp_pts=R.neto.mean(), exp_usd=R.neto.mean() * I["usd"], exp_bruto=R.res.mean())
                        
            for tag, a, b in PERIODOS:
                m = (R.fecha >= a) & (R.fecha <= b); x = R[m]
                fila[f"{tag}_exp_usd"] = x.neto.mean() * I["usd"]; fila[f"{tag}_wr"] = (x.neto > 0).mean(); fila[f"{tag}_ptp"] = (x.motivo == 1).mean()
                fila[f"{tag}_t"] = x.neto.mean() / (x.neto.std() / np.sqrt(len(x))) if len(x) > 2 else np.nan
            filas.append(fila)
        print(sym, flush=True)
    T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "vi_usuario.csv"), index=False)
    pd.set_option("display.width", 280)
    c = ["sym", "tend_estricta", "tp", "ema_exit", "entrada", "modo", "trades", "por_dia", "p_tp_5min", "wr_neto", "gan_media", "perd_media", "pf", "exp_usd", "DEV_exp_usd", "VAL1_exp_usd", "VAL2_exp_usd", "VAL2_t"]
    print(T[c].round(3).to_string(index=False))
