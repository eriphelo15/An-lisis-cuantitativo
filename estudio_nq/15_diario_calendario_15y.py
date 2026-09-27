"""Fase 15y-b — Reversión diaria, franjas horarias y calendario por periodo (DEV/VAL1/VAL2).
Unidades: bp brutos (diario) y % del ATR (franjas). Los costos diarios son < 1 bp hoy."""
import numpy as np, pandas as pd, os
from motor import Motor
from lib import RES_DIR, PERIODOS_15Y
M = Motor("all"); df = M.df; s = M.smin; di = M.day_id
rth = (s >= 930) & (s < 1320)
g = df[rth].groupby(di[rth])
A = pd.DataFrame({"o": g.adj_open.first(), "h": g.adj_high.max(), "l": g.adj_low.min(), "c": g.adj_close.last(),
                  "raw": g.close.last(), "n": g.size()})
A = A[A.n >= 385].copy(); A["date"] = M.days[A.index]; A = A.reset_index(drop=True)
d = A.c.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
A["ibs"] = (A.c - A.l) / (A.h - A.l)
A["rsi2"] = 100 - 100 / (1 + up.ewm(alpha=.5, adjust=False).mean() / dn.ewm(alpha=.5, adjust=False).mean())
A["streak"] = (d < 0).astype(int).groupby((d >= 0).cumsum()).cumsum()
A["up_streak"] = (d > 0).astype(int).groupby((d <= 0).cumsum()).cumsum()
for k in [20, 50, 100, 200]: A[f"sma{k}"] = A.c.rolling(k).mean()
A["ret_intradia"] = np.log(A.c / A.o) * 1e4
for k, col in [(1, "f1"), (2, "f2"), (5, "f5")]: A[col] = (A.c.shift(-k) - A.c) / A.raw * 1e4
A["f_on"] = (A.o.shift(-1) - A.c) / A.raw * 1e4
A = A.dropna(subset=["sma200", "f5"])
def per(mask, col, sign=1):
    out = {}
    for tag, a, b in PERIODOS_15Y:
        mm = mask & A.date.between(a, b); x = sign * A.loc[mm, col]
        out[f"{tag}_n"] = len(x); out[f"{tag}_bp"] = x.mean()
        out[f"{tag}_t"] = x.mean() / (x.std() / np.sqrt(len(x))) if len(x) > 2 else np.nan
        out[f"{tag}_wr"] = (x > 0).mean()
    return out
rows = []
base = pd.Series(True, index=A.index)
for col in ["f1", "f2", "f5"]:
    rows.append(dict(regla="base (todos)", salida=col, **per(base, col)))
    for tr in [None, 50, 200]:
        T = base if tr is None else A.c > A[f"sma{tr}"]
        tt = "" if tr is None else f" & >SMA{tr}"
        rows.append(dict(regla="base" + tt, salida=col, **per(T, col)))
        for th in [0.1, 0.2]: rows.append(dict(regla=f"IBS<{th}{tt}", salida=col, **per(T & (A.ibs < th), col)))
        for th in [10, 20]: rows.append(dict(regla=f"RSI2<{th}{tt}", salida=col, **per(T & (A.rsi2 < th), col)))
        for k in [2, 3]: rows.append(dict(regla=f"{k}+ bajistas{tt}", salida=col, **per(T & (A.streak >= k), col)))
        for k in [3, 4]: rows.append(dict(regla=f"{k}+ alcistas{tt} (short)", salida=col, **per(T & (A.up_streak >= k), col, -1)))
R = pd.DataFrame(rows); R.to_csv(os.path.join(RES_DIR, "f5_15y_diario.csv"), index=False)
pd.set_option("display.width", 260)
print("=== Reversión diaria (bp brutos) — orden por t en DEV ===")
cols = ["regla", "salida"] + [f"{p}_{m}" for p, *_ in PERIODOS_15Y for m in ("n", "bp", "t", "wr")]
print(R.sort_values("DEV_t", ascending=False)[cols].head(25).round(2).to_string(index=False))

# Franjas de 30 min en % ATR
Dd = M.D.dropna(subset=["atr"])
df["slot"] = s // 30
gg = df.groupby([di, df.slot])
S = pd.DataFrame({"o": gg.open.first(), "c": gg.close.last(), "seg0": gg.seg.first(), "seg1": gg.seg.last(), "n": gg.size()})
S = S[(S.seg0 == S.seg1) & (S.n >= 25)].reset_index(); S.columns = ["d", "slot"] + list(S.columns[2:])
S["atr"] = Dd.atr.reindex(S.d).to_numpy(); S = S.dropna(subset=["atr"])
S["x"] = (S.c - S.o) / S.atr * 100; S["date"] = M.days[S.d]
lab = lambda sl: f"{((sl*30+1080)%1440)//60:02d}:{((sl*30+1080)%1440)%60:02d}"
rows = []
for sl, G in S.groupby("slot"):
    r = {"franja": lab(sl)}
    for tag, a, b in PERIODOS_15Y:
        x = G[G.date.between(a, b)].x
        r[f"{tag}_atr%"] = x.mean(); r[f"{tag}_t"] = x.mean() / (x.std() / np.sqrt(len(x))); r[f"{tag}_n"] = len(x)
    rows.append(r)
F = pd.DataFrame(rows); F.to_csv(os.path.join(RES_DIR, "f5_15y_franjas.csv"), index=False)
print("\n=== Franjas de 30 min (% ATR) con |t_DEV| > 2 ===  (esperadas por azar ≈ 2.3 de 46)")
print(F[F.DEV_t.abs() > 2].round(2).to_string(index=False))

# Calendario
Dd = Dd.copy(); Dd["date"] = M.days[Dd.index]
Dd["x"] = (Dd.rth_c - Dd.rth_o) / Dd.atr * 100
Dd["on"] = (Dd.rth_o - Dd.prev_c) / Dd.atr * 100
Dd["tdm"] = Dd.groupby([Dd.date.dt.year, Dd.date.dt.month]).cumcount() + 1
Dd["tdm_r"] = Dd.groupby([Dd.date.dt.year, Dd.date.dt.month]).cumcount(ascending=False) + 1
Dd["opex"] = (Dd.date.dt.dayofweek == 4) & Dd.date.dt.day.between(15, 21)
rows = []
tests = {**{f"{n} RTH": (Dd.dow == k, "x") for k, n in enumerate(["Lun", "Mar", "Mié", "Jue", "Vie"])},
         **{f"{n} overnight": (Dd.dow == k, "on") for k, n in enumerate(["Lun", "Mar", "Mié", "Jue", "Vie"])},
         "todos RTH": (Dd.dow >= 0, "x"), "todos overnight": (Dd.dow >= 0, "on"),
         "últ. día mes RTH": (Dd.tdm_r == 1, "x"), "1-3 del mes RTH": (Dd.tdm <= 3, "x"), "OPEX RTH": (Dd.opex, "x"),
         "últ. día mes ON": (Dd.tdm_r == 1, "on"), "1-3 del mes ON": (Dd.tdm <= 3, "on")}
for name, (mask, col) in tests.items():
    r = {"prueba": name}
    for tag, a, b in PERIODOS_15Y:
        x = Dd.loc[mask & Dd.date.between(a, b), col].dropna()
        r[f"{tag}_atr%"] = x.mean(); r[f"{tag}_t"] = x.mean() / (x.std() / np.sqrt(len(x))); r[f"{tag}_n"] = len(x)
    rows.append(r)
C = pd.DataFrame(rows); C.to_csv(os.path.join(RES_DIR, "f5_15y_calendario.csv"), index=False)
print("\n=== Calendario (% ATR) ===")
print(C.round(2).to_string(index=False))
