"""Políticas de la fondeada pensadas para ESCALA (3 firmas x Growth+Select 50K, \$1,400/mes, 18 meses, reinversión).
Métrica principal: beneficio neto (cobrado - cuotas). Momentum de apertura, horarios distintos por cuenta."""
import numpy as np, pandas as pd, os, itertools, time
from escala import escala, params
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
SEL = {"S1 conservadora (R150 S60 T120 K1)": [150., 60., 120., 1., 1e9],
       "S2 media (R300 S60 T120 K1)": [300., 60., 120., 1., 1e9],
       "S3 media+ (R400 S60 T180 K2)": [400., 60., 180., 2., 1e9],
       "S4 agresiva (R500 S38 T148 K8 G150)": [500., 37.5, 147.5, 8., 150.],
       "S5 muy agresiva (R1000 S46 T98 K2 G150)": [1000., 45.75, 97.75, 2., 150.]}
RET = {"retiro en cuanto se pueda": -1., "esperar a retirar >= $1,000": 1000., "ir por el máximo ($2,500)": 2500.}
GRO = {"G1 (R252 S112 T163 K2 G450)": [252., 112., 163., 2., 450., -1.], "G2 agresiva (R868 S80 T112 K3 G450)": [868., 80.5, 112.5, 3., 450., -1.],
       "G1 + colchón 2500": [252., 112., 163., 2., 450., 2500.]}
TV = np.tile(np.array([16, 46, 76, 106, 151], float), (6, 1))
filas = []; t0 = time.time()
for (sn, sp), (rn, rv), (gn, gp) in itertools.product(SEL.items(), RET.items(), GRO.items()):
    if gn == "G1 + colchón 2500" and not (sn.startswith("S1") and rn.startswith("retiro")):
        continue
    g = params("growth"); s = params("select"); g[20:26] = gp; s[20:25] = sp; s[25] = rv
    P = np.stack([g, s] * 3)
    f = dict(select=sn, retiro=rn, growth=gn)
    for esc, D in LIB.items():
        cf, gas, cob, ne, nfo, cu = escala(D, 1500, 378, 1400.0, P, 4, 16, True, 5, 31, 5, TV, 1400.0)
        neto = cob - gas
        f.update({f"{esc}_neto": neto.mean(), f"{esc}_mediana": np.median(neto), f"{esc}_p10": np.quantile(neto, .1),
                  f"{esc}_p_ganar": (neto > 0).mean(), f"{esc}_cuotas": gas.mean(), f"{esc}_fondeadas": nfo.mean(), f"{esc}_cobrado": cob.mean()})
    filas.append(f); print(len(filas), sn[:3], rn[:10], gn[:3], round(f["cons_neto"]), round(f["opt_neto"]), f"{time.time()-t0:.0f}s", flush=True)
X = pd.DataFrame(filas); X["min_neto"] = X[["cons_neto", "opt_neto"]].min(axis=1)
X.to_csv(os.path.join(RES, "escala_politicas.csv"), index=False)
pd.set_option("display.width", 260)
print(X.sort_values("min_neto", ascending=False).round(0).to_string(index=False))
