"""Valida las políticas elegidas en una biblioteca de días distinta (2011-2020, escalada) y en 100K/150K."""
import numpy as np, pandas as pd, os, sys, itertools
import opt_fondeada as of
from motor_fondeo import examen
from reglas_tradeify import FONDEADA, EXAMEN
D21 = np.load("/home/user/data/dias_rth.npy"); D11 = np.load("/home/user/data/dias_rth_2011_2020.npy")
of.HOR = 250
rows = []
# políticas de examen óptimas (por plan) y fondeadas óptimas (estructura: R ~7.5% DD, S=60, rr=3, K=1)
for plan, sizes in EXAMEN.items():
    for size, r in sizes.items():
        best = None
        for fr, S, rr, K in itertools.product([0.15, 0.25, 0.6, 0.8, 1.0], [45, 60, 90], [2, 3, 4], [1, 2]):
            G = 1e9 if not r["consist"] else r["consist"] * r["target"] * 0.8
            ok, _ = examen(D21, 3000, float(r["target"]), float(r["dd"]), float(r["dll"] or 0), float(r["consist"] or 0), r["min_dias"],
                           float(fr * r["dd"]), float(S), float(S * rr), K, float(G), 1e9, r["max_mini"] * 10, 60, 5)
            if best is None or ok.mean() > best[0]: best = (ok.mean(), fr, S, rr, K, G)
        _, fr, S, rr, K, G = best
        res = {}
        for lab, D in [("2021-26", D21), ("2011-20", D11)]:
            ok, d = examen(D, 20000, float(r["target"]), float(r["dd"]), float(r["dll"] or 0), float(r["consist"] or 0), r["min_dias"],
                           float(fr * r["dd"]), float(S), float(S * rr), K, float(G), 1e9, r["max_mini"] * 10, 60, 77)
            res[lab] = ok.mean()
        rows.append(dict(fase="examen", plan=plan, size=size, politica=f"R={fr:.0%} DD, S={S}, T={S*rr}, K={K}", **res))
for tipo, tab in FONDEADA.items():
    for size, r in tab.items():
        best = None
        for fr, S, rr, K in itertools.product([0.035, 0.05, 0.075, 0.1], [40, 60, 90], [2, 3, 5], [1, 2, 3]):
            G = 4 * max(r.get("dia_min", 150), 100)
            cob, nret, viv, qb = of.correr(tipo, size, r, fr * r["dd"], S, rr, K, G, 1e9, 0, ns=1500, seed=31)
            if best is None or cob.mean() > best[0]: best = (cob.mean(), fr, S, rr, K, G)
        _, fr, S, rr, K, G = best
        res = {}
        for lab, D in [("2021-26", D21), ("2011-20", D11)]:
            of.D = D
            cob, nret, viv, qb = of.correr(tipo, size, r, fr * r["dd"], S, rr, K, G, 1e9, 0, ns=8000, seed=4242)
            res[lab] = cob.mean(); res[lab + "_pcobra"] = (nret > 0).mean()
        of.D = D21
        rows.append(dict(fase="fondeada", plan=tipo, size=size, politica=f"R={fr*r['dd']:.0f}$, S={S}, T={S*rr}, K={K}, G={G:.0f}", **res))
        print(rows[-1], flush=True)
V = pd.DataFrame(rows); V.to_csv(os.path.join(of.RES, "validacion_politicas.csv"), index=False)
pd.set_option("display.width", 220); print(V.round(3).to_string(index=False))
