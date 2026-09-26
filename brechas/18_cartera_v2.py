"""Cartera v2 en fondeo: A (pullback VI) + F (pre-FOMC 18:00->08:30, stop 0.5 ATR, NQ) [+ B experimental]."""
import sys, os, importlib, itertools
import numpy as np, pandas as pd
from calendario import FOMC
from base import periodo
B11 = importlib.import_module("11_bloques")
T = pd.read_csv("res_11_bloques.csv", parse_dates=["fecha"])
F = B11.ventana("NQ", -360, 510, 0.5, set(FOMC)); F["fecha"] = pd.to_datetime(F.fecha); F["bloque"] = "F pre-FOMC noche"
T = pd.concat([T[T.bloque != "C pre-FOMC"], F], ignore_index=True)
T.to_csv("res_18_bloques_v2.csv", index=False)
sys.path.insert(0, os.path.join("..", "fondeo"))
M = importlib.import_module("12_fondeo_cartera")
M.T = T.assign(o=T.bloque.map({"F pre-FOMC noche": 0, "B noche 00:30": 1, "B noche 05:30": 2, "A pullback VI": 3})).dropna(subset=["o"])
CART = {"A": ["A pullback VI"], "A + F": ["A pullback VI", "F pre-FOMC noche"],
        "A + F + B": ["A pullback VI", "F pre-FOMC noche", "B noche 00:30", "B noche 05:30"]}
filas = []
for nom, bl in CART.items():
    libs = {"2011-20": M.lib(bl, "2010-11-01", "2020-12-31"), "2021-26": M.lib(bl, "2021-01-01", "2026-03-13")}
    for Rusd, K in itertools.product([150, 250, 400], [2, 4]):
        f = dict(cartera=nom, Rusd=Rusd, K=K)
        for esc, (ini, rs, rr) in libs.items():
            ok, d = M.examen(ini, rs, rr, 3000, 3000., 2000., 0., 0.4, 3, float(Rusd) * 2.0, K, 1e9, 1e9, 40, 60, 5)
            cob, nr, vv = M.fondeada(ini, rs, rr, 3000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
            f.update({f"{esc}_aprueba": ok.mean(), f"{esc}_cobra": (nr > 0).mean(), f"{esc}_neto_ex": ok.mean() * cob.mean() - 99.0})
        filas.append(f)
X = pd.DataFrame(filas); X["min_neto"] = X[["2011-20_neto_ex", "2021-26_neto_ex"]].min(axis=1)
X.to_csv("res_18_fondeo_v2.csv", index=False)
pd.set_option("display.width", 250); print(X.sort_values("min_neto", ascending=False).groupby("cartera").head(2).round(2).to_string(index=False))
