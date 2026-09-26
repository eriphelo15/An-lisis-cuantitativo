"""Fase 3b — HOLDOUT (2025-01-01 .. 2026-03-13). Reglas CONGELADAS antes de ejecutar.
Se calcula sobre la serie completa (las features solo usan pasado) y se evalúan SOLO los
trades con entrada en el holdout. Se ejecuta una única vez."""
import numpy as np, pandas as pd, os
from importlib import import_module
dip = import_module("07_dip_trend")
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS, HOLDOUT_START
from scipy.stats import ttest_1samp

CONGELADAS = {
    "H1 dip: >=2 días bajistas & close>SMA50, salida close>high previo o 5 días": ("dip", 2),
    "H2 dip: >=3 días bajistas & close>SMA50, salida close>high previo o 5 días": ("dip", 3),
    "H3 momentum 15m: |r15|>0.35 ATR, a favor, stop 0.2 ATR, tgt 0.1 ATR, 15 min": ("r15",),
    "H4 slot 14:30-15:00 largo": ("slot", 1430, 1459, 1),
    "H5 lunes RTH largo (09:30->15:59)": ("monday",),
    "H6 slot 10:30-11:00 corto": ("slot", 1030, 1059, -1),
    "H7 ORB 60m go, stop 0.5 OR, tgt 0.5 OR": ("orb",),
}
out = {}; res = []
def summ(name, p, extra=None):
    p = np.asarray(p, float); n = len(p)
    t, pv = ttest_1samp(p, 0) if n > 2 else (np.nan, np.nan)
    r = dict(hipotesis=name, n=n, wr=(p > 0).mean(), exp_pts=p.mean(), total_pts=p.sum(),
             pf=p[p > 0].sum() / max(-p[p <= 0].sum(), 1e-9), t=t, p_unilateral=pv / 2 if t > 0 else 1 - pv / 2)
    if extra: r.update(extra)
    res.append(r)

# H1/H2
A = dip.daily("all")
for name, spec in CONGELADAS.items():
    if spec[0] == "dip":
        T = dip.backtest(A, 50, spec[1], 5, "connors")
        T = T[T.entry_date >= HOLDOUT_START]; out[name] = T
        summ(name, T.pnl, dict(peor_trade=T.pnl.min(), peor_mae=T.mae.min()))

M = Motor("all"); D = M.D.dropna(subset=["atr"]); s = M.smin; di = M.day_id
hold_day = M.days >= HOLDOUT_START
# H3
rth = (s >= 930) & (s < 1320)
ie = np.flatnonzero(rth & ((s - 930) % 15 == 14)); ib = ie - 14
ok = (di[ib] == di[ie]) & hold_day[di[ie]]; ie, ib = ie[ok], ib[ok]
r15 = M.c[ie] - M.o[ib]; atr = D.atr.reindex(di[ie]).to_numpy(); zr = r15 / atr
m = (np.abs(zr) > 0.35) & (s[ie] < hm2s(1530)) & ~np.isnan(zr)
ex = np.minimum(s[ie[m]] + 15, 1319); exm = (ex + 18 * 60) % 1440; exh = exm // 60 * 100 + exm % 60
st = M.run("H3", {}, ie[m], np.sign(r15[m]).astype(int), 0.2 * atr[m], 0.1 * atr[m], exh, guardar=False)
summ(list(CONGELADAS)[2], st["_pnl"])
# H4/H6 slots
for name, spec in CONGELADAS.items():
    if spec[0] != "slot": continue
    a, b, d = spec[1:]
    ia = np.flatnonzero(M.df.hm.to_numpy() == a); ia = ia[hold_day[di[ia]]]
    p = []
    for i in ia:
        j = i + (hm2s(b) - hm2s(a))
        if j < len(M.c) and di[j] == di[i] and s[j] == hm2s(b): p.append(d * (M.c[j] - M.o[i]) - COSTO_MKT_RT_PTS)
    summ(name, p)
# H5
H = D[(M.days[D.index] >= HOLDOUT_START) & (D.dow == 0)]
summ(list(CONGELADAS)[4], (H.rth_c - H.rth_o - COSTO_MKT_RT_PTS).to_numpy())
# H7
sig, dirn, rngs = [], [], []
for d in D.index[hold_day[D.index]]:
    i0 = M.i_rth0[d]; iK = i0 + 60
    if di[iK] != d: continue
    hi = M.h[i0:iK].max(); lo = M.l[i0:iK].min(); j = iK
    while di[j] == d and s[j] < hm2s(1500):
        if M.c[j] > hi: sig.append(j); dirn.append(1); rngs.append(hi - lo); break
        if M.c[j] < lo: sig.append(j); dirn.append(-1); rngs.append(hi - lo); break
        j += 1
rngs = np.array(rngs)
st = M.run("H7", {}, np.array(sig), np.array(dirn), 0.5 * rngs, 0.5 * rngs, 1559, guardar=False)
summ(list(CONGELADAS)[6], st["_pnl"])
# referencia: buy & hold en el holdout
Ah = A[A.date >= HOLDOUT_START]
R = pd.DataFrame(res)
# Holm-Bonferroni sobre las 7 hipótesis congeladas
R = R.sort_values("p_unilateral").reset_index(drop=True)
R["holm_umbral"] = 0.05 / (len(R) - R.index)
R["pasa_holm"] = (R.p_unilateral <= R.holm_umbral).cummin()
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(R.round(4).to_string(index=False))
print(f"\nReferencia buy&hold holdout: {Ah.c.iloc[-1] - Ah.c.iloc[0]:.0f} pts")
R.to_csv(os.path.join(RES_DIR, "f3_holdout.csv"), index=False)
for k in list(CONGELADAS)[:2]:
    out[k].to_csv(os.path.join(RES_DIR, f"f3_holdout_trades_{k[:2]}.csv"), index=False)
    print("\n", k, "\n", out[k].round(1).to_string(index=False))
