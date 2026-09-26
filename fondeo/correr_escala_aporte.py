"""18 meses con aporte mensual para cuotas (~\$1,400/mes), reinversión y 1-3 firmas tipo Tradeify (Growth + Select 50K cada una).
Estrategia: momentum de apertura (dirección de los primeros 15 min), horarios distintos por cuenta."""
import numpy as np, pandas as pd, os
from escala import escala, params
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"conservador (2011-20)": np.load("/home/user/data/dias_rth_2011_2020.npy"), "reciente (2021-26)": np.load("/home/user/data/dias_rth.npy")}
def plan(n_firmas):
    g = params("growth"); s = params("select")
    g[20:26] = [252., 112., 163., 2., 450., -1.]          # Growth fondeada (momentum)
    s[20:25] = [150., 60., 120., 1., 1e9]                 # Select Flex fondeada (momentum, la mejor)
    return np.stack([g, s] * n_firmas)
H = 378; filas = []
for esc, D in LIB.items():
    for nf in [1, 2, 3]:
        P = plan(nf)
        TV = np.tile(np.array([16, 46, 76, 106, 151], float), (P.shape[0], 1))
        for mx in [2, 5]:
            cf, g, c, ne, nfo, cu = escala(D, 3000, H, 1400.0, P, 4, 16, True, 5, 17, mx, TV, 1400.0)
            aportado = 1400.0 * (1 + (H - 1) // 21)
            neto = c - g
            filas.append(dict(escenario=esc, firmas=nf, cupos=5 * 2 * nf, examenes_paralelo=mx, aportado=aportado, cuotas_gastadas=g.mean(),
                              examenes=ne.mean(), fondeadas=nfo.mean(), cobrado=c.mean(), neto_media=neto.mean(), neto_mediana=np.median(neto),
                              p10=np.quantile(neto, .1), p25=np.quantile(neto, .25), p75=np.quantile(neto, .75), p90=np.quantile(neto, .9),
                              p_ganar=(neto > 0).mean(), roi_medio=neto.mean() / g.mean()))
            print(filas[-1]["escenario"], nf, mx, round(neto.mean()), flush=True)
T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "escala_aporte_18m.csv"), index=False)
pd.set_option("display.width", 250)
print(T.round({"aportado": 0, "cuotas_gastadas": 0, "examenes": 0, "fondeadas": 0, "cobrado": 0, "neto_media": 0, "neto_mediana": 0, "p10": 0, "p25": 0, "p75": 0, "p90": 0, "p_ganar": 3, "roi_medio": 2}).to_string(index=False))
