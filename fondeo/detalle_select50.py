"""Estadísticas operativas de la política elegida: Select 50K (examen) -> Select Flex 50K (fondeada)."""
import numpy as np, pandas as pd, json, os
from motor_fondeo import sim_dia, examen, actualizar_piso
from reglas_tradeify import FONDEADA, EXAMEN
out = {}
for esc, f in [("opt", "/home/user/data/dias_rth.npy"), ("cons", "/home/user/data/dias_rth_2011_2020.npy")]:
    D = np.load(f); rng = np.random.default_rng(1); np.random.seed(1)
    # --- día típico de la fondeada: 1 trade, 1 MNQ, stop 60, objetivo 180
    pn = np.array([sim_dia(D, rng.integers(len(D)), 150., 60., 180., 1, 600., 1e9, 1e9, 0., 40)[0] for _ in range(40000)])
    # --- día típico del examen: 2 MNQ, stop 60, objetivo 240
    pe = np.array([sim_dia(D, rng.integers(len(D)), 300., 60., 240., 1, 960., 1e9, 1e9, 0., 40)[0] for _ in range(40000)])
    # --- trayectoria fondeada detallada (python, reglas Flex)
    r = FONDEADA["select_flex"][50]
    t_first, pays, lifes, amounts = [], [], [], []
    for i in range(6000):
        p = 0.; mx = 0.; piso = -2000.; buenos = 0; first = None; tot = 0.; k = 0
        for dia in range(250):
            x = sim_dia(D, rng.integers(len(D)), 150., 60., 180., 1, 600., 1e9, p - piso, 0., 40)[0]
            p += x
            if p <= piso or p - piso < 123: break
            if x >= 150: buenos += 1
            mx = max(mx, p); piso = actualizar_piso(mx, 2000.)
            if buenos >= 5 and p > 0:
                m = min(2500., 0.5 * p)
                if m >= 250:
                    p -= m; tot += 0.9 * m; k += 1; buenos = 0; amounts.append(0.9 * m)
                    if first is None: first = dia + 1
        t_first.append(first if first else np.nan); pays.append(k); lifes.append(dia + 1)
    t_first = np.array(t_first, float)
    out[esc] = dict(
        fondeada_wr_dia=float((pn > 0).mean()), fondeada_dia_ganador=float(pn[pn > 0].mean()), fondeada_dia_perdedor=float(pn[pn <= 0].mean()),
        fondeada_dias_buenos=float((pn >= 150).mean()), fondeada_exp_dia=float(pn.mean()),
        examen_wr_dia=float((pe > 0).mean()), examen_dia_ganador=float(pe[pe > 0].mean()), examen_dia_perdedor=float(pe[pe <= 0].mean()),
        dias_a_primer_retiro_mediana=float(np.nanmedian(t_first)), p_primer_retiro=float(np.isfinite(t_first).mean()),
        retiro_medio_neto=float(np.mean(amounts)), retiros_media=float(np.mean(pays)), vida_media_dias=float(np.mean(lifes)),
        dist_retiros={int(k): float(v) for k, v in pd.Series(pays).value_counts(normalize=True).sort_index().items()})
    print(esc, json.dumps(out[esc], indent=1))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "resultados", "detalle_select50.json"), "w"))
