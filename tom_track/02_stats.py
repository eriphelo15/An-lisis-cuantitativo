"""Estadísticas del canal de día de Tom (índices). R = puntos / riesgo inicial (entrada-stop) por unidad de posición."""
import numpy as np, pandas as pd
T = pd.read_csv("tom_telegram_trades.csv", parse_dates=["fecha"])
I = T[T.canal.str.startswith("Day") & T.producto.isin(["DAX", "NASDAQ", "DOW", "FTSE"])].copy()
med = I.groupby("producto").riesgo.transform("median")
malos = (I.riesgo > 4 * med) | (I.riesgo < 0.2 * med) | I.pts.isna()
print("descartadas por dato raro:", malos.sum(), "de", len(I))
I = I[~malos].copy()
# costo por lado aprox en puntos (spread/tick+comisión): equivalente futuros
COSTO = {"NASDAQ": 0.79, "DOW": 3.2, "DAX": 1.5, "FTSE": 1.0}
I["R"] = I.pts / I.riesgo
I["Rn"] = (I.pts - I.producto.map(COSTO)) / I.riesgo
I["Rw"] = I.conv / I.riesgo            # ponderado por tamaño
I["pesoR"] = I.tam


def resumen(x, et):
    w = x.R > 0.05; l = x.R < -0.05
    return pd.Series(dict(n=len(x), WR=w.mean(), BE=(~w & ~l).mean(), perd=l.mean(),
                          gan_media_R=x.R[w].mean(), perd_media_R=x.R[l].mean(),
                          esperanza_R=x.R.mean(), esperanza_neta_R=x.Rn.mean(),
                          t=x.Rn.mean() / (x.Rn.std() / np.sqrt(len(x))),
                          PF=x.R[x.R > 0].sum() / -x.R[x.R < 0].sum(),
                          R_ponderado_tam=(x.Rw.sum() / x.tam.sum())), name=et)


filas = [resumen(I, "TOTAL")] + [resumen(g, k) for k, g in I.groupby("producto")]
I["m"] = I.fecha.dt.to_period("M")
print(pd.DataFrame(filas).round(3).to_string())
print(pd.DataFrame([resumen(g, str(k)) for k, g in I.groupby("m")]).round(3)[["n", "WR", "esperanza_R", "esperanza_neta_R"]].to_string())
# peor racha de pérdidas
s = (I.sort_values(["fecha", "hora"]).R < -0.05).astype(int).to_numpy()
mx = c = 0
for v in s:
    c = c + 1 if v else 0; mx = max(mx, c)
print("peor racha perdedora:", mx)
print("distribución de R:", np.percentile(I.R, [5, 10, 25, 50, 75, 90, 95]).round(2))
I.to_csv("tom_dia_indices.csv", index=False)
