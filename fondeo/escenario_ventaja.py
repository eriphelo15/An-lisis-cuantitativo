"""¿Cómo se vería el fondeo con una VENTAJA REAL de distintos tamaños?
Estrategias sintéticas con winrate p y relación ganancia/pérdida b (en múltiplos del riesgo), ~2 trades/día,
stop típico de NQ a precio de hoy (distribución real de riesgos del pullback VI). Costos reales de MNQ/NQ.
Se optimiza el tamaño para cada perfil y se mide examen Select 50K + fondeada Select Flex (3 años)."""
import numpy as np, pandas as pd, itertools, os
from prop_estrategia import biblioteca, examen, fondeada
RES = os.path.join(os.path.dirname(__file__), "resultados")
ini_r, rs_r, _ = biblioteca("2021-01-01", "2026-03-13", 0, 2.0)       # riesgos reales por trade (pts, precio de hoy)
rng = np.random.default_rng(11)
def sintetica(p, b):
    gana = rng.random(len(rs_r)) < p
    rr = np.where(gana, b * rs_r, -rs_r)
    return ini_r, rs_r, rr
PERFILES = [("Sin ventaja: 50% a 1:1", 0.50, 1.0), ("Ventaja pequeña: 55% a 1:1", 0.55, 1.0), ("Ventaja media: 60% a 1:1", 0.60, 1.0),
            ("Ventaja fuerte: 65% a 1:1", 0.65, 1.0), ("WR alto: 75% a 0.5:1 (sin ventaja)", 0.667, 0.5), ("WR alto con ventaja: 75% a 0.6:1", 0.75, 0.6),
            ("WR muy alto con ventaja: 85% a 0.3:1", 0.85, 0.3), ("Nuestro pullback VI real (~36% a 2:1)", None, None)]
filas = []
for nom, p, b in PERFILES:
    lib = biblioteca("2021-01-01", "2026-03-13", 0, 2.0) if p is None else sintetica(p, b)
    ini, rs, rr = lib
    exp_R = np.mean(rr / rs)
    mejor = None
    for Rusd, K in itertools.product([100, 150, 250, 400, 600, 900], [1, 2, 3]):
        ok, d = examen(ini, rs, rr, 3000, 3000., 2000., 0., 0.4, 3, float(Rusd) * 2.0, K, 1e9, 1e9, 40, 60, 5)
        cob, nr, vv = fondeada(ini, rs, rr, 3000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
        neto_ex = ok.mean() * cob.mean() - 99.0
        f = dict(perfil=nom, exp_R_bruto=exp_R, Rusd=Rusd, K=K, aprueba=ok.mean(), dias_aprobar=np.median(d[ok]) if ok.any() else np.nan,
                 ev_fondeada=cob.mean(), cobra=(nr > 0).mean(), retiros=nr.mean(), vida=vv.mean(), neto_por_examen=neto_ex,
                 neto_18m_16ex_mes=neto_ex * 16 * 18)
        if mejor is None or neto_ex > mejor["neto_por_examen"]: mejor = f
    filas.append(mejor); print(nom, round(mejor["neto_por_examen"]), flush=True)
T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "escenario_ventaja.csv"), index=False)
pd.set_option("display.width", 250); print(T.round(3).to_string(index=False))
