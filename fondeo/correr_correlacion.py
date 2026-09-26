"""Copiar vs diversificar vs independiente, con las políticas robustas halladas. 16 meses, caja $1,000."""
import numpy as np, pandas as pd, os, json
from escala import escala, params
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
def P_(flex="estable"):
    g = params("growth"); s = params("select")
    # Growth fondeada robusta: S 112, T 163, R 252, K2, G 450, sin colchón extra
    g[20:26] = [252., 112., 163., 2., 450., -1.]
    if flex == "estable":   # objetivo/stop ~0.9, cobra ~76-80%
        s[20:25] = [222., 104.5, 92., 1., 450.]
    else:                   # rápida: winrate bajo, lotería
        s[20:25] = [927., 55.75, 196., 1., 150.]
    return np.stack([g, s])
H = 336; rows = []
T_copia = np.full((2, 5), 16.0)
T_div = np.array([[16, 46, 76, 106, 151], [16, 46, 76, 106, 151]], float)   # 09:46, 10:16, 10:46, 11:16, 12:01
for esc, D in LIB.items():
    for flex in ["estable", "rapida"]:
        for combo in ["select", "ambos"]:
            P = P_(flex)
            if combo == "select": P[0, 26] = 0
            for lab, comun, TV, mx in [("copiar (mismo trade)", True, T_copia, 5), ("copiar, 1 examen a la vez", True, T_copia, 1),
                                        ("diversificar horario", True, T_div, 5), ("diversificar, 2 exámenes a la vez", True, T_div, 2),
                                        ("independiente (cota)", False, T_copia, 5)]:
                cf, g, c, ne, nf, cu = escala(D, 3000, H, 1000.0, P, 4, 16, comun, 5, 11, mx, TV)
                neto = cf - 1000
                rows.append(dict(escenario=esc, flex=flex, planes=combo, modo_cartera=lab, media=neto.mean(), mediana=np.median(neto),
                                 p10=np.quantile(neto, .1), p90=np.quantile(neto, .9), p_ganar=(neto > 0).mean(), p_quiebra=(cf < 93).mean(),
                                 cuotas=g.mean(), cobrado=c.mean(), examenes=ne.mean(), fondeadas=nf.mean()))
R = pd.DataFrame(rows); R.to_csv(os.path.join(RES, "correlacion_cartera.csv"), index=False)
pd.set_option("display.width", 250)
print(R.round({"media": 0, "mediana": 0, "p10": 0, "p90": 0, "p_ganar": 3, "p_quiebra": 3, "cuotas": 0, "cobrado": 0, "examenes": 1, "fondeadas": 1}).to_string(index=False))
