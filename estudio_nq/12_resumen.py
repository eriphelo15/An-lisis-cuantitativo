"""Fase 4 — Serie completa (DEV+HOLD) de los candidatos que replicaron + datos para el informe."""
import numpy as np, pandas as pd, json, os
from importlib import import_module
dip = import_module("07_dip_trend")
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS, HOLDOUT_START, PUNTO_USD
from scipy.stats import ttest_1samp
J = {}
A = dip.daily("all")
T = dip.backtest(A, 50, 2, 5, "connors")
M = Motor("all"); D = M.D.dropna(subset=["atr"]); s = M.smin; di = M.day_id
rth = (s >= 930) & (s < 1320)
ie = np.flatnonzero(rth & ((s - 930) % 15 == 14)); ib = ie - 14
ok = di[ib] == di[ie]; ie, ib = ie[ok], ib[ok]
r15 = M.c[ie] - M.o[ib]; atr = D.atr.reindex(di[ie]).to_numpy(); zr = r15 / atr
m = (np.abs(zr) > 0.35) & (s[ie] < hm2s(1530)) & ~np.isnan(zr)
ex = np.minimum(s[ie[m]] + 15, 1319); exm = (ex + 18 * 60) % 1440; exh = exm // 60 * 100 + exm % 60
st = M.run("H3", {}, ie[m], np.sign(r15[m]).astype(int), 0.2 * atr[m], 0.1 * atr[m], exh, guardar=False)
H3 = pd.DataFrame({"date": M.days[di[st["_idx"]]], "pnl": st["_pnl"]})
Mo = D[D.dow == 0]; H5 = pd.DataFrame({"date": M.days[Mo.index], "pnl": (Mo.rth_c - Mo.rth_o - COSTO_MKT_RT_PTS).to_numpy()})
H1 = T.rename(columns={"entry_date": "date"})[["date", "pnl"]]
for k, X in {"H1": H1, "H3": H3, "H5": H5}.items():
    p = X.pnl.to_numpy(); t, pv = ttest_1samp(p, 0)
    yr = X.groupby(X.date.dt.year).pnl.agg(["count", "mean", "sum", lambda x: (x > 0).mean()])
    yr.columns = ["n", "exp", "total", "wr"]
    eq = X.pnl.cumsum().to_numpy(); dd = float((np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max())
    J[k] = dict(n=len(p), wr=float((p > 0).mean()), exp=float(p.mean()), total=float(p.sum()), t=float(t), p=float(pv / 2),
                pf=float(p[p > 0].sum() / -p[p <= 0].sum()), maxdd=dd, avg_win=float(p[p > 0].mean()), avg_loss=float(p[p <= 0].mean()),
                por_año=yr.round(3).reset_index().to_dict("records"),
                curva=[[d.strftime("%Y-%m-%d"), round(float(v), 2)] for d, v in zip(X.date, X.pnl.cumsum())])
    print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in J[k].items() if a not in ("curva", "por_año")})
    print(yr.round(2).to_string())
bh = A[["date", "c"]]; J["bh"] = [[d.strftime("%Y-%m-%d"), round(float(v - bh.c.iloc[0]), 2)] for d, v in zip(bh.date, bh.c)]
json.dump(J, open(os.path.join(RES_DIR, "resumen_candidatos.json"), "w"), default=str)
