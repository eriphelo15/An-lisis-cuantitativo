"""Volume imbalance (VI): entre dos velas consecutivas, los CUERPOS no se solapan pero las MECHAS sí.
VI alcista: open[n] > close[n-1] (con ambas velas alcistas no requerido). Zona = [close[n-1], open[n]].
Hipótesis del usuario: el precio tiende a volver a rellenar esa zona.
Test honesto (carrera de barreras): tras formarse la VI, desde el cierre de la vela n:
   objetivo = borde lejano de la zona (relleno completo) a distancia d
   stop = k·d en contra.  Nulo martingala: P(objetivo primero) = k/(1+k).
Si P observada > nulo de forma consistente -> hay 'imán'. Además PnL neto de costos."""
import numpy as np, pandas as pd, os, sys
from numba import njit
from hougaard import cargar_dias, INSTR, PERIODOS
RES = os.path.join(os.path.dirname(__file__), "resultados")

@njit(cache=True)
def correr(A, tf, ks, min_d, t_fin):
    # A: (dias, 390, 4). Velas de 'tf' minutos. Devuelve filas: dia, k_idx, dir, d, gano(1/0/-1 tiempo), pnl_pts
    out = []
    nd = A.shape[0]; nb = 390 // tf
    for di in range(nd):
        O = np.empty(nb); H = np.empty(nb); L = np.empty(nb); C = np.empty(nb)
        for b in range(nb):
            O[b] = A[di, b * tf, 0]; C[b] = A[di, b * tf + tf - 1, 3]
            H[b] = A[di, b * tf:b * tf + tf, 1].max(); L[b] = A[di, b * tf:b * tf + tf, 2].min()
        for n in range(1, nb - 1):
            if (n + 1) * tf >= t_fin:
                break
            # VI alcista: cuerpo de n empieza por encima del cierre de n-1, mechas solapadas
            bull = O[n] > C[n - 1] and L[n] <= H[n - 1] and min(O[n], C[n]) > max(O[n - 1], C[n - 1])
            bear = O[n] < C[n - 1] and H[n] >= L[n - 1] and max(O[n], C[n]) < min(O[n - 1], C[n - 1])
            if not (bull or bear):
                continue
            e = C[n]
            if bull:
                lvl = max(O[n - 1], C[n - 1]); d_ = -1.0       # rellenar hacia abajo
            else:
                lvl = min(O[n - 1], C[n - 1]); d_ = 1.0
            dist = abs(e - lvl)
            if dist < min_d:
                continue
            for ki in range(len(ks)):
                stop = e - d_ * ks[ki] * dist
                res = 0; px = A[di, 385, 3]
                j = (n + 1) * tf
                while j <= 385:
                    hh = A[di, j, 1]; ll = A[di, j, 2]
                    hs = (ll <= stop) if d_ > 0 else (hh >= stop)
                    ht = (hh >= lvl) if d_ > 0 else (ll <= lvl)
                    if hs:
                        res = -1; px = stop; break
                    if ht:
                        res = 1; px = lvl; break
                    j += 1
                out.append((di, ki, d_, dist, res, d_ * (px - e)))
    return out

if __name__ == "__main__":
    ks = np.array([0.5, 1.0, 2.0, 4.0])
    filas = []
    for sym in ["NQ", "ES", "YM"]:
        A, atr, fechas, _ = cargar_dias(sym)
        I = INSTR[sym]; costo = I["com"] / I["usd"] + 2 * I["tick"]
        for tf in [1, 5, 15]:
            r = np.array(correr(A, tf, ks, 2 * I["tick"], 380))
            if len(r) == 0: continue
            R = pd.DataFrame(r, columns=["di", "ki", "dir", "d", "res", "pnl"])
            R["fecha"] = fechas[R.di.astype(int)]; R["k"] = ks[R.ki.astype(int)]
            R["pnl_neto"] = R.pnl - costo; R["atr"] = atr[R.di.astype(int)]
            for k, g in R.groupby("k"):
                nulo = k / (1 + k)
                fila = dict(sym=sym, tf=tf, k=k, n=len(g), p_relleno=(g.res == 1).mean(), nulo=nulo, exceso=(g.res == 1).mean() - nulo,
                            dist_media=g.d.mean(), neto_pts=g.pnl_neto.mean(), wr_neto=(g.pnl_neto > 0).mean())
                for tag, a, b in PERIODOS:
                    m = (g.fecha >= a) & (g.fecha <= b); x = g[m]
                    fila[f"{tag}_exceso"] = (x.res == 1).mean() - nulo; fila[f"{tag}_neto_atr%"] = (x.pnl_neto / x.atr).mean() * 100
                filas.append(fila)
            print(sym, tf, flush=True)
    T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "volume_imbalance.csv"), index=False)
    pd.set_option("display.width", 240)
    print(T.round(3).to_string(index=False))
