"""Fase 2b — Test de barreras vs nulo martingala.

Para un stop a S y un target a T, en una martingala P(target primero) = S/(S+T).
Un winrate alto SOLO es ventaja si supera ese nulo (y cubre costos).
Se registran TODAS las configuraciones probadas (para corrección por múltiples pruebas).
"""
import numpy as np, pandas as pd, itertools, os, sys
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS, COSTO_LMT_RT_PTS
from scipy.stats import binomtest

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
TAGF = os.environ.get("TAG", split)
M = Motor(split)
D = M.D.dropna(subset=["prev_c", "atr"]).copy()
D = D[D.index > 0]
pre = M.i_rth0[D.index] - 1          # barra 09:29 (señal antes de la apertura)
ok = M.day_id[pre] == D.index.to_numpy()
D = D[ok]; pre = pre[ok]
out = []

def reg(fam, params, st, S, T, cost):
    """añade winrate bruto vs nulo."""
    p = st["_pnl"] + cost                      # pnl bruto
    n = len(p)
    if n < 30: return
    decided = p != 0
    wr = (p > 0).mean()
    null = S / (S + T) if np.isscalar(S) else np.mean(S / (S + T))
    bt = binomtest(int((p > 0).sum()), n, null, alternative="two-sided").pvalue
    st.update(dict(fam=fam, wr_bruto=wr, wr_nulo=null, exceso_wr=wr - null, p_binom=bt, **params))
    out.append({k: v for k, v in st.items() if not k.startswith("_")})

# ---------------- F1: gap fade / gap go (entrada a la apertura 09:30) ----------------
for lo, hi in [(.05, .2), (.2, .35), (.35, .6), (.6, 3)]:
    m = (D.gap.abs() / D.atr).between(lo, hi).to_numpy()
    g = D.gap.abs().to_numpy()[m]; dirn = -np.sign(D.gap.to_numpy()[m])
    for sm in [0.5, 1.0, 2.0]:
        for tm in [0.5, 1.0]:
            for ex in [1100, 1559]:
                for mode, dd in [("fade", dirn), ("go", -dirn)]:
                    prm = dict(gap_atr=f"{lo}-{hi}", stop_x_gap=sm, tgt_x_gap=tm, salida=ex, modo=mode)
                    st = M.run(f"F1_gap_{mode}", prm, pre[m], dd, sm * g, tm * g, ex, cost=COSTO_MKT_RT_PTS)
                    reg(f"F1_gap_{mode}", prm, st, sm, tm, COSTO_MKT_RT_PTS)

# ---------------- F2/F3: fade o ruptura en niveles (limit en el nivel) ----------------
niveles = {"ONH": ("on_h", -1), "ONL": ("on_l", +1), "PDH": ("prev_h", -1), "PDL": ("prev_l", +1)}
for name, (col, fade_dir) in niveles.items():
    lvl = D[col].to_numpy(); o = D.rth_o.to_numpy(); atr = D.atr.to_numpy()
    inside = (o < lvl) if fade_dir == -1 else (o > lvl)
    dist = np.abs(lvl - o) / atr
    for dlo, dhi in [(0, .25), (.25, .6)]:
        m = inside & (dist > dlo) & (dist <= dhi)
        for sa in [0.1, 0.2, 0.4]:
            for ta in [0.05, 0.1, 0.2, 0.4]:
                for cancel in [1200, 1500]:
                    prm = dict(nivel=name, dist_atr=f"{dlo}-{dhi}", stop_atr=sa, tgt_atr=ta, cancel=cancel)
                    st = M.run_limit(f"F2_fade_{name}", prm, pre[m], fade_dir, lvl[m], cancel,
                                     sa * atr[m], ta * atr[m], 1559, cost=COSTO_LMT_RT_PTS)
                    reg(f"F2_fade_{name}", prm, st, sa, ta, COSTO_LMT_RT_PTS)

R = pd.DataFrame(out)
R.to_csv(os.path.join(RES_DIR, f"f2b_barreras_{TAGF}.csv"), index=False)
print("configuraciones probadas:", len(R))
cols = ["fam", "params", "n", "wr_bruto", "wr_nulo", "exceso_wr", "p_binom", "wr", "exp_pts", "pf", "t", "exp_A", "exp_B"]
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print("\nResumen por familia (media de exceso de WR sobre el nulo):")
print(R.groupby("fam").agg(n_cfg=("n", "size"), exceso_medio=("exceso_wr", "mean"), exp_medio=("exp_pts", "mean"), mejor_t=("t", "max")).round(4).to_string())
print("\nTop 20 por t-stat (neto de costos):")
print(R.sort_values("t", ascending=False)[cols].head(20).round(3).to_string(index=False))
