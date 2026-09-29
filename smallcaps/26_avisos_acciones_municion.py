"""Ronda 11 (pre-registro en HIPOTESIS_SELECCION.md): ¿el corto sale peor con < 5 M de acciones o sin munición activa?"""
import numpy as np
import pandas as pd
from scipy import stats

X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
X = X[~X.ambiguo & (X.precio >= 1) & (X.gap >= 0.5)].copy()
X["acciones"] = X.mcap_real / X.precio
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
X = X.merge(E[["sym", "fecha", "tipo"]], on=["sym", "fecha"], how="left")
X["pocas"] = X.acciones < 5e6
X["sin_mun"] = ~X.venta90 & ~X.s3


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                          PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, squeeze=None))


pd.set_option("display.width", 220)
Y = X[X.acciones.notna()]
print("con dato de acciones:", len(Y), "de", len(X))
for nom, col, W in [("acciones < 5 M", "pocas", Y), ("sin munición", "sin_mun", X)]:
    print(f"\n== {nom} ==")
    print(W.groupby(["per", col]).R.apply(met).unstack().round(3).to_string())
Y = Y.assign(escalon=pd.cut(Y.acciones, [0, 2e6, 5e6, 20e6, np.inf], labels=["< 2 M", "2-5 M", "5-20 M", "> 20 M"]))
print("\n== escalones de acciones ==")
print(Y.groupby(["per", "escalon"], observed=True).R.apply(met).unstack().round(3).to_string())
H = X[X.tipo == "H"]
print("\n== dentro del humo ==")
print(H.groupby(["per", "sin_mun"]).R.apply(met).unstack().round(3).to_string())
print(H[H.acciones.notna()].groupby(["per", "pocas"]).R.apply(met).unstack().round(3).to_string())
print("\n== las dos juntas (pocas y sin munición) vs resto ==")
Z = X[X.acciones.notna()].assign(ambas=lambda d: d.pocas & d.sin_mun)
print(Z.groupby(["per", "ambas"]).R.apply(met).unstack().round(3).to_string())

V = X[X.per.str.startswith("VAL")]; Dv = X[X.per.str.startswith("DEV")]
def t(W, col):
    W = W.dropna(subset=["R"]); return stats.ttest_ind(W[W[col]].R, W[~W[col]].R, equal_var=False).statistic
def d(W, col):
    return W[W[col]].R.mean() - W[~W[col]].R.mean()
O = pd.DataFrame([("HX1 < 5 M acciones peor", t(V[V.acciones.notna()], "pocas"), d(Dv[Dv.acciones.notna()], "pocas")),
                  ("HX2 sin munición peor", t(V, "sin_mun"), d(Dv, "sin_mun"))], columns=["hipotesis", "t_VAL", "dif_DEV"])
O["p"] = 2 * (1 - stats.norm.cdf(O.t_VAL.abs())); O = O.sort_values("p")
O["holm_ok"] = [p < 0.05 / (2 - i) for i, p in enumerate(O.p)]; O["holm_ok"] = O.holm_ok.cummin()
O["validada"] = O.holm_ok & (O.t_VAL < -2) & (O.dif_DEV < 0)
print("\n" + O.round(4).to_string(index=False))
X.to_csv("res_26_avisos.csv", index=False)
