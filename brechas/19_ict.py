"""Modelos ICT codificados de forma mecánica (NQ, ES, YM · 15 años · velas de 1 y 5 min · RTH).
Reglas conservadoras: órdenes límite se llenan si el precio toca el nivel; si en la misma vela de 1 min se toca el stop -> pérdida;
stop y objetivo en la misma vela -> pérdida; salida forzosa 15:55. Costo = comisión + 1 tick/lado, en R con el ATR de hoy.

 FVG      : FVG de 5 min con desplazamiento (cuerpo > 1.5x cuerpo medio de 20 velas), 09:35-15:00. Límite en el borde del FVG
            (entrada al 'retest'), stop en el extremo de la vela 1 del patrón, objetivo 2R. Válido 12 velas (1 h).
 FVG_CE   : igual pero entrada en el 50% del FVG (consequent encroachment).
 SB       : Silver Bullet 10:00-11:00: tras barrer el máx/mín del rango 09:30-10:00, primer FVG de 5 min en sentido contrario al barrido;
            límite en el borde, stop en el extremo del barrido, objetivo = lado opuesto del rango 09:30-10:00 (mín. 1R).
 JUDAS    : 09:30-10:30, el precio barre el máx (mín) de la sesión nocturna y una vela de 5 min cierra de vuelta dentro:
            venta (compra) al cierre, stop en el extremo del barrido, objetivo 2R.
 TURTLE   : igual que JUDAS pero con máx/mín del día anterior (Turtle Soup), 09:30-11:30.
 OTE      : impulso: entre 09:30 y 10:30 el día hace un tramo >= 0.35 ATR (mín->máx) sin retroceso de 50%; entrada límite al 70.5%
            de retroceso, stop al 100% (origen del tramo), objetivo extensión -27% (1.27 del tramo).  ~3.3R."""
import sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import cargar_dias, INSTR
from base import cargar

@njit(cache=True)
def jugar(A1, t0, lim, stop, tgt, d, expira, mercado):
    """A1: (390,4) 1-min del día. Devuelve (resultado_pts, riesgo_pts, lleno)."""
    e = lim; riesgo = abs(lim - stop)
    if riesgo <= 0: return 0.0, 0.0, False
    lleno = mercado; t = t0
    if not lleno:
        while t < min(t0 + expira, 385):
            o, h, l, c = A1[t, 0], A1[t, 1], A1[t, 2], A1[t, 3]
            if (d > 0 and l <= lim) or (d < 0 and h >= lim):
                lleno = True
                if (d > 0 and l <= stop) or (d < 0 and h >= stop):
                    return -riesgo, riesgo, True
                t += 1
                break
            # si el objetivo se alcanza antes de llenar, se cancela
            if (d > 0 and h >= tgt) or (d < 0 and l <= tgt):
                return 0.0, riesgo, False
            t += 1
        if not lleno: return 0.0, riesgo, False
    while t < 386:
        h, l = A1[t, 1], A1[t, 2]
        if (d > 0 and l <= stop) or (d < 0 and h >= stop): return -riesgo, riesgo, True
        if (d > 0 and h >= tgt) or (d < 0 and l <= tgt): return abs(tgt - e), riesgo, True
        t += 1
    return (A1[385, 3] - e) * d, riesgo, True

def b5(A1):
    B = A1.reshape(78, 5, 4)
    return np.stack([B[:, 0, 0], B[:, :, 1].max(1), B[:, :, 2].min(1), B[:, 4, 3]], axis=1)

def setups(A1, atr, onh, onl, pdh, pdl):
    B = b5(A1); body = np.abs(B[:, 3] - B[:, 0]); out = []
    avgb = pd.Series(body).rolling(20, min_periods=5).mean().to_numpy()
    # FVG y FVG_CE
    for i in range(3, 67):   # vela i cierra en 09:30+5(i+1); hasta ~15:00
        for d in (1, -1):
            gap = (B[i, 2] > B[i - 2, 1]) if d > 0 else (B[i, 1] < B[i - 2, 2])
            desp = body[i - 1] > 1.5 * (avgb[i - 2] if not np.isnan(avgb[i - 2]) else 1e9) and np.sign(B[i - 1, 3] - B[i - 1, 0]) == d
            if gap and desp:
                top, bot = (B[i, 2], B[i - 2, 1]) if d > 0 else (B[i - 2, 2], B[i, 1])
                stop = B[i - 2, 2] if d > 0 else B[i - 2, 1]
                for nom, lim in (("FVG", top if d > 0 else bot), ("FVG_CE", (top + bot) / 2)):
                    r = abs(lim - stop)
                    if r < 0.02 * atr: continue
                    out.append((nom, (i + 1) * 5, lim, stop, lim + d * 2 * r, d, 60, False))
    # SB
    hi, lo = B[:6, 1].max(), B[:6, 2].min(); barrido = 0; ext = np.nan
    for i in range(6, 18):
        if barrido == 0:
            if B[i, 1] > hi: barrido = 1; ext = B[i, 1]
            elif B[i, 2] < lo: barrido = -1; ext = B[i, 2]
        else:
            ext = max(ext, B[i, 1]) if barrido > 0 else min(ext, B[i, 2])
            d = -barrido
            gap = (B[i, 2] > B[i - 2, 1]) if d > 0 else (B[i, 1] < B[i - 2, 2])
            if gap:
                lim = B[i, 2] if d > 0 else B[i, 1]; r = abs(lim - ext)
                tgt = hi if d > 0 else lo
                if abs(tgt - lim) < r: tgt = lim + d * r
                if r > 0.02 * atr: out.append(("SB", (i + 1) * 5, lim, ext, tgt, d, 30, False))
                break
    # JUDAS / TURTLE
    for nom, H, L, fin in (("JUDAS", onh, onl, 12), ("TURTLE", pdh, pdl, 24)):
        if np.isnan(H): continue
        hecho = False; eh = -1e18; el = 1e18
        for i in range(0, fin):
            eh = max(eh, B[i, 1]); el = min(el, B[i, 2])
            if eh > H and B[i, 3] < H and not hecho:
                c = B[i, 3]; r = eh - c
                if r > 0.02 * atr: out.append((nom, (i + 1) * 5, c, eh + 0.0, c - 2 * r, -1, 1, True)); hecho = True
            if el < L and B[i, 3] > L and not hecho:
                c = B[i, 3]; r = c - el
                if r > 0.02 * atr: out.append((nom, (i + 1) * 5, c, el, c + 2 * r, 1, 1, True)); hecho = True
    # OTE
    H1 = A1[:60, 1]; L1 = A1[:60, 2]
    ih, il = int(np.argmax(H1)), int(np.argmin(L1)); leg = H1[ih] - L1[il]
    if leg >= 0.35 * atr:
        if il < ih:   # tramo alcista
            e = H1[ih] - 0.705 * leg; out.append(("OTE", 60, e, L1[il], H1[ih] + 0.27 * leg, 1, 120, False))
        else:
            e = L1[il] + 0.705 * leg; out.append(("OTE", 60, e, H1[ih], L1[il] - 0.27 * leg, -1, 120, False))
    return out

PER = [("DEV 2010-18", "2010-01-01", "2018-12-31"), ("VAL1 2019-21", "2019-01-01", "2021-03-12"), ("VAL2 2021-26", "2021-03-13", "2026-12-31")]
filas = []
for sym in ["NQ", "ES", "YM"]:
    A, atr, F, prev_c = cargar_dias(sym)
    d = cargar(sym, ("ts", "high", "low")); on = d[d.m < 570].groupby("fecha").agg(h=("high", "max"), l=("low", "min"))
    on = on.reindex(F)
    I = INSTR[sym]; costo = I["com"] / I["usd"] + 2 * I["tick"]; atr_hoy = np.nanmean(atr[-60:])
    T = []
    for k in range(1, len(A)):
        if np.isnan(atr[k]): continue
        pdh, pdl = A[k - 1, :, 1].max(), A[k - 1, :, 2].min()
        if (F[k] - F[k - 1]).days > 4: pdh = pdl = np.nan
        for nom, t0, lim, stop, tgt, dd, exp, mk in setups(A[k], atr[k], on.h.iloc[k], on.l.iloc[k], pdh, pdl):
            res, r, ll = jugar(A[k], t0, lim, stop, tgt, dd, exp, mk)
            if ll and r > 0:
                T.append((nom, F[k], res / r - costo / (r * atr_hoy / atr[k]), dd))
    T = pd.DataFrame(T, columns=["modelo", "f", "R", "d"])
    T = T.sort_values("f").groupby(["modelo", "f"]).head(1)   # 1 operación por modelo y día (la primera)
    for m, g in T.groupby("modelo"):
        fila = dict(sym=sym, modelo=m, n=len(g), por_año=len(g) / 15.4)
        for tag, a, b in PER:
            z = g[(g.f >= a) & (g.f <= b)].R
            fila[tag + " WR"] = (z > 0).mean(); fila[tag + " R"] = z.mean(); fila[tag + " t"] = z.mean() / z.std() * np.sqrt(len(z))
        yrs = g.groupby(g.f.dt.year).R.sum(); fila["años+"] = f"{(yrs > 0).sum()}/{len(yrs)}"
        filas.append(fila)
    print(sym, "listo", flush=True)
X = pd.DataFrame(filas); X.to_csv("res_19_ict.csv", index=False)
pd.set_option("display.width", 260); print(X.round(3).to_string(index=False))
