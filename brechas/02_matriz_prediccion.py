"""Matriz de predictibilidad: ¿el rendimiento de un tramo anticipa el de un tramo posterior (mismo día)?
Métrica: media del tramo posterior (bp) firmada por la dirección del tramo previo = beneficio de 'seguir' (momentum)
(negativo = reversión). Se reporta por periodo; interesa lo que es consistente en DEV, VAL1 y VAL2 en los tres índices."""
import itertools
import numpy as np, pandas as pd
from base import tramos, periodo, SYMS

B = ["prev_t0930", "prev_t16", "t18", "t00", "t03", "t0830", "t0930", "t10", "t12", "t14", "t1530", "t1550", "t16", "t1659"]
NOM = {"prev_t0930": "RTH ayer", "prev_t16": "noche", "t18": "18h", "t00": "00h", "t03": "03h", "t0830": "08:30", "t0930": "09:30",
       "t10": "10:00", "t12": "12:00", "t14": "14:00", "t1530": "15:30", "t1550": "15:50", "t16": "16:00", "t1659": "16:59"}
filas = []
for s in SYMS:
    T = tramos(s).copy()
    T["prev_t0930"] = T.t0930.shift(); T["prev_t16"] = T.t16.shift()
    T["P"] = periodo(T.index)
    # tramos candidatos: pares consecutivos de cortes y ventanas acumuladas
    pts = ["prev_t0930", "prev_t16", "t0930", "t10", "t12", "t14", "t1530", "t1550", "t16", "t1659"]
    ventanas = [(a, b) for a, b in itertools.combinations(pts, 2)]
    ret = {w: (T[w[1]] - T[w[0]]) / T.ref * 1e4 for w in ventanas}
    for (a, b), (c, d) in itertools.product(ventanas, ventanas):
        if pts.index(c) < pts.index(b):   # el objetivo debe empezar cuando termina la señal (o después)
            continue
        if pts.index(c) != pts.index(b):  # sólo objetivos que empiezan justo al acabar la señal
            continue
        x, y = ret[(a, b)], ret[(c, d)]
        f = np.sign(x) * y
        fila = dict(sym=s, señal=f"{NOM[a]}→{NOM[b]}", objetivo=f"{NOM[c]}→{NOM[d]}")
        for p in ["DEV", "VAL1", "VAL2"]:
            z = f[T.P == p].dropna()
            fila[p] = z.mean(); fila[p + "_t"] = z.mean() / z.std() * np.sqrt(len(z))
        filas.append(fila)
R = pd.DataFrame(filas)
R.to_csv("res_02_matriz.csv", index=False)
# consistentes: mismo signo en los 3 periodos y los 3 índices, |t| DEV > 2
g = R.groupby(["señal", "objetivo"])
res = g.agg(DEV=("DEV", "mean"), VAL1=("VAL1", "mean"), VAL2=("VAL2", "mean"),
            tDEV=("DEV_t", "min"), tV1=("VAL1_t", "min"), tV2=("VAL2_t", "min"),
            tDEVmax=("DEV_t", "max"), tV1max=("VAL1_t", "max"), tV2max=("VAL2_t", "max")).reset_index()
pos = (res.tDEV > 1.5) & (res.tV1 > 0.5) & (res.tV2 > 0.5)
neg = (res.tDEVmax < -1.5) & (res.tV1max < -0.5) & (res.tV2max < -0.5)
pd.set_option("display.width", 250)
print("MOMENTUM consistente (los 3 índices, 3 periodos):"); print(res[pos].round(2).sort_values("VAL2", ascending=False).to_string())
print("REVERSIÓN consistente:"); print(res[neg].round(2).sort_values("VAL2").to_string())
print("pares evaluados:", len(res))
