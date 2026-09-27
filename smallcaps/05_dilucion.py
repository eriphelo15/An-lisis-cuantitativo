"""Dilución en small caps con datos de la SEC (número de acciones de la portada de 10-K/10-Q, EDGAR XBRL frames).
A) Todas las empresas registradas en la SEC, incluidas las que ya dejaron de reportar (sin sesgo de supervivencia).
B) Los 8.604 gappers del estudio 02: acciones antes vs. 12 meses después, corrigiendo splits (Yahoo)."""
import glob, json, re
import numpy as np
import pandas as pd

S = "/home/user/data/sec"
D = "/home/user/data/smallcaps"


def frames(pat):
    fs = []
    for f in sorted(glob.glob(f"{S}/{pat}")):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if "data" not in j:
            continue
        x = pd.DataFrame(j["data"])
        fs.append(x)
    x = pd.concat(fs)
    x["end"] = pd.to_datetime(x["end"])
    return x.drop_duplicates(["cik", "end"])


SH = frames("CY*I.json")[["cik", "end", "val"]].rename(columns={"val": "acc"})
PF = frames("PF_CY*I.json")[["cik", "end", "val"]].rename(columns={"val": "pf"})
SH = SH[SH.acc > 0].sort_values(["cik", "end"])
print("empresas con número de acciones:", SH.cik.nunique(), "| observaciones:", len(SH))

# ---------------- A) año a año, por tamaño (public float del 10-K)
filas = []
ult = SH.groupby("cik").end.max()
for (cik, g) in SH.groupby("cik"):
    g = g.set_index("end").acc
    pf = PF[PF.cik == cik]
    for r in pf.itertuples():
        t0 = r.end
        a0 = g[(g.index > t0 - pd.Timedelta("120D")) & (g.index <= t0 + pd.Timedelta("120D"))]
        a1 = g[(g.index > t0 + pd.Timedelta("245D")) & (g.index <= t0 + pd.Timedelta("485D"))]
        if a0.empty:
            continue
        filas.append(dict(cik=cik, t0=t0, pf=r.pf, acc0=a0.iloc[0],
                          acc1=a1.iloc[-1] if len(a1) else np.nan,
                          sigue_2a=ult[cik] >= t0 + pd.Timedelta("700D")))
A = pd.DataFrame(filas)
A = A[(A.t0 >= "2014-01-01") & (A.t0 <= "2024-06-30")]
A["crec"] = A.acc1 / A.acc0
A["tam"] = pd.cut(A.pf, [0, 50e6, 300e6, 2e9, 1e15], labels=["< $50M", "$50-300M", "$300M-2B", "> $2B"])
print("\n=== A) Crecimiento del número de acciones en 12 meses, según el tamaño (public float) — todas las registradas en la SEC")
for tam, x in A.groupby("tam", observed=True):
    c = x.crec.dropna()
    sube = c[c >= 0.5]                                  # sin contaminación por contra-splits
    print(f"  {tam:9s} n={len(x):6d} | mediana {c.median()-1:+.0%} | diluye >20%: {(c>1.2).mean():.0%} | >100% (x2): {(c>2).mean():.0%}"
          f" | cae >50% (contra-split probable): {(c<0.5).mean():.0%} | deja de reportar en 2 años: {(~x.sigue_2a).mean():.0%}")
A.to_csv("/home/user/An-lisis-cuantitativo/smallcaps/res_05_dilucion_sec.csv", index=False)

# ---------------- B) gappers
tk = json.load(open(f"{S}/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
E = pd.read_parquet(f"{D}/eventos_gappers.parquet")
E["date"] = pd.to_datetime(E["date"])
sp = pd.read_parquet(f"{D}/splits.parquet")
sp["t"] = pd.to_datetime(sp["t"]).dt.tz_localize(None)
sh = {c: g.set_index("end").acc for c, g in SH.groupby("cik")}
res = []
for r in E.itertuples():
    c = t2c.get(r.sym)
    if c is None or c not in sh:
        continue
    g = sh[c]
    a0 = g[(g.index <= r.date) & (g.index > r.date - pd.Timedelta("150D"))]
    a1 = g[(g.index > r.date + pd.Timedelta("300D")) & (g.index <= r.date + pd.Timedelta("430D"))]
    if a0.empty or a1.empty:
        continue
    t0, t1 = a0.index[-1], a1.index[-1]
    s = sp[(sp.sym == r.sym) & (sp.t > t0) & (sp.t <= t1)]
    f = s.ratio.prod() if len(s) else 1.0
    res.append(dict(sym=r.sym, date=r.date, gap=r.gap, P=r.P, dil=(a1.iloc[-1] / f) / a0.iloc[-1], n_contra=int((s.ratio < 1).sum())))
B = pd.DataFrame(res)
print(f"\n=== B) Gappers: acciones 12 meses después vs. antes del gap (corrigiendo splits). Eventos con datos: {len(B)} de {len(E)}")
for nom, m in [("todos (gap >= 20%)", B.gap >= 0.2), ("gap 50-100%", (B.gap >= 0.5) & (B.gap < 1)), ("gap > 100%", B.gap >= 1)]:
    x = B[m]
    print(f"  {nom:18s} n={len(x):5d} | mediana de acciones x{x.dil.median():.2f} | diluye >20%: {(x.dil>1.2).mean():.0%}"
          f" | se multiplica x2+: {(x.dil>2).mean():.0%} | x5+: {(x.dil>5).mean():.0%} | con contra-split en ese año: {(x.n_contra>0).mean():.0%}")
for p, x in B.groupby("P"):
    print(f"  época {p}: n={len(x)} mediana x{x.dil.median():.2f}, x2+: {(x.dil>2).mean():.0%}")
B.to_csv("/home/user/An-lisis-cuantitativo/smallcaps/res_05_dilucion_gappers.csv", index=False)
print("\ncontra-splits (splits inversos) entre los 2.119 tickers gappers, 2014-2026:", int((sp.ratio < 1).sum()))
