"""Optimiza tamaño y paradas usando los trades reales de la estrategia pullback VI (NQ) en Tradeify 50K."""
import numpy as np, pandas as pd, itertools, os, time
from prop_estrategia import biblioteca, examen, fondeada
RES = os.path.join(os.path.dirname(__file__), "resultados")
t0 = time.time(); filas = []
for Robj in [2.0, 3.0]:
    libs = {"cons": biblioteca("2010-10-01", "2020-12-31", 0, Robj), "opt": biblioteca("2021-01-01", "2026-03-13", 0, Robj)}
    for esc, (ini, rs, rr) in libs.items():
        print(Robj, esc, "trades/día", round(len(rs) / (len(ini) - 1), 2), flush=True)
    # examen
    for plan, (target, dll, cons, mind) in {"growth": (3000., 1250., 0., 1), "select": (3000., 0., 0.4, 3)}.items():
        for Rusd, K, G in itertools.product([150, 250, 400, 600, 900, 1250], [1, 2, 3, 5], [300, 600, 1200, 1e9]):
            f = dict(fase="examen", plan=plan, Robj=Robj, Rusd=Rusd, K=K, G=G)
            for esc, (ini, rs, rr) in libs.items():
                ok, d = examen(ini, rs, rr, 3000, target, 2000., dll, cons, mind, float(Rusd), K, float(G), 1e9, 40, 60, 5)
                f[f"{esc}_p"] = ok.mean(); f[f"{esc}_dias"] = np.median(d[ok]) if ok.any() else np.nan
            filas.append(f)
    # fondeada
    for tipo, nombre in [(0, "growth"), (1, "select_flex")]:
        for Rusd, K, G, col in itertools.product([100, 150, 250, 400, 600, 900], [1, 2, 3, 5], [300, 600, 1200, 1e9], [-1, 2500] if tipo == 0 else [-1]):
            f = dict(fase="fondeada", plan=nombre, Robj=Robj, Rusd=Rusd, K=K, G=G, colchon=col)
            for esc, (ini, rs, rr) in libs.items():
                if tipo == 0:
                    cob, nr, vv = fondeada(ini, rs, rr, 2000, 0, 2000., 1250., 150., 3000., 0.35, 500., 1500., 3000., 0., float(col), float(Rusd), K, float(G), 1e9, 40, 250, 9)
                else:
                    cob, nr, vv = fondeada(ini, rs, rr, 2000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, float(G), 1e9, 40, 250, 9)
                f[f"{esc}_ev"] = cob.mean(); f[f"{esc}_pcobra"] = (nr > 0).mean(); f[f"{esc}_dias"] = vv.mean(); f[f"{esc}_nret"] = nr.mean()
            filas.append(f)
X = pd.DataFrame(filas); X.to_csv(os.path.join(RES, "prop_estrategia_grid.csv"), index=False)
print(f"{time.time()-t0:.0f}s")
pd.set_option("display.width", 250)
E = X[X.fase == "examen"].copy(); E["min_p"] = E[["cons_p", "opt_p"]].min(axis=1)
print(E.sort_values("min_p", ascending=False).groupby("plan").head(3)[["plan", "Robj", "Rusd", "K", "G", "cons_p", "opt_p", "cons_dias", "opt_dias"]].round(3).to_string(index=False))
Fd = X[X.fase == "fondeada"].copy(); Fd["min_ev"] = Fd[["cons_ev", "opt_ev"]].min(axis=1)
print(Fd.sort_values("min_ev", ascending=False).groupby("plan").head(4)[["plan", "Robj", "Rusd", "K", "G", "colchon", "cons_ev", "opt_ev", "cons_pcobra", "opt_pcobra", "cons_dias", "opt_dias", "cons_nret"]].round(2).to_string(index=False))
