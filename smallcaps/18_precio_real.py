"""Ronda 5 (pre-registro en HIPOTESIS_SELECCION.md): precio REAL (sin ajuste por splits posteriores), acciones < $1,
coste del locate en centavos y capitalización corregida.

Yahoo da los precios ajustados por splits posteriores: precio real = ajustado × producto de los ratios de los splits
posteriores a la fecha. splits.parquet trae la fecha como día 1 del mes → si hay split en el mismo mes del evento, el caso
es ambiguo y se aparta del análisis principal."""
import numpy as np
import pandas as pd
from scipy import stats

D = "/home/user/data/smallcaps"
SP = pd.read_parquet(f"{D}/splits.parquet")
SP["t"] = pd.to_datetime(SP.t)
X = pd.read_csv("res_11_seleccion.csv", parse_dates=["date"])
EV = pd.read_parquet(f"{D}/eventos_gappers.parquet")[["sym", "date", "open"]]
EV["date"] = pd.to_datetime(EV.date)
X = X.merge(EV, on=["sym", "date"], how="left")
assert X.open.notna().all()

por_sym = {s: g for s, g in SP.groupby("sym")}


def factor(sym, d):
    g = por_sym.get(sym)
    if g is None:
        return 1.0, False
    mes = pd.Timestamp(d.year, d.month, 1)
    amb = bool((g.t == mes).any())
    return float(g[g.t > mes].ratio.prod()), amb


F = [factor(s, d) for s, d in zip(X.sym, X.date)]
X["f"] = [a for a, _ in F]
X["ambiguo"] = [b for _, b in F]
X["precio"] = X.open * X.f                      # precio real de apertura
X["mcap_real"] = X.mcap * X.f                   # acciones (SEC, de esa fecha) × precio real
print(f"gappers: {len(X)} | con split posterior: {(X.f != 1).mean():.0%} | ambiguos (split el mismo mes): {X.ambiguo.sum()}")
print("precio de apertura ajustado vs real (mediana):", round(X.open.median(), 2), "→", round(X.precio.median(), 2))
print("capitalización (mediana) de la ronda 1 vs corregida: $%.0f M → $%.0f M" % (X.mcap.median() / 1e6, X.mcap_real.median() / 1e6))

# comprobación de cordura con casos conocidos
for s, d in [("WHLR", "2025-12-05"), ("GRML", "2026-09-21"), ("APUS", None)]:
    q = X[(X.sym == s) & ((X.date == d) if d else True)][["sym", "date", "open", "f", "precio", "ambiguo"]].tail(2)
    print(q.to_string(index=False, header=False))

E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
X["fecha"] = X.date.dt.strftime("%Y-%m-%d")
Z = E.merge(X, on=["sym", "fecha"], how="inner")
X.to_csv("res_18_precio_real.csv", index=False)


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan_media=g.mean(), perd_media=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)


COM = 0.05                                       # comisión ida y vuelta ≈ 0.05R con riesgo de $20
def neto(W, L):
    return W.R - L / (0.30 * W.precio) - COM


H = Z[(Z.tipo == "H") & (Z.gap >= 0.5) & ~Z.ambiguo].copy()
print(f"\nhumo con gap ≥ 50 %: {len(H)} (+ {((Z.tipo == 'H') & (Z.gap >= .5) & Z.ambiguo).sum()} ambiguos apartados)")
H["tramo"] = pd.cut(H.precio, [0, 1, 3, 10, 1e9], right=False, labels=["< $1", "$1-3", "$3-10", "≥ $10"])
filas = []
for per in ["DEV 2015-21", "VAL 2022-26", "TODO"]:
    W = H if per == "TODO" else H[H.per == per]
    for tr, g in W.groupby("tramo", observed=True):
        fila = dict(periodo=per, tramo=tr, **met(g.R))
        for L in (0.01, 0.02, 0.05):
            fila[f"R_neto_L{int(L*100)}c"] = neto(g, L).mean()
        filas.append(fila)
T = pd.DataFrame(filas)
T.to_csv("res_18_tramos.csv", index=False)
pd.set_option("display.width", 250)
print(T.round(3).to_string(index=False))

# hipótesis
out = []
for nom, col_si, serie, base in [
        ("HP1 humo gap≥50 %: R bruto, < $1 vs ≥ $1", None, "bruto", H),
        ("HP2 humo gap≥50 %: R neto (locate $0.02 + comisión), ≥ $1 vs < $1", None, "neto", H)]:
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        W = base[base.per == per]
        v = W.R if serie == "bruto" else neto(W, 0.02)
        si, no = (v[W.precio < 1], v[W.precio >= 1]) if serie == "bruto" else (v[W.precio >= 1], v[W.precio < 1])
        a, b = met(si), met(no)
        out.append(dict(hipotesis=nom, periodo=per, n_si=a["n"], R_si=a["R"], WR_si=a["WR"], PF_si=a["PF"],
                        n_no=b["n"], R_no=b["R"], PF_no=b["PF"], dif=a["R"] - b["R"],
                        t=stats.ttest_ind(si, no, equal_var=False).statistic if min(len(si), len(no)) > 2 else np.nan))
XX = X[~X.ambiguo & X.mcap_real.notna()]
for per in ["DEV 2015-21", "VAL 2022-26"]:
    W = XX[XX.per == per]; si, no = W[W.mcap_real < 30e6].R, W[W.mcap_real >= 30e6].R
    a, b = met(si), met(no)
    out.append(dict(hipotesis="HP3 capitalización corregida < $30 M (peor)", periodo=per, n_si=a["n"], R_si=a["R"], WR_si=a["WR"],
                    PF_si=a["PF"], n_no=b["n"], R_no=b["R"], PF_no=b["PF"], dif=a["R"] - b["R"],
                    t=stats.ttest_ind(si, no, equal_var=False).statistic))
O = pd.DataFrame(out)
v = O[O.periodo == "VAL 2022-26"].copy()
v["p"] = 2 * (1 - stats.norm.cdf(v.t.abs()))
v = v.sort_values("p"); m = len(v)
v["holm_ok"] = [p < 0.05 / (m - i) for i, p in enumerate(v.p)]
v["holm_ok"] = v.holm_ok.cummin()
O = O.merge(v[["hipotesis", "p", "holm_ok"]], on="hipotesis", how="left")
O.to_csv("res_18_hipotesis.csv", index=False)
print("\n" + O.round(4).to_string(index=False))

# capitalización corregida por tramos (todos los gappers ≥ 50 %, como en la ronda 1 / 07_filtros)
C = XX[XX.gap >= 0.5].copy()
C["cap"] = pd.cut(C.mcap_real, [0, 10e6, 30e6, 100e6, 1e15], labels=["<$10M", "$10-30M", "$30-100M", "≥$100M"])
print("\ngap ≥ 50 %, capitalización CORREGIDA:")
print(C.groupby(["per", "cap"], observed=True).R.agg(["count", "mean"]).round(3).to_string())
# nivel A del Radar (humo + gap≥50 + 424B 90 d + cap ≥ 30 M) con la capitalización corregida
A = Z[(Z.tipo == "H") & (Z.gap >= .5) & Z.venta90 & ~Z.ambiguo]
for per in ["DEV 2015-21", "VAL 2022-26"]:
    W = A[A.per == per]
    print(per, "nivel A (cap ronda 1 ≥ 30 M):", {k: round(x, 3) for k, x in met(W[W.mcap >= 30e6].R).items()},
          "| cap corregida ≥ 30 M:", {k: round(x, 3) for k, x in met(W[W.mcap_real >= 30e6].R).items()})
