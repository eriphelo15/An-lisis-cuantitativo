"""Panel completo de estadísticas de la estrategia overnight (15 años, neto de costos)."""
import numpy as np, pandas as pd, os, json
from motor import Motor
from lib import RES_DIR, COSTO_MKT_RT_PTS, PERIODOS_15Y, TICK
M = Motor("all"); df = M.df; s = M.smin; di = M.day_id
rth = (s >= 930) & (s < 1320)
g = df[rth].groupby(di[rth])
A = pd.DataFrame({"o": g.adj_open.first(), "c": g.adj_close.last(), "h": g.adj_high.max(), "l": g.adj_low.min(),
                  "raw_c": g.close.last(), "n": g.size()})
A = A[A.n >= 385].copy(); A["date"] = M.days[A.index]; A = A.reset_index(drop=True)
A["sma200"] = A.c.rolling(200).mean()
A["on_pts"] = A.o.shift(-1) - A.c
A["exit_date"] = A.date.shift(-1)
A["noches_cal"] = (A.exit_date - A.date).dt.days
A["dow"] = A.date.dt.dayofweek
A["ret_d"] = A.c.pct_change()
A["vol20"] = A.ret_d.rolling(20).std() * np.sqrt(252) * 100
A["rth_ret_hoy"] = (A.c - A.o) / A.raw_c * 1e4
# min adverso durante la noche (para MAE): low global entre 16:00 y 09:29 del día siguiente
lo_on = pd.Series(M.l).groupby(np.where(~rth, di, -1)).min()
adj_off = (df.adj_close - df.close).groupby(di).last()   # offset back-adjust por día
A = A.dropna(subset=["on_pts"])
VARS = {
    "A · Todas las noches": A.index == A.index,
    "B · Sin fines de semana": A.noches_cal == 1,
    "C · Solo si cierre > SMA200": A.c > A.sma200,
    "D · B + C combinadas": (A.noches_cal == 1) & (A.c > A.sma200),
}
def dd_stats(eq_bp, dates):
    peak = np.maximum.accumulate(np.r_[0, eq_bp])[1:]; dd = peak - eq_bp
    i = int(np.argmax(dd)); j = int(np.argmax(eq_bp[:i + 1] == peak[i])) if i > 0 else 0
    # duración más larga bajo el máximo (en días de calendario)
    under = dd > 0; longest = 0; start = None
    for k in range(len(dd)):
        if under[k] and start is None: start = k
        if (not under[k] or k == len(dd) - 1) and start is not None:
            longest = max(longest, (dates.iloc[k] - dates.iloc[start]).days); start = None
    return float(dd.max()), dates.iloc[j].strftime("%Y-%m-%d"), dates.iloc[i].strftime("%Y-%m-%d"), longest
def streaks(x):
    best = worst = cur_w = cur_l = 0
    for v in x:
        if v > 0: cur_w += 1; cur_l = 0
        else: cur_l += 1; cur_w = 0
        best = max(best, cur_w); worst = max(worst, cur_l)
    return best, worst
def core(X, extra_cost_ticks=0):
    cost = COSTO_MKT_RT_PTS + 2 * extra_cost_ticks * TICK
    pts = X.on_pts - cost
    bp = pts / X.raw_c * 1e4
    w, l = bp[bp > 0], bp[bp <= 0]
    years = (X.date.iloc[-1] - X.date.iloc[0]).days / 365.25
    eq = bp.cumsum().to_numpy()
    mdd, dd_from, dd_to, dd_dur = dd_stats(eq, X.date.reset_index(drop=True))
    ann_ret = bp.sum() / years
    downside = bp[bp < 0].std() if (bp < 0).any() else np.nan
    per_year_n = len(bp) / years
    ws, ls = streaks(bp.to_numpy())
    return dict(trades=len(bp), trades_año=per_year_n, wr=(bp > 0).mean(), avg_win_bp=w.mean(), avg_loss_bp=l.mean(),
                rr=w.mean() / -l.mean(), pf=w.sum() / -l.sum(), exp_bp=bp.mean(), exp_pts_hoy=bp.mean() * 2.5,
                exp_usd_nq_hoy=bp.mean() * 2.5 * 20, exp_usd_mnq_hoy=bp.mean() * 2.5 * 2, mediana_bp=bp.median(),
                t=bp.mean() / (bp.std() / np.sqrt(len(bp))), sharpe=bp.mean() / bp.std() * np.sqrt(per_year_n),
                sortino=bp.mean() / downside * np.sqrt(per_year_n), ret_anual_pct=ann_ret / 100, maxdd_pct=mdd / 100,
                calmar=(ann_ret / 100) / (mdd / 100), dd_desde=dd_from, dd_hasta=dd_to, dd_dias_max_bajo_agua=dd_dur,
                racha_ganadora=ws, racha_perdedora=ls, mejor_bp=bp.max(), peor_bp=bp.min(),
                p1=bp.quantile(.01), p5=bp.quantile(.05), p95=bp.quantile(.95), p99=bp.quantile(.99),
                asimetria=bp.skew(), curtosis=bp.kurt(),
                exposicion_pct=((X.exit_date + pd.Timedelta(hours=9.5)) - (X.date + pd.Timedelta(hours=16))).sum() / (A.exit_date.iloc[-1] - A.date.iloc[0]) * 100,
                noches_peor_que_menos2pct=int((bp < -200).sum()))
out = {"variantes": {}, "años": {}, "regimenes": {}, "dow": {}, "mes": {}, "costos": {}, "dd_top": {}, "curvas": {}}
bh = A.c.diff() / A.raw_c.shift() * 1e4
for name, mask in VARS.items():
    X = A[mask].copy()
    out["variantes"][name] = core(X)
    cost = COSTO_MKT_RT_PTS
    X["bp"] = (X.on_pts - cost) / X.raw_c * 1e4
    # años
    Y = X.groupby(X.date.dt.year).bp.agg(trades="size", wr=lambda x: (x > 0).mean(), ret_pct=lambda x: x.sum() / 100,
        pf=lambda x: x[x > 0].sum() / -x[x <= 0].sum(), peor_noche_pct=lambda x: x.min() / 100)
    Y["bh_pct"] = bh.groupby(A.date.dt.year).sum() / 100
    def ydd(x):
        e = x.cumsum().to_numpy(); return float((np.maximum.accumulate(np.r_[0, e])[1:] - e).max()) / 100
    Y["maxdd_pct"] = X.groupby(X.date.dt.year).bp.apply(ydd)
    out["años"][name] = Y.round(3).reset_index().rename(columns={"date": "año"}).to_dict("records")
    # regímenes
    R = {}
    def agg(m, lab):
        x = X.loc[m, "bp"]
        if len(x) < 20: return
        R[lab] = dict(trades=len(x), wr=(x > 0).mean(), exp_bp=x.mean(), pf=x[x > 0].sum() / -x[x <= 0].sum(),
                      t=x.mean() / (x.std() / np.sqrt(len(x))))
    for tag, a, b in PERIODOS_15Y: agg(X.date.between(a, b), f"Periodo {tag} ({a[:4]}-{b[:4]})")
    agg(X.c > X.sma200, "Tendencia: sobre SMA200"); agg(X.c <= X.sma200, "Tendencia: bajo SMA200")
    q = A.vol20.quantile([1 / 3, 2 / 3]).to_numpy()
    agg(X.vol20 <= q[0], f"Volatilidad baja (<{q[0]:.0f}% anual)"); agg((X.vol20 > q[0]) & (X.vol20 <= q[1]), "Volatilidad media")
    agg(X.vol20 > q[1], f"Volatilidad alta (>{q[1]:.0f}% anual)")
    bull = Y.index[Y.bh_pct > 0]; agg(X.date.dt.year.isin(bull), "Años alcistas del NQ"); agg(~X.date.dt.year.isin(bull), "Años bajistas del NQ")
    agg(X.rth_ret_hoy < 0, "Día RTH previo bajista"); agg(X.rth_ret_hoy >= 0, "Día RTH previo alcista")
    agg(X.rth_ret_hoy < -100, "Día RTH previo cae > 1%"); agg(X.rth_ret_hoy > 100, "Día RTH previo sube > 1%")
    out["regimenes"][name] = R
    out["dow"][name] = X.groupby("dow").bp.agg(trades="size", wr=lambda x: (x > 0).mean(), exp_bp="mean").round(3).rename(index=dict(enumerate(["Lun→Mar", "Mar→Mié", "Mié→Jue", "Jue→Vie", "Vie→Lun"]))).reset_index().to_dict("records")
    out["mes"][name] = X.groupby(X.date.dt.month).bp.agg(trades="size", wr=lambda x: (x > 0).mean(), exp_bp="mean").round(3).reset_index().rename(columns={"date": "mes"}).to_dict("records")
    out["costos"][name] = {f"+{k} ticks/lado": core(A[mask], k)["exp_bp"] for k in [0, 1, 2, 4, 8]}
    # top drawdowns
    e = X.bp.cumsum().to_numpy(); peak = np.maximum.accumulate(e); dates = X.date.reset_index(drop=True)
    eps = []; k = 0
    while k < len(e):
        if e[k] < peak[k]:
            st = k - 1
            while k < len(e) and e[k] < peak[st if st >= 0 else 0]: k += 1
            seg = e[st + 1:k]; tr = st + 1 + int(np.argmin(seg))
            eps.append(dict(inicio=dates[max(st, 0)].strftime("%Y-%m-%d"), valle=dates[tr].strftime("%Y-%m-%d"),
                            fin=dates[k].strftime("%Y-%m-%d") if k < len(e) else "sin recuperar", prof_pct=(peak[max(st, 0)] - e[tr]) / 100,
                            dias=((dates[k] if k < len(e) else dates.iloc[-1]) - dates[max(st, 0)]).days))
        k += 1
    out["dd_top"][name] = sorted(eps, key=lambda d: -d["prof_pct"])[:5]
    out["curvas"][name] = [[d.strftime("%Y-%m-%d"), round(v / 100, 2)] for d, v in zip(X.date, X.bp.cumsum())][::3]
out["curvas"]["Buy & hold"] = [[d.strftime("%Y-%m-%d"), round(v / 100, 2)] for d, v in zip(A.date[1:], bh.dropna().cumsum())][::3]
bhx = bh.dropna(); yrs = (A.date.iloc[-1] - A.date.iloc[0]).days / 365.25
e = bhx.cumsum().to_numpy(); out["bh"] = dict(ret_anual_pct=bhx.sum() / yrs / 100, maxdd_pct=float((np.maximum.accumulate(e) - e).max()) / 100,
    sharpe=bhx.mean() / bhx.std() * np.sqrt(252), wr=(bhx > 0).mean())
json.dump(out, open(os.path.join(RES_DIR, "f8_overnight_panel.json"), "w"), default=float)
pd.set_option("display.width", 250)
print(pd.DataFrame(out["variantes"]).round(3).to_string())
print("\nBuy&hold:", {k: round(v, 3) for k, v in out["bh"].items()})
for n in VARS:
    print("\n==", n); print(pd.DataFrame(out["años"][n]).to_string(index=False))
    print(pd.DataFrame(out["regimenes"][n]).T.round(3).to_string())
    print(pd.DataFrame(out["dow"][n]).to_string(index=False)); print("costos:", {k: round(v, 2) for k, v in out["costos"][n].items()})
    print(pd.DataFrame(out["dd_top"][n]).to_string(index=False))
