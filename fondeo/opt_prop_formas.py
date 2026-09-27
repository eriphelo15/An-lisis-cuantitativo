"""Fondeo Tradeify 50K con la entrada pullback VI y distintas formas de salida (incl. salida parcial de winrate alto)."""
import os, sys, importlib, itertools
import numpy as np, pandas as pd
from prop_estrategia import examen, fondeada
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "estudio_nq"))
RES = os.path.join(os.path.dirname(__file__), "resultados")
cwd = os.getcwd(); os.chdir(os.path.join(os.path.dirname(__file__), "..", "estudio_nq"))
vi = importlib.import_module("22_vi_usuario"); fm = importlib.import_module("25_pullback_formas")
A, E20, E50, F, atr = vi.dias_con_ema("NQ"); os.chdir(cwd)
atr_hoy = np.nanmean(atr[-60:])
def lib(desde, hasta, R1, par, R2, be):
    R = pd.DataFrame(np.array(fm.correr(A, E20, E50, atr, 120, R1, par, R2, be, 0.25)), columns=["di", "res", "rk", "fase"])
    esc = atr_hoy / atr[R.di.astype(int)]; R["rs"] = R.rk * esc; R["rr"] = R.res * esc
    dias = np.flatnonzero((F >= pd.Timestamp(desde)) & (F <= pd.Timestamp(hasta)) & ~np.isnan(atr))
    R = R[R.di.isin(dias)]; g = dict(tuple(R.groupby("di")))
    ini = np.zeros(len(dias) + 1, np.int64); rs, rr = [], []
    for i, d in enumerate(dias):
        if d in g: rs += g[d].rs.tolist(); rr += g[d].rr.tolist()
        ini[i + 1] = len(rs)
    return ini, np.array(rs), np.array(rr)
FORMAS = {"3R": (3.0, 0, 0, False), "2R": (2.0, 0, 0, False), "parcial 0.5R+BE+cierre": (0.5, 1, 0.0, True),
          "parcial 1R+BE+cierre": (1.0, 1, 0.0, True), "parcial 0.5R+BE+2R": (0.5, 1, 2.0, True)}
filas = []
for nom, f in FORMAS.items():
    libs = {"cons": lib("2010-10-01", "2020-12-31", *f), "opt": lib("2021-01-01", "2026-03-13", *f)}
    for Rusd, K in itertools.product([100, 150, 250, 400, 600], [1, 2, 3]):
        fila = dict(forma=nom, Rusd=Rusd, K=K)
        for esc, (ini, rs, rr) in libs.items():
            ok, d = examen(ini, rs, rr, 3000, 3000., 2000., 0., 0.4, 3, float(Rusd) * 2.5, K, 1e9, 1e9, 40, 60, 5)
            cob, nr, vv = fondeada(ini, rs, rr, 3000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
            fila.update({f"{esc}_aprueba": ok.mean(), f"{esc}_ev": cob.mean(), f"{esc}_cobra": (nr > 0).mean(), f"{esc}_vida": vv.mean(),
                         f"{esc}_neto_examen": ok.mean() * cob.mean() - 99.0})
        filas.append(fila)
    print(nom, flush=True)
X = pd.DataFrame(filas); X["min_neto"] = X[["cons_neto_examen", "opt_neto_examen"]].min(axis=1)
X.to_csv(os.path.join(RES, "prop_formas.csv"), index=False)
pd.set_option("display.width", 250)
print(X.sort_values("min_neto", ascending=False).groupby("forma").head(2).round(2).to_string(index=False))
