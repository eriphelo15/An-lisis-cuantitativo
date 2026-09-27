"""Fase 2e — 'Comprar la caída en tendencia' como estrategia sin solapamiento + robustez.
Entrada: cierre RTH (15:59) del día señal. Salida: cierre RTH cuando close > high de ayer
(salida Connors) o tras max_dias. Stop catastrófico opcional en múltiplos de ATR (al cierre)."""
import numpy as np, pandas as pd, os, sys, itertools
from motor import Motor
from lib import RES_DIR, COSTO_MKT_RT_PTS, PUNTO_USD

def daily(split):
    M = Motor(split); df = M.df
    rth = (M.smin >= 930) & (M.smin < 1320)
    g = df[rth].groupby(M.day_id[rth])
    A = pd.DataFrame({"o": g.adj_open.first(), "h": g.adj_high.max(), "l": g.adj_low.min(), "c": g.adj_close.last(),
                      "raw_c": g.close.last(), "n": g.size()})
    A = A[A.n >= 385].copy(); A["date"] = M.days[A.index]
    return A.reset_index(drop=True)

def backtest(A, sma=50, streak=2, max_dias=5, salida="connors", stop_atr=None, ibs_max=None):
    c = A.c.to_numpy(); h = A.h.to_numpy(); l = A.l.to_numpy()
    d = np.diff(c, prepend=np.nan)
    dn = (d < 0).astype(int)
    st = np.zeros(len(c), int)
    for i in range(1, len(c)): st[i] = st[i-1] + 1 if dn[i] else 0
    s = pd.Series(c).rolling(sma).mean().to_numpy()
    atr = pd.Series(h - l).rolling(14).mean().to_numpy()
    ibs = (c - l) / np.where(h > l, h - l, np.nan)
    trades = []; i = sma
    while i < len(c) - 1:
        sig = st[i] >= streak and c[i] > s[i]
        if ibs_max is not None: sig = sig and ibs[i] < ibs_max
        if not sig: i += 1; continue
        e = c[i]; j = i + 1; exit_px = None
        while j < len(c):
            if stop_atr is not None and c[j] < e - stop_atr * atr[i]:
                exit_px = c[j]; break
            if salida == "connors" and c[j] > h[j-1]: exit_px = c[j]; break
            if j - i >= max_dias: exit_px = c[j]; break
            j += 1
        if exit_px is None: break
        trades.append(dict(entry_date=A.date[i], exit_date=A.date[j], dias=j - i, pnl=exit_px - e - COSTO_MKT_RT_PTS,
                           mae=(l[i+1:j+1].min() - e)))
        i = j + 1 if salida else j
    return pd.DataFrame(trades)

def resume(T, dias_tot):
    if len(T) == 0: return {}
    p = T.pnl; eq = p.cumsum()
    dd = (eq.cummax().clip(lower=0) - eq).max()
    yrs = p.groupby(T.entry_date.dt.year).sum()
    exposure = T.dias.sum() / dias_tot
    return dict(n=len(T), wr=(p > 0).mean(), exp=p.mean(), pf=p[p > 0].sum() / -p[p <= 0].sum(), total=p.sum(),
                t=p.mean() / (p.std() / np.sqrt(len(p))), maxdd=dd, peor=p.min(), exposicion=exposure,
                años_pos=int((yrs > 0).sum()), **{f"y{y}": v for y, v in yrs.items()})

if __name__ == "__main__":
    A = daily("dev")
    rows = []
    for sma, streak, md, sal in itertools.product([20, 50, 100], [1, 2, 3], [1, 2, 3, 5, 10], ["connors", "tiempo"]):
        T = backtest(A, sma, streak, md, sal)
        rows.append(dict(sma=sma, streak=streak, max_dias=md, salida=sal, **resume(T, len(A))))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(RES_DIR, "f2e_dip_trend_grid_dev.csv"), index=False)
    pd.set_option("display.width", 250)
    print("Grid (", len(R), "configs ) — ordenado por t:")
    print(R.sort_values("t", ascending=False).head(25).round(3).to_string(index=False))
    print("\nFracción de configs con t>2:", (R.t > 2).mean().round(3), " con exp>0:", (R.exp > 0).mean().round(3))
    print("\nPlateau: t medio por (sma, streak) con salida connors:")
    print(R[R.salida == "connors"].pivot_table(index="sma", columns="streak", values="t", aggfunc="mean").round(2))
    print("WR medio por (sma, streak) connors:")
    print(R[R.salida == "connors"].pivot_table(index="sma", columns="streak", values="wr", aggfunc="mean").round(3))
    # buy&hold referencia
    bh = A.c.iloc[-1] - A.c.iloc[50]
    print(f"\nReferencia buy&hold DEV (desde día 50): {bh:.0f} pts; exposición 100%")
