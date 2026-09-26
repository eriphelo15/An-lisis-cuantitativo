"""Malaysian SnR (SNR) programado de forma mecánica, NQ/ES/YM, 15 años, RTH.
Niveles (en un marco superior: 15 min o 60 min), a partir de APERTURAS/CIERRES:
  A (resistencia): vela alcista seguida de bajista -> nivel = cierre de la alcista
  V (soporte):     vela bajista seguida de alcista -> nivel = cierre de la bajista
  Gap: dos velas del mismo color con hueco entre cierre y apertura -> nivel = cierre de la primera (se incluye como opción)
Fresco = aún no tocado por una mecha desde que se formó. Se opera el PRIMER toque (09:35-15:00). Validez del nivel: 2 días.
Entradas:
  'limite'      : orden límite en el nivel (relleno conservador: el precio debe cruzarlo 1 tick)
  'confirmacion': tras tocar el nivel, la primera vela de 1 min que cierra de vuelta a favor (verde en soporte, roja en resistencia)
                  dentro de los 5 min siguientes -> entrada al cierre; stop más allá del extremo del toque
Stop: nivel -/+ k·ATR (límite) o extremo del toque -/+ 2 ticks (confirmación). Objetivo 1R/2R. Cierre 15:55.
'Storyline': solo a favor de la tendencia de 60 min (EMA20 vs EMA50 de 60 min) o sin filtro.
Selección con 2010-18; comprobación 2019-23 y 2024-26."""
import sys, itertools
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import INSTR

def cargar(sym):
    d = pd.read_parquet(f"/home/user/data/{INSTR[sym]['parquet']}", columns=["ts", "adj_open", "adj_high", "adj_low", "adj_close"])
    hm = d.ts.dt.hour * 100 + d.ts.dt.minute
    d = d[(hm >= 930) & (hm < 1600)].copy(); d["dia"] = d.ts.dt.normalize(); d["k"] = d.ts.dt.hour * 60 + d.ts.dt.minute - 570
    D, F = [], []
    for f, g in d.groupby("dia"):
        if len(g) < 385 or g.k.min() != 0: continue
        a = np.full((390, 4), np.nan); a[g.k.to_numpy()] = g[["adj_open", "adj_high", "adj_low", "adj_close"]].to_numpy()
        D.append(pd.DataFrame(a).ffill().to_numpy()); F.append(f)
    A = np.stack(D); rng = A[:, :, 1].max(1) - A[:, :, 2].min(1)
    atr = pd.Series(rng).shift().rolling(14).mean().to_numpy()
    c60 = A.reshape(len(A), -1, 4)[:, 59::60, 3].ravel() if False else None
    return A, pd.DatetimeIndex(F), atr

@njit
def correr(A, atr, tf, usar_gap, modo, stop_k, rr, filtro, tick, validez_dias):
    nd = A.shape[0]; nb = 390 // tf
    # EMA 20/50 de 60 min encadenadas (cierres de cada hora RTH)
    e20 = np.zeros((nd, 7)); e50 = np.zeros((nd, 7)); a20 = 0.0; a50 = 0.0; ini = False
    for di in range(nd):
        for hb in range(7):
            t = min(hb * 60 + 59, 389); c = A[di, t, 3]
            if not ini: a20 = c; a50 = c; ini = True
            a20 += (c - a20) * 2 / 21; a50 += (c - a50) * 2 / 51
            e20[di, hb] = a20; e50[di, hb] = a50
    MAXL = 400
    lv = np.zeros(MAXL); tipo = np.zeros(MAXL, np.int64); nace_d = np.zeros(MAXL, np.int64); nace_t = np.zeros(MAXL, np.int64); vivo = np.zeros(MAXL, np.bool_)
    nl = 0; out = []
    for di in range(nd):
        if np.isnan(atr[di]): continue
        pos = 0; ent = 0.0; st = 0.0; tg = 0.0; r = 0.0
        pend = -1; pend_t = 0; pend_ext = 0.0; pend_lv = 0.0; pend_d = 0
        for t in range(390):
            o = A[di, t, 0]; h = A[di, t, 1]; l = A[di, t, 2]; c = A[di, t, 3]
            # 1) gestión de posición abierta
            if pos != 0:
                fin = False; px = 0.0
                if (pos > 0 and l <= st) or (pos < 0 and h >= st): px = st; fin = True
                elif (pos > 0 and h >= tg) or (pos < 0 and l <= tg): px = tg; fin = True
                elif t >= 385: px = c; fin = True
                if fin:
                    out.append((di, pos, pos * (px - ent), r, 1 if px == tg else 0)); pos = 0
                continue
            # 2) confirmación pendiente
            if pend >= 0:
                if pend_d > 0: pend_ext = min(pend_ext, l)
                else: pend_ext = max(pend_ext, h)
                if t - pend_t > 5: pend = -1
                elif (pend_d > 0 and c > o and c > pend_lv) or (pend_d < 0 and c < o and c < pend_lv):
                    ent = c; st = pend_ext - pend_d * 2 * tick; r = pend_d * (ent - st)
                    if r >= 4 * tick and r <= 0.25 * atr[di] and t < 360:
                        pos = pend_d; tg = ent + pos * rr * r
                    pend = -1
                    continue
            # 3) toques de niveles frescos
            if 5 <= t <= 330 and pos == 0 and pend < 0:
                mejor = -1; mdist = 1e18
                for j in range(nl):
                    if not vivo[j]: continue
                    if di - nace_d[j] > validez_dias: vivo[j] = False; continue
                    if nace_d[j] == di and nace_t[j] >= t: continue
                    toca = (l <= lv[j] <= h)
                    if toca:
                        dist = abs(o - lv[j])
                        if dist < mdist: mdist = dist; mejor = j
                if mejor >= 0:
                    j = mejor; vivo[j] = False      # deja de estar fresco
                    d = 1 if tipo[j] == 1 else -1    # 1 soporte -> compra, 2 resistencia -> venta
                    # dirección de llegada: soporte debe tocarse desde arriba
                    if (d > 0 and o < lv[j]) or (d < 0 and o > lv[j]): d = 0
                    hb = min(t // 60, 6)
                    ok_f = True
                    if filtro == 1:
                        hb2 = hb - 1
                        if hb2 < 0:
                            ok_f = (e20[di - 1, 6] > e50[di - 1, 6]) if d > 0 else (e20[di - 1, 6] < e50[di - 1, 6])
                        else:
                            ok_f = (e20[di, hb2] > e50[di, hb2]) if d > 0 else (e20[di, hb2] < e50[di, hb2])
                    if d != 0 and ok_f:
                        if modo == 0:   # límite en el nivel
                            if (d > 0 and l <= lv[j] - tick) or (d < 0 and h >= lv[j] + tick):
                                ent = lv[j]; st = ent - d * stop_k * atr[di]; r = stop_k * atr[di]
                                if (d > 0 and l <= st) or (d < 0 and h >= st):
                                    out.append((di, d, -r, r, 0))
                                else:
                                    pos = d; tg = ent + d * rr * r
                        else:
                            pend = j; pend_t = t; pend_lv = lv[j]; pend_d = d; pend_ext = l if d > 0 else h
            # 4) nuevos niveles al cerrar una vela del marco superior
            if (t + 1) % tf == 0 and t + 1 >= 2 * tf:
                b = (t + 1) // tf - 1
                o2 = A[di, (b - 1) * tf, 0]; c2 = A[di, b * tf - 1, 3]; o3 = A[di, b * tf, 0]; c3 = A[di, t, 3]
                nuevo = 0; nivel = 0.0
                if c2 > o2 and c3 < o3: nuevo = 2; nivel = c2
                elif c2 < o2 and c3 > o3: nuevo = 1; nivel = c2
                elif usar_gap and ((c2 > o2 and c3 > o3) or (c2 < o2 and c3 < o3)) and abs(o3 - c2) >= 2 * tick:
                    nivel = c2; nuevo = 1 if c3 > o3 else 2   # gap alcista = soporte, bajista = resistencia
                if nuevo > 0:
                    # reutilizar hueco
                    slot = -1
                    for j in range(nl):
                        if not vivo[j]: slot = j; break
                    if slot < 0 and nl < MAXL: slot = nl; nl += 1
                    if slot >= 0:
                        lv[slot] = nivel; tipo[slot] = nuevo; nace_d[slot] = di; nace_t[slot] = t; vivo[slot] = True
            # niveles tocados por mecha dejan de estar frescos (aunque no se operen)
            for j in range(nl):
                if vivo[j] and not (nace_d[j] == di and nace_t[j] >= t) and l <= lv[j] <= h: vivo[j] = False
    return out

PER = [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]
filas = []
for sym in ["NQ", "ES", "YM"]:
    A, F, atr = cargar(sym); I = INSTR[sym]; tick = I["tick"]; atr_hoy = float(np.nanmean(atr[-60:]))
    for tf, gap, modo, sk, rr, filt in itertools.product([15, 60], [False, True], [0, 1], [0.05, 0.1], [1.0, 2.0], [0, 1]):
        if modo == 1 and sk == 0.1: continue   # el stop de la confirmación no usa k
        R = pd.DataFrame(correr(A, atr, tf, gap, modo, sk, rr, filt, tick, 2), columns=["di", "d", "pts", "r", "tp"])
        if len(R) < 100: continue
        f = F[R.di.astype(int)]; esc = atr_hoy / atr[R.di.astype(int)]
        costo = I["com"] / I["usd"] + np.where(R.tp == 1, 0, 1) * tick + (0 if modo == 0 else tick)
        R["Rn"] = (R.pts * esc - costo) / (R.r * esc)
        fila = dict(sym=sym, tf=tf, gap=gap, entrada="límite" if modo == 0 else "confirmación", stop=sk if modo == 0 else "extremo", rr=rr,
                    storyline="60m" if filt else "no", n=len(R), por_dia=len(R) / len(A))
        for tag, a, b in PER:
            x = R.Rn[(f >= a) & (f <= b)]
            fila[tag] = x.mean(); fila[tag + " WR"] = (R.pts[(f >= a) & (f <= b)] > 0).mean(); fila[tag + " t"] = x.mean() / x.std() * np.sqrt(len(x))
        filas.append(fila)
    print(sym, flush=True)
X = pd.DataFrame(filas); X.to_csv("res_32_snr.csv", index=False)
pd.set_option("display.width", 260)
c = ["sym", "tf", "gap", "entrada", "stop", "rr", "storyline", "por_dia", "2010-18", "2010-18 WR", "2010-18 t", "2019-23", "2019-23 t", "2024-26", "2024-26 WR", "2024-26 t"]
for s in ["NQ", "ES", "YM"]:
    Y = X[X.sym == s].sort_values("2010-18", ascending=False)
    print(f"\n{s}: mejores 5 elegidas con 2010-18"); print(Y[c].head(5).round(3).to_string(index=False))
    print("  positivas en los 3 periodos:", ((Y["2010-18"] > 0) & (Y["2019-23"] > 0) & (Y["2024-26"] > 0)).sum(), "de", len(Y),
          "| media R:", Y[["2010-18", "2019-23", "2024-26"]].mean().round(3).to_dict())
