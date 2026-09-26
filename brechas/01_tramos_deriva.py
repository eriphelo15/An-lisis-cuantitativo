"""¿Dónde está la deriva? Rendimiento medio por tramo horario, NQ/ES/YM, por periodo. Y el tramo nocturno operable en fondeo."""
import numpy as np, pandas as pd
from base import tramos, periodo, COSTO_PTS, SYMS

SEG = [("cerrado 17-18h (+finde)", "prev_t1659", "t18"), ("18-20h", "t18", "t20"), ("20-00h", "t20", "t00"),
       ("00-03h", "t00", "t03"), ("03-08:30 Europa", "t03", "t0830"), ("08:30-09:30 pre", "t0830", "t0930"),
       ("09:30-10", "t0930", "t10"), ("10-12", "t10", "t12"), ("12-14", "t12", "t14"), ("14-15:30", "t14", "t1530"),
       ("15:30-15:50", "t1530", "t1550"), ("15:50-16", "t1550", "t16"), ("16-17 post", "t16", "t1659"),
       ("NOCHE OPERABLE 18:00->09:30", "t18", "t0930"), ("NOCHE 00:00->09:30", "t00", "t0930"),
       ("RTH 09:30->16:00", "t0930", "t16")]
filas = []
for s in SYMS:
    T = tramos(s).copy()
    T["prev_t1659"] = T.t1659.shift()
    T["P"] = periodo(T.index)
    ref = T.ref
    costo_hoy_bp = COSTO_PTS[s] / ref.iloc[-60:].mean() * 1e4
    for nom, a, b in SEG:
        r = (T[b] - T[a]) / ref * 1e4
        for p in ["DEV", "VAL1", "VAL2", "TODO"]:
            x = r[(T.P == p) if p != "TODO" else T.P != ""].dropna()
            filas.append(dict(sym=s, tramo=nom, per=p, n=len(x), media_bp=x.mean(), t=x.mean() / x.std() * np.sqrt(len(x)),
                              pos=(x > 0).mean(), neto_bp=x.mean() - costo_hoy_bp))
R = pd.DataFrame(filas)
pd.set_option("display.width", 250)
tab = R.pivot_table(index=["sym", "tramo"], columns="per", values=["media_bp", "t"], sort=False).round(2)
print(tab.to_string())
R.to_csv("res_01_tramos.csv", index=False)
