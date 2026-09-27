"""Misma señal (pullback VI filtrado, 1 operación al día) con distintas GESTIONES, medidas por lo que da tranquilidad:
acierto, % de meses positivos, peor racha perdedora, caída máxima (en R) y suavidad de la curva (R² de la curva de capital).
Costes a precios de hoy, en R. Periodos por separado."""
import sys, importlib
import numpy as np, pandas as pd
sys.path.insert(0, "../estudio_nq")
vi = importlib.import_module("22_vi_usuario")
A, E20, E50, F, atr = vi.dias_con_ema("NQ"); tick = 0.25; atr_hoy = float(np.nanmean(atr[-60:]))
S = pd.read_parquet("/home/user/data/pullback_señales_nq.parquet")
S = S[(S.dist_ema50_R > 0.0689) & (S.pend20_a_favor > 0.074) & (S.mov_apertura_a_favor > 0.1582)].sort_values(["f", "n"]).groupby("f").head(1)
costo_R_hoy = lambda rk, di: (5.76 / 20 + 2 * tick) / (rk * atr_hoy / atr[di])   # por contrato, en R

def gestionar(di, n, d, rk, p1, frac, be, r2, cierre):
    """p1: objetivo parcial en R (None = sin parcial); frac: fracción que sale en p1; be: stop a breakeven tras p1;
    r2: objetivo del resto en R (None = hasta el cierre)."""
    e = A[di, n, 3]; st = e - d * rk; parte = 0.0; hecho = False; res = 0.0
    for k in range(n + 1, 386):
        o, h, l, c = A[di, k]
        stop_now = e if (hecho and be) else st
        if (d > 0 and l <= stop_now) or (d < 0 and h >= stop_now):
            px = o if ((d > 0 and o < stop_now) or (d < 0 and o > stop_now)) else stop_now
            resto = d * (px - e) / rk
            return parte + (1 - frac if hecho else 1) * resto
        if p1 is not None and not hecho and ((d > 0 and h >= e + d * p1 * rk) or (d < 0 and l <= e + d * p1 * rk)):
            hecho = True; parte = frac * p1
        if r2 is not None and ((d > 0 and h >= e + d * r2 * rk) or (d < 0 and l <= e + d * r2 * rk)):
            return parte + (1 - frac if hecho else 1) * r2
    c = A[di, 385, 3]; resto = d * (c - e) / rk
    return parte + (1 - frac if hecho else 1) * resto

VAR = {"A · objetivo 2R (base)": (None, 0, False, 2.0),
       "B · objetivo 1R": (None, 0, False, 1.0),
       "C · 50% a 0.5R + BE + resto 2R": (0.5, 0.5, True, 2.0),
       "D · 50% a 0.5R + BE + resto al cierre": (0.5, 0.5, True, None),
       "E · 50% a 1R + BE + resto 2R": (1.0, 0.5, True, 2.0),
       "F · 70% a 0.5R + BE + resto 2R": (0.5, 0.7, True, 2.0),
       "G · 50% a 0.3R + BE + resto 2R": (0.3, 0.5, True, 2.0)}
filas = []; curvas = {}
for nom, (p1, frac, be, r2) in VAR.items():
    R = np.array([gestionar(int(r.di), int(r.n), int(r.d), r.rk, p1, frac, be, r2, True) - costo_R_hoy(r.rk, int(r.di)) for r in S.itertuples()])
    X = pd.DataFrame(dict(f=S.f.to_numpy(), R=R))
    m = X.groupby(X.f.dt.to_period("M")).R.sum()
    eq = X.R.cumsum().to_numpy(); dd = (np.maximum.accumulate(eq) - eq).max()
    racha = mx = 0
    for v in X.R: racha = racha + 1 if v < 0 else 0; mx = max(mx, racha)
    r2c = np.corrcoef(np.arange(len(eq)), eq)[0, 1] ** 2
    fila = dict(gestión=nom, acierto=(X.R > 0).mean(), R_medio=X.R.mean(), meses_pos=(m > 0).mean(), peor_racha=mx, caida_max_R=dd,
                suavidad_R2=r2c, R_total_por_caida=eq[-1] / dd)
    for tag, a, b in [("2010-18", "2010", "2018-12-31"), ("2019-23", "2019", "2023-12-31"), ("2024-26", "2024", "2026-12-31")]:
        fila[tag] = X.R[(X.f >= a) & (X.f <= b)].mean()
    filas.append(fila); curvas[nom] = (X.f, eq)
T = pd.DataFrame(filas); T.to_csv("res_33_suavidad.csv", index=False)
pd.set_option("display.width", 250); print(T.round(3).to_string(index=False))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(13, 6))
for nom, col in [("A · objetivo 2R (base)", "#3b6fb6"), ("D · 50% a 0.5R + BE + resto al cierre", "#2e9e4f"), ("C · 50% a 0.5R + BE + resto 2R", "#9bc79f")]:
    f, eq = curvas[nom]; ax.plot(f, eq, lw=1.8, color=col, label=nom)
ax.axhline(0, color="#888", lw=0.8); ax.set_ylabel("R acumulados"); ax.grid(alpha=0.2); ax.legend(frameon=False)
ax.set_title("Pullback VI filtrado (NQ, 1 operación/día, costes de hoy): misma señal, distinta gestión", loc="left")
for s in ["top", "right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig("curvas_gestion.png", dpi=110)
