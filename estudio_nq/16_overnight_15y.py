"""Estrategia 'overnight': comprar al cierre RTH (15:59) y vender en la apertura RTH siguiente (09:30).
Comparada con buy&hold y con 'solo RTH'. Serie back-adjusted para cruzar rolls. Neto de costos."""
import numpy as np, pandas as pd, os, json
from motor import Motor
from lib import RES_DIR, COSTO_MKT_RT_PTS, PERIODOS_15Y
M = Motor("all"); df = M.df; s = M.smin; di = M.day_id
rth = (s >= 930) & (s < 1320)
g = df[rth].groupby(di[rth])
A = pd.DataFrame({"o": g.adj_open.first(), "c": g.adj_close.last(), "raw_c": g.close.last(), "n": g.size()})
A = A[A.n >= 385].copy(); A["date"] = M.days[A.index]; A = A.reset_index(drop=True)
A["sma200"] = A.c.rolling(200).mean()
A["on_pts"] = A.o.shift(-1) - A.c                 # noche que empieza hoy
A["rth_pts"] = A.c - A.o
A["on_bp"] = A.on_pts / A.raw_c * 1e4; A["rth_bp"] = A.rth_pts / A.raw_c * 1e4
A["dow"] = A.date.dt.dayofweek
A["gap_days"] = (A.date.shift(-1) - A.date).dt.days
A = A.dropna(subset=["on_pts"])
def met(pts, bp, dates, label):
    net = pts - COSTO_MKT_RT_PTS; netbp = bp - COSTO_MKT_RT_PTS / A.loc[pts.index, "raw_c"] * 1e4
    eq = netbp.cumsum(); dd = (eq.cummax() - eq).max()
    yrs = netbp.groupby(dates.dt.year).sum()
    sharpe = netbp.mean() / netbp.std() * np.sqrt(252)
    r = dict(estrategia=label, n=len(net), wr=(net > 0).mean(), pts_trade=net.mean(), bp_trade=netbp.mean(),
             t=netbp.mean() / (netbp.std() / np.sqrt(len(netbp))), sharpe_anual=sharpe, maxdd_bp=dd, años_pos=int((yrs > 0).sum()), n_años=len(yrs))
    for tag, a, b in PERIODOS_15Y:
        m = dates.between(a, b); x = netbp[m]
        r[f"{tag}_bp"] = x.mean(); r[f"{tag}_t"] = x.mean() / (x.std() / np.sqrt(len(x))); r[f"{tag}_wr"] = (x > 0).mean()
    return r, yrs
rows = []; Y = {}
for label, mask in [("Overnight todas las noches", A.index == A.index),
                    ("Overnight sin fines de semana", A.gap_days == 1),
                    ("Overnight solo si close > SMA200", A.c > A.sma200),
                    ("Solo RTH (apertura→cierre)", None)]:
    if mask is None:
        r, y = met(A.rth_pts, A.rth_bp, A.date, label)
    else:
        X = A[mask]; r, y = met(X.on_pts, X.on_bp, X.date, label)
    rows.append(r); Y[label] = y
# buy & hold (sin costos, bp diarios cierre a cierre)
bh = (A.c.diff() / A.raw_c.shift() * 1e4).dropna()
eq = bh.cumsum(); rows.append(dict(estrategia="Buy & hold (referencia)", n=len(bh), wr=(bh > 0).mean(), bp_trade=bh.mean(),
     t=bh.mean() / (bh.std() / np.sqrt(len(bh))), sharpe_anual=bh.mean() / bh.std() * np.sqrt(252), maxdd_bp=(eq.cummax() - eq).max()))
Y["Buy & hold"] = bh.groupby(A.date.loc[bh.index].dt.year).sum()
R = pd.DataFrame(rows); pd.set_option("display.width", 260)
print(R.round(3).to_string(index=False))
print("\nSuma anual en bp netos:"); print(pd.DataFrame(Y).round(0).to_string())
print("\nOvernight por día de la noche (bp netos medios):", A.groupby("dow").on_bp.mean().round(2).to_dict())
R.to_csv(os.path.join(RES_DIR, "f6_15y_overnight.csv"), index=False)
# curvas para informe
cur = {"on": [[d.strftime("%Y-%m-%d"), round(v, 1)] for d, v in zip(A.date, (A.on_bp - COSTO_MKT_RT_PTS / A.raw_c * 1e4).cumsum())][::5],
       "rth": [[d.strftime("%Y-%m-%d"), round(v, 1)] for d, v in zip(A.date, (A.rth_bp - COSTO_MKT_RT_PTS / A.raw_c * 1e4).cumsum())][::5],
       "bh": [[d.strftime("%Y-%m-%d"), round(v, 1)] for d, v in zip(A.date.loc[bh.index], bh.cumsum())][::5]}
json.dump(cur, open(os.path.join(RES_DIR, "f6_curvas_overnight.json"), "w"))
