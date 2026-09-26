"""Desglose anual 2010-2026 (serie 15y) de H1, H3, H5 en unidades relativas, bruto y neto."""
import numpy as np, pandas as pd, os
from importlib import import_module
dip = import_module("07_dip_trend")
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS
A = dip.daily("all")
T = dip.backtest(A, 50, 2, 5, "connors")
px = A.set_index("date").c
# precio real de entrada (raw) para bp: usar raw_c del día de entrada
raw = A.set_index("date").raw_c
T["bp_net"] = T.pnl / raw.reindex(T.entry_date).to_numpy() * 1e4
T["bp_gross"] = (T.pnl + COSTO_MKT_RT_PTS) / raw.reindex(T.entry_date).to_numpy() * 1e4
# nulo: todos los días en tendencia, mismo esquema de salida
c = A.c.to_numpy(); h = A.h.to_numpy(); sma = pd.Series(c).rolling(50).mean().to_numpy()
null = []
for i in np.flatnonzero(c > sma):
    if i >= len(c) - 6: continue
    j = i + 1
    while j < len(c) - 1 and not (c[j] > h[j-1]) and j - i < 5: j += 1
    null.append((A.date[i], (c[j] - c[i]) / A.raw_c[i] * 1e4))
N = pd.DataFrame(null, columns=["date", "bp"])
M = Motor("all"); D = M.D.dropna(subset=["atr"]); s = M.smin; di = M.day_id
rth = (s >= 930) & (s < 1320)
ie = np.flatnonzero(rth & ((s - 930) % 15 == 14)); ib = ie - 14
ok = di[ib] == di[ie]; ie, ib = ie[ok], ib[ok]
r15 = M.c[ie] - M.o[ib]; atr = D.atr.reindex(di[ie]).to_numpy(); zr = r15 / atr
m = (np.abs(zr) > 0.35) & (s[ie] < hm2s(1530)) & ~np.isnan(zr)
ex = np.minimum(s[ie[m]] + 15, 1319); exm = (ex + 18 * 60) % 1440; exh = exm // 60 * 100 + exm % 60
st = M.run("H3", {}, ie[m], np.sign(r15[m]).astype(int), 0.2 * atr[m], 0.1 * atr[m], exh, cost=0.0, guardar=False)
a3 = D.atr.reindex(di[st["_idx"]]).to_numpy()
H3 = pd.DataFrame({"date": M.days[di[st["_idx"]]], "gross": st["_pnl"], "atr": a3})
H3["net"] = H3.gross - COSTO_MKT_RT_PTS; H3["gross_atr"] = H3.gross / H3.atr; H3["cost_atr"] = COSTO_MKT_RT_PTS / H3.atr
Mo = D[D.dow == 0]
H5 = pd.DataFrame({"date": M.days[Mo.index], "bp": np.log(Mo.rth_c / Mo.rth_o).to_numpy() * 1e4})
allD = pd.DataFrame({"date": M.days[D.index], "bp": np.log(D.rth_c / D.rth_o).to_numpy() * 1e4})
y = lambda d: d.dt.year
R = pd.DataFrame({
  "H1_n": T.groupby(y(T.entry_date)).size(), "H1_wr": T.groupby(y(T.entry_date)).pnl.apply(lambda x: (x > 0).mean()),
  "H1_bp_bruto": T.groupby(y(T.entry_date)).bp_gross.mean(), "nulo_tend_bp": N.groupby(y(N.date)).bp.mean(),
  "H3_n": H3.groupby(y(H3.date)).size(), "H3_wr_bruto": H3.groupby(y(H3.date)).gross.apply(lambda x: (x > 0).mean()),
  "H3_bruto_%ATR": H3.groupby(y(H3.date)).gross_atr.mean() * 100, "H3_costo_%ATR": H3.groupby(y(H3.date)).cost_atr.mean() * 100,
  "H5_lunes_bp": H5.groupby(y(H5.date)).bp.mean(), "resto_dias_bp": allD[allD.date.dt.dayofweek != 0].groupby(y(allD.date)).bp.mean()})
pd.set_option("display.width", 250)
print(R.round(2).to_string())
R.to_csv(os.path.join(RES_DIR, "f4_15y_por_año.csv"))
for lab, a, b in [("2010-2020", 2010, 2020), ("2021-2026", 2021, 2026)]:
    t = T[y(T.entry_date).between(a, b)]; h3 = H3[y(H3.date).between(a, b)]; n = N[y(N.date).between(a, b)]
    print(f"\n{lab}: H1 bp bruto {t.bp_gross.mean():.1f} vs nulo en tendencia {n.bp.mean():.1f}  (n={len(t)})  | "
          f"H3 bruto {h3.gross_atr.mean()*100:.2f}% ATR, t_bruto={h3.gross.mean()/(h3.gross.std()/np.sqrt(len(h3))):.2f}, WR bruto {(h3.gross>0).mean():.3f} (n={len(h3)})")
