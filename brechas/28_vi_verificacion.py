"""Verificación del VI original (con añadidos y salida por cualquier EMA):
 1) un simulador independiente en Python puro que registra cada entrada, se compara con el motor rápido (numba) de los 15 años;
 2) lista de operaciones para revisar en TradingView (últimos días, datos Yahoo) y en el replay de Tradovate (muestra histórica con contrato);
 3) gráficos de una muestra de operaciones históricas."""
import importlib, random
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src = open("26_vi_segundo_vi.py").read().split("for min_rec in")[0]
exec(src.replace("@njit(cache=True)", "@njit"))  # define correr (numba), A, E20, E50, F, atr, atr_hoy, I, tick
T0 = pd.Timestamp("2000-01-01 09:30")
hm = lambda k: (T0 + pd.Timedelta(minutes=int(k))).strftime("%H:%M")

def dia_puro(A1, e20, e50, t_fin=120, tick=0.25, max_add=3):
    ops = []; d = 0; ents = []; tp = None; t_last = 0
    for k in range(1, 389):
        o1, h1, l1, c1 = A1[k - 1]; o, h, l, c = A1[k]
        salio = False
        if d != 0:
            px = mot = None
            if (d > 0 and h >= tp + tick) or (d < 0 and l <= tp - tick): px, mot = tp, "TP"
            elif (d > 0 and (c < e20[k] or c < e50[k])) or (d < 0 and (c > e20[k] or c > e50[k])): px, mot = c, "EMA"
            elif k - t_last >= 5: px, mot = c, "5 min"
            if mot:
                ops.append(dict(dir="COMPRA" if d > 0 else "VENTA", entradas=[(hm(t), p) for t, p in ents], tp=tp, salida_hora=hm(k),
                                salida_precio=px, motivo=mot, pts=sum(d * (px - p) for _, p in ents), nc=len(ents)))
                d = 0; ents = []; salio = True
        if salio or k >= t_fin: continue
        up = c > e20[k] and c > e50[k] and e20[k] > e50[k]; dn = c < e20[k] and c < e50[k] and e20[k] < e50[k]
        s = 0
        if up and max(o, c) < min(o1, c1) and h >= l1: s, ntp = 1, max(o, c)
        elif dn and min(o, c) > max(o1, c1) and l <= h1: s, ntp = -1, min(o, c)
        if s == 0 or abs(ntp - c) < tick: continue
        if d == 0: d, ents, tp, t_last = s, [(k, c)], ntp, k
        elif s == d and len(ents) < 1 + max_add: ents.append((k, c)); tp, t_last = ntp, k
    return ops

# 1) comparación con el motor rápido (puntos brutos, sin escalar)
R = pd.DataFrame(correr(A, E20, E50, np.ones(len(A)), 1.0, 120, 1, 0.0, tick), columns=["di", "k", "d", "nc", "pts", "mot"])
tot_numba = R.pts.sum(); n_numba = len(R)
filas = []
for di in range(len(A)):
    for op in dia_puro(A[di], E20[di], E50[di]):
        op["di"] = di; filas.append(op)
P = pd.DataFrame(filas)
print(f"Motor rápido: {n_numba} operaciones, {tot_numba:.2f} pts | Simulador independiente: {len(P)} operaciones, {P.pts.sum():.2f} pts")

# contrato de cada día
S = pd.read_parquet("/home/user/data/nq15_1m.parquet", columns=["ts", "symbol"])
S = S[(S.ts.dt.hour == 10) & (S.ts.dt.minute == 0)].assign(f=lambda x: x.ts.dt.normalize()).set_index("f").symbol
P["fecha"] = F[P.di.values]; P["contrato"] = P.fecha.map(S)
P["usd_1NQ"] = (P.pts - P.nc * np.where(P.motivo == "TP", 1, 2) * tick) * 20 - P.nc * 5.76
# días tras cambio de contrato (EMAs distintas en Tradovate): se excluyen de la muestra
P["cambio_reciente"] = P.contrato != P.contrato.shift(1).where(P.di.diff() <= 3)
random.seed(7)
azar = P[(P.fecha >= "2016-01-01")].sample(12, random_state=7)
grandes = P[P.fecha >= "2016-01-01"].nsmallest(4, "usd_1NQ")
añadidos = P[(P.nc > 1) & (P.fecha >= "2016-01-01")].sample(4, random_state=3)
M = pd.concat([azar, grandes, añadidos]).drop_duplicates(subset=["di", "salida_hora"]).sort_values("fecha")
def fmt(r):
    return pd.Series(dict(fecha=r.fecha.strftime("%Y-%m-%d"), contrato=r.contrato, dir=r.dir,
                          entradas=" + ".join(f"{t} @ {p:.2f}" for t, p in r.entradas), TP=f"{r.tp:.2f}",
                          salida=f"{r.salida_hora} @ {r.salida_precio:.2f} ({r.motivo})", pts=round(r.pts, 2), usd_1NQ=round(r.usd_1NQ)))
L = M.apply(fmt, axis=1); L.to_csv("verificacion_tradovate.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(L.to_string(index=False))

# 3) gráficos
def graf(ax, r):
    di = int(r.di); ks = [int((pd.Timestamp("2000-01-01 " + t) - T0).seconds // 60) for t, _ in r.entradas]
    kx = int((pd.Timestamp("2000-01-01 " + r.salida_hora) - T0).seconds // 60)
    a, b = max(ks[0] - 12, 1), min(kx + 5, 389); x = np.arange(a, b)
    for t in x:
        oo, hh, ll, cc = A[di, t]
        ax.vlines(t, ll, hh, color="#1f1f1f", lw=0.8)
        ax.add_patch(plt.Rectangle((t - 0.35, min(oo, cc)), 0.7, max(abs(cc - oo), 0.25), facecolor="#1f1f1f" if cc < oo else "white", edgecolor="#1f1f1f", lw=0.8))
    ax.plot(x, E20[di, a:b], color="#3b9ae1", lw=1.6); ax.plot(x, E50[di, a:b], color="#f0a030", lw=1.6)
    for (t, p), k in zip(r.entradas, ks):
        ax.plot(k, p, marker="v" if r.dir == "VENTA" else "^", ms=9, color="#b03030" if r.dir == "VENTA" else "#2e9e4f", zorder=5)
    ax.hlines(r.tp, ks[-1], kx, color="#2e9e4f", ls="--", lw=1.2)
    ax.plot(kx, r.salida_precio, marker="X", ms=10, color="#2e9e4f" if r.usd_1NQ > 0 else "#b03030", zorder=5)
    ax.set_xticks(x[::5]); ax.set_xticklabels([hm(t) for t in x[::5]], fontsize=7)
    ax.set_title(f"{r.fecha:%Y-%m-%d} {r.contrato} · {r.dir} x{r.nc} · {r.motivo} · {r.pts:+.2f} pts (${r.usd_1NQ:+.0f})", fontsize=9, loc="left")
    ax.tick_params(axis="y", labelsize=7); ax.grid(alpha=0.15)
fig, axs = plt.subplots(4, 5, figsize=(26, 16)); axs = axs.ravel()
for ax, (_, r) in zip(axs, M.iterrows()): graf(ax, r)
for ax in axs[len(M):]: ax.axis("off")
fig.suptitle("VI original (con añadidos) · muestra de 15 años para verificar en Tradovate · EMA20 azul, EMA50 naranja, ▲▼ entradas, línea verde = TP final, X = salida", fontsize=13)
fig.tight_layout(); fig.savefig("verificacion_muestra.png", dpi=90)
