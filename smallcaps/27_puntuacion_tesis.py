"""Ronda 12 (pre-registro en HIPOTESIS_SELECCION.md): puntuación global de la tesis de corto. Pesos de DEV 2015-21, prueba en VAL 2022-26."""
import json
import numpy as np
import pandas as pd
from scipy import stats

X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
Z = E.merge(X, on=["sym", "fecha"], how="inner")
Z = Z[~Z.ambiguo & (Z.precio >= 1) & ~Z.tipo.isin(["C", "R", "F", "S"])].copy()
F = pd.DataFrame(index=Z.index)
F["gap_50_100"] = ((Z.gap >= .5) & (Z.gap < 1)).astype(float)
F["gap_100"] = (Z.gap >= 1).astype(float)
for t in ["H", "B", "K"]:
    F[f"cat_{t}"] = (Z.tipo == t).astype(float)
for c in ["venta90", "s3", "serie", "solo_pr"]:
    F[c] = Z[c].astype(float)
D, V = Z.per.str.startswith("DEV"), Z.per.str.startswith("VAL")
A = np.c_[np.ones(D.sum()), F[D].values]
coef, *_ = np.linalg.lstsq(A, Z.loc[D, "R"].values, rcond=None)
pesos = dict(zip(["constante"] + list(F.columns), coef.round(4)))
Z["pred"] = coef[0] + F.values @ coef[1:]
ref = np.sort(Z.loc[D, "pred"].values)
Z["puntuacion"] = np.searchsorted(ref, Z.pred, side="right") / len(ref) * 100
Z["tercio"] = pd.cut(Z.puntuacion, [-1, 100 / 3, 200 / 3, 101], labels=["bajo", "medio", "alto"])


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(), PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan))


pd.set_option("display.width", 200)
print("pesos (DEV):", json.dumps(pesos))
print(Z.groupby(["per", "tercio"], observed=True).R.apply(met).unstack().round(3).to_string())
print("\ndentro de gap ≥ 50 %:")
print(Z[Z.gap >= .5].groupby(["per", "tercio"], observed=True).R.apply(met).unstack().round(3).to_string())
rho, p = stats.spearmanr(Z.loc[V, "puntuacion"], Z.loc[V, "R"])
alto, bajo = Z[V & (Z.tercio == "alto")].R, Z[V & (Z.tercio == "bajo")].R
t = stats.ttest_ind(alto, bajo, equal_var=False).statistic
print(f"\nHS1 Spearman VAL rho={rho:.3f} p={p:.4f} → {'OK' if p < .05 and rho > 0 else 'NO'}")
print(f"HS2 alto−bajo VAL {alto.mean() - bajo.mean():+.3f}R t={t:.2f} → {'OK' if t > 2 else 'NO'}")
rd, pdv = stats.spearmanr(Z.loc[D, "puntuacion"], Z.loc[D, "R"]); print(f"(DEV, dentro de muestra: rho={rd:.3f})")
json.dump(dict(pesos=pesos, ref_dev=list(map(float, ref))), open("puntuacion_pesos.json", "w"))
Z[["sym", "fecha", "per", "gap", "tipo", "R", "puntuacion", "tercio"]].to_csv("res_27_puntuacion.csv", index=False)
