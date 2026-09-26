"""Deriva pre-FOMC como operación concreta (NQ, ES, YM): largo al abrir Globex 18:00 la víspera, salida a las 08:30 / 09:30 / 14:00
(el comunicado es a las 14:00). Stop protector k·ATR. R con costo de hoy. Condición por VIX (según literatura, más fuerte con VIX alto)."""
import numpy as np, pandas as pd, importlib
from base import periodo, COSTO_PTS
from calendario import FOMC
from externos import externos
B = importlib.import_module("11_bloques")
ATR_HOY = {"NQ": 364.0, "ES": 71.0, "YM": 536.0}
filas = []
for s in ["NQ", "ES", "YM"]:
    for fin, fn in [(510, "08:30"), (570, "09:30"), (840, "14:00")]:
        for k in [0.3, 0.5]:
            D = B.ventana(s, -360, fin, k, set(FOMC)); D["fecha"] = pd.to_datetime(D.fecha)
            D["R"] = D.R_bruto - COSTO_PTS[s] / (k * ATR_HOY[s]); D["P"] = periodo(pd.DatetimeIndex(D.fecha))
            X = externos(pd.DatetimeIndex(D.fecha)); D["vix"] = X.VIX.to_numpy()
            fila = dict(sym=s, salida=fn, stop_atr=k)
            for p in ["DEV", "VAL1", "VAL2"]:
                z = D[D.P == p].R; fila[p] = z.mean(); fila[p + "_WR"] = (z > 0).mean(); fila[p + "_n"] = len(z)
            fila["todo_t"] = D.R.mean() / D.R.std() * np.sqrt(len(D))
            med = D.vix.median(); fila["VIX alto"] = D[D.vix > med].R.mean(); fila["VIX bajo"] = D[D.vix <= med].R.mean()
            yrs = D.groupby(pd.DatetimeIndex(D.fecha).year).R.sum(); fila["años+"] = f"{(yrs > 0).sum()}/{len(yrs)}"
            filas.append(fila)
X = pd.DataFrame(filas); X.to_csv("res_17_pre_fomc.csv", index=False)
pd.set_option("display.width", 250); print(X.round(3).to_string(index=False))
