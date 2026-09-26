"""Escaneo masivo de reglas simples con validación estricta.
Rejilla de 15 min (18:00→16:45). Regla = (hora de entrada, horizonte, condición de 1-2 variables) -> dirección fijada en DEV.
Aceptada solo si: t_DEV >= 3 en el índice de descubrimiento y mismo signo con t >= 1 en VAL1 y VAL2 en LOS TRES índices.
Se compara el número de reglas aceptadas con el de datos barajados (nulo) para saber cuántas serían suerte."""
import itertools, sys
import numpy as np, pandas as pd
from base import cargar, periodo, SYMS
from externos import externos
from calendario import marcas

PASO = 15
GRID = np.arange(-360, 1020, PASO)          # minutos relativos al día de trading

def rejilla(sym):
    d = cargar(sym, ("ts", "close", "adj_close"))
    d = d[np.isin(d.m, GRID)]
    A = d.pivot_table(index="fecha", columns="m", values="adj_close").reindex(columns=GRID)
    ref = d[d.m == 570].groupby("fecha").close.first()
    A = A.loc[ref.index]
    A = A.ffill(axis=1)
    return A, ref

rng = np.random.default_rng(0)
datos = {}
for s in SYMS:
    A, ref = rejilla(s)
    datos[s] = (A, ref)
f = datos["NQ"][0].index.intersection(datos["ES"][0].index).intersection(datos["YM"][0].index)
f = f[f >= "2011-01-01"]
P = periodo(f); X = externos(f); C = marcas(f)
col = {m: i for i, m in enumerate(GRID)}

def lr(A, a, b):
    return np.log(A[:, col[b]] / A[:, col[a]]) * 1e4

ENTRADAS = [m for m in GRID if 0 <= m <= 945 and m % 30 == 0]
HOR = [15, 30, 60, 120, "cierre"]

def features(A, t):
    """variables conocidas en el minuto t (terciles con cortes de DEV)"""
    F = {}
    if t - 15 >= -360: F["r15"] = lr(A, t - 15, t)
    if t - 60 >= -360: F["r60"] = lr(A, t - 60, t)
    if t > 570: F["desde_apert"] = lr(A, 570, t)
    F["noche"] = lr(A, -360, min(t, 570)) if t > -360 else None
    F["ayer"] = np.r_[np.nan, lr(A, 570, 960)[:-1]]
    F["sem5"] = pd.Series(lr(A, 570, 960)).rolling(5).sum().shift().to_numpy()
    F = {k: v for k, v in F.items() if v is not None}
    F["vix"] = X.VIX.to_numpy(); F["ts_vix"] = X.ratio_3m.to_numpy(); F["dvix"] = X.dvix.to_numpy()
    F["dow"] = C.dow.to_numpy().astype(float)
    return F

def buckets(v, dev):
    if np.nanstd(v) == 0: return None
    if len(np.unique(v[~np.isnan(v)])) <= 7:
        return v
    q = np.nanquantile(v[dev], [1/3, 2/3])
    b = np.where(v <= q[0], 0, np.where(v >= q[1], 2, 1)).astype(float); b[np.isnan(v)] = np.nan
    return b

def escanear(barajar=False):
    res = []
    arrs = {s: datos[s][0].loc[f].to_numpy() for s in SYMS}
    perm = rng.permutation(len(f)) if barajar else None
    dev = P == "DEV"
    for t in ENTRADAS:
        Fs = {s: features(arrs[s], t) for s in SYMS}
        B = {s: {k: buckets(v, dev) for k, v in Fs[s].items()} for s in SYMS}
        for h in HOR:
            fin = 960 if h == "cierre" else t + h
            if fin > 1005 or fin <= t: continue
            Y = {s: lr(arrs[s], t, fin) for s in SYMS}
            if barajar:
                Y = {s: y[perm] for s, y in Y.items()}   # rompe la relación variable->futuro, conserva todo lo demás
            keys = list(B["NQ"].keys())
            conds = [(k,) for k in keys] + list(itertools.combinations(keys, 2))
            for cnd in conds:
                vals = [np.unique(B["NQ"][k][~np.isnan(B["NQ"][k])]) for k in cnd]
                for combo in itertools.product(*vals):
                    ok = True; fila = dict(t=t, h=h, cond=cnd, val=combo)
                    signo = None
                    for s in SYMS:
                        m = np.ones(len(f), bool)
                        for k, v in zip(cnd, combo):
                            m &= B[s][k] == v
                        y = Y[s]
                        tt = {}
                        for p in ["DEV", "VAL1", "VAL2"]:
                            z = y[m & (P == p)]; z = z[~np.isnan(z)]
                            if len(z) < 30: ok = False; break
                            tt[p] = (z.mean(), z.mean() / z.std() * np.sqrt(len(z)), len(z))
                        if not ok: break
                        if signo is None:
                            signo = np.sign(tt["DEV"][0])
                            if abs(tt["DEV"][1]) < 3: ok = False; break
                        for p in ["DEV", "VAL1", "VAL2"]:
                            if np.sign(tt[p][0]) != signo or abs(tt[p][1]) < 1.0: ok = False; break
                        if not ok: break
                        for p in tt: fila[f"{s}_{p}"] = tt[p][0]; fila[f"{s}_{p}_t"] = tt[p][1]; fila[f"{s}_{p}_n"] = tt[p][2]
                    if ok:
                        fila["dir"] = "largo" if signo > 0 else "corto"; res.append(fila)
    return pd.DataFrame(res)

if __name__ == "__main__":
    real = escanear(False)
    real.to_csv("res_08_escaneo.csv", index=False)
    print("reglas aceptadas (real):", len(real))
    nulos = [len(escanear(True)) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 3)]
    print("reglas aceptadas con datos barajados:", nulos)
    if len(real):
        pd.set_option("display.width", 250)
        c = ["t", "h", "cond", "val", "dir"] + [f"{s}_{p}" for s in SYMS for p in ["DEV", "VAL1", "VAL2"]]
        print(real[c].round(1).to_string())
