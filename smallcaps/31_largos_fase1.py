"""Ronda 14 — lado largo, fase 1 (pre-registro en HIPOTESIS_SELECCION.md). Hipótesis de CAMPO medidas con el setup base largo."""
import numpy as np
import pandas as pd
from scipy import stats

D = "/home/user/data/smallcaps"
X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
P = pd.read_csv("res_29_precios.csv")
assert (X.sym.values == P.sym.values).all()
X["precio_v"] = P.precio_T.fillna(P.precio_corr).fillna(P.precio).values
X = X[(~X.ambiguo) | P.precio_T.notna().values]
E = pd.read_parquet(f"{D}/eventos_gappers.parquet")[["sym", "date", "open", "high", "low", "close", "n_o", "n_h", "n_l", "n_c"]]
X = X.drop(columns=["open"]).merge(E, on=["sym", "date"])
L = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
X = X.merge(L[["sym", "fecha", "tipo"]], on=["sym", "fecha"], how="left")
X = X[X.precio_v >= 1].copy()
STOP, DESL, COSTE = 0.20, 0.02, 0.005


def largo(r, dias=1):
    st = r.open * (1 - STOP)
    if r.low <= st:
        return ((st * (1 - DESL) - r.open) / r.open - COSTE) / STOP
    if dias == 1:
        return ((r.close - r.open) / r.open - COSTE) / STOP
    if pd.isna(r.n_o):
        return np.nan
    if r.n_o <= st:
        return ((r.n_o - r.open) / r.open - COSTE) / STOP
    if r.n_l <= st:
        return ((st * (1 - DESL) - r.open) / r.open - COSTE) / STOP
    return ((r.n_c - r.open) / r.open - COSTE) / STOP


X["RL"] = X.apply(largo, axis=1)
X["RL2"] = X.apply(lambda r: largo(r, 2), axis=1)
X["cola50"] = X.high >= X.open * 1.5
X["cola100"] = X.high >= X.open * 2
X["municion"] = X.venta90.astype(bool) | X.s3.astype(bool)
X["acciones"] = X.mcap_real / X.precio
X["real"] = X.tipo.isin(["K", "B"])


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                          PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, dolares=20 * v.sum()))


pd.set_option("display.width", 220)
Dm = X.per.str.startswith("DEV")
print("universo largo (≥ $1):", len(X), "| con etiqueta:", X.tipo.notna().sum())
print("\nTODOS los gappers (base):\n", X.groupby("per").RL.apply(met).unstack().round(3).to_string())
print("\npor tipo de catalizador (etiquetados):\n", X[X.tipo.notna()].groupby(["tipo", "per"]).RL.apply(met).unstack().round(3).to_string())
G = {"HL1 real sin munición": X.real & ~X.municion, "real CON munición": X.real & X.municion,
     "HL3 real sin mun. <5M acc": X.real & ~X.municion & (X.acciones < 5e6), "real sin mun. ≥5M": X.real & ~X.municion & (X.acciones >= 5e6),
     "humo (control)": X.tipo == "H", "sin munición (todos)": ~X.municion}
filas = []
for k, m in G.items():
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        s = X[m & (X.per == per)]
        filas.append(dict(grupo=k, per=per, **met(s.RL).round(3).to_dict(), R_dia2=round(s.RL2.mean(), 3),
                          cola50=round(s.cola50.mean(), 3), cola100=round(s.cola100.mean(), 3)))
print("\n", pd.DataFrame(filas).to_string(index=False))
T = pd.read_csv("res_30_ronda12_corregida.csv").merge(X[["sym", "fecha", "RL", "RL2"]], on=["sym", "fecha"])
print("\nHL4 por tercio de la tesis CORTA (corregida):\n", T.groupby(["per", "tercio"]).RL.apply(met).unstack().round(3).to_string())


def tt(a, b):
    return stats.ttest_ind(a.dropna(), b.dropna(), equal_var=False)


V = X.per == "VAL 2022-26"
res = []
h1 = X[X.real & ~X.municion]
for per in ["DEV 2015-21", "VAL 2022-26"]:
    s = h1[h1.per == per].RL.dropna(); res.append(("HL1", per, s.mean(), stats.ttest_1samp(s, 0).statistic if len(s) > 2 else np.nan))
for per in ["DEV 2015-21", "VAL 2022-26"]:
    a = X[X.real & ~X.municion & (X.per == per)].RL; b = X[X.real & X.municion & (X.per == per)].RL
    res.append(("HL2", per, a.mean() - b.mean(), tt(a, b).statistic))
for per in ["DEV 2015-21", "VAL 2022-26"]:
    a = X[X.real & ~X.municion & (X.acciones < 5e6) & (X.per == per)].RL; b = X[X.real & ~X.municion & (X.acciones >= 5e6) & (X.per == per)].RL
    res.append(("HL3", per, a.mean() - b.mean(), tt(a, b).statistic if len(a) > 2 else np.nan))
for per in ["DEV 2015-21", "VAL 2022-26"]:
    s = T[(T.per == per) & (T.tercio == "bajo")].RL.dropna(); res.append(("HL4", per, s.mean(), stats.ttest_1samp(s, 0).statistic))
H = pd.DataFrame(res, columns=["hip", "per", "valor", "t"])
print("\n", H.round(3).to_string(index=False))
v = H[H.per.str.startswith("VAL")].set_index("hip"); d = H[H.per.str.startswith("DEV")].set_index("hip")
pv = {h: stats.norm.sf(v.loc[h, "t"]) for h in v.index}
for k, (h, p) in enumerate(sorted(pv.items(), key=lambda x: x[1])):
    ok = v.loc[h, "valor"] > 0 and d.loc[h, "valor"] > 0 and v.loc[h, "t"] > 2 and p < 0.05 / (4 - k)
    print(h, "p", round(p, 4), "umbral Holm", round(0.05 / (4 - k), 4), "→", "VALIDADA" if ok else "NO validada")
X.to_csv("res_31_largos.csv", index=False)
