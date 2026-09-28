"""Ronda 6 (pre-registro en HIPOTESIS_SELECCION.md): humo con gap 20-50 %, gappers sin 8-K, día 2 del humo.
Precio real (ronda 5), precio ≥ $1, casos ambiguos por split fuera. Setup base: corto a la apertura, stop +30 % (5 % de
deslizamiento), coste 1 %, salida al cierre."""
import numpy as np
import pandas as pd
from scipy import stats

STOP, DESL, COSTE = 0.30, 0.05, 0.01
X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
EV = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")[["sym", "date", "n_o", "n_h", "n_l", "n_c"]]
EV["date"] = pd.to_datetime(EV.date)
X = X.merge(EV, on=["sym", "date"], how="left")
X = X[~X.ambiguo & (X.precio >= 1)]
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
Z = E.merge(X, on=["sym", "fecha"], how="inner")


def r_setup(o, h, c):
    if not (o > 0 and h > 0 and c > 0):
        return np.nan
    if h >= o * (1 + STOP):
        return -((o * (1 + STOP) * (1 + DESL) - o) / o + COSTE) / STOP
    return ((o - c) / o - COSTE) / STOP


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, t0=v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan)


filas = []
def add(nom, W, col="R"):
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        V = W[W.per == per]
        filas.append(dict(grupo=nom, periodo=per, **met(V[col]), squeeze=(V.mae > .5).mean() if col == "R" else np.nan))


# HM1 humo 20-50 %
g2050 = Z[(Z.gap >= .2) & (Z.gap < .5)]
add("HM1 humo gap 20-50 %", g2050[g2050.tipo == "H"])
add("    resto gap 20-50 %", g2050[g2050.tipo != "H"])
# HM2 sin 8-K, gap ≥ 50 %
add("HM2 sin 8-K, gap ≥ 50 %", X[(X.gap >= .5) & (X.cat == "sin 8-K")])
add("    con 8-K, gap ≥ 50 %", X[(X.gap >= .5) & (X.cat != "sin 8-K")])
# HM3 día 2 del humo con gap ≥ 50 %
H = Z[(Z.tipo == "H") & (Z.gap >= .5)].copy()
H["R2"] = [r_setup(o, h, c) for o, h, c in zip(H.n_o, H.n_h, H.n_c)]
H["mae"] = H.n_h / H.n_o - 1
add("HM3 día 2 del humo gap ≥ 50 %", H, col="R2")
H1 = H[H.gap >= 1]
add("    día 2, humo gap ≥ 100 %", H1, col="R2")
T = pd.DataFrame(filas)
T.to_csv("res_19_mas_oportunidades.csv", index=False)
pd.set_option("display.width", 250)
print(T.round(3).to_string(index=False))

# hipótesis y Holm (VAL)
v1a, v1b = g2050[(g2050.tipo == "H") & (g2050.per == "VAL 2022-26")].R, g2050[(g2050.tipo != "H") & (g2050.per == "VAL 2022-26")].R
tests = [("HM1 humo vs resto (20-50 %)", stats.ttest_ind(v1a, v1b, equal_var=False).statistic),
         ("HM2 sin 8-K ≠ 0", met(X[(X.gap >= .5) & (X.cat == "sin 8-K") & (X.per == "VAL 2022-26")].R)["t0"]),
         ("HM3 día 2 humo ≠ 0", met(H[H.per == "VAL 2022-26"].R2)["t0"])]
O = pd.DataFrame(tests, columns=["hipotesis", "t_VAL"])
O["p"] = 2 * (1 - stats.norm.cdf(O.t_VAL.abs()))
O = O.sort_values("p"); m = len(O)
O["holm_ok"] = [p < 0.05 / (m - i) for i, p in enumerate(O.p)]
O["holm_ok"] = O.holm_ok.cummin()
print("\n" + O.round(4).to_string(index=False))
# frecuencia en el último año (precio ≥ $1)
dias = len(pd.bdate_range("2025-09-26", "2026-09-25"))
U = X[X.date >= "2025-09-26"]
print(f"\nfrecuencia último año ({dias} días hábiles): gap 20-50 % ≥ $1: {((U.gap >= .2) & (U.gap < .5)).sum() / dias:.2f}/día · "
      f"gap ≥ 50 % sin 8-K ≥ $1: {((U.gap >= .5) & (U.cat == 'sin 8-K')).sum() / dias:.2f}/día")
print("proporción de humo entre los clasificados con gap 20-50 % (2024-26):",
      round((g2050[g2050.date >= "2024-01-01"].tipo == "H").mean(), 2))
