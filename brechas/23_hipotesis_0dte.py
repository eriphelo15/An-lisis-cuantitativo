"""Prueba de las hipótesis registradas en HIPOTESIS_0DTE.md (commit 36477f8). Reglas exactamente como están escritas.
'Movimiento grande' = tercil superior de |movimiento|/ATR en DEV0 (normalizado por ATR para que sea comparable entre años)."""
import sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, "../estudio_nq")
from hougaard import cargar_dias, INSTR
from externos import externos

DEV0 = ("2021-03-15", "2023-12-31"); FIN = ("2024-01-01", "2026-03-13")

@njit(cache=True)
def orb(A1, hi, lo):
    for t in range(15, 386):
        h, l = A1[t, 1], A1[t, 2]
        if h >= hi and l <= lo: return -1.0
        if h >= hi:
            for u in range(t + 1, 386):
                if A1[u, 2] <= lo: return -1.0
            return (A1[385, 3] - hi) / (hi - lo)
        if l <= lo:
            for u in range(t + 1, 386):
                if A1[u, 1] >= hi: return -1.0
            return (lo - A1[385, 3]) / (hi - lo)
    return np.nan

filas = []; detalle = {}
for sym in ["NQ", "ES", "YM"]:
    A, atr, F, prev_c = cargar_dias(sym); I = INSTR[sym]; costo = I["com"] / I["usd"] + 2 * I["tick"]
    m0 = (F >= DEV0[0]) & (F <= FIN[1]); A, atr, F, prev_c = A[m0], atr[m0], F[m0], prev_c[m0]
    atr_hoy = np.nanmean(atr[-60:]); esc = atr_hoy / atr
    X = externos(F); vix = X.VIX.to_numpy(); r9 = X.ratio_9d.to_numpy()
    vmed = pd.Series(X.VIX.to_numpy()).rolling(252, min_periods=100).median().to_numpy()
    # para la mediana de 252 días usamos también el VIX previo a 2021
    Xall = externos(pd.bdate_range("2019-01-01", F[-1])); vm_all = Xall.VIX.rolling(252).median(); vmed = vm_all.reindex(F).to_numpy()
    dev = (F <= DEV0[1]); rondo = {"NQ": 100.0, "ES": 25.0, "YM": 200.0}[sym]
    o = lambda t: A[:, t, 0]; c = lambda t: A[:, t, 3]
    def tercil(x): return np.nanquantile(np.abs(x[dev]), 2 / 3)
    H = {}
    # H1
    mv = (o(30) - prev_c) / atr; th = tercil(mv); d = -np.sign(mv); act = np.abs(mv) >= th
    H["H1 reversión del cierre"] = np.where(act, d * (c(388) - o(360)), np.nan)
    # H2
    mv = (o(270) - o(30)) / atr; th = tercil(mv); act = np.abs(mv) >= th
    H["H2 reversión de la tarde"] = np.where(act, -np.sign(mv) * (c(379) - o(270)), np.nan)
    # H3
    r3 = np.full(len(A), np.nan)
    for k in range(len(A)):
        for w in range(60, 331, 30):
            mv = A[k, w, 0] - A[k, w - 30, 0]
            if abs(mv) > 0.25 * atr[k]:
                r3[k] = -np.sign(mv) * (A[k, min(w + 30, 389), 0] - A[k, w, 0]); break
    H["H3 reversión tras latigazo 30min"] = r3
    # H4
    p = o(330); lvl = np.round(p / rondo) * rondo; dist = lvl - p
    act = (np.abs(dist) < 0.1 * atr) & (np.abs(dist) > I["tick"])
    H["H4 imán de strikes"] = np.where(act, np.sign(dist) * (c(388) - p), np.nan)
    # H5 / H6
    mv = o(210) - o(0); sgn = np.sign(mv)
    H["H5 gamma por VIX"] = np.where(~np.isnan(vmed), np.where(vix < vmed, -sgn, sgn) * (c(379) - o(210)), np.nan)
    H["H6 gamma por VIX9D/VIX"] = np.where(~np.isnan(r9), np.where(r9 < 1, -sgn, sgn) * (c(379) - o(210)), np.nan)
    # H7 / H8 (en R -> convertimos a puntos con el riesgo = rango inicial)
    hi = A[:, :15, 1].max(1); lo = A[:, :15, 2].min(1)
    Rorb = np.array([orb(A[k], hi[k], lo[k]) for k in range(len(A))]); pts_orb = Rorb * (hi - lo)
    H["H7 ORB 15min"] = pts_orb
    H["H8 ORB con VIX alto"] = np.where(vix > vmed, pts_orb, np.nan)
    for nom, raw in H.items():
        net = raw * esc - costo
        fila = dict(hip=nom, sym=sym)
        for tag, m in (("DEV0", dev), ("FINAL", ~dev)):
            x = net[m & ~np.isnan(net)]
            fila[f"{tag} n"] = len(x); fila[f"{tag} $"] = x.mean() * I["usd"]; fila[f"{tag} t"] = x.mean() / x.std() * np.sqrt(len(x))
            fila[f"{tag} WR"] = (x > 0).mean()
        filas.append(fila)
R = pd.DataFrame(filas); R.to_csv("res_23_hipotesis_0dte.csv", index=False)
pd.set_option("display.width", 220)
print(R.round(2).to_string(index=False))
print("\nVeredicto NQ (éxito: DEV0 > 0, FINAL > 0 y t_FINAL >= 2.0; Holm con 8 -> t >= 2.5 para la mejor):")
for _, r in R[R.sym == "NQ"].iterrows():
    ok = r["DEV0 $"] > 0 and r["FINAL $"] > 0 and r["FINAL t"] >= 2.0
    print(f"  {r.hip:34s} DEV0 {r['DEV0 $']:+7.1f}$  FINAL {r['FINAL $']:+7.1f}$ (t {r['FINAL t']:+.2f})  -> {'PASA' if ok else 'no pasa'}")
