"""Señales de referencia del pullback VI filtrado (mismas reglas que el indicador Pine) para NQ, ene-mar 2026.
Sirve para comprobar que el indicador de TradingView marca las mismas operaciones."""
import sys, importlib
import numpy as np, pandas as pd
sys.path.insert(0, "../estudio_nq")
vi = importlib.import_module("22_vi_usuario")
A, E20, E50, F, atr = vi.dias_con_ema("NQ"); tick = 0.25
filas = []
for di in np.flatnonzero(F >= "2026-01-01"):
    at = atr[di]; o930 = A[di, 0, 0]
    for n in range(1, 120):
        o1, c1, h1, l1 = A[di, n - 1, 0], A[di, n - 1, 3], A[di, n - 1, 1], A[di, n - 1, 2]
        o, h, l, c = A[di, n]
        e20, e50 = E20[di, n], E50[di, n]; pend = e20 - E20[di, n - 10] if n >= 10 else np.nan
        d = 0
        if e20 > e50 and c > e20 and c > e50 and max(o, c) < min(o1, c1) and h >= l1: d = 1
        elif e20 < e50 and c < e20 and c < e50 and min(o, c) > max(o1, c1) and l <= h1: d = -1
        if d == 0: continue
        stop = e50 - d * 2 * tick; r = d * (c - stop)
        if not (d * (c - o930) > 0.158 * at and d * pend > 0.074 * at and max(0.069 * at, 4 * tick) <= r <= 0.25 * at): continue
        tgt = c + d * 2 * r; res = None; mot = None
        for k in range(n + 1, 386):
            ok, hh, ll, cc = A[di, k]
            if (d > 0 and ll <= stop) or (d < 0 and hh >= stop):
                px = ok if (d > 0 and ok < stop) or (d < 0 and ok > stop) else stop; res = d * (px - c) / r; mot = "STOP"; break
            if (d > 0 and hh >= tgt) or (d < 0 and ll <= tgt): res = 2.0; mot = "OBJETIVO"; break
        if res is None: res = d * (A[di, 385, 3] - c) / r; mot = "15:55"
        filas.append(dict(fecha=F[di].strftime("%Y-%m-%d"), hora=(pd.Timestamp("2000-01-01 09:30") + pd.Timedelta(minutes=n)).strftime("%H:%M"),
                          dir="COMPRA" if d > 0 else "VENTA", entrada=c, stop=round(stop, 2), objetivo=round(tgt, 2),
                          stop_pts=round(r, 2), ATR=round(at, 1), salida=mot, R=round(res, 2)))
        break
X = pd.DataFrame(filas); X.to_csv("senales_referencia_2026.csv", index=False)
print(X.to_string(index=False)); print("\nops", len(X), "acierto", f"{(X.R>0).mean():.0%}", "R medio", round(X.R.mean(), 3), "R total", round(X.R.sum(), 2))
