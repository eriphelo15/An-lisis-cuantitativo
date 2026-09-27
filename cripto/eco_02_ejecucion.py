"""Candidatos de eco_01: corto a nuevos listados (7 d) y corto tras pump > 50 % (3 d).
Ejecución realista en el PERPETUO de Binance: precio del perpetuo, funding cobrado/pagado, costos,
y retorno ajustado al mercado (índice equiponderado de altcoins y BTC)."""
import glob, io, zipfile
import numpy as np
import pandas as pd
import eco_base as e

C = 0.001
fut = e.panel("fut", "1d"); fut["sym"] = fut.sym.astype(str)
FP = fut.pivot(index="t", columns="sym", values="c")
spot = e.panel("spot", "1d"); spot["sym"] = spot.sym.astype(str)
spot = spot[~spot.sym.str.contains(r"(?:UP|DOWN|BULL|BEAR)USDT$")]
SP = spot.pivot(index="t", columns="sym", values="c")
SQ = spot.pivot(index="t", columns="sym", values="qv")
# índice equiponderado de altcoins líquidas (sin BTC ni estables)
Rs = SP.pct_change(fill_method=None).clip(-0.9, 3)
liq = SQ.rolling(30, min_periods=10).mean().shift(1) > 1e6
alt = Rs.where(liq).drop(columns=["BTCUSDT"], errors="ignore").mean(axis=1)
ALT = (1 + alt.fillna(0)).cumprod()
BTC = SP["BTCUSDT"]

fr = []
for f in glob.glob("/home/user/data/cripto/eco/fr/*.zip"):
    try:
        z = zipfile.ZipFile(f); d = pd.read_csv(z.open(z.namelist()[0]))
    except Exception:
        continue
    d["sym"] = f.split("/")[-1].rsplit("-", 2)[0]
    fr.append(d)
FR = pd.concat(fr)
FR["t"] = pd.to_datetime(FR.calc_time, unit="ms", utc=True)
FR = {s: g.set_index("t")["last_funding_rate"].sort_index() for s, g in FR.groupby("sym")}
futset = set(FP.columns)


def perp(sym):
    b = sym[:-4]
    for c in [sym, "1000" + sym, "1000000" + b + "USDT", "1M" + sym]:
        if c in futset:
            return c


def corto(sym, t_in, dias):
    p = perp(sym)
    if p is None:
        return None
    s = FP[p].dropna()
    if t_in not in s.index:
        return None                                   # el perpetuo aún no existía
    t_out = t_in + pd.Timedelta(days=dias)
    s2 = s.loc[:t_out]
    p_in, p_out = s.loc[t_in], s2.iloc[-1]            # si se retiró, último precio
    f = FR.get(p)
    fund = f.loc[(f.index > t_in + pd.Timedelta("23h59min")) & (f.index <= t_out + pd.Timedelta("23h59min"))].sum() if f is not None else 0.0
    bruto = -(p_out / p_in - 1)
    a = ALT.reindex([t_in, t_out], method="ffill").values
    b = BTC.reindex([t_in, t_out], method="ffill").values
    return dict(perp=p, bruto=bruto, funding=fund, neto=bruto + fund - 2 * C,
                vs_alt=bruto + fund - 2 * C + (a[1] / a[0] - 1),        # corto moneda + largo índice
                vs_btc=bruto + fund - 2 * C + (b[1] / b[0] - 1),
                peor_intra=(s2.max() / p_in - 1))                       # peor subida (contra el corto) al cierre


def reporte(nombre, D):
    D["per"] = np.where(D.t <= pd.Timestamp("2022-12-31", tz="UTC"), "DEV", "VAL")
    print(f"\n=== {nombre}")
    for p in ["DEV", "VAL"]:
        x = D[D.per == p]
        if len(x) < 3:
            print(f"  {p}: n={len(x)}"); continue
        t = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v))
        print(f"  {p}: n={len(x):3d} | neto {x.neto.mean():+.1%} (t {t(x.neto):+.1f}, WR {(x.neto>0).mean():.0%}, mediana {x.neto.median():+.1%})"
              f" | funding medio {x.funding.mean():+.2%} | vs índice alts {x.vs_alt.mean():+.1%} (t {t(x.vs_alt):+.1f})"
              f" | vs BTC {x.vs_btc.mean():+.1%} (t {t(x.vs_btc):+.1f})"
              f" | peor operación {x.neto.min():+.0%} | ops con pérdida > 30%: {(x.neto < -0.3).mean():.0%}")
    y = D.groupby(D.t.dt.year).neto.agg(["count", "mean", lambda v: (v > 0).mean()])
    y.columns = ["n", "media", "WR"]
    print("  por año:", " | ".join(f"{i}: n{int(r.n)} {r.media:+.1%} WR{r.WR:.0%}" for i, r in y.iterrows()))


L = pd.read_csv("res_eco_listados.csv", parse_dates=["t0"])
cob = []
res = []
for r in L.itertuples():
    t_in = r.t0 if r.t0.tzinfo else r.t0.tz_localize("UTC")
    o = corto(r.sym, t_in, 7)
    cob.append(o is not None)
    if o:
        res.append(dict(sym=r.sym, t=t_in, meme=r.meme, **o))
D1 = pd.DataFrame(res)
print("Nuevos listados con perpetuo disponible el día 1:", sum(cob), "de", len(cob))
reporte("CORTO a nuevo listado spot: entrar al cierre del día 1 en el perpetuo, salir a los 7 días", D1)
D1.to_csv("res_eco_corto_listados.csv", index=False)

E = pd.read_csv("res_eco_pumps.csv", parse_dates=["t"])
for u, dias in [(0.5, 3), (0.5, 7), (1.0, 3)]:
    x = E[(E.u == u)]
    res = []
    for r in x.itertuples():
        o = corto(r.sym, r.t, dias)
        if o:
            res.append(dict(sym=r.sym, t=r.t, meme=r.meme, **o))
    D = pd.DataFrame(res)
    print(f"\npumps >{u:.0%}: {len(x)} eventos, {len(D)} con perpetuo")
    reporte(f"CORTO tras día de pump > {u:.0%}: entrar al cierre, salir a los {dias} días", D)
    D.to_csv(f"res_eco_corto_pump_{int(u*100)}_{dias}d.csv", index=False)
