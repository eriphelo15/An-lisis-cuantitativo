"""Filtros de contexto con umbrales fijados SOLO en DEV (2010-2018) y evaluados fuera de muestra (2019-2026).
Filtros con lógica de mercado (no optimizados por fuerza bruta): stop no minúsculo, EMA20 inclinada a favor,
el día ya se mueve a favor, el día ya tiene rango."""
import numpy as np, pandas as pd, os, itertools
from hougaard import PERIODOS
S = pd.read_parquet("/home/user/data/pullback_señales_nq.parquet")
dev = S[S.f <= "2018-12-31"]
U = {"stop": dev.dist_ema50_R.quantile(0.25), "pend": dev.pend20_a_favor.median(), "mov": dev.mov_apertura_a_favor.median(), "rango": dev.rango_dia_hasta_atr.median()}
print("Umbrales fijados en DEV:", {k: round(v, 4) for k, v in U.items()})
F = {"stop no minúsculo": S.dist_ema50_R > U["stop"], "EMA20 inclinada a favor": S.pend20_a_favor > U["pend"],
     "día a favor": S.mov_apertura_a_favor > U["mov"], "día con rango": S.rango_dia_hasta_atr > U["rango"]}
filas = []
for k in range(0, 5):
    for combo in itertools.combinations(F.keys(), k):
        m = pd.Series(True, index=S.index)
        for c in combo: m &= F[c]
        g = S[m]
        fila = dict(filtros=" + ".join(combo) if combo else "ninguno (base)", n_filtros=len(combo), trades=len(g), por_dia=len(g) / S.di.nunique(),
                    R_medio=g.R_neto.mean(), wr=(g.R_neto > 0).mean())
        for tag, a, b in PERIODOS:
            y = g[(g.f >= a) & (g.f <= b)].R_neto
            fila[f"{tag}_R"] = y.mean(); fila[f"{tag}_t"] = y.mean() / (y.std() / np.sqrt(len(y)))
        yrs = g.groupby(g.f.dt.year).R_neto.mean(); fila["años_pos"] = f"{int((yrs > 0).sum())}/{len(yrs)}"
        filas.append(fila)
T = pd.DataFrame(filas).sort_values(["n_filtros", "DEV_R"])
T.to_csv("resultados/pullback_filtrado.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
print(T.round(3).to_string(index=False))
