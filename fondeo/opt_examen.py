"""Optimiza la política del EXAMEN (maximizar probabilidad de aprobar) para Growth y Select, 4 tamaños."""
import numpy as np, pandas as pd, itertools, os, time
from motor_fondeo import examen
from reglas_tradeify import EXAMEN
D = np.load("/home/user/data/dias_rth.npy")
RES = os.path.join(os.path.dirname(__file__), "resultados"); os.makedirs(RES, exist_ok=True)
rows = []; t0 = time.time()
for plan, sizes in EXAMEN.items():
    for size, r in sizes.items():
        dd, tgt = r["dd"], r["target"]; mm = r["max_mini"] * 10
        dll = r["dll"] or 0.0; cons = r["consist"] or 0.0
        for fr, S, rr, K in itertools.product([0.15, 0.25, 0.4, 0.6, 0.8, 1.0], [10, 15, 20, 30, 45, 60], [0.5, 1, 1.5, 2, 3, 4], [1, 2, 3, 5]):
            R = fr * dd
            Gs = [1e9] if cons == 0 else [cons * tgt * 0.5, cons * tgt * 0.8, cons * tgt * 0.95]
            for G in Gs:
                ok, d = examen(D, 3000, float(tgt), float(dd), float(dll), float(cons), r["min_dias"], float(R), float(S), float(S * rr),
                               K, float(G), 1e9, mm, 60, 11)
                rows.append(dict(plan=plan, size=size, riesgo_frac_dd=fr, R=R, S=S, rr=rr, K=K, G=G, pass_=ok.mean(), dias=d[ok].mean() if ok.any() else np.nan))
        print(plan, size, f"{time.time()-t0:.0f}s", flush=True)
R = pd.DataFrame(rows); R.to_csv(os.path.join(RES, "opt_examen_grid.csv"), index=False)
best = R.sort_values("pass_", ascending=False).groupby(["plan", "size"]).head(3)
pd.set_option("display.width", 200)
print(best.sort_values(["plan", "size", "pass_"], ascending=[True, True, False]).round(3).to_string(index=False))
