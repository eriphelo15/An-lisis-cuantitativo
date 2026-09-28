"""Ronda 4 (pre-registro en HIPOTESIS_SELECCION.md): día de tema por palabras poco comunes del nombre + lista fija de temas."""
import collections, glob, json, os, re
import numpy as np
import pandas as pd
from scipy import stats

X = pd.read_csv("res_11_seleccion.csv", parse_dates=["date"]).drop(columns=["cat"])
tk = json.load(open("/home/user/data/sec/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
nom = {}
for f in glob.glob("/home/user/data/sec/subs/*.parquet"):
    x = pd.read_parquet(f, columns=["cik", "name"]); nom[int(x.cik.iloc[0])] = str(x.name.iloc[0])
X["nombre"] = X.sym.map(lambda s: nom.get(t2c.get(s), ""))
C = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
C["date"] = pd.to_datetime(C.fecha)
X = X.merge(C[["sym", "date", "tipo"]], on=["sym", "date"], how="left")

TEMAS = {"IA": r"\bartificial intelligence\b|\bAI\b|\bA\.I\.", "cripto": r"blockchain|bitcoin|crypto|digital asset|\btoken",
         "cuántica": r"quantum", "drones/defensa": r"\bdrone|defense|defence", "nuclear/uranio": r"nuclear|uranium",
         "minerales": r"rare earth|lithium|greenland", "robótica/espacio": r"robot|\bspace\b|satellite"}
pal = lambda n: set(re.findall(r"[a-z]{4,}", n.lower()))
frec = collections.Counter(w for n in X.nombre for w in pal(n))


def palabras(r):
    s = {w for w in pal(r.nombre) if frec[w] <= 15}
    txt = r.nombre
    f = f"/home/user/data/sec/pr/{r.sym}_{r.date.date()}.txt"
    if os.path.exists(f):
        txt += " " + open(f).read()
    s |= {"#" + k for k, p in TEMAS.items() if re.search(p, txt, re.I)}
    return s


X["pal"] = [palabras(r) for r in X.itertuples()]
X["tema"] = False; X["lider"] = False; X["palabra_tema"] = ""
for d, g in X.groupby("date"):
    cnt = collections.defaultdict(list)
    for i, r in g.iterrows():
        for w in r.pal:
            cnt[w].append(i)
    for w, idx in cnt.items():
        if len(set(X.loc[idx, "sym"])) >= 2:
            X.loc[idx, "tema"] = True
            X.loc[idx, "palabra_tema"] = X.loc[idx, "palabra_tema"] + w + " "
            X.loc[X.loc[idx, "gap"].idxmax(), "lider"] = True
X[["sym", "date", "gap", "nombre", "tipo", "tema", "lider", "palabra_tema", "R", "mae", "dia2", "per"]].to_csv("res_17_tema.csv", index=False)


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)


pd.set_option("display.width", 220)
print("GRML/GLND 21-sep-2026:\n", X[X.date == "2026-09-21"][["sym", "gap", "tema", "lider", "palabra_tema"]].to_string())
print("\nfrecuencia día de tema (gap>=50):", X[X.gap >= .5].tema.mean().round(3))
print("palabras de tema más comunes:", collections.Counter(w for s in X[X.tema].palabra_tema for w in s.split()).most_common(25))
G = X[X.gap >= .5]
filas = []
for per in ["DEV 2015-21", "VAL 2022-26"]:
    W = G[G.per == per]
    for nom_, m in [("día normal", ~W.tema), ("día de tema", W.tema), ("tema: líder", W.tema & W.lider), ("tema: seguidor", W.tema & ~W.lider),
                    ("humo día normal", (W.tipo == "H") & ~W.tema), ("humo día de tema", (W.tipo == "H") & W.tema)]:
        filas.append(dict(periodo=per, grupo=nom_, **met(W[m].R), squeeze=(W[m].mae > .5).mean(), dia2=W[m].dia2.mean()))
T = pd.DataFrame(filas); T.to_csv("res_17_resumen.csv", index=False); print(T.round(3).to_string(index=False))

out = []
for per in ["DEV 2015-21", "VAL 2022-26"]:
    W = G[G.per == per]
    for nom_, a, b in [("HT1 normal vs tema", ~W.tema, W.tema), ("HT2 seguidor vs líder", W.tema & ~W.lider, W.tema & W.lider),
                       ("HT3 humo normal vs humo tema", (W.tipo == "H") & ~W.tema, (W.tipo == "H") & W.tema)]:
        out.append(dict(hipotesis=nom_, periodo=per, dif_R=W[a].R.mean() - W[b].R.mean(),
                        t=stats.ttest_ind(W[a].R, W[b].R, equal_var=False).statistic))
O = pd.DataFrame(out); O.to_csv("res_17_hipotesis.csv", index=False); print(O.round(3).to_string(index=False))
v = O[O.periodo == "VAL 2022-26"].copy(); v["p"] = 2 * (1 - stats.norm.cdf(v.t.abs())); v = v.sort_values("p")
v["holm_ok"] = [p < 0.05 / (len(v) - i) for i, p in enumerate(v.p)]; v["holm_ok"] = v.holm_ok.cummin()
print(v.round(4).to_string(index=False))
