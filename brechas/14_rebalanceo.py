"""Rebalanceo de fin de mes (fondos de pensiones 60/40): si las acciones subieron mucho en el mes, venden al final (y al revés).
Señal: rendimiento del mes hasta el cierre del día -4 (percentil con cortes DEV). Objetivo: rendimiento de los 3 últimos días hábiles
(RTH y 18:00->16:00). Hipótesis con razón económica, fijada de antemano (no escaneada)."""
import numpy as np, pandas as pd
from base import tramos, periodo, SYMS
from calendario import marcas
for s in SYMS:
    T = tramos(s); C = marcas(T.index); P = periodo(T.index)
    mes = T.index.to_period("M")
    c16 = T.t16; first = T.t0930.groupby(mes).transform("first")
    fin = C.dia_mes_fin.to_numpy()
    filas = []
    for m, g in T.groupby(mes):
        idx = np.flatnonzero(mes == m)
        if len(idx) < 10: continue
        i4 = idx[fin[idx] == 4]
        if len(i4) == 0: continue
        i4 = i4[0]
        mtd = (c16.iloc[i4] - T.t0930.iloc[idx[0]]) / T.ref.iloc[i4] * 1e4
        last3 = idx[fin[idx] <= 3]
        fut = (T.t16.iloc[last3[-1]] - c16.iloc[i4]) / T.ref.iloc[i4] * 1e4
        filas.append(dict(mes=str(m), P=P[i4], mtd=mtd, fut=fut))
    D = pd.DataFrame(filas)
    q = D[D.P == "DEV"].mtd.quantile([0.25, 0.75]).to_numpy()
    D["g"] = np.where(D.mtd <= q[0], "mes muy bajista", np.where(D.mtd >= q[1], "mes muy alcista", "medio"))
    t = D.groupby(["g", "P"]).fut.agg(["mean", "count"]).unstack("P").round(1)
    print(s); print(t.to_string())
