"""Ronda 8 (pre-registro en HIPOTESIS_SELECCION.md): "primer día rojo" de Edu Trades / Hamlin, corto el MISMO día.
Diario 2015-2026, precio real por splits (ronda 5), ambiguos fuera. Sin mirar el futuro: en D solo se conoce hasta D-1.
A = corto a la apertura de D; B = corto cuando D toca el cierre de D-1 (green to red). Stop apertura × 1.30, salida al cierre."""
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
d = d.rename(columns=str.lower).rename(columns={"date": "date"}).sort_values(["sym", "date"])
d["date"] = pd.to_datetime(d["date"])
d = d[(d.open > 0) & (d.high > 0) & (d.low > 0) & (d.close > 0)]

filas = []
for sym, g in d.groupby("sym"):
    if len(g) < 5:
        continue
    o, h, l, c, v = (g[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    fechas = g.date.to_numpy()
    verde = np.r_[False, c[1:] > c[:-1]]
    sinrojo = np.r_[False, l[1:] >= c[:-1]]            # criterio Hamlin: no se pone rojo en el día
    volsube = np.r_[False, v[1:] > v[:-1]]
    sp = por_sym.get(sym)
    racha = 0
    for i in range(1, len(g)):
        # racha de días verdes que termina en i-1
        racha = racha + 1 if verde[i - 1] else 0
        if racha < 2 or i - 1 - racha < 0:
            continue
        j0 = i - racha                                  # primer día de la racha
        base = c[j0 - 1]
        subida = c[i - 1] / base - 1
        if subida < 0.5:
            continue
        dolvol = c[i - 1] * v[i - 1]
        if dolvol < 1e6 or not (o[i] > c[i - 1]):
            continue
        # precio real
        f, amb = 1.0, False
        if sp is not None:
            mes = pd.Timestamp(fechas[i]).replace(day=1)
            amb = bool((sp.t == mes).any())
            f = float(sp[sp.t > mes].ratio.prod())
        precio = o[i] * f
        if amb or precio < 1:
            continue
        vol_crec = bool(all(v[k] > v[k - 1] for k in range(j0 + 1, i)))
        sin_rojo = bool(sinrojo[j0:i].all())
        stop = o[i] * (1 + STOP)
        salida_stop = stop * (1 + DESL)
        # A: corto a la apertura
        if h[i] >= stop:
            RA = -((salida_stop - o[i]) / o[i] + COSTE) / STOP
        else:
            RA = ((o[i] - c[i]) / o[i] - COSTE) / STOP
        # B: green to red (toca el cierre de D-1)
        RB = np.nan
        if l[i] <= c[i - 1]:
            e = c[i - 1]
            riesgo = stop - e
            if h[i] >= stop:
                RB = -((salida_stop - e) + COSTE * e) / riesgo
            else:
                RB = ((e - c[i]) - COSTE * e) / riesgo
        filas.append(dict(sym=sym, date=pd.Timestamp(fechas[i]), episodio=f"{sym}_{pd.Timestamp(fechas[j0]).date()}",
                          k=racha, subida=subida, vol_crec=vol_crec, sin_rojo=sin_rojo, precio=precio,
                          primero=(racha == 2), RA=RA, RB=RB, riesgoB_pct=(stop - c[i - 1]) / c[i - 1],
                          rojo=c[i] < c[i - 1], mae=h[i] / o[i] - 1))

X = pd.DataFrame(filas)
X["per"] = np.where(X.date.dt.year <= 2021, "DEV 2015-21", "VAL 2022-26")
X.to_csv("res_21_candidatos.csv", index=False)


def met(v, ep=None):
    v = v.dropna()
    g, p = v[v > 0], v[v <= 0]
    out = dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
               PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan)
    if ep is not None:                                   # t con la media por episodio
        m = pd.Series(v.values, index=ep.loc[v.index].values).groupby(level=0).mean()
        out["episodios"] = len(m)
        out["t_ep"] = m.mean() / m.std() * np.sqrt(len(m)) if len(m) > 2 else np.nan
    return out


filas = []
def add(nombre, W, col):
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        V = W[W.per == per]
        filas.append(dict(grupo=nombre, setup=col[1], periodo=per, **met(V[col], V.episodio)))


P = X[X.subida >= 1.0]
full = P[P.vol_crec]
add("patrón completo (≥+100 %, volumen creciente)", full, "RA")
add("patrón completo (≥+100 %, volumen creciente)", full, "RB")
add("≥+100 %, volumen NO creciente", P[~P.vol_crec], "RB")
# descriptivos
add("desc: ≥+50 %, volumen creciente", X[X.vol_crec], "RA")
add("desc: ≥+50 %, volumen creciente", X[X.vol_crec], "RB")
add("desc: completo, k = 2", full[full.k == 2], "RB")
add("desc: completo, k ≥ 3", full[full.k >= 3], "RB")
add("desc: completo + racha sin rojo intradía (Hamlin)", full[full.sin_rojo], "RA")
add("desc: completo + racha sin rojo intradía (Hamlin)", full[full.sin_rojo], "RB")
T = pd.DataFrame(filas)
T.to_csv("res_21_primer_dia_rojo.csv", index=False)
pd.set_option("display.width", 250)
print(T.round(3).to_string(index=False))

# hipótesis (VAL) + Holm
V = X[X.per == "VAL 2022-26"]
Vf, Vp = V[(V.subida >= 1) & V.vol_crec], V[(V.subida >= 1) & ~V.vol_crec]
def t_diff(a, b):
    ma = a.dropna().groupby(a.dropna().index.map(X.episodio)).mean()
    mb = b.dropna().groupby(b.dropna().index.map(X.episodio)).mean()
    return stats.ttest_ind(ma, mb, equal_var=False).statistic
tests = [("HR1 setup A, patrón completo", met(Vf.RA, Vf.episodio)["t_ep"]),
         ("HR2 setup B, patrón completo", met(Vf.RB, Vf.episodio)["t_ep"]),
         ("HR3 volumen creciente vs no (B)", t_diff(Vf.RB, Vp.RB))]
O = pd.DataFrame(tests, columns=["hipotesis", "t_VAL"])
O["p"] = 2 * (1 - stats.norm.cdf(O.t_VAL.abs()))
O = O.sort_values("p"); m = len(O)
O["holm_ok"] = [p < 0.05 / (m - i) for i, p in enumerate(O.p)]
O["holm_ok"] = O.holm_ok.cummin()
print("\n" + O.round(4).to_string(index=False))

# costes: locate 1 % del precio y comisión 0.05R
for s, riesgo in [("RA", 0.30)]:
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        W = full[full.per == per][s].dropna()
        print(f"{per} {s} neto (locate 1 % = {0.01 / riesgo:.3f}R + comisión 0.05R): {W.mean() - 0.01 / riesgo - 0.05:+.3f}R")
for per in ["DEV 2015-21", "VAL 2022-26"]:
    W = full[full.per == per].dropna(subset=["RB"])
    print(f"{per} RB neto (locate 1 % en R según el riesgo real + 0.05R): {(W.RB - 0.01 / W.riesgoB_pct - 0.05).mean():+.3f}R")
print("\nfrecuencia último año (patrón completo, candidatos/día hábil):",
      round((full.date >= "2025-09-26").sum() / len(pd.bdate_range('2025-09-26', '2026-09-25')), 2),
      "| B con entrada:", round(((full.date >= "2025-09-26") & full.RB.notna()).sum() / 252, 2))
print("% de candidatos del patrón que acaban rojos (cierre D < cierre D-1):", round(full.rojo.mean(), 2))
# casos citados por Edu
print(X[X.sym.isin(["DAIC", "DFNS", "TGL", "BMNR", "BNAI"])][["sym", "date", "k", "subida", "vol_crec", "precio", "RA", "RB"]]
      .round(2).tail(15).to_string(index=False))
