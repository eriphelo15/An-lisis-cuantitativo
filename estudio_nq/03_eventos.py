"""Fase 2a — Estudio de eventos (DEV): probabilidades de toque de niveles y momentum intradía."""
import numpy as np, pandas as pd, os
from motor import Motor, hm2s
from lib import RES_DIR
M = Motor("dev"); D = M.D.dropna(subset=["prev_c", "atr"]).copy()
s = M.smin
print("días utilizables:", len(D))

def touch_time(d, level, above):
    """minuto de sesión del primer toque de 'level' en RTH (>= 09:30); nan si no toca."""
    i0 = M.i_rth0[d]; idx = np.arange(i0, i0 + 390)
    idx = idx[(M.day_id[idx] == d) & (s[idx] < 1320)]
    hit = M.h[idx] >= level if above else M.l[idx] <= level
    k = np.flatnonzero(hit)
    return s[idx[k[0]]] if len(k) else np.nan

rows = []
for d, r in D.iterrows():
    o = r.rth_o; i0 = M.i_rth0[d]
    rec = dict(d=d, gap=r.gap, atr=r.atr, g_atr=r.gap / r.atr)
    rec["t_fill"] = touch_time(d, r.prev_c, r.gap < 0)
    rec["t_onh"] = touch_time(d, r.on_h, True); rec["t_onl"] = touch_time(d, r.on_l, False)
    rec["t_pdh"] = touch_time(d, r.prev_h, True); rec["t_pdl"] = touch_time(d, r.prev_l, False)
    rec["open_in_on"] = r.on_l < o < r.on_h
    rec["open_in_pd"] = r.prev_l < o < r.prev_h
    # momentum intradía
    c = M.c; idx = np.arange(i0, i0 + 390)
    def px(hm):
        k = i0 + (hm2s(hm) - 930); return c[k] if M.day_id[k] == d and s[k] == hm2s(hm) else np.nan
    rec["r_first30"] = np.log(px(959) / o); rec["r_1000_1530"] = np.log(px(1529) / px(959))
    rec["r_last30"] = np.log(px(1559) / px(1529)); rec["r_1530"] = np.log(px(1529) / r.prev_c)
    rec["r_rest"] = np.log(px(1559) / px(959))
    rows.append(rec)
E = pd.DataFrame(rows).set_index("d")
E["year"] = M.days[E.index].year
E.to_csv(os.path.join(RES_DIR, "f2a_eventos.csv"))
S = lambda hm: hm2s(hm)

print("\n=== Relleno de gap (toca cierre previo) por tamaño de gap / ATR ===")
E["gb"] = pd.cut(E.g_atr.abs(), [0, .1, .2, .35, .5, .75, 5])
for t in [1000, 1030, 1200, 1559]:
    E[f"f{t}"] = E.t_fill <= S(t)
print(E.groupby("gb", observed=True)[[f"f{t}" for t in [1000, 1030, 1200, 1559]]].mean().round(3).assign(n=E.groupby("gb", observed=True).size()).to_string())
print("por dirección del gap (todas):", E.groupby(np.sign(E.gap))[["f1030", "f1559"]].mean().round(3).to_dict())

print("\n=== Toque de máximo/mínimo overnight cuando abre DENTRO del rango ON ===")
X = E[E.open_in_on]
print("n=%d  P(toca ONH)=%.3f  P(toca ONL)=%.3f  P(toca alguno)=%.3f  P(ambos)=%.3f" % (len(X), X.t_onh.notna().mean(), X.t_onl.notna().mean(), (X.t_onh.notna() | X.t_onl.notna()).mean(), (X.t_onh.notna() & X.t_onl.notna()).mean()))
print("=== Toque de PDH/PDL cuando abre dentro del rango de ayer ===")
X = E[E.open_in_pd]
print("n=%d  P(PDH)=%.3f  P(PDL)=%.3f  alguno=%.3f ambos=%.3f" % (len(X), X.t_pdh.notna().mean(), X.t_pdl.notna().mean(), (X.t_pdh.notna() | X.t_pdl.notna()).mean(), (X.t_pdh.notna() & X.t_pdl.notna()).mean()))

print("\n=== Momentum intradía (Gao-Han-Li-Zhou) ===")
for a, b in [("r_first30", "r_last30"), ("r_1530", "r_last30"), ("r_first30", "r_rest"), ("r_1000_1530", "r_last30")]:
    x = E[[a, b]].dropna(); c = x.corr().iloc[0, 1]
    hit = (np.sign(x[a]) == np.sign(x[b])).mean()
    print(f"  {a:>12} -> {b:<9}: corr={c:+.3f}  mismo signo={hit:.3f}  n={len(x)}  z≈{c*np.sqrt(len(x)):+.2f}")
    for y, g in x.groupby(E.year): print(f"       {y}: corr={g.corr().iloc[0,1]:+.3f} n={len(g)}")
