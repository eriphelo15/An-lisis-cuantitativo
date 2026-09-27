"""Efectos de calendario sobre tramos del día (NQ/ES/YM, por periodo). Referencia = resto de días."""
import numpy as np, pandas as pd
from base import tramos, periodo, SYMS, COSTO_PTS
from calendario import marcas

TR = {"noche 18→09:30": ("t18", "t0930"), "09:30→14:00": ("t0930", "t14"), "14:00→16:00": ("t14", "t16"),
      "RTH": ("t0930", "t16"), "día completo 18→16:59": ("t18", "t1659"), "00→16": ("t00", "t16")}
filas = []
for s in SYMS:
    T = tramos(s).copy(); C = marcas(T.index); P = periodo(T.index)
    EV = {"FOMC": C.fomc, "pre-FOMC": C.pre_fomc, "fin mes -2": C.tom == -2, "fin mes -1": C.tom == -1, "inicio mes +1": C.tom == 1,
          "inicio mes +2": C.tom == 2, "inicio mes +3": C.tom == 3, "OPEX": C.opex, "cuádruple": C.cuadruple, "post-OPEX": C.post_opex,
          "pre-festivo": C.pre_festivo, "lunes": C.dow == 0, "martes": C.dow == 1, "miércoles": C.dow == 2, "jueves": C.dow == 3, "viernes": C.dow == 4}
    for en, m in EV.items():
        m = np.asarray(m)
        for tn, (a, b) in TR.items():
            r = ((T[b] - T[a]) / T.ref * 1e4).to_numpy()
            fila = dict(sym=s, evento=en, tramo=tn)
            for p in ["DEV", "VAL1", "VAL2"]:
                x = r[m & (P == p)]; x = x[~np.isnan(x)]
                fila[p] = x.mean(); fila[p + "_n"] = len(x); fila[p + "_t"] = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
            filas.append(fila)
R = pd.DataFrame(filas); R.to_csv("res_03_calendario.csv", index=False)
R["min_t"] = R[["DEV_t", "VAL1_t", "VAL2_t"]].min(axis=1); R["max_t"] = R[["DEV_t", "VAL1_t", "VAL2_t"]].max(axis=1)
pd.set_option("display.width", 250)
cols = ["sym", "evento", "tramo", "DEV", "VAL1", "VAL2", "DEV_n", "VAL2_n", "DEV_t", "VAL1_t", "VAL2_t"]
print("ALCISTAS consistentes:"); print(R[R.min_t > 1.0].sort_values("min_t", ascending=False)[cols].round(1).to_string())
print("BAJISTAS consistentes:"); print(R[R.max_t < -1.0].sort_values("max_t")[cols].round(1).to_string())
