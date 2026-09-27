import numpy as np, pandas as pd, json, os, time
from escala import escala, params
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
H = 336; rows = []; curvas = {}
for esc, D in LIB.items():
    for combo in ["growth", "select", "ambos"]:
        P = np.stack([params("growth"), params("select")])
        if combo == "growth": P[1, 26] = 0
        if combo == "select": P[0, 26] = 0
        for comun in [True, False]:
            t = time.time()
            cf, g, c, ne, nf, cu = escala(D, 2000, H, 1000.0, P, 2, 16, comun, 5, 7)
            neto = cf - 1000.0
            rows.append(dict(escenario=esc, planes=combo, dia_comun=comun, neto_media=neto.mean(), neto_mediana=np.median(neto),
                             p10=np.quantile(neto, .1), p90=np.quantile(neto, .9), p_ganar=(neto > 0).mean(), p_quiebra=(cf < 100).mean(),
                             gasto_cuotas=g.mean(), cobrado=c.mean(), examenes=ne.mean(), fondeadas=nf.mean(), seg=time.time() - t))
            curvas[f"{esc}|{combo}|{int(comun)}"] = {q: np.quantile(cu, q, axis=0)[::7].round(0).tolist() for q in [0.1, 0.5, 0.9]}
            print(rows[-1], flush=True)
R = pd.DataFrame(rows); R.to_csv(os.path.join(RES, "escala_16m.csv"), index=False)
json.dump(curvas, open(os.path.join(RES, "escala_curvas.json"), "w"))
pd.set_option("display.width", 250); print(R.round(0).to_string(index=False))
