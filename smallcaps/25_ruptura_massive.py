"""Ronda 10 (pre-registro en HIPOTESIS_SELECCION.md): backtest de la ruptura de la vela de 1 min de las 9:30 (reglas del usuario)
con datos de Massive (antes Polygon), oct-2024 → sep-2026, sin sesgo de supervivencia. Usa lo descargado por 24_massive_descarga.py."""
import os
import numpy as np
import pandas as pd
from scipy import stats

OUT = "/home/user/data/massive"
COSTE, RMIN = 0.005, 0.02


def velas(sym, fecha):
    f = f"{OUT}/m1/{sym}_{fecha}.parquet"
    if not os.path.exists(f):
        return None
    x = pd.read_parquet(f)
    if x.empty:
        return pd.DataFrame()
    x.index = pd.to_datetime(x.t, unit="ms", utc=True).dt.tz_convert("America/New_York")
    return x.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}).between_time("09:30", "15:59")


def regla(x, coste=COSTE):
    t = x.index.strftime("%H:%M"); c = x.close.to_numpy()
    o, l = x.open.iloc[0], x.low.iloc[0]
    for i in range(1, len(x)):
        if t[i] > "11:00":
            break
        if c[i] < l:
            e = c[i]; r = max((o - e) / e, RMIN)
            for j in range(i + 1, len(x)):
                if c[j] > o or t[j] >= "11:30":
                    return dict(estado="stop" if c[j] > o else "11:30", entrada=t[i], salida=t[j], R=((e - c[j]) / e - coste) / r)
            return dict(estado="fin datos", entrada=t[i], salida=t[-1], R=((e - c[-1]) / e - coste) / r)
    return dict(estado="no rompió", R=np.nan)


def referencia(x):
    o = x.open.iloc[0]
    w = x[x.index.strftime("%H:%M") <= "11:30"]
    if w.high.max() >= o * 1.3:
        return -((o * 1.3 * 1.05 - o) / o + 0.01) / 0.3
    return ((o - w.close.iloc[-1]) / o - 0.01) / 0.3


E = pd.read_parquet(f"{OUT}/gappers.parquet")
lab = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo_cat"})
filas = []
for r in E.itertuples():
    x = velas(r.sym, r.fecha)
    if x is None:
        continue                                  # aún no descargado
    if x.empty or x.index[0].strftime("%H:%M") != "09:30" or len(x) < 30:
        filas.append(dict(sym=r.sym, fecha=r.fecha, gap=r.gap, estado="sin vela 9:30")); continue
    precio = x.open.iloc[0]
    if precio < 1:
        filas.append(dict(sym=r.sym, fecha=r.fecha, gap=r.gap, precio=precio, estado="< $1")); continue
    a = regla(x)
    filas.append(dict(sym=r.sym, fecha=r.fecha, gap=r.gap, precio=precio, tipo=r.tipo, **a,
                      R1=regla(x, 0.01)["R"] if a["estado"] not in ("no rompió",) else np.nan,
                      Rref=referencia(x)))
X = pd.DataFrame(filas)
for col in ["R", "R1", "Rref", "precio", "tipo", "entrada", "salida"]:
    if col not in X:
        X[col] = np.nan
X["per"] = np.where(X.fecha < "2025-10-01", "DEV oct24-sep25", "VAL oct25-sep26")
X["tramo"] = np.where(X.gap >= 1, "≥ 100 %", np.where(X.gap >= .5, "50-100 %", "20-50 %"))
X["g50"] = X.gap >= .5
X = X.merge(lab, left_on=["sym", "fecha"], right_on=["sym", "fecha"], how="left")
X.to_csv("res_25_ruptura_massive.csv", index=False)
op = X[X.R.notna()]


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    s = v.sort_values()
    return pd.Series(dict(n=len(v), R=v.mean(), mediana=v.median(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                          PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, t=v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan,
                          sin5=s.iloc[:-5].mean() if len(v) > 10 else np.nan, peor=v.min(), dolares=20 * v.sum()))


pd.set_option("display.width", 250)
print("descargados:", len(X), "| estados:", X.estado.value_counts().to_dict())
print("\n== Regla (coste 0.5 %) por gap y periodo ==")
print(op.groupby(["g50", "per"]).R.apply(met).unstack().round(2).to_string())
print("\n== por tramo ==")
print(op.groupby(["tramo", "per"]).R.apply(met).unstack().round(2).to_string())
print("\n== coste 1 % ==")
print(op.groupby(["g50", "per"]).R1.apply(met).unstack().round(2).to_string())
print("\n== referencia: corto a la apertura, stop 30 %, salida 11:30 (mismos días con operación) ==")
print(op.groupby(["g50", "per"]).Rref.apply(met).unstack().round(2).to_string())
print("\n== gap ≥ 50 % por tipo de catalizador (etiqueta ronda 2b, donde exista) ==")
print(op[op.g50].groupby("tipo_cat").R.apply(met).unstack().round(2).to_string())

# hipótesis (VAL) + Holm
V = op[op.per.str.startswith("VAL")]; Dv = op[op.per.str.startswith("DEV")]
hb1 = met(V[V.g50].R)["t"]
hb2 = stats.ttest_ind(V[V.g50].R, V[~V.g50].R, equal_var=False).statistic
dif = (V[V.g50].R - V[V.g50].Rref).dropna(); hb3 = dif.mean() / dif.std() * np.sqrt(len(dif))
O = pd.DataFrame([("HB1 regla gap ≥ 50 % > 0", hb1), ("HB2 ≥ 50 % mejor que 20-50 %", hb2), ("HB3 regla mejor que referencia", hb3)],
                 columns=["hipotesis", "t_VAL"])
O["p"] = 2 * (1 - stats.norm.cdf(O.t_VAL.abs())); O = O.sort_values("p")
O["holm_ok"] = [p < 0.05 / (3 - i) for i, p in enumerate(O.p)]; O["holm_ok"] = O.holm_ok.cummin()
print("\n" + O.round(4).to_string(index=False))
print("DEV (signo): HB1", round(Dv[Dv.g50].R.mean(), 3), "| HB2 dif", round(Dv[Dv.g50].R.mean() - Dv[~Dv.g50].R.mean(), 3),
      "| HB3 dif", round((Dv[Dv.g50].R - Dv[Dv.g50].Rref).mean(), 3))
dias = X.fecha.nunique()
print("frecuencia gap ≥ 50 % con operación por día:", round(op.g50.sum() / max(dias, 1), 2), "| días:", dias)
