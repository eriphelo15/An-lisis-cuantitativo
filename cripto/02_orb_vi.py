"""H8: ORB 15 min (00:00 UTC y 9:30 NY) y frecuencia de VI en cripto."""
import numpy as np
import pandas as pd
from numba import njit
import base_cripto as b

C = b.COSTO


@njit
def orb(O, H, L, Cl, t0, dur, tfin):
    n = O.shape[0]
    out = np.full(n, np.nan)
    for d in range(n):
        a = t0[d]
        if a < 0:
            continue
        hi = H[d, a:a + dur].max()
        lo = L[d, a:a + dur].min()
        rng = hi - lo
        if rng <= 0:
            continue
        pos = 0
        ent = 0.0
        for m in range(a + dur, tfin[d]):
            if pos == 0:
                if H[d, m] > hi:
                    pos, ent = 1, hi
                    if L[d, m] < lo:         # conservador: stop en la misma vela
                        out[d] = -1.0
                        break
                elif L[d, m] < lo:
                    pos, ent = -1, lo
                    if H[d, m] > hi:
                        out[d] = -1.0
                        break
            else:
                if (pos == 1 and L[d, m] <= lo) or (pos == -1 and H[d, m] >= hi):
                    out[d] = -1.0
                    break
        else:
            if pos != 0:
                out[d] = pos * (Cl[d, tfin[d] - 1] - ent) / rng
            continue
        if pos != 0 and np.isnan(out[d]):
            out[d] = -1.0
    return out


filas = []
for sym in ["BTCUSDT", "ETHUSDT"]:
    df = b.cargar(sym)
    A, fechas = b.matriz_dias(df)
    fechas = fechas.tz_localize("UTC") if fechas.tz is None else fechas
    O, H, L, Cl = [np.ascontiguousarray(A[..., k]) for k in range(4)]

    # frecuencia de VI (hueco entre cuerpos) en 1 minuto
    o, c = df["o"].values, df["c"].values
    vi = (np.maximum(o[1:], c[1:]) < np.minimum(o[:-1], c[:-1])) | (np.minimum(o[1:], c[1:]) > np.maximum(o[:-1], c[:-1]))
    print(sym, "velas 1m con VI:", f"{vi.mean()*100:.3f}%", "| open == close previo:", f"{(o[1:]==c[:-1]).mean()*100:.1f}%")

    ny = pd.DatetimeIndex(fechas).tz_convert("America/New_York")
    off = np.array([(pd.Timestamp(f.date()).tz_localize("America/New_York") + pd.Timedelta("9h30min")).tz_convert("UTC").hour * 60 for f in ny]) + 30
    for nom, t0, dur_fin in [("00:00 UTC", np.zeros(len(fechas), np.int64), 240),
                             ("09:30 NY", off.astype(np.int64), 240)]:
        for dur in [15, 30]:
            t0a = t0.copy()
            tfin = np.minimum(t0a + dur + dur_fin, 1440).astype(np.int64)
            r = orb(O, H, L, Cl, t0a, dur, tfin)
            # costo en R: 2*C*precio / rango
            rng = np.array([H[d, t0a[d]:t0a[d]+dur].max() - L[d, t0a[d]:t0a[d]+dur].min() for d in range(len(fechas))])
            px = np.array([Cl[d, t0a[d]] for d in range(len(fechas))])
            costR = 2 * C * px / np.where(rng > 0, rng, np.nan)
            net = r - costR
            for pn, a, z in b.PER:
                m = (fechas >= pd.Timestamp(a, tz="UTC")) & (fechas <= pd.Timestamp(z, tz="UTC")) & ~np.isnan(net)
                x = net[m]
                filas.append(dict(sym=sym, var=f"ORB {dur} min {nom}", per=pn, n=len(x), R=x.mean(),
                                  R_bruto=r[m].mean(), costo_R=np.nanmean(costR[m]), t=x.mean()/x.std()*np.sqrt(len(x)), wr=(x>0).mean()))
out = pd.DataFrame(filas)
out.to_csv("res_02_orb.csv", index=False)
print(out.round(3).to_string())
