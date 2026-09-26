"""Gappers de small caps (datos diarios Yahoo 2015-2026).
Evento: apertura >= +20% sobre el cierre de ayer; volumen medio en $ de los 20 días previos < $20M (acción pequeña/poco líquida);
volumen en $ del día >= $1M (operable) y volumen >= 3x la media (en juego). Se descartan datos imposibles.
Resultados por operación (en %), con stops conservadores (si el máximo/mínimo del día toca el stop, se asume que saltó).
Costes: spread + deslizamiento de ida y vuelta de 1% (base); sensibilidad 0.5% y 2%. En cortos no se incluye el coste de préstamo."""
import glob
import numpy as np, pandas as pd
D = pd.concat([pd.read_parquet(f) for f in glob.glob("/home/user/data/smallcaps/diario/*.parquet")])
D = D.rename(columns=str.lower).sort_values(["sym", "date"])
D = D[(D.open > 0) & (D.close > 0) & (D.high >= D[["open", "close"]].max(axis=1)) & (D.low <= D[["open", "close"]].min(axis=1))]
g = D.groupby("sym")
D["pc"] = g.close.shift(); D["dv"] = D.close * D.volume
D["dv20"] = g.dv.transform(lambda x: x.shift().rolling(20, min_periods=10).mean())
D["v20"] = g.volume.transform(lambda x: x.shift().rolling(20, min_periods=10).mean())
D["n_o"] = g.open.shift(-1); D["n_c"] = g.close.shift(-1); D["n_h"] = g.high.shift(-1); D["n_l"] = g.low.shift(-1)
D["gap"] = D.open / D.pc - 1
E = D[(D.gap >= 0.20) & (D.gap < 5) & (D.dv20 < 20e6) & (D.dv >= 1e6) & (D.volume >= 3 * D.v20)].copy()
E["año"] = pd.to_datetime(E.date).dt.year
E["P"] = np.where(E.año <= 2019, "2015-19", np.where(E.año <= 2022, "2020-22", "2023-26"))
o, h, l, c = E.open, E.high, E.low, E.close
R = {}
R["LARGO apertura->cierre"] = c / o - 1
R["CORTO apertura->cierre"] = 1 - c / o
for s in [0.10, 0.20, 0.30]:
    R[f"CORTO stop {int(s*100)}%"] = np.where(h >= o * (1 + s), -s, 1 - c / o)
    R[f"LARGO stop {int(s*100)}%"] = np.where(l <= o * (1 - s), -s, c / o - 1)
# corto con objetivo: stop 20%, objetivo 20% (si ambos se tocan -> pérdida, conservador)
R["CORTO stop 20% / obj 20%"] = np.where(h >= o * 1.2, -0.2, np.where(l <= o * 0.8, 0.2, 1 - c / o))
# día 2
cierre_fuerte = c >= l + 0.8 * (h - l)
R["DÍA 2 largo (si cerró fuerte)"] = np.where(cierre_fuerte, E.n_c / E.n_o - 1, np.nan)
R["DÍA 2 corto (si cerró débil)"] = np.where(~cierre_fuerte, 1 - E.n_c / E.n_o, np.nan)
R["DÍA 2 corto, stop 20% (todos)"] = np.where(E.n_h >= E.n_o * 1.2, -0.2, 1 - E.n_c / E.n_o)
print(f"Eventos: {len(E)} en {E.sym.nunique()} acciones; por año:", E.groupby("año").size().to_dict())
filas = []
for nom, r in R.items():
    r = pd.Series(np.asarray(r, float), index=E.index)
    for p in ["2015-19", "2020-22", "2023-26", "TODO"]:
        x = (r[E.P == p] if p != "TODO" else r).dropna() * 100
        if len(x) < 20: continue
        w = x.clip(x.quantile(0.01), x.quantile(0.99))
        filas.append(dict(estrategia=nom, periodo=p, n=len(x), acierto=(x - 1 > 0).mean(), media_bruta=x.mean(), mediana=x.median(),
                          media_sin_extremos=w.mean(), neto_05=x.mean() - 0.5, neto_1=x.mean() - 1, neto_2=x.mean() - 2,
                          t_neto1=(x.mean() - 1) / x.std() * np.sqrt(len(x)), peor=x.min()))
T = pd.DataFrame(filas); T.to_csv("res_02_gappers.csv", index=False)
pd.set_option("display.width", 250); print(T.round(2).to_string(index=False))
E.to_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
