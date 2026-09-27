"""Módulo 5: setups de corto en gappers, medidos en R (riesgo = distancia al stop).
- Intradía con velas de 1 hora (Yahoo, ~2 años, gappers >=20 % desde 2024-10-15).
- Día 2 y 'first red day' con velas diarias 2015-2026.
Ejecución conservadora: si la vela toca el stop se pierde 1R + deslizamiento; costes 1 % ida y vuelta.
Sensibilidad: deslizamiento extra en el stop del 5 % del precio (halts / huecos al alza)."""
import glob
import numpy as np
import pandas as pd

D = "/home/user/data/smallcaps"
COSTE = 0.01
E = pd.read_parquet(f"{D}/eventos_gappers.parquet")
E["date"] = pd.to_datetime(E["date"])


def trade(bars, i0, entry, stop, desliz=0.0):
    """Corto desde la vela i0 (entra a su apertura) hasta el cierre del día. Devuelve R neto."""
    riesgo = stop - entry
    if riesgo <= 0:
        return np.nan
    for i in range(i0, len(bars)):
        if bars.High.iat[i] >= stop:
            salida = max(stop, bars.Open.iat[i]) * (1 + desliz)   # si abre por encima del stop, sale a la apertura
            return (entry - salida - COSTE * entry) / riesgo
    return (entry - bars.Close.iat[-1] - COSTE * entry) / riesgo


filas = []
for f in glob.glob(f"{D}/h1/*.parquet"):
    sym = f.split("/")[-1][:-8]
    h = pd.read_parquet(f)
    if h.index.tz is None:
        h.index = h.index.tz_localize("UTC")
    h.index = h.index.tz_convert("America/New_York")
    ev = E[(E.sym == sym) & (E.date >= "2024-10-15")]
    for r in ev.itertuples():
        b = h[h.index.date == r.date.date()].between_time("09:30", "15:59")
        if len(b) < 6 or b.index[0].strftime("%H:%M") != "09:30":
            continue
        o = b.Open.iat[0]
        res = {}
        for des, suf in [(0.0, ""), (0.05, " +desliz5%")]:
            # A: corto a la apertura, stop +30 %
            res["A corto apertura, stop +30%" + suf] = trade(b, 0, o, o * 1.30, des)
            # B: primera hora roja -> corto 10:30, stop = máximo +2 %
            if b.Close.iat[0] < b.Open.iat[0]:
                hod = b.High.iat[0]
                res["B 1ª hora roja → corto 10:30" + suf] = trade(b, 1, b.Open.iat[1], hod * 1.02, des)
            # C: máximo en la 1ª hora y 2ª hora no lo supera -> corto 11:30
            if b.High.iat[1] < b.High.iat[0]:
                hod = b.High.iat[0]
                res["C máximo fallido (1ª hora) → corto 11:30" + suf] = trade(b, 2, b.Open.iat[2], hod * 1.02, des)
            # E: fade de la tarde: 13:30 bajo la apertura y bajo el VWAP
            tp = (b.High + b.Low + b.Close) / 3
            vw = (tp * b.Volume).cumsum() / b.Volume.cumsum().replace(0, np.nan)
            k = 4  # vela de 13:30
            if len(b) > k + 1 and b.Open.iat[k] < o and b.Open.iat[k] < vw.iat[k - 1]:
                hod = b.High.iloc[:k].max()
                res["E fade de la tarde (13:30, bajo apertura y VWAP)" + suf] = trade(b, k, b.Open.iat[k], hod * 1.02, des)
        hod_hora = b.High.values.argmax()
        for k_, v in res.items():
            filas.append(dict(sym=sym, date=r.date, gap=r.gap, setup=k_, R=v, hod_hora=hod_hora))
I = pd.DataFrame(filas).dropna()
I.to_csv("res_06_setups_intradia.csv", index=False)


def resumen(x):
    return pd.Series(dict(n=len(x), WR=(x.R > 0).mean(), R_media=x.R.mean(), R_mediana=x.R.median(),
                          peor=x.R.min(), t=x.R.mean() / x.R.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan))


print("=== INTRADÍA (velas 1 h, gappers desde 2024-10-15)")
for nom, m in [("todos (gap >= 20 %)", I.gap >= 0.2), ("gap >= 50 %", I.gap >= 0.5), ("gap >= 100 %", I.gap >= 1.0)]:
    print(f"\n-- {nom}")
    print(I[m].groupby("setup").apply(resumen).round(3).to_string())
I["semestre"] = I.date.dt.year.astype(str) + np.where(I.date.dt.month <= 6, "-S1", "-S2")
print("\n-- por semestre (gap >= 50 %, sin deslizamiento extra), R medio")
print(I[(I.gap >= 0.5) & ~I.setup.str.contains("desliz")].pivot_table(index="setup", columns="semestre", values="R", aggfunc="mean").round(2).to_string())

# ---------------- DIARIO: día 2 y first red day (2015-2026)
d = pd.concat([pd.read_parquet(f) for f in glob.glob(f"{D}/diario/*.parquet")])
d = d.rename(columns=str.lower).sort_values(["sym", "date"])
d["date"] = pd.to_datetime(d["date"])
filas = []
for sym, g in d.groupby("sym"):
    g = g.reset_index(drop=True)
    o, h, l, c = g.open.values, g.high.values, g.low.values, g.close.values
    pc = np.r_[np.nan, c[:-1]]
    ret = c / pc - 1
    for i in range(2, len(g) - 1):
        # Día 2: día 1 = gapper (abre >= +50 % sobre cierre previo) que cierra en la mitad baja de su rango
        if o[i] / pc[i] - 1 >= 0.5 and h[i] > l[i]:
            pos = (c[i] - l[i]) / (h[i] - l[i])
            e, st = o[i + 1], h[i] * 1.02
            if st > e * 1.03:                      # riesgo mínimo 3 % (evita stops pegados a la entrada)
                sal = st if h[i + 1] >= st else c[i + 1]
                R = (e - sal - COSTE * e) / (st - e)
                filas.append(dict(sym=sym, date=g.date[i], setup="F día 2: corto apertura, stop máx. día 1" + (" (día 1 cerró débil)" if pos < 0.5 else " (día 1 cerró fuerte)"), R=R))
        # First red day: 2 días seguidos subiendo >= 20 % y luego el primer día rojo -> corto al día siguiente
        if i >= 3 and ret[i - 1] >= 0.2 and ret[i - 2] >= 0.2 and c[i] < o[i] and c[i] < pc[i]:
            e, st = o[i + 1], h[i] * 1.02
            if st > e * 1.03:
                sal = st if h[i + 1] >= st else c[i + 1]
                filas.append(dict(sym=sym, date=g.date[i], setup="G first red day: corto al día siguiente, stop máx. día rojo", R=(e - sal - COSTE * e) / (st - e)))
F = pd.DataFrame(filas).dropna()
F = F[np.isfinite(F.R)]
F["epoca"] = pd.cut(F.date.dt.year, [2014, 2019, 2022, 2026], labels=["2015-19", "2020-22", "2023-26"])
F.to_csv("res_06_setups_diario.csv", index=False)
print("\n=== DIARIO (2015-2026)")
print(F.groupby(["setup", "epoca"], observed=True).apply(resumen).round(3).to_string())
