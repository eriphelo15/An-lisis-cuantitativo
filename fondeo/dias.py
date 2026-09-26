"""Biblioteca de días reales de NQ (RTH 09:30-15:59, 1 min) escalados al nivel de precio actual.
Se usan los días de 2021-03 a 2026-03 (régimen reciente) y se escala cada día a NQ = 24,500
conservando el movimiento porcentual, para que la volatilidad en puntos sea la de hoy."""
import os, numpy as np, pandas as pd
DATA = os.environ.get("NQ_DATA_DIR", "/home/user/data")
NIVEL = 24500.0

def construir(desde="2021-03-15", hasta="2026-03-13"):
    df = pd.read_parquet(os.path.join(DATA, "nq15_1m.parquet"), columns=["ts", "open", "high", "low", "close"])
    df = df[(df.ts >= desde) & (df.ts <= hasta + " 23:59")]
    hm = df.ts.dt.hour * 100 + df.ts.dt.minute
    df = df[(hm >= 930) & (hm < 1600)].copy()
    df["d"] = df.ts.dt.normalize(); df["k"] = (df.ts.dt.hour * 60 + df.ts.dt.minute) - 570
    out, fechas = [], []
    for d, g in df.groupby("d"):
        if len(g) < 385: continue
        a = np.full((390, 4), np.nan); a[g.k.to_numpy()] = g[["open", "high", "low", "close"]].to_numpy()
        a = pd.DataFrame(a).ffill().bfill().to_numpy()
        base = a[0, 0]; a = (a - base) * (NIVEL / base)      # puntos desde la apertura, escalados
        out.append(a); fechas.append(d)
    arr = np.stack(out).astype(np.float64)
    np.save(os.path.join(DATA, "dias_rth.npy"), arr)
    pd.Series(fechas).to_csv(os.path.join(DATA, "dias_rth_fechas.csv"), index=False)
    return arr

if __name__ == "__main__":
    a = construir(); print(a.shape, "rango medio del día (pts):", np.mean(a[:, :, 1].max(1) - a[:, :, 2].min(1)).round(1))
