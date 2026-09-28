"""Validación de criterios de selección (pre-registro: HIPOTESIS_SELECCION.md).
Para cada gapper se reconstruye lo que EDGAR mostraba ANTES de las 9:30 del día del gap (hora de aceptación) y se mide
el resultado del corto. DEV 2015-2021 / VAL 2022-2026."""
import glob, json
import numpy as np
import pandas as pd
from scipy import stats

D = "/home/user/data/smallcaps"
S = "/home/user/data/sec"
COSTE = 0.01

E = pd.read_parquet(f"{D}/eventos_gappers.parquet").dropna(subset=["open", "high", "close"]).copy()
E["date"] = pd.to_datetime(E["date"])
tk = json.load(open(f"{S}/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
E["cik"] = E.sym.map(t2c)
E = E[E.cik.notna()].copy()
E["cik"] = E.cik.astype(int)

# ---------- documentos EDGAR con hora (acceptanceDateTime viene en UTC)
subs = {}
for f in glob.glob(f"{S}/subs/*.parquet"):
    x = pd.read_parquet(f)
    x["t"] = pd.to_datetime(x.acceptanceDateTime, utc=True, errors="coerce").dt.tz_convert("America/New_York").dt.tz_localize(None)
    subs[int(x.cik.iloc[0])] = x.dropna(subset=["t"]).sort_values("t")
E = E[E.cik.isin(subs)].copy()

# ---------- acciones en circulación (portada) para la capitalización
fr = []
for f in glob.glob(f"{S}/CY*I.json"):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if "data" in j:
        fr.append(pd.DataFrame(j["data"]))
SH = pd.concat(fr); SH["end"] = pd.to_datetime(SH["end"])
acc = {c: g.sort_values("end").set_index("end")["val"] for c, g in SH.groupby("cik")}

filas = []
for r in E.itertuples():
    x = subs[r.cik]
    corte = r.date + pd.Timedelta(hours=9, minutes=30)
    cierre_prev = (r.date - pd.offsets.BDay(1)) + pd.Timedelta(hours=16)
    antes = x[x.t < corte]
    ult = lambda dias: antes[antes.t >= corte - pd.Timedelta(days=dias)]
    f = antes.form.astype(str)
    s3 = ult(3 * 365).form.isin(["S-3", "S-3/A", "F-3", "F-3/A", "S-3ASR"]).any()
    p424_90 = ult(90).form.astype(str).str.startswith("424B").any()
    p424_365 = ult(365).form.astype(str).str.startswith("424B").sum()
    k8 = x[(x.t > cierre_prev) & (x.t < corte) & x.form.isin(["8-K", "8-K/A"])]
    its = ",".join(k8["items"].astype(str))
    if k8.empty:
        cat = "sin 8-K"
    elif "1.01" in its:
        cat = "8-K con acuerdo (1.01)"
    elif all(i.strip() in ("7.01", "8.01", "9.01", "") for i in its.split(",")):
        cat = "8-K solo nota de prensa (7.01/8.01)"
    else:
        cat = "8-K otros items"
    y = ult(365)
    k8y = y[y.form.isin(["8-K", "8-K/A"])]["items"].astype(str)
    rs = k8y.str.contains("5.03").any()
    aviso = k8y.str.contains("3.01").any()
    extranjera = f.isin(["20-F", "6-K", "20-F/A"]).any()
    a = acc.get(r.cik)
    sh = a[(a.index <= r.date) & (a.index > r.date - pd.Timedelta(days=200))] if a is not None else pd.Series(dtype=float)
    mcap = sh.iloc[-1] * r.open if len(sh) else np.nan
    # resultados del corto
    stop = r.open * 1.30
    if r.high >= stop:
        R = -(0.30 * 1.05 + 0.05 * 0 + COSTE) / 0.30        # salida en stop con 5 % de deslizamiento
        R = -((stop * 1.05 - r.open) / r.open + COSTE) / 0.30
    else:
        R = ((r.open - r.close) / r.open - COSTE) / 0.30
    filas.append(dict(sym=r.sym, date=r.date, gap=r.gap, sic2=str(x.sic.iloc[0])[:2], s3=s3, venta90=p424_90,
                      serie=p424_365 >= 3, cat=cat, rs_aviso=rs or aviso, extranjera=extranjera, mcap=mcap,
                      R=R, corto_pct=(r.open - r.close) / r.open - COSTE, mae=r.high / r.open - 1,
                      dia2=(r.close - r.n_c) / r.close if pd.notna(r.n_c) else np.nan))
X = pd.DataFrame(filas)
# día de tema: >=2 gappers (>=50 %) del mismo sector SIC-2 el mismo día
g50 = X[X.gap >= 0.5].groupby(["date", "sic2"]).size()
X["tema"] = [g50.get((d, s), 0) >= 2 if gp >= 0.5 else g50.get((d, s), 0) >= 1 for d, s, gp in zip(X.date, X.sic2, X.gap)]
X.loc[X.sic2.isin(["", "0", "00"]), "tema"] = False
X["sin8k"] = X.cat == "sin 8-K"
X["solo_pr"] = X.cat == "8-K solo nota de prensa (7.01/8.01)"
X["municion"] = X.venta90 | X.serie
X["A"] = X.municion & X.sin8k & ~X.tema
X["cap_menor30"] = X.mcap < 30e6
X["per"] = np.where(X.date.dt.year <= 2021, "DEV 2015-21", "VAL 2022-26")
X.to_csv("res_11_seleccion.csv", index=False)


def met(v):
    v = v.dropna()
    g, p = v[v > 0], v[v <= 0]
    return dict(n=len(v), esperanza_R=v.mean(), WR=(v > 0).mean(), gan_media_R=g.mean(), perd_media_R=p.mean(),
                PF=g.sum() / -p.sum() if len(p) and p.sum() < 0 else np.nan)


print("gappers con historial EDGAR:", len(X), "| DEV", (X.per == "DEV 2015-21").sum(), "| VAL", (X.per == "VAL 2022-26").sum())
hip = [("H1 shelf S-3", "s3", True), ("H2 venta 424B en 90 días", "venta90", True), ("H3 diluidor en serie (≥3 424B/año)", "serie", True),
       ("H4 sin 8-K antes de abrir", "sin8k", True), ("H5 8-K solo nota de prensa (vs 1.01)", "solo_pr", True),
       ("H6 contra-split o aviso de bolsa en 12 meses", "rs_aviso", True), ("H7 NO es día de tema", "tema", False),
       ("H8 capitalización < $30 M", "cap_menor30", None), ("H9 empresa extranjera", "extranjera", None),
       ("H10 combinación A", "A", True)]
out = []
for nom, col, mejor in hip:
    for per in ["DEV 2015-21", "VAL 2022-26"]:
        Z = X[X.per == per]
        if col == "solo_pr":
            Z = Z[Z.cat.isin(["8-K solo nota de prensa (7.01/8.01)", "8-K con acuerdo (1.01)"])]
        si = Z[Z[col] == (mejor if mejor is not None else True)]
        no = Z[Z[col] != (mejor if mejor is not None else True)]
        t = stats.ttest_ind(si.R, no.R, equal_var=False).statistic if len(si) > 2 and len(no) > 2 else np.nan
        a, b = met(si.R), met(no.R)
        out.append(dict(hipotesis=nom, periodo=per, n_cumple=a["n"], R_cumple=a["esperanza_R"], WR_cumple=a["WR"], PF_cumple=a["PF"],
                        gan_media=a["gan_media_R"], perd_media=a["perd_media_R"], n_resto=b["n"], R_resto=b["esperanza_R"],
                        PF_resto=b["PF"], dif_R=a["esperanza_R"] - b["esperanza_R"], t=t,
                        squeeze_cumple=(si.mae > .5).mean(), squeeze_resto=(no.mae > .5).mean(),
                        corto_pct_cumple=si.corto_pct.mean() * 100, dia2_cumple=si.dia2.mean() * 100, dia2_resto=no.dia2.mean() * 100))
O = pd.DataFrame(out)
O.to_csv("res_11_seleccion_resumen.csv", index=False)
pd.set_option("display.width", 250)
print(O[["hipotesis", "periodo", "n_cumple", "R_cumple", "WR_cumple", "PF_cumple", "n_resto", "R_resto", "PF_resto", "dif_R", "t", "squeeze_cumple", "squeeze_resto"]].round(3).to_string(index=False))
# Holm en VAL
v = O[(O.periodo == "VAL 2022-26") & ~O.hipotesis.str.startswith(("H8", "H9"))].copy()
v["p"] = 2 * (1 - stats.norm.cdf(v.t.abs()))
v = v.sort_values("p"); m = len(v)
v["holm_ok"] = [p < 0.05 / (m - i) for i, p in enumerate(v.p)]
v["holm_ok"] = v.holm_ok.cummin()
print("\nHolm (VAL):"); print(v[["hipotesis", "dif_R", "t", "p", "holm_ok"]].round(4).to_string(index=False))
