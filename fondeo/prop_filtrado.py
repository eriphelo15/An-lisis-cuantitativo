"""Fondeo Tradeify 50K con el pullback VI FILTRADO (umbrales de DEV). Trades reales escalados al precio de hoy."""
import numpy as np, pandas as pd, itertools, os
from prop_estrategia import examen, fondeada
RES = os.path.join(os.path.dirname(__file__), "resultados")
S = pd.read_parquet("/home/user/data/pullback_señales_nq.parquet")
z = np.load("/home/user/data/nq15_rth_ema.npz", allow_pickle=True); atr = z["atr"]; F = pd.DatetimeIndex(z["f"])
atr_hoy = np.nanmean(atr[-60:])
dev = S[S.f <= "2018-12-31"]
U = dict(stop=dev.dist_ema50_R.quantile(0.25), pend=dev.pend20_a_favor.median(), mov=dev.mov_apertura_a_favor.median())
FILT = {"sin filtro": pd.Series(True, index=S.index),
        "stop + día a favor": (S.dist_ema50_R > U["stop"]) & (S.mov_apertura_a_favor > U["mov"]),
        "stop + EMA20 + día a favor": (S.dist_ema50_R > U["stop"]) & (S.mov_apertura_a_favor > U["mov"]) & (S.pend20_a_favor > U["pend"])}
def lib(mask, desde, hasta):
    R = S[mask].copy(); esc = atr_hoy / atr[R.di.astype(int)]
    R["rs"] = R.rk * esc; R["rr"] = R.res * esc
    dias = np.flatnonzero((F >= pd.Timestamp(desde)) & (F <= pd.Timestamp(hasta)) & ~np.isnan(atr))
    R = R[R.di.isin(dias)]; g = dict(tuple(R.groupby("di")))
    ini = np.zeros(len(dias) + 1, np.int64); rs, rr = [], []
    for i, d in enumerate(dias):
        if d in g: rs += g[d].rs.tolist(); rr += g[d].rr.tolist()
        ini[i + 1] = len(rs)
    return ini, np.array(rs), np.array(rr)
filas = []
for fn, m in FILT.items():
    libs = {"cons": lib(m, "2010-10-01", "2020-12-31"), "opt": lib(m, "2021-01-01", "2026-03-13")}
    for Rusd, K in itertools.product([150, 250, 400, 600, 900], [1, 2, 3]):
        f = dict(filtro=fn, Rusd=Rusd, K=K)
        for esc, (ini, rs, rr) in libs.items():
            ok, d = examen(ini, rs, rr, 3000, 3000., 2000., 0., 0.4, 3, float(Rusd) * 2.0, K, 1e9, 1e9, 40, 60, 5)
            cob, nr, vv = fondeada(ini, rs, rr, 3000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
            f.update({f"{esc}_aprueba": ok.mean(), f"{esc}_dias_ex": np.median(d[ok]) if ok.any() else np.nan, f"{esc}_ev": cob.mean(),
                      f"{esc}_cobra": (nr > 0).mean(), f"{esc}_retiros": nr.mean(), f"{esc}_vida": vv.mean(), f"{esc}_neto_ex": ok.mean() * cob.mean() - 99.0,
                      f"{esc}_por_cupo_año": cob.mean() / (vv.mean() / 252)})
        filas.append(f)
    print(fn, flush=True)
X = pd.DataFrame(filas); X["min_neto_ex"] = X[["cons_neto_ex", "opt_neto_ex"]].min(axis=1)
X.to_csv(os.path.join(RES, "prop_filtrado.csv"), index=False)
pd.set_option("display.width", 260)
print(X.sort_values("min_neto_ex", ascending=False).groupby("filtro").head(2).round(2).to_string(index=False))
