"""Ronda 7 (pre-registro en HIPOTESIS_SELECCION.md): subgrupos del humo con gap 20-50 % (precio real ≥ $1)."""
import numpy as np
import pandas as pd
from scipy import stats

X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
X = X[~X.ambiguo & (X.precio >= 1)]
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
Z = E.merge(X, on=["sym", "fecha"], how="inner")
H = Z[(Z.tipo == "H") & (Z.gap >= .2) & (Z.gap < .5)].copy()
H["solo_pr"] = H.cat == "8-K solo nota de prensa (7.01/8.01)"
H["con_101"] = H.cat == "8-K con acuerdo (1.01)"
H["s3b"] = H.s3.astype(bool)
print("humo 20-50 % (≥ $1):", len(H), H.per.value_counts().to_dict())


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, t0=v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan)


filas, tests = [], []
for nom, si_m, no_m in [("HS1 con 424B 90 d", H.venta90 == True, H.venta90 != True),
                        ("HS2 con shelf S-3", H.s3b, ~H.s3b),
                        ("HS3 solo nota de prensa (vs 1.01)", H.solo_pr, H.con_101)]:
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        P = H.per == per
        a, b = met(H[si_m & P].R), met(H[no_m & P].R)
        filas.append(dict(subgrupo=nom, periodo=per, **{f"{k}_si": v for k, v in a.items()}, n_no=b["n"], R_no=b["R"], PF_no=b["PF"]))
        if per == "VAL 2022-26":
            tests.append((nom, stats.ttest_ind(H[si_m & P].R, H[no_m & P].R, equal_var=False).statistic))
T = pd.DataFrame(filas)
T.to_csv("res_20_humo_20_50.csv", index=False)
pd.set_option("display.width", 250)
print(T.round(3).to_string(index=False))
O = pd.DataFrame(tests, columns=["hipotesis", "t_dif_VAL"])
O["p"] = 2 * (1 - stats.norm.cdf(O.t_dif_VAL.abs()))
O = O.sort_values("p"); m = len(O)
O["holm_ok"] = [p < 0.05 / (m - i) for i, p in enumerate(O.p)]
O["holm_ok"] = O.holm_ok.cummin()
print("\n" + O.round(4).to_string(index=False))
