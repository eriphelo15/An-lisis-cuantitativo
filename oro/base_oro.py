"""Base para el estudio del oro (GC, 1 min, 2021-03 a 2026-03). Día de trading CME 18:00 -> 17:00 ET.
Matriz por día: minutos relativos a medianoche ET, de -360 (18:00 del día anterior) a 1019 (16:59) -> 1380 minutos.
Precios back-ajustados (adj_*) para que las diferencias sean exactas entre contratos. EMAs sobre la sesión completa."""
import os
import numpy as np, pandas as pd
CACHE = "/home/user/data/gc_dias.npz"
TICK = 0.1; USD_PT = 100.0; COSTO_PTS = 5.76 / 100 + 2 * 0.1     # GC: comisión + 1 tick por lado
PER = [("DEV 2021-03..2023-06", "2021-03-01", "2023-06-30"), ("VAL 2023-07..2026-03", "2023-07-01", "2026-03-31")]

def cargar():
    if os.path.exists(CACHE):
        z = np.load(CACHE, allow_pickle=True); return z["A"], z["E20"], z["E50"], pd.DatetimeIndex(z["F"]), z["ref"]
    d = pd.read_parquet("/home/user/data/gc_1m.parquet", columns=["ts", "close", "adj_open", "adj_high", "adj_low", "adj_close"])
    d["e20"] = d.adj_close.ewm(span=20, adjust=False).mean(); d["e50"] = d.adj_close.ewm(span=50, adjust=False).mean()
    m = d.ts.dt.hour * 60 + d.ts.dt.minute; nxt = d.ts.dt.hour >= 18
    d["fecha"] = d.ts.dt.normalize() + pd.to_timedelta(nxt.astype(int), unit="D")
    d["fecha"] = d.fecha + pd.to_timedelta(np.where(d.fecha.dt.dayofweek == 5, 2, 0), unit="D")
    d["m"] = np.where(nxt, m - 1440, m) + 360
    A, E20, E50, F, ref = [], [], [], [], []
    for f, g in d.groupby("fecha"):
        if len(g) < 1000: continue
        a = np.full((1380, 6), np.nan); k = g.m.to_numpy(); ok = (k >= 0) & (k < 1380)
        a[k[ok]] = g[["adj_open", "adj_high", "adj_low", "adj_close", "e20", "e50"]].to_numpy()[ok]
        a = pd.DataFrame(a).ffill().bfill().to_numpy()
        A.append(a[:, :4]); E20.append(a[:, 4]); E50.append(a[:, 5]); F.append(f); ref.append(g.close.iloc[len(g) // 2])
    A, E20, E50 = np.stack(A), np.stack(E20), np.stack(E50)
    np.savez(CACHE, A=A, E20=E20, E50=E50, F=np.array(F), ref=np.array(ref))
    return A, E20, E50, pd.DatetimeIndex(F), np.array(ref)

def idx(hhmm):
    h, mm = divmod(hhmm, 100); t = h * 60 + mm
    return (t - 1440 if h >= 18 else t) + 360

if __name__ == "__main__":
    A, E20, E50, F, ref = cargar(); print(A.shape, F[0], F[-1])
