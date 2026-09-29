"""Ronda 9 (pre-registro en HIPOTESIS_SELECCION.md): ideas de las listas de Edu Trades.
E1 = overextended gap down (tras sobre extensión, D abre bajo el cierre de D-1). E2 = historial de spikes previos rojos/verdes.
Diario 2015-2026, precio real por splits (ronda 5), ambiguos fuera, precio ≥ $1. Sin mirar el futuro."""
import glob
import numpy as np
import pandas as pd
from scipy import stats

D = "/home/user/data/smallcaps"
STOP, DESL, COSTE = 0.30, 0.05, 0.01

SP = pd.read_parquet(f"{D}/splits.parquet")
SP["t"] = pd.to_datetime(SP.t)
por_sym = {s: g for s, g in SP.groupby("sym")}

d = pd.concat([pd.read_parquet(f) for f in glob.glob(f"{D}/diario/*.parquet")])
d = d.rename(columns=str.lower).sort_values(["sym", "date"])
d["date"] = pd.to_datetime(d["date"])
d = d[(d.open > 0) & (d.high > 0) & (d.low > 0) & (d.close > 0)]
G = {s: g.reset_index(drop=True) for s, g in d.groupby("sym")}


def factor(sym, fecha):
    sp = por_sym.get(sym)
    if sp is None:
        return 1.0, False
    mes = pd.Timestamp(fecha).replace(day=1)
    return float(sp[sp.t > mes].ratio.prod()), bool((sp.t == mes).any())


def r_a(o, h, c):
    if h >= o * (1 + STOP):
        return -((o * (1 + STOP) * (1 + DESL) - o) / o + COSTE) / STOP
    return ((o - c) / o - COSTE) / STOP


# ---------------- E1: candidatos (abre bajo y abre sobre el cierre de D-1) ----------------
filas = []
for sym, g in G.items():
    if len(g) < 5:
        continue
    o, h, l, c, v = (g[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    fechas = g.date.to_numpy()
    verde = np.r_[False, c[1:] > c[:-1]]
    racha = 0
    for i in range(1, len(g)):
        racha = racha + 1 if verde[i - 1] else 0
        if racha < 2 or i - 1 - racha < 0:
            continue
        j0 = i - racha
        subida = c[i - 1] / c[j0 - 1] - 1
        if subida < 0.5 or c[i - 1] * v[i - 1] < 1e6 or o[i] == c[i - 1]:
            continue
        f, amb = factor(sym, fechas[i])
        if amb or o[i] * f < 1:
            continue
        gapdown = o[i] < c[i - 1]
        RA = r_a(o[i], h[i], c[i])
        RB = np.nan
        if gapdown:
            stop = max(c[i - 1] * 1.02, o[i] * 1.03)
            riesgo = (stop - o[i]) / o[i]
            if h[i] >= stop:
                RB = -((stop * 1.02 - o[i]) / o[i] + COSTE) / riesgo
            else:
                RB = ((o[i] - c[i]) / o[i] - COSTE) / riesgo
        filas.append(dict(sym=sym, date=pd.Timestamp(fechas[i]), episodio=f"{sym}_{pd.Timestamp(fechas[j0]).date()}",
                          k=racha, subida=subida, gapdown=gapdown, precio=o[i] * f, RA=RA, RB=RB,
                          riesgoB=riesgo if gapdown else np.nan, gap_pct=o[i] / c[i - 1] - 1))
C = pd.DataFrame(filas)
C["per"] = np.where(C.date.dt.year <= 2021, "DEV 2015-21", "VAL 2022-26")
C.to_csv("res_22_e1_candidatos.csv", index=False)


def met(v, ep=None):
    v = v.dropna()
    g, p = v[v > 0], v[v <= 0]
    out = dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
               PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)
    if ep is not None:
        m = pd.Series(v.values, index=ep.loc[v.index].values).groupby(level=0).mean()
        out["episodios"] = len(m)
        out["t_ep"] = m.mean() / m.std() * np.sqrt(len(m)) if len(m) > 2 else np.nan
    else:
        out["t0"] = v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan
    return out


T = []
def add(nom, W, col, ep=True):
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        V = W[W.per == per]
        T.append(dict(grupo=nom, col=col, periodo=per, **met(V[col], V.episodio if ep else None)))


E1 = C[(C.subida >= 1) & C.gapdown]
UP = C[(C.subida >= 1) & ~C.gapdown]
add("E1 gap down, subida ≥ 100 %", E1, "RA")
add("E1 gap down, subida ≥ 100 %", E1, "RB")
add("abre sobre el cierre (ronda 8 sin filtro de volumen), ≥ 100 %", UP, "RA")
add("desc: E1 gap down, subida ≥ 50 %", C[C.gapdown], "RA")
add("desc: E1 gap down, subida ≥ 50 %", C[C.gapdown], "RB")

# ---------------- E2: historial de spikes en los gappers ≥ 50 % ----------------
X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
X = X[~X.ambiguo & (X.precio >= 1) & (X.gap >= 0.5)].copy()
E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
X = X.merge(E[["sym", "fecha", "tipo"]], on=["sym", "fecha"], how="left")
hist = []
for sym, fecha in zip(X.sym, X.date):
    g = G.get(sym)
    if g is None:
        hist.append((np.nan, np.nan, np.nan)); continue
    idx = np.searchsorted(g.date.to_numpy(), np.datetime64(fecha))
    if idx >= len(g) or g.date.iloc[idx] != fecha:
        hist.append((np.nan, np.nan, np.nan)); continue
    fin = idx - 10
    ini = np.searchsorted(g.date.to_numpy(), np.datetime64(fecha - pd.Timedelta(days=365)))
    ini = max(ini, 1)
    if fin <= ini:
        hist.append((0, np.nan, np.nan)); continue
    w = g.iloc[ini:fin]
    pc = g.close.iloc[ini - 1:fin - 1].to_numpy()
    sp = w.high.to_numpy() >= pc * 1.20
    n = int(sp.sum())
    if n == 0:
        hist.append((0, np.nan, np.nan)); continue
    o_, h_, c_ = w.open.to_numpy()[sp], w.high.to_numpy()[sp], w.close.to_numpy()[sp]
    rojo = (c_ < o_).mean()
    devuelve = ((h_ - c_) >= 0.5 * (h_ - pc[sp])).mean()
    hist.append((n, rojo, devuelve))
X[["n_spk", "rojo", "devuelve"]] = pd.DataFrame(hist, index=X.index)
X["grupo_h"] = np.select([X.n_spk == 0, X.rojo >= 2 / 3, X.rojo < 2 / 3], ["sin spikes", "mayoría roja", "mayoría verde"], "sin datos")
X["grupo_d"] = np.select([X.n_spk == 0, X.devuelve >= 2 / 3, X.devuelve < 2 / 3], ["sin spikes", "mayoría devuelve", "mayoría aguanta"], "sin datos")
X.to_csv("res_22_e2_historial.csv", index=False)
for gname in ["sin spikes", "mayoría roja", "mayoría verde"]:
    add(f"E2 {gname} (gap ≥ 50 %)", X[X.grupo_h == gname], "R", ep=False)
for gname in ["mayoría roja", "mayoría verde"]:
    add(f"desc: E2 humo {gname}", X[(X.grupo_h == gname) & (X.tipo == "H")], "R", ep=False)
for gname in ["mayoría devuelve", "mayoría aguanta"]:
    add(f"desc: E2 {gname} (devuelve ≥ mitad)", X[X.grupo_d == gname], "R", ep=False)

T = pd.DataFrame(T)
T.to_csv("res_22_ronda9.csv", index=False)
pd.set_option("display.width", 250)
print(T.round(3).to_string(index=False))

# ---------------- hipótesis (VAL) + Holm ----------------
V1, VU = E1[E1.per == "VAL 2022-26"], UP[UP.per == "VAL 2022-26"]
def ep_mean(W, col):
    W = W.dropna(subset=[col]); return W.groupby("episodio")[col].mean()
XV = X[X.per == "VAL 2022-26"]
tests = [("HG1 E1 setup A ≠ 0", met(V1.RA, V1.episodio)["t_ep"]),
         ("HG2 E1 setup B ≠ 0", met(V1.RB, V1.episodio)["t_ep"]),
         ("HG3 gap down vs gap up (A)", stats.ttest_ind(ep_mean(V1, "RA"), ep_mean(VU, "RA"), equal_var=False).statistic),
         ("HE2 mayoría roja vs verde", stats.ttest_ind(XV[XV.grupo_h == "mayoría roja"].R, XV[XV.grupo_h == "mayoría verde"].R,
                                                       equal_var=False).statistic)]
XD = X[X.per == "DEV 2015-21"]
print("\nDEV (signo): HE2 dif =", round(XD[XD.grupo_h == "mayoría roja"].R.mean() - XD[XD.grupo_h == "mayoría verde"].R.mean(), 3),
      "| HG3 dif =", round(E1[E1.per == "DEV 2015-21"].RA.mean() - UP[UP.per == "DEV 2015-21"].RA.mean(), 3))
O = pd.DataFrame(tests, columns=["hipotesis", "t_VAL"])
O["p"] = 2 * (1 - stats.norm.cdf(O.t_VAL.abs()))
O = O.sort_values("p"); m = len(O)
O["holm_ok"] = [p < 0.05 / (m - i) for i, p in enumerate(O.p)]
O["holm_ok"] = O.holm_ok.cummin()
print("\n" + O.round(4).to_string(index=False))

# neto de locate 1 % + comisión 0.05R
for per in ["DEV 2015-21", "VAL 2022-26"]:
    W = E1[E1.per == per]
    print(f"{per} E1 A neto: {W.RA.mean() - 0.01 / 0.30 - 0.05:+.3f}R | B neto: {(W.RB - 0.01 / W.riesgoB - 0.05).mean():+.3f}R"
          f" | riesgo B mediano {W.riesgoB.median():.1%}")
dias = len(pd.bdate_range("2025-09-26", "2026-09-25"))
print(f"frecuencia último año: E1 (≥100 %) {(E1.date >= '2025-09-26').sum() / dias:.2f}/día; "
      f"E2 mayoría roja gap ≥ 50 % {((X.date >= '2025-09-26') & (X.grupo_h == 'mayoría roja')).sum() / dias:.2f}/día")
print("reparto E2:", X.grupo_h.value_counts().to_dict())
