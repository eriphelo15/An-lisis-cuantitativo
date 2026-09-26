"""Fase 2f — Familias intradía: ORB, desviación de VWAP, momentum/reversión de 15 min (DEV)."""
import numpy as np, pandas as pd, os, sys, itertools
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS, COSTO_LMT_RT_PTS
split = sys.argv[1] if len(sys.argv) > 1 else "dev"
M = Motor(split); D = M.D.dropna(subset=["atr"]); s = M.smin; di = M.day_id
N = len(M.c)

# ---------------- ORB: rango de los primeros K minutos; entrada en el primer cierre fuera ----------------
def orb_signals(K):
    sig, dirn, rng, days = [], [], [], []
    for d in D.index:
        i0 = M.i_rth0[d]; iK = i0 + K
        if iK + 1 >= N or di[iK] != d: continue
        hi = M.h[i0:iK].max(); lo = M.l[i0:iK].min()
        j = iK
        while j < N and di[j] == d and s[j] < hm2s(1500):
            if M.c[j] > hi: sig.append(j); dirn.append(1); break
            if M.c[j] < lo: sig.append(j); dirn.append(-1); break
            j += 1
        else:
            continue
        rng.append(hi - lo); days.append(d)
    return np.array(sig), np.array(dirn), np.array(rng), np.array(days)

for K in [5, 15, 30, 60]:
    sig, dirn, rng, days = orb_signals(K)
    atr = D.loc[days, "atr"].to_numpy()
    for mode in ["go", "fade"]:
        dd = dirn if mode == "go" else -dirn
        for sx, tx in itertools.product([0.5, 1.0], [0.5, 1.0, 2.0]):
            for ex in [1200, 1559]:
                M.run(f"ORB_{mode}", dict(K=K, stop_x_or=sx, tgt_x_or=tx, salida=ex), sig, dd, sx * rng, tx * rng, ex)

# ---------------- VWAP: desviación en múltiplos de sigma de sesión RTH ----------------
df = M.df
rth = (s >= 930) & (s < 1320)
tp = (M.h + M.l + M.c) / 3
key = np.where(rth, di, -1)
pv = pd.Series(tp * M.v).groupby(key).cumsum().to_numpy(); vv = pd.Series(M.v).groupby(key).cumsum().to_numpy()
vwap = pv / vv
dev = M.c - vwap
sd = pd.Series(dev ** 2 * M.v).groupby(key).cumsum().to_numpy() / vv
z = dev / np.sqrt(np.maximum(sd, 1e-9))
elig = rth & (s >= hm2s(1000)) & (s <= hm2s(1500))
for zth in [2.0, 2.5, 3.0]:
    for mode in ["revert", "go"]:
        # primer cruce del umbral por día y lado
        cross_up = elig & (z > zth) & (np.roll(z, 1) <= zth)
        cross_dn = elig & (z < -zth) & (np.roll(z, 1) >= -zth)
        idx = np.flatnonzero(cross_up | cross_dn)
        first = pd.Series(idx).groupby([di[idx], np.sign(z[idx])]).first().to_numpy()
        dirn = -np.sign(z[first]).astype(int) if mode == "revert" else np.sign(z[first]).astype(int)
        atr = D.atr.reindex(di[first]).to_numpy(); ok = ~np.isnan(atr)
        first, dirn, atr = first[ok], dirn[ok], atr[ok]
        dist = np.abs(dev[first])
        for sx, tx in itertools.product([0.1, 0.2], [0.5, 1.0]):
            # target = fracción de la distancia al VWAP; stop en ATR
            M.run(f"VWAP_{mode}", dict(z=zth, stop_atr=sx, tgt_x_dist=tx), first, dirn, sx * atr, tx * dist, 1559)

# ---------------- 15 min: tras un bloque de 15m extremo (|r|>k·sd), continuar o revertir ----------------
b = (s - 930) // 15
blk_end = rth & ((s - 930) % 15 == 14)
ie = np.flatnonzero(blk_end); ib = ie - 14
ok = (di[ib] == di[ie]); ie, ib = ie[ok], ib[ok]
r15 = M.c[ie] - M.o[ib]
atr = D.atr.reindex(di[ie]).to_numpy()
zr = r15 / atr
for k in [0.15, 0.25, 0.35]:
    m = (np.abs(zr) > k) & (s[ie] < hm2s(1530)) & ~np.isnan(zr)
    for mode in ["cont", "rev"]:
        dd = np.sign(r15[m]).astype(int) * (1 if mode == "cont" else -1)
        for sx, tx in itertools.product([0.1, 0.2], [0.1, 0.2]):
            for hold in [15, 30]:
                ex = np.minimum(s[ie[m]] + hold, 1319)
                exh = ((ex + 18 * 60) % 1440) // 60 * 100 + ((ex + 18 * 60) % 1440) % 60
                M.run(f"R15_{mode}", dict(k_atr=k, stop_atr=sx, tgt_atr=tx, hold=hold), ie[m], dd, sx * atr[m], tx * atr[m], exh)

R = M.guardar_registro(f"f2f_intradia_{split}.csv")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print("configs:", len(R))
print(R.groupby("label").agg(n_cfg=("n", "size"), exp_medio=("exp_pts", "mean"), wr_medio=("wr", "mean"), t_max=("t", "max"), t_medio=("t", "mean")).round(3).to_string())
print("\nTop 15 por t:")
print(R.sort_values("t", ascending=False)[["label", "params", "n", "wr", "exp_pts", "pf", "t", "exp_A", "exp_B"]].head(15).round(3).to_string(index=False))
