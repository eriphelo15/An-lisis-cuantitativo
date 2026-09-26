"""Fase 1 — Caracterización estadística (solo DEV)."""
import numpy as np, pandas as pd
from lib import load_1m, daily_table, RES_DIR
import os
df = load_1m("dev")
print("DEV:", df.tday.min().date(), "->", df.tday.max().date(), "barras", len(df))
same = (df.seg == df.seg.shift()) & (df.ts.diff() <= pd.Timedelta("2min"))
df["r"] = np.where(same, np.log(df.close).diff(), np.nan)

# 1) volatilidad y volumen por minuto del día (ET)
by = df.groupby("hm").agg(vol=("r", "std"), volume=("volume", "mean"), mean_r=("r", "mean"), n=("r", "count"))
by["vol_bp"] = by.vol * 1e4
by.to_csv(os.path.join(RES_DIR, "f1_perfil_intradia.csv"))
h = df.groupby(df.ts.dt.hour).agg(vol_bp=("r", lambda x: x.std()*1e4), vol=("volume","mean"), drift_bp=("r", lambda x: x.mean()*1e4*60))
print("\nPor hora (vol 1m en bp, volumen medio, drift/h en bp):\n", h.round(3).to_string())

# 2) autocorrelación de retornos a varias escalas (dentro de RTH, sin cruzar días)
def acf_at(freq):
    x = df[df.rth].set_index("ts").groupby("tday").close.resample(freq).last().dropna()
    r = np.log(x).groupby(level=0).diff().dropna()
    r1 = r.groupby(level=0).shift(1)
    m = r1.notna()
    c = np.corrcoef(r[m], r1[m])[0, 1]
    return c, m.sum()
print("\nAutocorrelación lag-1 en RTH:")
for f in ["1min", "5min", "15min", "30min", "60min"]:
    c, n = acf_at(f); print(f"  {f:>6}: rho={c:+.4f}  n={n}  z={c*np.sqrt(n):+.2f}")

# 3) Variance ratio intradía (RTH) q=5,15,30,60 sobre retornos 1m
rr = df.loc[df.rth, ["tday", "r"]].dropna()
v1 = rr.r.var()
print("\nVariance ratio (RTH, base 1m):")
for q in [5, 15, 30, 60, 390]:
    s = rr.groupby("tday").r.apply(lambda x: x.rolling(q).sum().iloc[q-1::q]).dropna()
    print(f"  q={q:>3}: VR={s.var()/(q*v1):.3f}")

# 4) Diario
d = daily_table(df)
d["ret_rth"] = np.log(d.rth_close / d.rth_open)
d["ret_on"] = np.log(d.rth_open / d.prev_close)
print("\nDías:", len(d), " RTH ret std %.4f  ON ret std %.4f" % (d.ret_rth.std(), d.ret_on.std()))
print("corr(ON, RTH mismo día) = %.3f" % d[["ret_on","ret_rth"]].corr().iloc[0,1])
d["ret_rth_prev"] = d.ret_rth.shift()
print("corr(RTH ayer, RTH hoy) = %.3f" % d[["ret_rth_prev","ret_rth"]].corr().iloc[0,1])
d["dow"] = d.index.dayofweek
print("\nRTH por día de semana (media bp, % up, n):")
print(d.groupby("dow").ret_rth.agg(mean_bp=lambda x: x.mean()*1e4, up=lambda x: (x>0).mean(), n="count").round(3).to_string())
print("\nON por día de semana:")
print(d.groupby("dow").ret_on.agg(mean_bp=lambda x: x.mean()*1e4, up=lambda x: (x>0).mean(), n="count").round(3).to_string())
yr = d.groupby(d.index.year).agg(rth_bp=("ret_rth", lambda x: x.sum()*1e4), on_bp=("ret_on", lambda x: x.sum()*1e4), rng=("rng","mean"))
print("\nPor año, suma de retornos RTH vs overnight (bp) y rango RTH medio (pts):\n", yr.round(1).to_string())
d.to_parquet(os.path.join(RES_DIR, "..", "..", "..", "..", "data", "daily_dev.parquet")) if False else None
