"""Fase 2d — Reversión a la media diaria (DEV). Entrada al cierre RTH (15:59), salidas
al día siguiente (apertura 09:30 o cierre 15:59). Precios back-adjusted para cruzar rolls."""
import numpy as np, pandas as pd, os, sys
from motor import Motor
from lib import RES_DIR, COSTO_MKT_RT_PTS
split = sys.argv[1] if len(sys.argv) > 1 else "dev"
M = Motor(split); df = M.df
rth = (M.smin >= 930) & (M.smin < 1320)
g = df[rth].groupby(M.day_id[rth])
A = pd.DataFrame({"o": g.adj_open.first(), "h": g.adj_high.max(), "l": g.adj_low.min(), "c": g.adj_close.last(), "n": g.size()})
A = A[A.n >= 385].copy()
A["date"] = M.days[A.index]
A["ibs"] = (A.c - A.l) / (A.h - A.l)
A["ret"] = A.c.diff()
d = A.c.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
for k in [2, 3]:
    rs = up.ewm(alpha=1 / k, adjust=False).mean() / dn.ewm(alpha=1 / k, adjust=False).mean()
    A[f"rsi{k}"] = 100 - 100 / (1 + rs)
A["down_streak"] = (d < 0).astype(int).groupby((d >= 0).cumsum()).cumsum()
A["sma50"] = A.c.rolling(50).mean(); A["sma20"] = A.c.rolling(20).mean(); A["sma5"] = A.c.rolling(5).mean()
A["trend"] = A.c > A.sma50
A["atr"] = (A.h - A.l).rolling(14).mean()
# resultados futuros (puntos) desde el cierre de hoy
A["to_open"] = A.o.shift(-1) - A.c
A["to_close"] = A.c.shift(-1) - A.c
A["to_close2"] = A.c.shift(-2) - A.c
A["year"] = A.date.dt.year
A = A.dropna(subset=["sma50", "to_close2"])
res = []
def ev(name, mask, col):
    sgn = -1 if "short" in name else 1
    x = sgn * A.loc[mask, col] - COSTO_MKT_RT_PTS
    n = len(x)
    if n < 20: return
    t = x.mean() / (x.std() / np.sqrt(n))
    yrs = x.groupby(A.loc[mask, "year"]).mean()
    res.append(dict(regla=name, salida=col, n=n, wr=(x > 0).mean(), exp_pts=x.mean(), pf=x[x > 0].sum() / -x[x < 0].sum(),
                    t=t, años_pos=int((yrs > 0).sum()), n_años=len(yrs), **{f"y{y}": v for y, v in yrs.items()}))
base = pd.Series(True, index=A.index)
for col in ["to_open", "to_close", "to_close2"]:
    ev("todos los días (base)", base, col)
    for th in [0.1, 0.2, 0.3]:
        ev(f"IBS<{th}", A.ibs < th, col); ev(f"IBS<{th} & tendencia", (A.ibs < th) & A.trend, col)
        ev(f"IBS>{1-th} (short)", A.ibs > 1 - th, col)
    for th in [5, 10, 20]:
        ev(f"RSI2<{th}", A.rsi2 < th, col); ev(f"RSI2<{th} & tendencia", (A.rsi2 < th) & A.trend, col)
    for k in [2, 3, 4]:
        ev(f"{k}+ días bajistas", A.down_streak >= k, col); ev(f"{k}+ días bajistas & tendencia", (A.down_streak >= k) & A.trend, col)
    ev("cierre < SMA5 & tendencia", (A.c < A.sma5) & A.trend, col)
R = pd.DataFrame(res)
R.to_csv(os.path.join(RES_DIR, f"f2d_diario_{split}.csv"), index=False)
pd.set_option("display.width", 250)
print(R.sort_values("t", ascending=False).round(3).to_string(index=False))
