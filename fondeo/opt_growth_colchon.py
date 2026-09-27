"""Growth 50K: política de colchón + retiro máximo, objetivo = USD netos por cupo y año.
Tasa por cupo = (E[cobros] - cuota/P(aprobar)) / (días de vida de la fondeada / 252).
(Los exámenes se pueden correr en paralelo y aprueban en ~2 días, así que el cupo lo ocupa la fondeada.)"""
import numpy as np, pandas as pd, itertools, os, sys, time
from motor_fondeo import fondeada, examen
from reglas_tradeify import FONDEADA, EXAMEN
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"opt": np.load("/home/user/data/dias_rth.npy"), "cons": np.load("/home/user/data/dias_rth_2011_2020.npy")}
CUOTA = 93.0
r = FONDEADA["growth"][50]; e = EXAMEN["growth"][50]
def f_run(D, R, S, rr, K, G, col, modo=0, t_ini=1, ns=1500, seed=5, hor=250):
    return fondeada(D, ns, 0, 50., 2000., 1250., 150., 3000., 0.35, 500., 1500., 3000., 0., 0., 0., 0.,
                    float(R), float(S), float(S * rr), K, float(G), 1e9, 40, 0., hor, seed, modo, t_ini, float(col))
def e_run(D, modo=0, t_ini=1, ns=20000, seed=8):
    ok, d = examen(D, ns, 3000., 2000., 1250., 0., 1, 1200., 60., 180., 2, 1e9, 1e9, 40, 60, seed, modo, t_ini)
    return ok.mean(), np.median(d[ok])
def tasa(cob, viv, p_ap):
    net = cob.mean() - CUOTA / p_ap
    return net, net / (viv.mean() / 252.0)
if __name__ == "__main__":
    t0 = time.time(); D = LIB["opt"]
    p_ap, _ = e_run(D)
    rows = []
    for R, S, rr, K, G, col in itertools.product([100, 150, 250, 400, 600], [20, 40, 60, 90], [1, 2, 3], [1, 2], [300, 600, 1e9],
                                                  [-1, 0, 500, 1000, 1500, 2500]):
        cob, nret, viv, qb = f_run(D, R, S, rr, K, G, col)
        net, ta = tasa(cob, viv, p_ap)
        rows.append(dict(R=R, S=S, rr=rr, K=K, G=G, colchon=col, ev=cob.mean(), p_cobra=(nret > 0).mean(), n_ret=nret.mean(),
                         dias=viv.mean(), neto_cupo=net, neto_cupo_año=ta))
    X = pd.DataFrame(rows); X.to_csv(os.path.join(RES, "growth50_colchon_grid.csv"), index=False)
    print(f"grid {len(X)} en {time.time()-t0:.0f}s; P(aprobar examen)={p_ap:.3f}")
    pd.set_option("display.width", 220)
    print("\nMejor por colchón (máx. neto por cupo y año):")
    print(X.sort_values("neto_cupo_año", ascending=False).groupby("colchon").head(1).round(2).to_string(index=False))
    print("\nTop 10 por neto por cupo (valor por cuenta):")
    print(X.sort_values("neto_cupo", ascending=False).head(10).round(2).to_string(index=False))
