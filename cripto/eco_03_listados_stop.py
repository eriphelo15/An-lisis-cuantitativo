"""Corto a nuevos listados (7 d) con stop loss sobre máximos diarios del perpetuo, y separando memecoins."""
import numpy as np
import pandas as pd
import eco_base as e

C = 0.001
fut = e.panel("fut", "1d"); fut["sym"] = fut.sym.astype(str)
FH = fut.pivot(index="t", columns="sym", values="h")
FC = fut.pivot(index="t", columns="sym", values="c")
D = pd.read_csv("res_eco_corto_listados.csv", parse_dates=["t"])
filas = []
for stop in [None, 0.2, 0.3, 0.5]:
    for r in D.itertuples():
        hs = FH[r.perp].loc[r.t + pd.Timedelta("1D"): r.t + pd.Timedelta("7D")]
        p_in = FC.at[r.t, r.perp]
        neto = r.neto
        if stop is not None and len(hs) and (hs >= p_in * (1 + stop)).any():
            neto = -stop - 0.005 - 2 * C          # 0.5 % de deslizamiento en el stop, sin funding (conservador: ya incluido abajo)
            neto += min(r.funding, 0)
        filas.append(dict(stop=stop, sym=r.sym, t=r.t, meme=r.meme, neto=neto))
X = pd.DataFrame(filas)
X["per"] = np.where(X.t <= pd.Timestamp("2022-12-31", tz="UTC"), "DEV", "VAL")
X["grupo"] = np.where(X.meme, "meme", "no meme")
t = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
for (stop, g), x in X[X.per == "VAL"].groupby(["stop", "grupo"], dropna=False):
    y = x.groupby(x.t.dt.year).neto.mean()
    print(f"stop {stop}  {g:8s} n={len(x):3d} media {x.neto.mean():+.1%} t {t(x.neto):+.1f} WR {(x.neto>0).mean():.0%} peor {x.neto.min():+.0%}"
          f" | años: " + " ".join(f"{a}:{v:+.1%}" for a, v in y.items()))
for stop in [None, 0.3]:
    x = X[(X.stop.isna() if stop is None else X.stop == stop) & ~X.meme & (X.per == "VAL")].sort_values("t")
    # cartera: 5 % del capital por operación, sin apalancamiento adicional
    m = x.groupby(x.t.dt.to_period("M")).neto.sum() * 0.05
    print(f"\nstop {stop} no meme, 5% del capital por operación: meses {len(m)}, positivos {(m>0).mean():.0%},"
          f" media mensual {m.mean():+.1%}, peor mes {m.min():+.1%}, mejor {m.max():+.1%}, total {(1+m).prod()-1:+.0%}")
X.to_csv("res_eco_listados_stop.csv", index=False)
