"""Fase 0 — Auditoría de NQ_continuous.csv (barras de 1 minuto)."""
import pandas as pd, numpy as np, sys
RAW = sys.argv[1] if len(sys.argv) > 1 else "/home/user/data/NQ_continuous.csv"
df = pd.read_csv(RAW)
print(df.dtypes); print(df.describe(include="all").T.head(12))
df["ts"] = pd.to_datetime(df["timestamp"])
print("rango:", df.ts.min(), "->", df.ts.max(), "filas", len(df))
print("duplicados ts:", df.ts.duplicated().sum(), " no monótono:", (df.ts.diff().dt.total_seconds() < 0).sum())
print("OHLC inválidos:", ((df.high < df[["open","close"]].max(1)) | (df.low > df[["open","close"]].min(1)) | (df.high < df.low)).sum())
print("vol<=0:", (df.volume <= 0).sum(), " NaN:", df.isna().sum().sum())
# ticks
frac = (df.close * 4) % 1
print("precios fuera de tick 0.25:", (frac.abs() > 1e-6).sum())
# símbolos / rolls
sym = df.symbol
chg = df.index[sym != sym.shift()]
print("contratos:", sym.nunique(), list(sym.unique()))
print("\nRolls (salto de precio en el cambio de contrato):")
for i in chg[1:]:
    prev, cur = df.iloc[i-1], df.iloc[i]
    print(f"  {cur.ts}  {prev.symbol}->{cur.symbol}  close_prev={prev.close:.2f} open={cur.open:.2f} gap={cur.open-prev.close:+.2f}  gap_min={(cur.ts-prev.ts)}")
# gaps de tiempo
d = df.ts.diff()
print("\nDistribución de huecos (min):", d.dt.total_seconds().div(60).value_counts().head(10).to_dict())
big = df.loc[d > pd.Timedelta("3h"), "ts"]
print("huecos > 3h:", len(big))
# horas presentes
print("\nbarras por hora:", df.ts.dt.hour.value_counts().sort_index().to_dict())
print("día semana:", df.ts.dt.dayofweek.value_counts().sort_index().to_dict())
# retornos extremos
r = np.log(df.close).diff()
same = sym == sym.shift()
r = r[same & (d <= pd.Timedelta("5min"))]
print("\nretorno 1m: std %.6f  |r|>1%%: %d  max %.4f min %.4f" % (r.std(), (r.abs() > .01).sum(), r.max(), r.min()))
print(df.loc[r.abs().nlargest(8).index, ["ts","open","high","low","close","volume","symbol"]])
# precio por año (para ver ajuste)
print(df.groupby(df.ts.dt.year).close.agg(["first","last","min","max"]))
