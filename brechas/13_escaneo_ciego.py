"""Escaneo con validación CIEGA: las reglas se seleccionan SOLO con DEV (2011-2018) exigiendo t>=2.5 en los TRES índices
con el mismo signo. Después se mira, sin tocar nada, su resultado medio en VAL1 (2019-21) y VAL2 (2021-26).
Esto estima honestamente cuánto de lo 'descubierto' por un escaneo masivo sobrevive fuera de muestra."""
import importlib, itertools
import numpy as np, pandas as pd
E = importlib.import_module("08_escaneo_masivo")
from base import SYMS
f, P = E.f, E.P
arrs = {s: E.datos[s][0].loc[f].to_numpy() for s in SYMS}
dev = P == "DEV"
res = []
for t in E.ENTRADAS:
    Fs = {s: E.features(arrs[s], t) for s in SYMS}
    B = {s: {k: E.buckets(v, dev) for k, v in Fs[s].items()} for s in SYMS}
    for h in E.HOR:
        fin = 960 if h == "cierre" else t + h
        if fin > 1005 or fin <= t: continue
        Y = {s: E.lr(arrs[s], t, fin) for s in SYMS}
        keys = list(B["NQ"].keys())
        for cnd in [(k,) for k in keys] + list(itertools.combinations(keys, 2)):
            vals = [np.unique(B["NQ"][k][~np.isnan(B["NQ"][k])]) for k in cnd]
            for combo in itertools.product(*vals):
                fila = dict(t=t, h=h, cond=cnd, val=combo); ok = True; sg = None
                for s in SYMS:
                    m = np.ones(len(f), bool)
                    for k, v in zip(cnd, combo): m &= B[s][k] == v
                    z = Y[s][m & dev]; z = z[~np.isnan(z)]
                    if len(z) < 40: ok = False; break
                    tt = z.mean() / z.std() * np.sqrt(len(z))
                    if sg is None: sg = np.sign(tt)
                    if np.sign(tt) != sg or abs(tt) < 2.5: ok = False; break
                    fila[f"{s}_DEV"] = z.mean() * sg
                    for p in ["VAL1", "VAL2"]:
                        w = Y[s][m & (P == p)]; w = w[~np.isnan(w)]
                        fila[f"{s}_{p}"] = w.mean() * sg if len(w) else np.nan
                        fila[f"{s}_{p}_sd"] = w.std(); fila[f"{s}_{p}_n"] = len(w)
                if ok:
                    fila["dir"] = sg; res.append(fila)
R = pd.DataFrame(res); R.to_csv("res_13_escaneo_ciego.csv", index=False)
print("reglas seleccionadas con DEV:", len(R))
for s in SYMS:
    print(s, "bp medios (en la dirección elegida)  DEV %.2f | VAL1 %.2f | VAL2 %.2f" % (R[f"{s}_DEV"].mean(), R[f"{s}_VAL1"].mean(), R[f"{s}_VAL2"].mean()),
          "| positivas VAL1 %.0f%%, VAL2 %.0f%%" % (100 * (R[f"{s}_VAL1"] > 0).mean(), 100 * (R[f"{s}_VAL2"] > 0).mean()))
pd.set_option("display.width", 250)
R["val_min"] = R[[f"{s}_{p}" for s in SYMS for p in ["VAL1", "VAL2"]]].min(axis=1)
print(R.sort_values("val_min", ascending=False)[["t", "h", "cond", "val", "dir"] + [f"{s}_{p}" for s in SYMS for p in ["DEV", "VAL1", "VAL2"]]].head(25).round(1).to_string())
