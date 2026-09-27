"""Auditoría: ¿los resultados publicados cuadran con el precio real? NASDAQ vs NQ y DOW vs YM (futuros, 1 minuto).
La hora del canal es de Londres. Base (futuro - contado) = cierre del futuro en el minuto de entrada - entrada publicada.
Para cada trade: ¿tocó el stop antes de la salida publicada? ¿el precio de salida publicado fue alcanzable?"""
import numpy as np, pandas as pd
I = pd.read_csv("tom_dia_indices.csv", parse_dates=["fecha"])
FUT = {"NASDAQ": "/home/user/data/nq15_1m.parquet", "DOW": "/home/user/data/ym15_1m.parquet"}
res = []
for prod, f in FUT.items():
    X = I[I.producto == prod].copy()
    d = pd.read_parquet(f, columns=["ts", "open", "high", "low", "close"])
    d = d[(d.ts >= "2022-12-25") & (d.ts <= "2024-05-05")].set_index("ts")
    for _, r in X.iterrows():
        try:
            t0 = pd.Timestamp(f"{r.fecha.date()} {r.hora}").tz_localize("Europe/London").tz_convert("America/New_York").tz_localize(None)
            t1 = pd.Timestamp(f"{r.fecha.date()} {r.hora_sal}").tz_localize("Europe/London").tz_convert("America/New_York").tz_localize(None)
        except Exception:
            continue
        if t1 < t0 or t0 not in d.index:
            continue
        seg = d.loc[t0:t1]
        base = d.loc[t0 - pd.Timedelta(minutes=1):t0].close.mean() - r.ent   # aprox.
        # base robusta: la que hace que la entrada caiga dentro del rango de la vela de entrada
        lo, hi = d.loc[t0, "low"] - r.ent, d.loc[t0, "high"] - r.ent
        base = np.clip(base, lo, hi)
        s = 1 if r.dir == "Long" else -1
        adv = (seg.low.min() - base - r.ent) * s if s > 0 else (r.ent - (seg.high.max() - base))
        fav = (seg.high.max() - base - r.ent) if s > 0 else (r.ent - (seg.low.min() - base))
        ex = r.salida
        alcanzable = (seg.low.min() - base - 0.25 * r.riesgo) <= ex <= (seg.high.max() - base + 0.25 * r.riesgo)
        res.append(dict(producto=prod, fecha=r.fecha, R=r.R, riesgo=r.riesgo, min_R=adv / r.riesgo, max_R=fav / r.riesgo,
                        salida_alcanzable=alcanzable, minutos=(t1 - t0).seconds / 60))
A = pd.DataFrame(res)
A["gan"] = A.R > 0.05
A["stop_tocado_antes"] = A.min_R < -1.15   # holgura 15% por la base aproximada
A["gano_mas_de_lo_posible"] = A.R > A.max_R + 0.15
print("trades auditados:", len(A), "de", I.producto.isin(FUT).sum())
print(A.groupby("producto")[["salida_alcanzable"]].mean())
print("ganadoras con stop tocado antes de la salida (inconsistentes):", (A.gan & A.stop_tocado_antes).sum(), "de", A.gan.sum())
print("trades con R publicado > máximo favorable posible:", A.gano_mas_de_lo_posible.sum())
print("pérdidas registradas peores que el stop (<-1.1R):", (A.R < -1.1).sum())
A.to_csv("auditoria_precios.csv", index=False)
