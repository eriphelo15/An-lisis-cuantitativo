"""Ronda 2b (pre-registro en HIPOTESIS_SELECCION.md): catalizador clasificado a mano y a ciegas.
Une las etiquetas (clasificacion_catalizador.csv, hecha sin ver resultados) con el resultado del corto (res_11_seleccion.csv)."""
import numpy as np
import pandas as pd
from scipy import stats

NOM = {"C": "compra en efectivo", "F": "financiación", "R": "resultados", "B": "biotech real (FDA/datos)",
       "K": "contrato real con cifra", "H": "humo / cosmético", "S": "corporativo / bolsa", "O": "otros"}
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})   # id, sym, fecha, tipo
X = pd.read_csv("res_11_seleccion.csv", parse_dates=["date"]).drop(columns=["cat"])
X["fecha"] = X.date.dt.strftime("%Y-%m-%d")
Z = E.merge(X, on=["sym", "fecha"], how="inner")
Z["catalizador"] = Z.tipo.map(NOM)
print("gappers con catalizador clasificado:", len(Z), "de", len(E))


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan_media=g.mean(), perd_media=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)


filas = []
for per in ["DEV 2015-21", "VAL 2022-26", "TODO"]:
    W = Z if per == "TODO" else Z[Z.per == per]
    for c, g in W.groupby("catalizador"):
        filas.append(dict(periodo=per, catalizador=c, **met(g.R), squeeze=(g.mae > .5).mean()))
    for nom, msk in [("gap >= 50 % | humo", (W.gap >= .5) & (W.tipo == "H")), ("gap >= 50 % | resto", (W.gap >= .5) & (W.tipo != "H"))]:
        filas.append(dict(periodo=per, catalizador=nom, **met(W[msk].R), squeeze=(W[msk].mae > .5).mean()))
T = pd.DataFrame(filas)
T.to_csv("res_15_por_catalizador.csv", index=False)
pd.set_option("display.width", 220)
print(T.round(3).to_string(index=False))

hip = [("H11b humo vs real (B+K+R)", lambda W: W[W.tipo.isin(["H", "B", "K", "R"])]),
       ("H12b humo vs todo lo demás", lambda W: W)]
out = []
for nom, sub in hip:
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        W = sub(Z[Z.per == per]); si, no = W[W.tipo == "H"], W[W.tipo != "H"]
        a, b = met(si.R), met(no.R)
        out.append(dict(hipotesis=nom, periodo=per, n_humo=a["n"], R_humo=a["R"], WR_humo=a["WR"], PF_humo=a["PF"],
                        n_resto=b["n"], R_resto=b["R"], PF_resto=b["PF"], dif_R=a["R"] - b["R"],
                        t=stats.ttest_ind(si.R, no.R, equal_var=False).statistic))
O = pd.DataFrame(out)
v = O[O.periodo == "VAL 2022-26"].copy(); v["p"] = 2 * (1 - stats.norm.cdf(v.t.abs()))
O = O.merge(v[["hipotesis", "p"]], on="hipotesis", how="left")
O.to_csv("res_15_hipotesis.csv", index=False)
print(O.round(4).to_string(index=False))
