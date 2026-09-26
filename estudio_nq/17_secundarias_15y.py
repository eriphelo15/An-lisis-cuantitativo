"""OPEX viernes corto (RTH) y momentum 15m k=0.25 por año, 15 años, neto de costos reales."""
import numpy as np, pandas as pd, os
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS
M = Motor("all"); D = M.D.dropna(subset=["atr"]).copy(); s = M.smin; di = M.day_id
D["date"] = M.days[D.index]
O = D[(D.date.dt.dayofweek == 4) & D.date.dt.day.between(15, 21)].copy()
O["net"] = (O.rth_o - O.rth_c) - COSTO_MKT_RT_PTS; O["atr%"] = (O.rth_o - O.rth_c) / O.atr * 100
print("OPEX viernes corto RTH: n=%d WR=%.3f net medio=%.1f pts  t=%.2f" % (len(O), (O.net > 0).mean(), O.net.mean(), O.net.mean() / (O.net.std() / np.sqrt(len(O)))))
print(O.groupby(O.date.dt.year).agg(n=("net", "size"), wr=("net", lambda x: (x > 0).mean()), net=("net", "mean"), atr_pct=("atr%", "mean")).round(2).T.to_string())
# trimestral (marzo/jun/sep/dic, 'triple witching') vs mensual
q = O.date.dt.month.isin([3, 6, 9, 12])
for lab, m in [("trimestral", q), ("mensual no trimestral", ~q)]:
    x = O.loc[m, "atr%"]; print(f"  {lab}: n={m.sum()} media={x.mean():.1f}% ATR t={x.mean()/(x.std()/np.sqrt(len(x))):.2f} WR={(x>0).mean():.3f}")
rth = (s >= 930) & (s < 1320)
ie = np.flatnonzero(rth & ((s - 930) % 15 == 14)); ib = ie - 14
ok = di[ib] == di[ie]; ie, ib = ie[ok], ib[ok]
r15 = M.c[ie] - M.o[ib]; atr = D.atr.reindex(di[ie]).to_numpy(); zr = r15 / atr
m = (np.abs(zr) > 0.25) & (s[ie] < hm2s(1530)) & ~np.isnan(zr)
ex = np.minimum(s[ie[m]] + 30, 1319); exm = (ex + 1080) % 1440; exh = exm // 60 * 100 + exm % 60
st = M.run("R15", {}, ie[m], np.sign(r15[m]).astype(int), 0.2 * atr[m], 0.1 * atr[m], exh, cost=0.0, guardar=False)
X = pd.DataFrame({"date": M.days[di[st["_idx"]]], "g": st["_pnl"], "atr": D.atr.reindex(di[st["_idx"]]).to_numpy()})
X["net"] = X.g - COSTO_MKT_RT_PTS
Yr = X.groupby(X.date.dt.year).agg(n=("g", "size"), wr_neto=("net", lambda x: (x > 0).mean()), bruto_atr=("g", lambda x: 0), neto_pts=("net", "mean"))
Yr["bruto_%ATR"] = X.groupby(X.date.dt.year).apply(lambda d: (d.g / d.atr).mean() * 100)
Yr["costo_%ATR"] = X.groupby(X.date.dt.year).apply(lambda d: (COSTO_MKT_RT_PTS / d.atr).mean() * 100)
print("\nMomentum 15m (k=0.25, stop 0.2, tgt 0.1, 30 min) por año:")
print(Yr.drop(columns="bruto_atr").round(2).to_string())
print("años con bruto > 0:", int((Yr["bruto_%ATR"] > 0).sum()), "de", len(Yr), "| años con neto > 0:", int((Yr.neto_pts > 0).sum()))
O.to_csv(os.path.join(RES_DIR, "f7_15y_opex.csv")); Yr.to_csv(os.path.join(RES_DIR, "f7_15y_r15_por_año.csv"))
