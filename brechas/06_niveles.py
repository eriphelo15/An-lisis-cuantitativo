"""Niveles clave: al PRIMER toque en RTH (09:35-15:30) de un nivel, ¿rebota o lo rompe?
Test simétrico: desde el nivel, ¿llega antes a +k·ATR (rebote) o a -k·ATR (ruptura)? Nulo martingala = 50%.
Niveles: máximo/mínimo de ayer (RTH), cierre de ayer, máximo/mínimo nocturno, apertura de hoy, VWAP no (se ve aparte), números redondos."""
import numpy as np, pandas as pd
from numba import njit
from base import cargar, periodo

@njit(cache=True)
def primer_toque(H, L, C, nivel, desde_arriba, t0, t1, k):
    """devuelve (minuto toque, resultado 1=rebote, 0=ruptura, -1=nada)"""
    n = H.shape[0]
    for t in range(t0, t1):
        if L[t] <= nivel <= H[t]:
            # dirección de llegada
            if t == 0:
                return -1, -1
            reb = nivel + k if desde_arriba else nivel - k
            rup = nivel - k if desde_arriba else nivel + k
            for u in range(t + 1, n):
                hr = H[u] >= reb if desde_arriba else L[u] <= reb
                hu = L[u] <= rup if desde_arriba else H[u] >= rup
                if hu:
                    return t, 0
                if hr:
                    return t, 1
            return t, -1
    return -1, -1

filas = []
for s in ["NQ", "ES", "YM"]:
    d = cargar(s, ("ts", "open", "high", "low", "close", "adj_close"))
    d["off"] = d.adj_close - d.close
    for c in ["open", "high", "low"]:
        d[c] = d[c] + d.off
    d["close"] = d.adj_close
    fechas = np.array(sorted(d.fecha.unique()))
    g = dict(tuple(d.groupby("fecha")))
    prev = None; atrs = []
    for f in fechas:
        x = g[f]; r = x[(x.m >= 570) & (x.m < 960)]; on = x[x.m < 570]
        if len(r) < 385:
            prev = None; continue
        rng = r.high.max() - r.low.min()
        if prev is not None and len(atrs) >= 14:
            atr = np.mean(atrs[-14:]); k = 0.1 * atr
            H, L, C = r.high.to_numpy(), r.low.to_numpy(), r.close.to_numpy()
            o = r.open.iloc[0]
            niveles = {"max_ayer": prev["h"], "min_ayer": prev["l"], "cierre_ayer": prev["c"],
                       "max_noche": on.high.max() if len(on) else np.nan, "min_noche": on.low.min() if len(on) else np.nan}
            base = 100.0 if s == "NQ" else (25.0 if s == "ES" else 200.0)
            niveles["redondo"] = np.round(o / base) * base   # (ajuste: precio back-ajustado ≠ real; se corrige abajo)
            # redondo sobre precio REAL
            off = r.off.iloc[0]
            real_o = o - off
            for j, lv in enumerate([np.floor(real_o / base) * base, np.ceil(real_o / base) * base]):
                niveles[f"redondo_{j}"] = lv + off
            del niveles["redondo"]
            for nom, lv in niveles.items():
                if np.isnan(lv):
                    continue
                desde_arriba = o > lv
                t, res = primer_toque(H, L, C, lv, desde_arriba, 5, 360, k)
                if t >= 0 and res >= 0:
                    filas.append(dict(sym=s, fecha=f, nivel=nom.split("_")[0] if nom.startswith("redondo") else nom, t=t, rebote=res, arriba=desde_arriba))
        prev = dict(h=r.high.max(), l=r.low.min(), c=r.close.iloc[-1]); atrs.append(rng)
R = pd.DataFrame(filas); R["P"] = periodo(pd.DatetimeIndex(R.fecha))
R.to_csv("res_06_niveles.csv", index=False)
t = R.groupby(["sym", "nivel", "P"]).rebote.agg(["mean", "count"]).unstack("P")
print((t.round(3)).to_string())
