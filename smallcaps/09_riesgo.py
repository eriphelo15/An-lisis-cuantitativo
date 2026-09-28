"""Módulo 7: cuánto puede subir en contra un gapper (colas) y qué tamaño aguanta una cuenta.
1) Subida máxima en contra desde la apertura (día 1 y días 1-2), 8 604 gappers 2015-2026 (datos diarios).
2) Monte Carlo de una cuenta con los R reales del setup A (corto apertura gaps >=100 %, stop +30 %, con 5 % de deslizamiento)
   de 06_setups, a distintos riesgos por operación."""
import numpy as np
import pandas as pd

E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
E = E.dropna(subset=["open", "high"])
E["mae1"] = E.high / E.open - 1
E["mae2"] = np.maximum(E.high, E.n_h.fillna(0)) / E.open - 1
print("=== Subida máxima EN CONTRA de un corto abierto en la apertura")
for nom, m in [("gap 20-50 %", (E.gap >= .2) & (E.gap < .5)), ("gap 50-100 %", (E.gap >= .5) & (E.gap < 1)), ("gap >= 100 %", E.gap >= 1)]:
    x = E[m]
    print(f"{nom:13s} n={len(x):5d} | día 1: mediana {x.mae1.median():+.0%}  p75 {x.mae1.quantile(.75):+.0%}  p90 {x.mae1.quantile(.9):+.0%}  p99 {x.mae1.quantile(.99):+.0%}"
          f"  | >+30 %: {(x.mae1>.3).mean():.0%}  >+50 %: {(x.mae1>.5).mean():.0%}  >+100 %: {(x.mae1>1).mean():.1%}"
          f"  || días 1-2: p90 {x.mae2.quantile(.9):+.0%}  >+100 %: {(x.mae2>1).mean():.1%}")

I = pd.read_csv("res_06_setups_intradia.csv")
R = I[(I.gap >= 1) & (I.setup == "A corto apertura, stop +30% +desliz5%")].R.values
print(f"\n=== Monte Carlo: {len(R)} operaciones reales (R medio {R.mean():+.3f}, peor {R.min():.2f}); 200 operaciones por trayectoria, 20 000 trayectorias")
rng = np.random.default_rng(1)
for riesgo in [0.005, 0.01, 0.02, 0.05, 0.10]:
    tray = rng.choice(R, size=(20000, 200))
    capital = np.cumprod(1 + riesgo * tray, axis=1)
    dd = 1 - capital / np.maximum.accumulate(np.concatenate([np.ones((20000, 1)), capital], axis=1)[:, 1:], axis=1)
    mdd = dd.max(axis=1)
    fin = capital[:, -1]
    print(f"riesgo {riesgo:4.1%} por operación | resultado mediano {np.median(fin)-1:+.0%} | peor 5 % {np.quantile(fin,.05)-1:+.0%}"
          f" | caída máxima mediana {np.median(mdd):.0%} | prob. caída > 30 %: {(mdd>.3).mean():.0%} | > 50 %: {(mdd>.5).mean():.0%}")
racha = []
for t in rng.choice(R, size=(20000, 200)):
    r = m_ = 0
    for v in t:
        r = r + 1 if v < 0 else 0; m_ = max(m_, r)
    racha.append(m_)
print(f"peor racha de pérdidas seguidas en 200 operaciones: mediana {np.median(racha):.0f}, p90 {np.quantile(racha,.9):.0f}")
