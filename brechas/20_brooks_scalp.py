"""Scalping estilo Al Brooks: segunda entrada (H2 / L2) a favor de tendencia en velas de 5 min, entrada stop 1 tick más allá de la vela señal.
Probamos objetivos pequeños con stop MAYOR que el objetivo (lo que da alto % de acierto):
  stop = extremo opuesto de la vela señal - 1 tick (riesgo r); objetivo = r/2, r/3 y r (1:1); y la variante 'ES 1 punto' (objetivo 4 ticks, stop 8/12 ticks).
Tendencia: cierre > EMA20 (5 min) y EMA20 subiendo (bajista: al revés). Ventana 09:35-15:30. Ejecución conservadora en 1 min."""
import sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import cargar_dias, INSTR

@njit(cache=True)
def sim(A1, t0, ent, stop, tgt, d):
    """entrada stop desde el minuto t0 (válida 5 min); luego stop/objetivo; misma vela -> pérdida."""
    t = t0; lleno = False
    while t < min(t0 + 5, 385):
        if (d > 0 and A1[t, 1] >= ent) or (d < 0 and A1[t, 2] <= ent):
            lleno = True
            if (d > 0 and A1[t, 2] <= stop) or (d < 0 and A1[t, 1] >= stop): return stop - ent if d > 0 else ent - stop, True
            if (d > 0 and A1[t, 3] >= tgt) or (d < 0 and A1[t, 3] <= tgt): return abs(tgt - ent), True
            t += 1; break
        t += 1
    if not lleno: return 0.0, False
    while t < 386:
        if (d > 0 and A1[t, 2] <= stop) or (d < 0 and A1[t, 1] >= stop): return -abs(ent - stop), True
        if (d > 0 and A1[t, 1] >= tgt) or (d < 0 and A1[t, 2] <= tgt): return abs(tgt - ent), True
        t += 1
    return (A1[385, 3] - ent) * d, True

def señales(B, ema):
    """H2 / L2 en velas de 5 min."""
    out = []
    for d in (1, -1):
        cnt = 0; en_pb = False
        for i in range(3, 72):
            tend = (B[i, 3] - ema[i]) * d > 0 and (ema[i] - ema[i - 3]) * d > 0
            if not tend: cnt = 0; en_pb = False; continue
            if (d > 0 and B[i, 1] < B[i - 1, 1]) or (d < 0 and B[i, 2] > B[i - 1, 2]):
                en_pb = True
            if en_pb and ((d > 0 and B[i, 1] > B[i - 1, 1]) or (d < 0 and B[i, 2] < B[i - 1, 2])):
                cnt += 1
                if cnt == 2:
                    out.append((i, d)); cnt = 0; en_pb = False
    return out

filas = []
for sym in ["ES", "NQ"]:
    A, atr, F, _ = cargar_dias(sym); I = INSTR[sym]; tick = I["tick"]; costo = I["com"] / I["usd"] + 2 * tick
    n = A.shape[0]; R = A.reshape(n, 78, 5, 4)
    B = np.stack([R[:, :, 0, 0], R[:, :, :, 1].max(2), R[:, :, :, 2].min(2), R[:, :, 4, 3]], axis=2)
    C = B[:, :, 3].ravel(); ema = pd.Series(C).ewm(span=20, adjust=False).mean().to_numpy().reshape(n, 78)
    atr_hoy = np.nanmean(atr[-60:])
    res = []
    for k in range(20, n):
        for i, d in señales(B[k], ema[k]):
            sb = B[k, i]; ent = sb[1] + tick if d > 0 else sb[2] - tick
            stp = sb[2] - tick if d > 0 else sb[1] + tick; r = abs(ent - stp)
            if r < 4 * tick: continue
            for nom, tg in (("obj 1:1", r), ("obj = riesgo/2", r / 2), ("obj = riesgo/3", r / 3)):
                pnl, ll = sim(A[k], (i + 1) * 5, ent, stp, ent + d * tg, d)
                if ll: res.append((nom, F[k], pnl, r, atr[k]))
            if sym == "ES":
                for nom, sl in (("ES 1 pt, stop 2 pt", 2.0), ("ES 1 pt, stop 3 pt", 3.0)):
                    pnl, ll = sim(A[k], (i + 1) * 5, ent, ent - d * sl, ent + d * 1.0, d)
                    if ll: res.append((nom, F[k], pnl, sl, atr[k]))
    X = pd.DataFrame(res, columns=["tipo", "f", "pnl", "r", "atr"])
    for tipo, g in X.groupby("tipo"):
        fijo = tipo.startswith("ES 1")
        # en puntos, con costo real de hoy; para escalas relativas se reescala al ATR de hoy
        esc = 1.0 if fijo else atr_hoy / g.atr
        net = g.pnl * esc - costo; rr = g.r * esc
        fila = dict(sym=sym, tipo=tipo, n=len(g), WR_bruto=(g.pnl > 0).mean(), WR_neto=(net > 0).mean(),
                    R_bruto=(g.pnl / g.r).mean(), R_neto=(net / rr).mean(), usd_por_trade=(net * I["usd"]).mean())
        for tag, a, b in [("2010-18", "2010", "2018-12-31"), ("2019-26", "2019", "2026-12-31")]:
            m = (g.f >= a) & (g.f <= b); fila[tag] = (net[m] / rr[m]).mean()
        filas.append(fila)
Y = pd.DataFrame(filas); Y.to_csv("res_20_brooks.csv", index=False)
pd.set_option("display.width", 220); print(Y.round(3).to_string(index=False))
