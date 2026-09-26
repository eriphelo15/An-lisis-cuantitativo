"""Fase 3a — Validación de candidatos dentro de DEV: permutación, estrés de costos, vecindad."""
import numpy as np, pandas as pd, itertools
from importlib import import_module
dip = import_module("07_dip_trend")
from motor import Motor, hm2s
from lib import COSTO_MKT_RT_PTS, TICK
rng = np.random.default_rng(42)

# ---------- H1/H2: dip en tendencia ----------
A = dip.daily("dev")
for streak in [2, 3]:
    T = dip.backtest(A, 50, streak, 5, "connors")
    obs = T.pnl.mean()
    # nulo: mismas reglas de salida pero entradas en días aleatorios en tendencia (c > sma50), mismo nº de trades
    c = A.c.to_numpy(); sma = pd.Series(c).rolling(50).mean().to_numpy(); h = A.h.to_numpy()
    cand = np.flatnonzero(c > sma); cand = cand[cand < len(c) - 6]
    null = []
    for _ in range(3000):
        e = rng.choice(cand, len(T), replace=False); p = []
        for i in e:
            j = i + 1
            while j < len(c) and not (c[j] > h[j-1]) and j - i < 5: j += 1
            p.append(c[min(j, len(c)-1)] - c[i] - COSTO_MKT_RT_PTS)
        null.append(np.mean(p))
    null = np.array(null)
    pv = (null >= obs).mean()
    boots = [rng.choice(T.pnl.to_numpy(), len(T)).mean() for _ in range(5000)]
    print(f"H{streak-1} dip streak>={streak}: n={len(T)} WR={ (T.pnl>0).mean():.3f} exp={obs:.1f} pts | nulo aleatorio en tendencia: media={null.mean():.1f} p95={np.quantile(null,.95):.1f}  p-valor perm={pv:.4f}")
    print(f"     IC95 bootstrap exp: [{np.quantile(boots,.025):.1f}, {np.quantile(boots,.975):.1f}]   MAE mediana={T.mae.median():.0f} pts, peor MAE={T.mae.min():.0f}")
    for extra in [2, 4, 8]:
        print(f"     costo extra {extra} ticks: exp={obs - extra*TICK:.1f}")

# ---------- H3: momentum 15m ----------
M = Motor("dev"); D = M.D.dropna(subset=["atr"]); s = M.smin; di = M.day_id
rth = (s >= 930) & (s < 1320)
ie = np.flatnonzero(rth & ((s - 930) % 15 == 14)); ib = ie - 14
ok = di[ib] == di[ie]; ie, ib = ie[ok], ib[ok]
r15 = M.c[ie] - M.o[ib]; atr = D.atr.reindex(di[ie]).to_numpy(); zr = r15 / atr
def run15(k, sx, tx, hold, cost=COSTO_MKT_RT_PTS, guardar=False):
    m = (np.abs(zr) > k) & (s[ie] < hm2s(1530)) & ~np.isnan(zr)
    ex = np.minimum(s[ie[m]] + hold, 1319); exm = (ex + 18 * 60) % 1440; exh = exm // 60 * 100 + exm % 60
    return M.run("R15", {}, ie[m], np.sign(r15[m]).astype(int), sx * atr[m], tx * atr[m], exh, cost=cost, guardar=False)
print("\nH3 momentum 15m — vecindad (t-stat):")
rows = []
for k, sx, tx in itertools.product([0.25, 0.3, 0.35, 0.4, 0.45], [0.15, 0.2, 0.25, 0.3], [0.08, 0.1, 0.12, 0.15]):
    st = run15(k, sx, tx, 15); rows.append(dict(k=k, sx=sx, tx=tx, n=st["n"], wr=st["wr"], exp=st["exp_pts"], t=st["t"], A=st["exp_A"], B=st["exp_B"]))
V = pd.DataFrame(rows)
print(V.pivot_table(index="k", columns="sx", values="t", aggfunc="mean").round(2))
print("fracción configs t>2:", (V.t > 2).mean().round(3), "  exp>0:", (V.exp > 0).mean().round(3))
print("WR medio por k:", V.groupby("k").wr.mean().round(3).to_dict())
st = run15(0.35, 0.2, 0.1, 15)
p = st["_pnl"]; print(f"\nH3 elegido: n={st['n']} WR={st['wr']:.3f} exp={st['exp_pts']:.2f} pts  t={st['t']:.2f}")
for extra in [1, 2, 4]:
    print(f"     costo extra {extra} ticks: exp={st['exp_pts'] - extra*TICK:.2f}")
yrs = M.days[di[st['_idx']]].year
print("     por año:", pd.Series(p).groupby(yrs).agg(["mean", "count", lambda x: (x > 0).mean()]).round(3).to_dict("index"))
