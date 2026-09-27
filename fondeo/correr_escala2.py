import numpy as np, pandas as pd, json, os
from escala import escala, params
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
H = 336; rows = []; curvas = {}
for esc, D in LIB.items():
    for combo in ["growth", "select", "ambos"]:
        P = np.stack([params("growth"), params("select")])
        if combo == "growth": P[1, 26] = 0
        if combo == "select": P[0, 26] = 0
        for comun, mx in [(True, 1), (True, 2), (True, 5), (False, 5)]:
            cf, g, c, ne, nf, cu = escala(D, 3000, H, 1000.0, P, 2, 16, comun, 5, 7, mx)
            neto = cf - 1000.0
            rows.append(dict(escenario=esc, planes=combo, correlacion="mismo día" if comun else "independiente", examenes_paralelo=mx,
                             neto_media=neto.mean(), neto_mediana=np.median(neto), p10=np.quantile(neto, .1), p25=np.quantile(neto, .25), p75=np.quantile(neto, .75),
                             p90=np.quantile(neto, .9), p_ganar=(neto > 0).mean(), p_quiebra=(cf < 93).mean(),
                             gasto_cuotas=g.mean(), cobrado=c.mean(), examenes=ne.mean(), fondeadas=nf.mean()))
            curvas[f"{esc}|{combo}|{'comun' if comun else 'indep'}|{mx}"] = {str(q): (np.quantile(cu, q, axis=0)[::7] - 1000).round(0).tolist() for q in [0.1, 0.25, 0.5, 0.75, 0.9]}
R = pd.DataFrame(rows); R.to_csv(os.path.join(RES, "escala_16m.csv"), index=False)
json.dump(curvas, open(os.path.join(RES, "escala_curvas.json"), "w"))
pd.set_option("display.width", 250)
print(R.assign(p_ganar=R.p_ganar.round(3), p_quiebra=R.p_quiebra.round(3)).round({"neto_media": 0, "neto_mediana": 0, "p10": 0, "p25": 0, "p75": 0, "p90": 0, "gasto_cuotas": 0, "cobrado": 0, "examenes": 1, "fondeadas": 1}).to_string(index=False))
