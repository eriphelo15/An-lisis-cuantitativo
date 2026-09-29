"""Variante con las reglas reales del usuario (29-sep-2026): ruptura de la vela de 1 min de las 9:30, solo cortos,
UN SOLO intento por acción (si le saca el cierre sobre la apertura de las 9:30, no vuelve a entrar), entrada hasta 11:00,
todo cerrado a las 11:30. 1R = entrada → apertura 9:30 (mín. 2 %). Coste 0.5 % del precio. Exploratorio."""
import os, sys
import numpy as np
import pandas as pd

D = "/home/user/data/smallcaps"


def uno(x, fin="11:30", coste=0.005):
    x = x.between_time("09:30", "15:59")
    if len(x) < 10 or x.index[0].strftime("%H:%M") != "09:30":
        return None
    o, l = x.open.iloc[0], x.low.iloc[0]
    t = x.index.strftime("%H:%M"); c = x.close.to_numpy()
    for i in range(1, len(x)):
        if t[i] > "11:00":
            return dict(R=np.nan, entrada=None, salida=None)
        if c[i] < l:
            e, te = c[i], t[i]
            r = max((o - e) / e, 0.02)
            for j in range(i + 1, len(x)):
                if c[j] > o:
                    return dict(R=((e - c[j]) / e - coste) / r, entrada=f"{te} {e:.4f}", salida=f"{t[j]} {c[j]:.4f} (stop)")
                if t[j] >= fin:
                    return dict(R=((e - c[j]) / e - coste) / r, entrada=f"{te} {e:.4f}", salida=f"{t[j]} {c[j]:.4f} (hora)")
            return None
    return None


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), R=round(v.mean(), 2), mediana=round(v.median(), 2), WR=round((v > 0).mean(), 2), gan=round(g.mean(), 2),
                perd=round(p.mean(), 2), PF=round(g.sum() / -p.sum(), 2) if p.sum() < 0 else np.nan,
                sin_3_mejores=round(v.sort_values().iloc[:-3].mean(), 2) if len(v) > 5 else np.nan)


if __name__ == "__main__":
    E = pd.read_parquet(f"{D}/eventos_recientes.parquet"); E["date"] = pd.to_datetime(E.date)
    filas = []
    for sub, desde in [("m1", "2026-08-31"), ("m5", "2026-07-01")]:
        for _, e in E[(E.date >= desde) & (E.open >= 1) & (E.gap >= 0.2)].iterrows():
            f = f"{D}/{sub}/{e.sym}.parquet"
            if not os.path.exists(f):
                continue
            x = pd.read_parquet(f); x.columns = [c.lower() for c in x.columns]
            r = uno(x[x.index.date == e.date.date()])
            if r and r["entrada"]:
                filas.append(dict(datos=sub, sym=e.sym, fecha=e.date.date(), tramo="≥ 50 %" if e.gap >= .5 else "20-50 %", **r))
    X = pd.DataFrame(filas); X.to_csv("res_23b_usuario.csv", index=False)
    for (sub, tr), W in X.groupby(["datos", "tramo"]):
        print(sub, tr, met(W.R))
