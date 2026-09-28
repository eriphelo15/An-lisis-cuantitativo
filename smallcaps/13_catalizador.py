"""Ronda 2 (pre-registro en HIPOTESIS_SELECCION.md): contenido del catalizador y temas de moda."""
import glob, json, os, re
import numpy as np
import pandas as pd
from scipy import stats

PR = "/home/user/data/sec/pr"
X = pd.read_csv("res_11_seleccion.csv", parse_dates=["date"])
tk = json.load(open("/home/user/data/sec/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
nombres = {}
for f in glob.glob("/home/user/data/sec/subs/*.parquet"):
    x = pd.read_parquet(f, columns=["cik", "name"])
    nombres[int(x.cik.iloc[0])] = str(x.name.iloc[0])
X["nombre"] = X.sym.map(lambda s: nombres.get(t2c.get(s), ""))

DOLAR = re.compile(r"\$\s?\d[\d,\.]*\s?(million|billion|mm|m\b|bn)", re.I)
TEMAS = {"IA": r"\bartificial intelligence\b|\bAI\b|\bA\.I\.", "cripto": r"blockchain|bitcoin|crypto|digital asset|\btoken", "cuántica": r"quantum",
         "drones/defensa": r"\bdrone|defense|defence", "nuclear/uranio": r"nuclear|uranium", "minerales": r"rare earth|lithium|greenland",
         "robótica/espacio": r"robot|\bspace\b|satellite"}


def clasificar(t, items):
    tl = t.lower()
    if re.search(r"merger agreement|to be acquired|definitive agreement to be acquired", tl) and re.search(r"per share in cash|all-cash|all cash", tl):
        return "compra en efectivo"
    if "2.02" in items or re.search(r"reports? [^.]{0,80}results|financial results", tl):
        return "resultados"
    if (re.search(r"\bfda\b", tl) and re.search(r"approv|clear|grant|designation", tl)) or re.search(r"topline|primary endpoint", tl):
        return "FDA / clínico"
    tiene_d = bool(DOLAR.search(t))
    if re.search(r"agreement|contract|purchase order|\border\b|award", tl) and tiene_d:
        return "contrato con cifra"
    if re.search(r"letter of intent|\bloi\b|memorandum of understanding|\bmou\b|non-binding|partnership|collaboration|explore|exploring|pilot", tl) and not tiene_d:
        return "humo"
    return "otros"


cat, dolar, tema_txt = [], [], []
for r in X.itertuples():
    f = f"{PR}/{r.sym}_{r.date.date()}.txt"
    if os.path.exists(f):
        t = open(f).read()
        items = t.split("\n", 1)[0]
        cat.append(clasificar(t, items)); dolar.append(bool(DOLAR.search(t)))
        tema_txt.append([k for k, p in TEMAS.items() if re.search(p, t, re.I)])
    else:
        cat.append(None); dolar.append(None); tema_txt.append([])
X["cat_txt"], X["dolar"] = cat, dolar
X["temas"] = [sorted(set(tt) | {k for k, p in TEMAS.items() if re.search(p, n, re.I)}) for tt, n in zip(tema_txt, X.nombre)]
X["tema_moda"] = X.temas.map(len) > 0
# día de tema: >= 2 gappers (>= 50 %) el mismo día con una palabra clave de tema en común
cont = {}
for d, ts, gp in zip(X.date, X.temas, X.gap):
    if gp >= 0.5:
        for k in ts:
            cont[(d, k)] = cont.get((d, k), 0) + 1
X["dia_tema"] = [any(cont.get((d, k), 0) >= (2 if gp >= 0.5 else 1) for k in ts) for d, ts, gp in zip(X.date, X.temas, X.gap)]
X.to_csv("res_13_catalizador.csv", index=False)


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(), PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)


print("gappers con texto de catalizador:", X.cat_txt.notna().sum())
print("\n== Por tipo de catalizador (setup A, R) ==")
filas = []
for per in ["DEV 2015-21", "VAL 2022-26"]:
    for c, g in X[(X.per == per) & X.cat_txt.notna()].groupby("cat_txt"):
        m = met(g.R); filas.append(dict(periodo=per, catalizador=c, **m, squeeze=(g.mae > .5).mean()))
print(pd.DataFrame(filas).round(3).to_string(index=False))

hip = [("H11 humo vs real (FDA/contrato/resultados)", lambda Z: Z[Z.cat_txt.isin(["humo", "FDA / clínico", "contrato con cifra", "resultados"])], lambda Z: Z.cat_txt == "humo"),
       ("H12 sin cifra en dólares", lambda Z: Z[Z.dolar.notna()], lambda Z: Z.dolar == False),
       ("H14 NO es tema de moda", lambda Z: Z, lambda Z: ~Z.tema_moda),
       ("H15 NO es día de tema", lambda Z: Z, lambda Z: ~Z.dia_tema)]
out = []
for nom, sub, cond in hip:
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        Z = sub(X[X.per == per]); c = cond(Z).astype(bool)
        si, no = Z[c], Z[~c]
        a, b = met(si.R), met(no.R)
        out.append(dict(hipotesis=nom, periodo=per, n_cumple=a["n"], R_cumple=a["R"], WR_cumple=a["WR"], PF_cumple=a["PF"],
                        n_resto=b["n"], R_resto=b["R"], PF_resto=b["PF"], dif_R=a["R"] - b["R"],
                        t=stats.ttest_ind(si.R, no.R, equal_var=False).statistic, squeeze_cumple=(si.mae > .5).mean(), squeeze_resto=(no.mae > .5).mean()))
O = pd.DataFrame(out); O.to_csv("res_13_resumen.csv", index=False)
print("\n== Hipótesis ==")
print(O.round(3).to_string(index=False))
v = O[O.periodo == "VAL 2022-26"].copy(); v["p"] = 2 * (1 - stats.norm.cdf(v.t.abs())); v = v.sort_values("p")
v["holm_ok"] = [p < 0.05 / (len(v) - i) for i, p in enumerate(v.p)]; v["holm_ok"] = v.holm_ok.cummin()
print("\nHolm (VAL):"); print(v[["hipotesis", "dif_R", "t", "p", "holm_ok"]].round(4).to_string(index=False))
print("\n== Temas de moda (todos los periodos): R por tema ==")
Y = X.explode("temas").dropna(subset=["temas"])
print(Y.groupby("temas").R.apply(lambda v: pd.Series(met(v))).unstack().round(3).to_string())
