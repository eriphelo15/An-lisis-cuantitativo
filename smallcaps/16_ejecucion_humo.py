"""Ronda 3 (pre-registro en HIPOTESIS_SELECCION.md): ejecución dentro de la selección, con velas de 1 h.
E0 corto a la apertura · E1/E1c 1ª hora roja/verde · E2/E2c bajo/sobre VWAP a las 11:30. Salida al cierre."""
import os
import numpy as np
import pandas as pd
from scipy import stats

COSTE, DESL = 0.01, 0.05
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
E["fecha"] = pd.to_datetime(E.fecha)
X = pd.read_csv("res_11_seleccion.csv", parse_dates=["date"]).drop(columns=["cat"])
Z = E.merge(X, left_on=["sym", "fecha"], right_on=["sym", "date"])
Z = Z[(Z.fecha >= "2023-10-27") & (Z.fecha <= "2026-09-25")]


def corto(entrada, stop, resto):
    """resto: velas posteriores (High, Close). Stop con deslizamiento; si no, salida al último cierre."""
    for h in resto.High.values:
        if h >= stop:
            sal = stop * (1 + DESL); break
    else:
        sal = resto.Close.values[-1] if len(resto) else entrada
    return ((entrada - sal) / entrada - COSTE) / ((stop - entrada) / entrada)


cache, filas = {}, []
for r in Z.itertuples():
    f = f"/home/user/data/smallcaps/h1/{r.sym}.parquet"
    if not os.path.exists(f):
        continue
    if r.sym not in cache:
        m = pd.read_parquet(f)
        if hasattr(m.columns, "levels"):
            m.columns = m.columns.get_level_values(0)
        if m.index.tz is None:
            m.index = m.index.tz_localize("UTC")
        cache[r.sym] = m.tz_convert("America/New_York")
    m = cache[r.sym]
    b = m[m.index.date == r.fecha.date()].between_time("09:30", "15:30")
    if len(b) < 4 or b.Open.iloc[0] <= 0:
        continue
    o = b.Open.iloc[0]
    d = dict(sym=r.sym, fecha=r.fecha, tipo=r.tipo, gap=r.gap, per="DEV" if r.fecha < pd.Timestamp("2025-01-01") else "VAL")
    # E0: corto a la apertura, stop +30 % (la 1ª vela también cuenta)
    d["E0"] = corto(o, o * 1.30, b)
    # E1 / E1c: a las 10:30 según color de la 1ª hora
    e1 = b.Close.iloc[0]; st1 = max(b.High.iloc[0] * 1.05, e1 * 1.03)
    r1 = corto(e1, st1, b.iloc[1:])
    d["E1"] = r1 if e1 < o else np.nan
    d["E1c"] = r1 if e1 >= o else np.nan
    # E2 / E2c: a las 11:30 según VWAP de las 2 primeras velas
    t = (b.High + b.Low + b.Close) / 3
    v = b.Volume.clip(lower=0)
    vw = (t.iloc[:2] * v.iloc[:2]).sum() / v.iloc[:2].sum() if v.iloc[:2].sum() > 0 else t.iloc[:2].mean()
    e2 = b.Close.iloc[1]; st2 = max(b.High.iloc[:2].max() * 1.05, e2 * 1.03)
    r2 = corto(e2, st2, b.iloc[2:])
    d["E2"] = r2 if e2 < vw else np.nan
    d["E2c"] = r2 if e2 >= vw else np.nan
    filas.append(d)
R = pd.DataFrame(filas)
R.to_csv("res_16_ejecucion.csv", index=False)


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)


pd.set_option("display.width", 220)
print("casos con velas de 1 h:", len(R), "| humo:", (R.tipo == "H").sum())
t_ = []
for grupo, G in [("HUMO", R[R.tipo == "H"]), ("HUMO gap>=50%", R[(R.tipo == "H") & (R.gap >= .5)]), ("RESTO", R[R.tipo != "H"])]:
    for per in ["DEV", "VAL"]:
        W = G[G.per == per]
        for reg in ["E0", "E1", "E1c", "E2", "E2c"]:
            t_.append(dict(grupo=grupo, periodo=per, regla=reg, **met(W[reg])))
T = pd.DataFrame(t_); T.to_csv("res_16_resumen.csv", index=False)
print(T.round(3).to_string(index=False))

H = R[R.tipo == "H"]; out = []
for per in ["DEV", "VAL"]:
    W = H[H.per == per]
    for nom, a, b_, pareado in [("HE1 roja vs verde", "E1", "E1c", False), ("HE2 bajo vs sobre VWAP", "E2", "E2c", False),
                                ("HE3 E2 vs E0 (mismas acciones)", "E2", "E0", True)]:
        if pareado:
            w = W.dropna(subset=[a]); dif = (w[a] - w[b_]); tt = dif.mean() / dif.std() * np.sqrt(len(dif)); dm = dif.mean()
        else:
            dm = W[a].mean() - W[b_].mean(); tt = stats.ttest_ind(W[a].dropna(), W[b_].dropna(), equal_var=False).statistic
        out.append(dict(hipotesis=nom, periodo=per, dif_R=dm, t=tt))
O = pd.DataFrame(out)
v = O[O.periodo == "VAL"].copy(); v["p"] = 2 * (1 - stats.norm.cdf(v.t.abs())); v = v.sort_values("p")
v["holm_ok"] = [p < 0.05 / (len(v) - i) for i, p in enumerate(v.p)]; v["holm_ok"] = v.holm_ok.cummin()
print(O.round(3).to_string(index=False)); print(v.round(4).to_string(index=False))
O.to_csv("res_16_hipotesis.csv", index=False)
