"""Relaciones entre NQ, ES, YM en RTH (1 minuto):
(a) adelanto/retraso: ¿el rendimiento de un índice en el minuto t anticipa el de otro en t+1..t+5?
(b) divergencia: residuo del NQ frente al ES desde las 09:30 (beta rolling); ¿revierte en los próximos 15/30/60 min?"""
import numpy as np, pandas as pd
from base import cargar, periodo

def rth(sym):
    d = cargar(sym, ("ts", "adj_close", "close"))
    d = d[(d.m >= 570) & (d.m < 960)]
    return d.pivot_table(index="fecha", columns="m", values="adj_close"), d.groupby("fecha").close.first()

NQ, refn = rth("NQ"); ES, refe = rth("ES"); YM, refy = rth("YM")
f = NQ.index.intersection(ES.index).intersection(YM.index)
NQ, ES, YM = NQ.loc[f].ffill(axis=1), ES.loc[f].ffill(axis=1), YM.loc[f].ffill(axis=1)
refn, refe, refy = refn.loc[f], refe.loc[f], refy.loc[f]
P = periodo(f)
lr = lambda A: np.log(A).diff(axis=1).to_numpy()[:, 1:]
rn, re_, ry = lr(NQ), lr(ES), lr(YM)
print("(a) adelanto/retraso: correlación del minuto t de X con t+k de Y")
for nx, x in [("ES", re_), ("NQ", rn), ("YM", ry)]:
    for ny, y in [("NQ", rn), ("ES", re_), ("YM", ry)]:
        if nx == ny: continue
        out = []
        for k in [1, 2, 5]:
            for p in ["DEV", "VAL2"]:
                m = P == p
                a = x[m][:, :-k].ravel(); b = y[m][:, k:].ravel(); ok = ~np.isnan(a) & ~np.isnan(b)
                out.append(f"k={k} {p}: {np.corrcoef(a[ok], b[ok])[0,1]:+.4f}")
        print(f"{nx}→{ny}", " | ".join(out))
# (b) divergencia NQ vs ES
print("\n(b) divergencia NQ-ES desde la apertura: resultado del NQ en los próximos H min, firmado para apostar a la reversión (bp)")
cn = np.log(NQ.to_numpy() / NQ.to_numpy()[:, :1]); ce = np.log(ES.to_numpy() / ES.to_numpy()[:, :1])
# beta estable ~ 1.2 (estimada en DEV sobre rendimientos diarios RTH)
dn = cn[:, -1]; de = ce[:, -1]; m = P == "DEV"
beta = np.polyfit(de[m], dn[m], 1)[0]; print("beta NQ/ES:", round(beta, 2))
res = cn - beta * ce
sd = np.nanstd(res[P == "DEV"], axis=0)
for t0 in [30, 60, 120, 180]:
    z = res[:, t0] / sd[t0]
    for H in [15, 30, 60]:
        fut = (cn[:, t0 + H] - cn[:, t0]) * 1e4   # NQ solo
        futs = ((cn[:, t0 + H] - cn[:, t0]) - beta * (ce[:, t0 + H] - ce[:, t0])) * 1e4  # diferencial
        line = f"t0={t0:3d} H={H:2d} "
        for p in ["DEV", "VAL1", "VAL2"]:
            k = (P == p) & (np.abs(z) > 1.5)
            g = -np.sign(z[k]) * fut[k]; gs = -np.sign(z[k]) * futs[k]
            line += f"| {p} n={k.sum():3d} NQ {g.mean():+5.1f}bp t={g.mean()/g.std()*np.sqrt(len(g)):+4.1f} spread {gs.mean():+4.1f} t={gs.mean()/gs.std()*np.sqrt(len(gs)):+4.1f} "
        print(line)
