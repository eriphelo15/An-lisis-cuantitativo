"""Evalúa SRS, ASRS, 1BP y 1BN (Hougaard) en NQ, ES, YM. Variantes pre-fijadas (no optimizadas)."""
import itertools, os, pandas as pd, numpy as np
from hougaard import evaluar
RES = os.path.join(os.path.dirname(__file__), "resultados")
V_bracket = [dict(stop=s, R=R, rev=rev, buf=2) for s, R, rev in itertools.product([0, 1, 2], [0, 1, 2, 3], [True, False])]
for v in V_bracket:
    if v["stop"] == 2: v["stop_atr"] = 0.1
V_asrs = [dict(v, barra=b) for v in V_bracket for b in (4, 5)]
V_1b = [dict(stop=2, stop_atr=sa, R=R, rev=False, buf=2) for sa, R in itertools.product([0.1, 0.2, 0.3], [0, 1, 2, 3])]
out = []
for sym in ["NQ", "ES", "YM"]:
    for est, V in [("SRS", V_bracket), ("ASRS", V_asrs), ("1BP", V_1b), ("1BN", V_1b)]:
        out.append(evaluar(sym, est, V)); print(sym, est, flush=True)
R = pd.concat(out, ignore_index=True); R.to_csv(os.path.join(RES, "hougaard_eval.csv"), index=False)
pd.set_option("display.width", 260)
cols = ["sym", "estrategia", "stop", "R", "rev", "barra", "stop_atr", "n", "wr", "exp_usd", "pf", "t", "DEV_atr%", "DEV_t", "VAL1_atr%", "VAL1_t", "VAL2_atr%", "VAL2_t"]
cols = [c for c in cols if c in R.columns]
print("\nResumen por estrategia e instrumento (media de variantes, t medio, mejor t):")
print(R.groupby(["estrategia", "sym"]).agg(variantes=("n", "size"), wr=("wr", "mean"), exp_usd=("exp_usd", "mean"), t_medio=("t", "mean"), t_max=("t", "max"),
      dev_t=("DEV_t", "mean"), val1_t=("VAL1_t", "mean"), val2_t=("VAL2_t", "mean")).round(2).to_string())
print("\nTop 15 por t (todas):")
print(R.sort_values("t", ascending=False)[cols].head(15).round(2).to_string(index=False))
