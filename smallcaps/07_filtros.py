"""¿Qué filtros de selección separan los gappers que se desinflan? Setups del 06 cruzados con datos SEC
(acciones en circulación antes del evento): capitalización a la apertura y rotación del float (volumen del día / acciones)."""
import glob, json
import numpy as np
import pandas as pd

S = "/home/user/data/sec"
fs = []
for f in glob.glob(f"{S}/CY*I.json"):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if "data" in j:
        fs.append(pd.DataFrame(j["data"]))
SH = pd.concat(fs)
SH["end"] = pd.to_datetime(SH["end"])
SH = SH.sort_values("end")
tk = json.load(open(f"{S}/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
I = pd.read_csv("res_06_setups_intradia.csv", parse_dates=["date"])
E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
E["date"] = pd.to_datetime(E["date"])
I = I.merge(E[["sym", "date", "open", "volume"]], on=["sym", "date"], how="left")
acc = {}
for c, g in SH.groupby("cik"):
    acc[c] = g.set_index("end")["val"]
def acciones(sym, d):
    c = t2c.get(sym)
    if c is None or c not in acc:
        return np.nan
    s = acc[c][(acc[c].index <= d) & (acc[c].index > d - pd.Timedelta("200D"))]
    return s.iloc[-1] if len(s) else np.nan
cache = {}
I["acc"] = [cache.setdefault((s, d), acciones(s, d)) for s, d in zip(I.sym, I.date)]
I["mcap"] = I.acc * I.open
I["rot"] = I.volume / I.acc
I = I[I.acc.notna() & (I.rot < 1000)]
print("eventos con acciones SEC:", I[["sym", "date"]].drop_duplicates().shape[0])
base = I[~I.setup.str.contains("desliz") & (I.gap >= 0.5)]
def r(x):
    return pd.Series(dict(n=len(x), WR=(x.R > 0).mean(), R=x.R.mean(), t=x.R.mean() / x.R.std() * np.sqrt(len(x))))
base["cap"] = pd.cut(base.mcap, [0, 10e6, 30e6, 100e6, 1e13], labels=["<$10M", "$10-30M", "$30-100M", ">$100M"])
base["rotacion"] = pd.cut(base.rot, [0, 1, 3, 10, 1000], labels=["<1x", "1-3x", "3-10x", ">10x"])
print("\n-- gap>=50%: por capitalización a la apertura")
print(base.groupby(["setup", "cap"], observed=True).apply(r).round(3).to_string())
print("\n-- gap>=50%: por rotación del float en el día (volumen / acciones)")
print(base.groupby(["setup", "rotacion"], observed=True).apply(r).round(3).to_string())
