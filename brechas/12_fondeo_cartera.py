"""Fondeo Tradeify 50K (Select examen -> Select Flex) con la CARTERA de bloques vs. solo el pullback VI.
Operaciones reales (R bruto) escaladas al ATR de hoy; costos por contrato en el simulador (MNQ $2.82 ida+vuelta con deslizamiento)."""
import sys, os, itertools
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fondeo"))
from prop_estrategia import examen, fondeada
ATR_HOY = 364.0
T = pd.read_csv("res_11_bloques.csv", parse_dates=["fecha"])
ORDEN = {"C pre-FOMC": 0, "B noche 00:30": 1, "B noche 05:30": 2, "A pullback VI": 3}
T = T[T.bloque.isin(ORDEN)].copy(); T["o"] = T.bloque.map(ORDEN)
DIAS = pd.DatetimeIndex(sorted(pd.read_parquet("/home/user/data/tramos_NQ.parquet").index))

def lib(bloques, desde, hasta):
    X = T[T.bloque.isin(bloques)].sort_values(["fecha", "o"])
    X["rs"] = X.riesgo_atr * ATR_HOY; X["rr"] = X.R_bruto * X.rs
    dias = DIAS[(DIAS >= desde) & (DIAS <= hasta)]
    g = dict(tuple(X.groupby("fecha")))
    ini = np.zeros(len(dias) + 1, np.int64); rs, rr = [], []
    for i, d in enumerate(dias):
        if d in g: rs += g[d].rs.tolist(); rr += g[d].rr.tolist()
        ini[i + 1] = len(rs)
    return ini, np.array(rs), np.array(rr)

CARTERAS = {"solo A (pullback)": ["A pullback VI"], "A + B (noche)": ["A pullback VI", "B noche 00:30", "B noche 05:30"],
            "A + B + C (FOMC)": list(ORDEN)}
filas = []
for nom, bl in CARTERAS.items():
    libs = {"2011-20": lib(bl, "2010-11-01", "2020-12-31"), "2021-26": lib(bl, "2021-01-01", "2026-03-13")}
    for Rusd, K in itertools.product([150, 250, 400, 600], [2, 4]):
        f = dict(cartera=nom, Rusd=Rusd, K=K)
        for esc, (ini, rs, rr) in libs.items():
            ok, d = examen(ini, rs, rr, 3000, 3000., 2000., 0., 0.4, 3, float(Rusd) * 2.0, K, 1e9, 1e9, 40, 60, 5)
            cob, nr, vv = fondeada(ini, rs, rr, 3000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
            f.update({f"{esc}_aprueba": ok.mean(), f"{esc}_dias": np.median(d[ok]) if ok.any() else np.nan, f"{esc}_cobra": (nr > 0).mean(),
                      f"{esc}_cobrado": cob.mean(), f"{esc}_neto_ex": ok.mean() * cob.mean() - 99.0})
        filas.append(f)
    print(nom, flush=True)
X = pd.DataFrame(filas); X["min_neto"] = X[["2011-20_neto_ex", "2021-26_neto_ex"]].min(axis=1)
X.to_csv("res_12_fondeo_cartera.csv", index=False)
pd.set_option("display.width", 260)
print(X.sort_values("min_neto", ascending=False).groupby("cartera").head(3).round(2).to_string(index=False))
