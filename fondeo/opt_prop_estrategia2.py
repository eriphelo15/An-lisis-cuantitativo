"""Fondeada con la estrategia pullback VI (NQ, 3R): valor por cuenta en 3 años y por cupo-año, según tamaño.
Comparado con entradas aleatorias (misma estructura de stop/objetivo) = sin ventaja."""
import numpy as np, pandas as pd, itertools, os
from prop_estrategia import biblioteca, fondeada, examen
RES = os.path.join(os.path.dirname(__file__), "resultados")
libs = {"cons": biblioteca("2010-10-01", "2020-12-31", 0, 3.0), "opt": biblioteca("2021-01-01", "2026-03-13", 0, 3.0)}
# versión 'sin ventaja': mismos trades pero con el signo del resultado aleatorizado (misma distribución de tamaños)
rng = np.random.default_rng(0)
def sin_ventaja(ini, rs, rr):
    # voltear cada trade: resultado = -res con prob 0.5 (una apuesta simétrica con la misma forma)
    s = np.where(rng.random(len(rr)) < 0.5, 1.0, -1.0)
    # un trade volteado de un bracket asimétrico no es simétrico; usamos -res - 0 para mantener magnitudes
    return ini, rs, rr * s
filas = []
for esc, lib in libs.items():
    for modo, (ini, rs, rr) in [("estrategia", lib), ("sin ventaja", sin_ventaja(*lib))]:
        for tipo, nombre in [(1, "select_flex"), (0, "growth")]:
            for Rusd, K in itertools.product([75, 100, 150, 250, 400, 600, 900], [1, 2, 3]):
                if tipo == 1:
                    cob, nr, vv = fondeada(ini, rs, rr, 3000, 1, 2000., 0., 150., 0., 0., 250., 2500., 2500., 0.5, -1., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
                else:
                    cob, nr, vv = fondeada(ini, rs, rr, 3000, 0, 2000., 1250., 150., 3000., 0.35, 500., 1500., 3000., 0., 2500., float(Rusd), K, 1e9, 1e9, 40, 750, 21)
                filas.append(dict(esc=esc, modo=modo, plan=nombre, Rusd=Rusd, K=K, ev_3años=cob.mean(), p_cobra=(nr > 0).mean(), n_ret=nr.mean(),
                                  vida_dias=vv.mean(), ev_por_año_vida=cob.mean() / (vv.mean() / 252), p50=np.median(cob), p90=np.quantile(cob, .9)))
X = pd.DataFrame(filas); X.to_csv(os.path.join(RES, "prop_estrategia_fondeada.csv"), index=False)
pd.set_option("display.width", 250)
for plan in ["select_flex", "growth"]:
    Y = X[X.plan == plan]
    print(f"\n=== {plan}: valor por cuenta fondeada (3 años) ===")
    print(Y.pivot_table(index=["Rusd", "K"], columns=["esc", "modo"], values="ev_3años").round(0).to_string())
    print(Y.pivot_table(index=["Rusd", "K"], columns=["esc", "modo"], values="p_cobra").round(2).to_string())
    print(Y.pivot_table(index=["Rusd", "K"], columns=["esc", "modo"], values="vida_dias").round(0).to_string())
