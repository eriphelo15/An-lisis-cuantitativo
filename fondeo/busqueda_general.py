"""Búsqueda aleatoria amplia en el espacio de estrategias para la FONDEADA (Growth 50K y Select Flex 50K).
Incluye estructuras de winrate alto (objetivo << stop). Métrica por época (2011-20 y 2021-26):
  neto_cupo      = E[cobros] - cuota / P(aprobar)       (valor por cupo llenado)
  neto_cupo_año  = neto_cupo / (vida media de la fondeada en años)
Selección robusta: se ordena por el MÍNIMO entre épocas."""
import numpy as np, pandas as pd, os, time, sys
from motor_fondeo import fondeada, examen
from reglas_tradeify import FONDEADA, EXAMEN
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
CUOTA = {"growth": 93.0, "select_flex": 99.0}
TIPO = {"growth": 0, "select_flex": 1}
MODOS = [(0, 1), (1, 1), (2, 16), (2, 31), (3, 16)]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
rng = np.random.default_rng(2026)
# P(aprobar) del examen por plan y modo (política de examen óptima ya encontrada)
PAP = {}
for (m, ti) in MODOS:
    for esc, D in LIB.items():
        ok, _ = examen(D, 20000, 3000., 2000., 1250., 0., 1, 2000., 60., 180., 2, 1e9, 1e9, 40, 60, 3, m, ti)
        PAP[("growth", m, ti, esc)] = ok.mean()
        ok, _ = examen(D, 20000, 3000., 2000., 0., .4, 3, 300., 60., 240., 1, 960., 1e9, 40, 60, 3, m, ti)
        PAP[("select_flex", m, ti, esc)] = ok.mean()
rows = []; t0 = time.time()
for i in range(N):
    tipo = ["growth", "select_flex"][i % 2]
    r = FONDEADA[tipo][50]
    m, ti = MODOS[rng.integers(len(MODOS))]
    S = float(np.round(np.exp(rng.uniform(np.log(6), np.log(120))) * 4) / 4)
    rr = float(np.exp(rng.uniform(np.log(0.1), np.log(5))))
    T = max(0.5, np.round(S * rr * 4) / 4)
    R = float(np.exp(rng.uniform(np.log(40), np.log(1200))))
    K = int(rng.choice([1, 2, 3, 5, 8]))
    G = float(rng.choice([150, 225, 450, 900, 1e9]))
    L = float(rng.choice([1.0, 2.0, 1e6])); L = L * R if L < 1e5 else 1e9
    rfrac = float(rng.choice([0.0, 0.0, 0.1, 0.25, 0.5]))
    col = float(rng.choice([-1, 1000, 2500])) if tipo == "growth" else -1.0
    rec = dict(tipo=tipo, modo=m, t_ini=ti, S=S, T=T, rr=T / S, R=R, K=K, G=G, L=L, rfrac=rfrac, colchon=col)
    for esc, D in LIB.items():
        cob, nret, viv, qb = fondeada(D, 700, TIPO[tipo], 50., 2000., float(r.get("dll") or 0), 150., float(r.get("saldo_min", 0.)),
                                      float(r.get("cons", 0.) or 0.), float(r.get("pmin", 250.)),
                                      float(r["pmax"][0] if isinstance(r["pmax"], tuple) else r["pmax"]),
                                      float(r["pmax"][1] if isinstance(r["pmax"], tuple) else r["pmax"]), float(r.get("frac", 0.)),
                                      0., 0., 0., R, S, T, K, G, L, 40, 0., 250, 1000 + i, m, ti, col, rfrac)
        pap = PAP[(tipo, m, ti, esc)]
        net = cob.mean() - CUOTA[tipo] / pap
        rec.update({f"{esc}_ev": cob.mean(), f"{esc}_pcobra": (nret > 0).mean(), f"{esc}_nret": nret.mean(), f"{esc}_dias": viv.mean(),
                    f"{esc}_pap": pap, f"{esc}_neto_cupo": net, f"{esc}_neto_año": net / (viv.mean() / 252)})
    rows.append(rec)
    if i % 1000 == 999: print(i + 1, f"{time.time()-t0:.0f}s", flush=True)
X = pd.DataFrame(rows)
X["min_neto_cupo"] = X[["cons_neto_cupo", "opt_neto_cupo"]].min(axis=1)
X["min_neto_año"] = X[["cons_neto_año", "opt_neto_año"]].min(axis=1)
X.to_csv(os.path.join(RES, "busqueda_general.csv"), index=False)
pd.set_option("display.width", 260)
c = ["tipo", "modo", "t_ini", "S", "T", "rr", "R", "K", "G", "L", "rfrac", "colchon", "cons_ev", "opt_ev", "cons_pcobra", "opt_pcobra", "cons_dias", "cons_neto_cupo", "opt_neto_cupo", "min_neto_año"]
for tipo in TIPO:
    Y = X[X.tipo == tipo]
    print(f"\n=== {tipo}: top por valor robusto por cupo ===")
    print(Y.sort_values("min_neto_cupo", ascending=False)[c].head(8).round(2).to_string(index=False))
    print(f"=== {tipo}: top por valor robusto por cupo-año ===")
    print(Y.sort_values("min_neto_año", ascending=False)[c].head(5).round(2).to_string(index=False))
