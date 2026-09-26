"""E2 (después del listado), E5 (pumps y memecoins), E6 (momentum cruzado), E7 (lotería/supervivencia). Velas diarias spot."""
import re
import numpy as np
import pandas as pd
import eco_base as e

C = 0.001        # 0.10 % por lado
EXCL = re.compile(r".+(UP|DOWN|BULL|BEAR)USDT$|^(USDC|BUSD|TUSD|USDP|FDUSD|DAI|PAX|EUR|GBP|AUD|TRY|BRL|USD1|RLUSD|XUSD|UST|USTC|USDE|PYUSD|AEUR|EURI|BKRW|SUSD|U)USDT$")
d = e.panel("spot", "1d")
d = d[~d.sym.astype(str).str.match(EXCL)].copy()
d["sym"] = d.sym.astype(str)
d = d[~d.sym.str.contains(r"(UP|DOWN|BULL|BEAR)USDT$")]
d["b"] = d.sym.map(e.base)
d["meme"] = d.b.isin(e.MEMES)
P = d.pivot(index="t", columns="sym", values="c")
Q = d.pivot(index="t", columns="sym", values="qv")
fin = P.index[-1]
DEV_FIN = pd.Timestamp("2022-12-31", tz="UTC")
print("monedas:", P.shape[1], "| memecoins:", d[d.meme].sym.nunique())


def per(ts):
    return np.where(ts <= DEV_FIN, "DEV", "VAL")


def tstat(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan


# ---------------- E7 lotería y E2 después del listado
primer = P.apply(lambda s: s.first_valid_index())
ultimo = P.apply(lambda s: s.last_valid_index())
filas = []
btc = P["BTCUSDT"]
for s in P.columns:
    t0 = primer[s]
    if t0 <= pd.Timestamp("2017-09-01", tz="UTC"):
        continue                                    # monedas que ya existían al arrancar los datos
    serie = P[s].dropna()
    p0 = serie.iloc[0]                              # cierre del primer día
    r = dict(sym=s, meme=e.base(s) in e.MEMES, t0=t0, activo=ultimo[s] == fin,
             mult_final=serie.iloc[-1] / p0, mult_max=serie.max() / p0,
             btc_mult=btc.loc[serie.index[-1]] / btc.loc[t0] if t0 in btc.index else np.nan,
             vol0=Q.loc[t0, s])
    for k in [1, 7, 30, 90, 365]:
        r[f"r{k}"] = serie.iloc[k] / p0 - 1 if len(serie) > k else (serie.iloc[-1] / p0 - 1 if ultimo[s] != fin else np.nan)
    filas.append(r)
L = pd.DataFrame(filas)
L["per"] = per(L.t0)
L.to_csv("res_eco_listados.csv", index=False)
print("\n=== E7: comprar cada moneda nueva al cierre de su primer día en Binance y mantener hasta hoy / retiro")
print("monedas listadas:", len(L), "| ya retiradas:", (~L.activo).sum())
for nom, m in [("todas", L.index == L.index), ("memecoins", L.meme), ("no meme", ~L.meme)]:
    x = L[m]
    print(f"{nom:10s} n={len(x):4d}  pierde >90%: {(x.mult_final < 0.1).mean():.0%}  pierde >50%: {(x.mult_final < 0.5).mean():.0%}"
          f"  gana (x>1): {(x.mult_final > 1).mean():.0%}  x10 o más: {(x.mult_final >= 10).mean():.1%}"
          f"  mediana x{x.mult_final.median():.2f}  | llegó a x10 en algún momento: {(x.mult_max >= 10).mean():.1%}"
          f"  | le ganó a BTC: {(x.mult_final > x.btc_mult).mean():.0%}")

print("\n=== E2: retorno desde el cierre del día 1 (media, mediana, % que sube, t de un CORTO neto)")
for k in [1, 7, 30, 90, 365]:
    for p in ["DEV", "VAL"]:
        x = L.loc[L.per == p, f"r{k}"].dropna()
        corto = -x - 2 * C
        print(f"  +{k:3d} d {p}: n={len(x):3d} media {x.mean():+.1%}  mediana {x.median():+.1%}  sube {(x>0).mean():.0%}"
              f"  | corto neto media {corto.mean():+.1%} t {tstat(corto):+.1f}  WR corto {(corto>0).mean():.0%}")

# ---------------- E5 pumps
R = P.pct_change(fill_method=None)
edad = P.notna().cumsum()
volm = Q.rolling(30, min_periods=10).mean().shift(1)
Pf = P.ffill(limit=10)                        # moneda retirada: se usa su último precio
fwd = {k: Pf.shift(-k) / P - 1 for k in [1, 3, 7]}
ev = []
for umbral in [0.2, 0.5, 1.0]:
    m = (R > umbral) & (edad > 30) & (volm > 5e6)
    for t, s in zip(*np.where(m.values)):
        ts, sym = P.index[t], P.columns[s]
        ev.append(dict(u=umbral, t=ts, sym=sym, meme=e.base(sym) in e.MEMES, r0=R.iat[t, s],
                       **{f"f{k}": fwd[k].iat[t, s] for k in fwd}))
E = pd.DataFrame(ev)
E["per"] = per(E.t)
E.to_csv("res_eco_pumps.csv", index=False)
print("\n=== E5: tras un día de subida > umbral (monedas con volumen medio > $5M/día, > 30 días listadas)")
print("   retorno siguiente del precio (LARGO bruto); estrategia = la dirección que diga DEV, neta de costos")
for u in [0.2, 0.5, 1.0]:
    for g, gm in [("todas", None), ("meme", True), ("no meme", False)]:
        x = E[(E.u == u) & ((E.meme == gm) if gm is not None else True)]
        lin = f"  >{u:.0%} {g:8s}"
        for k in [1, 3, 7]:
            dv = x.loc[x.per == "DEV", f"f{k}"].dropna(); vl = x.loc[x.per == "VAL", f"f{k}"].dropna()
            sg = np.sign(dv.mean()) if len(dv) else 1
            lin += (f" | {k}d DEV {dv.mean():+.1%} (n{len(dv)}) VAL {vl.mean():+.1%} (n{len(vl)})"
                    f" estr.VAL {sg*vl.mean()-2*C:+.1%} t{tstat(sg*vl-2*C):+.1f}")
        print(lin)

# ---------------- E6 momentum cruzado semanal
lunes = P.index[P.index.dayofweek == 0]
Pw, Qw = P.loc[lunes], volm.loc[lunes]
Ew = edad.loc[lunes]
rw_next = Pw.shift(-1) / Pw - 1
# moneda retirada durante la semana: usar su último precio
Pff = P.ffill(limit=10).loc[lunes]
rw_next = rw_next.fillna(Pff.shift(-1) / Pw - 1)
res = []
for look in [1, 4]:
    past = Pw / Pw.shift(look) - 1
    for i in range(look, len(lunes) - 1):
        ok = (Qw.iloc[i] > 1e6) & (Ew.iloc[i] > 60) & past.iloc[i].notna() & rw_next.iloc[i].notna()
        if ok.sum() < 30:
            continue
        pr = past.iloc[i][ok]; nx = rw_next.iloc[i][ok].clip(-0.99, 5)
        q = pr.rank(pct=True)
        top, bot = nx[q >= 0.9].mean(), nx[q <= 0.1].mean()
        res.append(dict(look=look, t=lunes[i], top=top, bot=bot, ls=(top - bot) / 2 - 2 * C, n=ok.sum(),
                        mkt=nx.mean()))
W = pd.DataFrame(res)
W["per"] = per(W.t)
print("\n=== E6: momentum cruzado semanal (top 10% ganadoras vs bottom 10% perdedoras), por semana")
for look in [1, 4]:
    for p in ["DEV", "VAL"]:
        x = W[(W.look == look) & (W.per == p)]
        print(f"  pasado {look} sem {p}: semanas {len(x)}  top {x.top.mean():+.2%}  bottom {x.bot.mean():+.2%}  mercado {x.mkt.mean():+.2%}"
              f"  | L/S neto {x.ls.mean():+.2%}/sem t {tstat(x.ls):+.1f}  | reversión (corto top, largo bottom) neto {(-(x.top-x.bot)/2-2*C).mean():+.2%} t {tstat(-(x.top-x.bot)/2-2*C):+.1f}")
W.to_csv("res_eco_momentum.csv", index=False)
