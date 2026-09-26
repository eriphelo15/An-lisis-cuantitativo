"""E4 a fondo: corto en el perpetuo tras anuncio de retiro spot, con funding real, mitades de tiempo y anuncio de futuros."""
import glob, json, os, re, urllib.request, zipfile
import numpy as np
import pandas as pd
import eco_base as e
import eco_04_anuncios as a4

DIR = e.DIR
R = pd.read_csv("res_eco_anuncio_retiro.csv", parse_dates=["ts"])
R = R[R.fuente == "binance perp"]


def lee(f):
    try:
        z = zipfile.ZipFile(f); return pd.read_csv(z.open(z.namelist()[0]))
    except Exception:
        return None


fr = {}
for r in R.itertuples():
    p = a4.perp_de(r.tk)
    for m in {r.ts.strftime("%Y-%m"), (r.ts + pd.Timedelta("8D")).strftime("%Y-%m")}:
        f = f"{DIR}/fr/{p}-{m}.zip"
        if not os.path.exists(f):
            try:
                d = urllib.request.urlopen(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{p}/{p}-fundingRate-{m}.zip", timeout=30).read()
                open(f, "wb").write(d)
            except Exception:
                pass
    ds = [x for x in (lee(f) for f in glob.glob(f"{DIR}/fr/{p}-*.zip")) if x is not None]
    if ds:
        d = pd.concat(ds)
        fr[r.tk] = pd.Series(d.last_funding_rate.values, index=pd.to_datetime(d.calc_time, unit="ms", utc=True)).sort_index()

A = json.load(open(f"{DIR}/anuncios.json"))
fd = [(x["title"], pd.to_datetime(x["releaseDate"], unit="ms", utc=True)) for x in A if re.search(r"Futures Will (Delist|Close)", x["title"])]
out = []
for r in R.itertuples():
    t0 = r.ts.floor("1h")
    row = dict(tk=r.tk, ts=r.ts)
    f = fr.get(r.tk)
    for h in [1, 4, 24]:
        fund = f[(f.index > t0 + pd.Timedelta("1h")) & (f.index <= t0 + pd.Timedelta(hours=h + 1))].sum() if f is not None else np.nan
        row[f"c{h}"] = -getattr(r, f"r{h}") + fund - 0.002
        row[f"f{h}"] = fund
    m = [(t, ts) for t, ts in fd if re.search(rf"\b(1000)?{r.tk}USDT\b", t) and abs((ts - r.ts).total_seconds()) < 3 * 86400]
    row["fut_anuncio"] = m[0][1] if m else pd.NaT
    row["fut_titulo"] = m[0][0] if m else ""
    out.append(row)
X = pd.DataFrame(out).sort_values("ts")
print("con funding:", X.f4.notna().sum(), "de", len(X))
t = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v))
mid = X.ts.iloc[len(X) // 2]
for nom, x in [("todo", X), (f"1a mitad (<{mid.date()})", X[X.ts < mid]), ("2a mitad", X[X.ts >= mid])]:
    print(f"{nom} n{len(x)}: " + " | ".join(
        f'{h}h neto {x[f"c{h}"].mean():+.1%} t{t(x[f"c{h}"].dropna()):+.1f} WR{(x[f"c{h}"]>0).mean():.0%} funding {x[f"f{h}"].mean():+.2%}' for h in [1, 4, 24]))
print("\npeores 4h:\n", X.sort_values("c4").head(5)[["tk", "ts", "c4", "f4"]].to_string())
print("\nretiro del perpetuo anunciado cerca (±3 días):", X.fut_anuncio.notna().sum(), "de", len(X))
# liquidez del perpetuo en las 4 h siguientes (volumen en USDT por hora)
liq = []
for r in X.itertuples():
    p = a4.perp_de(r.tk)
    fs = sorted(glob.glob(f"{DIR}/k/futures_um_monthly_klines_{p}_1h_{p}-1h-{r.ts.strftime('%Y-%m')}.zip"))
    d = e._zip(fs[0]) if fs else None
    liq.append(d.set_index("t").qv.loc[r.ts.floor("1h"): r.ts.floor("1h") + pd.Timedelta("4h")].median() if d is not None else np.nan)
X["vol_hora"] = liq
print("volumen mediano por hora en el perpetuo tras el anuncio: $", f"{np.nanmedian(liq):,.0f}", "| p25 $", f"{np.nanpercentile(liq,25):,.0f}")
print("por año 4h:", X.groupby(X.ts.dt.year).c4.agg(["count", "mean"]).round(3).to_dict("index"))
X.to_csv("res_eco_retiro_corto.csv", index=False)
