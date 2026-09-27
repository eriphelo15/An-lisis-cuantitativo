"""¿El régimen de VIX (nivel, estructura temporal, cambios) predice la dirección de tramos del día siguiente?
Cuantiles fijados en DEV, aplicados a VAL1/VAL2."""
import numpy as np, pandas as pd
from base import tramos, periodo, SYMS
from externos import externos
TR = {"noche 18→09:30": ("t18", "t0930"), "RTH": ("t0930", "t16"), "18→16": ("t18", "t16"), "09:30→10": ("t0930", "t10"), "10→16": ("t10", "t16")}
VARS = ["VIX", "ratio_9d", "ratio_3m", "dvix", "vix_pct252", "vix_z20", "VVIX", "d10y", "d2y", "dusd"]
filas = []
for s in SYMS:
    T = tramos(s); X = externos(T.index); P = periodo(T.index)
    for v in VARS:
        q = np.nanquantile(X[v][P == "DEV"], [0.2, 0.8])
        grp = np.where(X[v] <= q[0], "bajo", np.where(X[v] >= q[1], "alto", "medio"))
        grp[X[v].isna().to_numpy()] = "na"
        for tn, (a, b) in TR.items():
            r = ((T[b] - T[a]) / T.ref * 1e4).to_numpy()
            for g in ["bajo", "alto"]:
                fila = dict(sym=s, var=v, grupo=g, tramo=tn)
                for p in ["DEV", "VAL1", "VAL2"]:
                    x = r[(grp == g) & (P == p)]; x = x[~np.isnan(x)]
                    fila[p] = x.mean(); fila[p + "_t"] = x.mean() / x.std() * np.sqrt(len(x)); fila[p + "_n"] = len(x)
                filas.append(fila)
R = pd.DataFrame(filas); R.to_csv("res_04_vix.csv", index=False)
R["min_t"] = R[["DEV_t", "VAL1_t", "VAL2_t"]].min(axis=1); R["max_t"] = R[["DEV_t", "VAL1_t", "VAL2_t"]].max(axis=1)
pd.set_option("display.width", 250); c = ["sym", "var", "grupo", "tramo", "DEV", "VAL1", "VAL2", "DEV_t", "VAL1_t", "VAL2_t", "VAL2_n"]
print("alcistas consistentes"); print(R[R.min_t > 1.3].sort_values("min_t", ascending=False)[c].round(1).head(30).to_string())
print("bajistas consistentes"); print(R[R.max_t < -1.0].sort_values("max_t")[c].round(1).head(20).to_string())
