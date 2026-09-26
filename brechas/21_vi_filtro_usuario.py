"""VI del usuario (contra-tendencia, entrada al cierre de la vela VI, TP en el hueco, salida a 5 min o cierre al otro lado de la EMA20)
+ el filtro discrecional que describe: NO operar si la distancia entrada->hueco (recompensa) es pequeña frente al riesgo potencial.
Medidas de riesgo potencial probadas (en el momento de entrar):
  r_ema  : distancia del cierre a la EMA20 (nivel cuya ruptura te saca)
  r_vela : rango de la vela VI (máx - mín)
  r_ext  : distancia del cierre al extremo de la vela VI en contra (mecha)
Umbrales fijados con DEV (2010-18) y comprobados en 2019-26. Resultados en puntos NQ al ATR de hoy, con costos."""
import sys, importlib
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import INSTR
vi = importlib.import_module("22_vi_usuario")

@njit(cache=True)
def correr(A, E20, E50, t_fin, tp_modo, n_min, tick):
    out = []
    for di in range(A.shape[0]):
        n = 1; ocupado = -1
        while n < t_fin:
            if n <= ocupado: n += 1; continue
            o1 = A[di, n - 1, 0]; c1 = A[di, n - 1, 3]; h1 = A[di, n - 1, 1]; l1 = A[di, n - 1, 2]
            o = A[di, n, 0]; h = A[di, n, 1]; l = A[di, n, 2]; c = A[di, n, 3]
            up = c > E20[di, n] and c > E50[di, n] and E20[di, n] > E50[di, n]
            dn = c < E20[di, n] and c < E50[di, n] and E20[di, n] < E50[di, n]
            d = 0.0; tp = 0.0
            if up and max(o, c) < min(o1, c1) and h >= l1:
                d = 1.0; tp = max(o, c) if tp_modo == 0 else min(o1, c1)
            elif dn and min(o, c) > max(o1, c1) and l <= h1:
                d = -1.0; tp = min(o, c) if tp_modo == 0 else max(o1, c1)
            if d == 0.0 or abs(tp - c) < tick: n += 1; continue
            e = c; res = 0.0; k = n + 1; fin = min(n + n_min, 389); motivo = 0
            while k <= fin:
                hh = A[di, k, 1]; ll = A[di, k, 2]; cc = A[di, k, 3]
                if (d > 0 and hh >= tp + tick) or (d < 0 and ll <= tp - tick):
                    res = d * (tp - e); motivo = 1; break
                if (d > 0 and cc < E20[di, k]) or (d < 0 and cc > E20[di, k]):
                    res = d * (cc - e); motivo = 2; break
                if k == fin: res = d * (cc - e); motivo = 3
                k += 1
            r_ema = abs(c - E20[di, n]); r_vela = h - l; r_ext = (c - l) if d > 0 else (h - c)
            out.append((di, n, d, res, motivo, abs(tp - c), r_ema, r_vela, r_ext))
            ocupado = k; n = k + 1
    return out

if __name__ == "__main__":
    for sym in ["NQ", "ES", "YM"]:
        A, E20, E50, F, atr = vi.dias_con_ema(sym); I = INSTR[sym]; tick = I["tick"]
        c_mkt = I["com"] / I["usd"] + 2 * tick; c_tp = I["com"] / I["usd"] + tick
        atr_hoy = np.nanmean(atr[-60:])
        for tpm, tpn in [(0, "TP borde del hueco"), (1, "TP hueco completo")]:
            R = pd.DataFrame(correr(A, E20, E50, 120, tpm, 5, tick), columns=["di", "n", "d", "res", "mot", "rec", "r_ema", "r_vela", "r_ext"])
            R["f"] = F[R.di.astype(int)]; R["atr"] = atr[R.di.astype(int)]; R = R[R.atr > 0]
            esc = atr_hoy / R.atr
            R["neto"] = R.res * esc - np.where(R.mot == 1, c_tp, c_mkt)       # puntos a la escala de hoy
            dev = R.f <= "2018-12-31"; val = R.f >= "2019-01-01"
            print(f"\n===== {sym} · {tpn} · señales {len(R)} ({len(R)/len(A):.1f}/día)")
            def linea(nom, m):
                out = []
                for tag, p in (("2010-18", dev), ("2019-26", val)):
                    x = R.neto[m & p]; w = x[x > 0]; lo = x[x <= 0]
                    out.append(f"{tag}: n={len(x):6d} WR={100*(x>0).mean():4.1f}% gan={w.mean():5.1f} perd={lo.mean():6.1f} res={x.mean():+5.2f}pts ({x.mean()*I['usd']:+6.1f}$)")
                print(f"  {nom:36s}", " | ".join(out))
            linea("sin filtro", np.ones(len(R), bool))
            for med in ["r_ema", "r_vela", "r_ext"]:
                for q in [1.0, 0.5]:
                    m = R.rec >= q * R[med]
                    linea(f"recompensa >= {q} x {med}", m)
            # recompensa mínima absoluta (en ATR del día)
            for k in [0.01, 0.02, 0.03]:
                linea(f"recompensa >= {k} ATR", R.rec >= k * R.atr)
