import numpy as np, pandas as pd, itertools, os
from opt_growth_colchon import f_run, e_run, tasa, LIB, RES
pd.set_option("display.width", 220)
rows = []
pols = {"equilibrada (R250 S60 T180 K2)": (250, 60, 3, 2, 600), "rápida (R600 S60 T120 K2)": (600, 60, 2, 2, 300), "lenta (R400 S90 T180 K1)": (400, 90, 2, 1, 600)}
for esc, D in LIB.items():
    for mode, tini, lab in [(0, 1, "aleatoria 09:31"), (1, 1, "solo largos 09:31"), (2, 16, "momentum 15 min (09:46)"), (3, 16, "fade 15 min (09:46)"), (2, 31, "momentum 30 min (10:01)"), (3, 31, "fade 30 min (10:01)")]:
        p_ap, dmed = e_run(D, mode, tini)
        for pn, (R, S, rr, K, G) in pols.items():
            for col in [-1, 0, 1000, 2500, 3500]:
                cob, nret, viv, qb = f_run(D, R, S, rr, K, G, col, mode, tini, ns=6000, seed=91)
                net, ta = tasa(cob, viv, p_ap)
                rows.append(dict(escenario=esc, entrada=lab, politica=pn, colchon=col, p_aprobar=p_ap, ev_fondeada=cob.mean(), p_cobra=(nret > 0).mean(),
                                 n_ret=nret.mean(), dias=viv.mean(), neto_cupo=net, neto_cupo_año=ta))
X = pd.DataFrame(rows); X.to_csv(os.path.join(RES, "growth50_colchon_modos.csv"), index=False)
print("== Efecto del colchón (entrada aleatoria) ==")
print(X[X.entrada == "aleatoria 09:31"].pivot_table(index=["politica", "colchon"], columns="escenario", values=["ev_fondeada", "p_cobra", "neto_cupo_año"]).round(2).to_string())
print("\n== Reglas de entrada (política equilibrada, colchón 2500) ==")
Y = X[(X.politica.str.startswith("equilibrada")) & (X.colchon == 2500)]
print(Y.pivot_table(index="entrada", columns="escenario", values=["p_aprobar", "ev_fondeada", "neto_cupo"]).round(3).to_string())
