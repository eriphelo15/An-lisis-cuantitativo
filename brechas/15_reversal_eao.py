"""Validación de la estrategia del usuario 'Reversal [EAO]' (base: Dead Simple Reversal, @paidtofade), velas de 5 min.
Lógica (del .pine del usuario):
  compra: vela anterior bajista, actual alcista, cierre > apertura de la anterior, y el mínimo de las últimas nearTerm velas
          está por debajo del mínimo de longTerm velas medido 1..4 velas antes (barrido de mínimos).  Venta: simétrico.
  sesión 09:30 -> end_hora. Entrada al cierre de la vela señal. Stop = sl_mult * ATR(14, 5 min). Objetivo = tp_rr * stop.
  Salida forzosa 15:55. Una posición a la vez.
Su grid de 8 años (≈2018-2026) eligió: near=2, long=20, fin 10:00, sin filtro de cuerpo, SL 2 ATR, TP 2.5R (WR 34%, PF 1.32).
Aquí: mismos parámetros en 15 años; 2010-2017 es fuera de muestra para su optimización."""
import sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import cargar_dias, INSTR

def a5(A):
    n = A.shape[0]; B = A.reshape(n, 78, 5, 4)
    return np.stack([B[:, :, 0, 0], B[:, :, :, 1].max(2), B[:, :, :, 2].min(2), B[:, :, 4, 3]], axis=2)

@njit(cache=True)
def correr(B, atr5, near, long_, fin_bar, sl_mult, tp_rr, costo, solo_largos):
    n = B.shape[0]; out = []
    for d in range(n):
        pos = 0; e = 0.0; sl = 0.0; tp = 0.0; r = 0.0
        for j in range(long_ + 5, 78):
            o, h, l, c = B[d, j, 0], B[d, j, 1], B[d, j, 2], B[d, j, 3]
            if pos != 0:
                if pos > 0:
                    if l <= sl: out.append((d, j, pos, (sl - e - costo) / r)); pos = 0
                    elif h >= tp: out.append((d, j, pos, (tp - e - costo) / r)); pos = 0
                else:
                    if h >= sl: out.append((d, j, pos, (e - sl - costo) / r)); pos = 0
                    elif l <= tp: out.append((d, j, pos, (e - tp - costo) / r)); pos = 0
                if pos != 0 and j == 77:
                    out.append((d, j, pos, ((c - e) * pos - costo) / r)); pos = 0
                continue
            if j >= fin_bar or np.isnan(atr5[d, j]):
                continue
            # usa barras del mismo día (RTH); ventanas que empiezan antes de la apertura no se evalúan (j >= long_+5)
            nearLow = B[d, j - near + 1:j + 1, 2].min(); nearHigh = B[d, j - near + 1:j + 1, 1].max()
            c3 = False; c6 = False
            for k in range(1, 5):
                if B[d, j - k - long_ + 1:j - k + 1, 2].min() > nearLow: c3 = True
                if B[d, j - k - long_ + 1:j - k + 1, 1].max() < nearHigh: c6 = True
            po, pc = B[d, j - 1, 0], B[d, j - 1, 3]
            buy = pc < po and c > o and c > po and c3
            sell = (not solo_largos) and pc > po and c < o and c < po and c6
            if buy or sell:
                pos = 1 if buy else -1; e = c; r = sl_mult * atr5[d, j]
                sl = e - pos * r; tp = e + pos * tp_rr * r
    return out

def atr_5m(B):
    """ATR(14) sobre velas de 5 min encadenadas entre días (solo RTH)."""
    n = B.shape[0]; H = B[:, :, 1].ravel(); L = B[:, :, 2].ravel(); C = B[:, :, 3].ravel()
    pc = np.r_[np.nan, C[:-1]]
    tr = np.nanmax(np.vstack([H - L, np.abs(H - pc), np.abs(L - pc)]), axis=0)
    atr = pd.Series(tr).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
    return atr.reshape(n, 78)

if __name__ == "__main__":
    filas = []
    for sym in ["NQ", "ES", "YM"]:
        A, atrd, F, _ = cargar_dias(sym); B = a5(A); at = atr_5m(B)
        # la apertura de 09:30 como barra 0: near/long necesitan barras previas -> se permite desde la barra long+5
        # Para ventana 09:30-10:00 con long=20 necesitamos barras previas: usamos también la sesión anterior (encadenado)
        I = INSTR[sym]; costo_hoy_pts = I["com"] / I["usd"] + 2 * I["tick"]
        # encadenar días: añadir las últimas 30 barras del día anterior delante
        prev = np.concatenate([np.full((1, 30, 4), np.nan), B[:-1, -30:, :]], axis=0)
        BB = np.concatenate([prev, B], axis=1); AT = np.concatenate([np.full((B.shape[0], 30), np.nan), at], axis=1)
        for near, lg, fin, sl, tp in [(2, 20, "10:00", 2.0, 2.5), (2, 20, "10:30", 2.0, 2.5), (3, 20, "10:00", 2.0, 2.5), (2, 50, "10:00", 2.0, 2.5),
                                     (2, 20, "10:00", 2.0, 2.0), (2, 20, "10:00", 2.0, 1.5), (3, 50, "11:30", 2.0, 2.5)]:
            fin_bar = 30 + (int(fin[:2]) * 60 + int(fin[3:]) - 570) // 5
            # sólo señales desde la barra 30 (09:30) en adelante
            res = correr(BB, AT, near, lg, fin_bar, sl, tp, 0.0, False)
            R = pd.DataFrame(res, columns=["d", "j", "pos", "Rb"]); R = R[R.j >= 30]
            R["f"] = F[R.d.astype(int)]
            # costo con el ratio de hoy: costo_pts / riesgo_pts, riesgo = sl * ATR5 (en ATR de hoy)
            atr5_hoy = np.nanmean(at[-60:]); R["R"] = R.Rb - costo_hoy_pts / (sl * atr5_hoy)
            fila = dict(sym=sym, near=near, long=lg, fin=fin, sl=sl, tp=tp, n=len(R))
            for tag, a, b in [("2010-17 (ciego)", "2010-01-01", "2017-12-31"), ("2018-26 (su grid)", "2018-01-01", "2026-12-31")]:
                z = R[(R.f >= a) & (R.f <= b)].R
                fila[tag + " WR"] = (z > 0).mean(); fila[tag + " R"] = z.mean(); fila[tag + " t"] = z.mean() / z.std() * np.sqrt(len(z)); fila[tag + " n"] = len(z)
            filas.append(fila); print(fila, flush=True)
    X = pd.DataFrame(filas); X.to_csv("res_15_reversal_eao.csv", index=False)
    pd.set_option("display.width", 250); print(X.round(3).to_string())
