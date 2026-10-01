"""Ronda 13 (pre-registro en HIPOTESIS_SELECCION.md): E4 de Edu — precio del gap frente al precio de la última colocación.
Paso 'descargar': baja la portada de cada folleto 424B1/4/5 y extrae el precio. Paso 'medir': cruza con el setup base."""
import glob, html, json, os, re, sys, time, urllib.request
import numpy as np
import pandas as pd
from scipy import stats

S, D = "/home/user/data/sec", "/home/user/data/smallcaps"
P = f"{S}/prosp"
UA = {"User-Agent": "research eriphelo15 contact@example.com"}
FORMS = ("424B1", "424B4", "424B5")


def eventos():
    R = pd.read_csv("res_18_precio_real.csv")
    g = R[(R.gap >= .5) & (R.precio >= 1) & (~R.ambiguo)].copy()
    tk = json.load(open(f"{S}/tickers.json"))
    t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
    g["cik"] = g.sym.map(t2c).astype(int)
    g["date"] = pd.to_datetime(g.date)
    subs = {}
    for f in glob.glob(f"{S}/subs/*.parquet"):
        x = pd.read_parquet(f)
        x = x[x.form.isin(FORMS)].copy()
        if len(x):
            x["t"] = pd.to_datetime(x.acceptanceDateTime, utc=True, errors="coerce").dt.tz_convert("America/New_York").dt.tz_localize(None)
            subs[int(x.cik.iloc[0])] = x.dropna(subset=["t"]).sort_values("t")
    filas = []
    for r in g.itertuples():
        x = subs.get(r.cik)
        pc = (r.date - pd.offsets.BDay(1)) + pd.Timedelta(hours=16)
        y = x[(x.t < pc) & (x.t >= pc - pd.Timedelta(days=365))] if x is not None else None
        if y is None or y.empty:
            filas.append(dict(sym=r.sym, date=r.date, acc=None)); continue
        u = y.iloc[-1]
        filas.append(dict(sym=r.sym, date=r.date, acc=u.accessionNumber, form=u.form, t_col=u.t, cik=r.cik, doc=u.primaryDocument))
    return g, pd.DataFrame(filas)


def texto(cik, acc, doc):
    f = f"{P}/{acc}.txt"
    if os.path.exists(f):
        return open(f).read()
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}"
    for k in range(4):
        try:
            h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()[:700000].decode("utf-8", "ignore")
            time.sleep(0.13)
            h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
            t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()[:120000]
            open(f, "w").write(t)
            return t
        except Exception:
            time.sleep(2 * (k + 1))
    return None


NUM = r"\$\s?([0-9]{1,4}(?:,[0-9]{3})*(?:\.[0-9]{1,6})?)"
PATS = [
    r"(?:combined |initial )?(?:public )?offering price (?:of|is|equal to|will be)?\s*(?:US)?" + NUM + r"\s*per (?:share|ADS|American Depositary Share|unit|common unit|ordinary share|Class A)",
    r"(?:at|for) a (?:combined |sale )?price (?:of )?(?:US)?" + NUM + r"\s*per (?:share|ADS|unit|ordinary share)",
    r"(?:price to (?:the )?public|public offering price)[^$]{0,80}?" + NUM + r"\s*per (?:share|ADS|unit)",
]
# precio "supuesto" de un folleto ATM (assumed / indicative / assuming sales) no es una colocación con precio
SUPUESTO = re.compile(r"assum|indicative|illustrat|hypothetical|for example|non-affiliates|agreed to purchase|completed|consummated|"
                      r"closed (?:our|its|an?)|repurchas|selling (?:stock|share|security) ?holders|were to sell", re.I)   # 160 car. antes
CERCA = re.compile(r"exercis|concession|underwriting discount|entitles the holder|Junior Participating|Rights Agreement|Subscription Right|conversion price", re.I)  # 60 car. antes
NOMINAL = re.compile(r"par value", re.I)                                                                           # 25 car. antes


def precio(t):
    if not t:
        return None, None, "sin texto"
    atm = bool(re.search(r"at[- ]the[- ]market|“at the market”|\"at the market\"", t[:25000], re.I))
    for lim in (20000, 60000):            # primero la portada
        cab = t[:lim]
        for i, p in enumerate(PATS):
            for m in re.finditer(p, cab, re.I):
                a = max(0, m.start() - 160)
                ctx = cab[a:m.end() + 40]
                v = float(m.group(1).replace(",", ""))
                if (SUPUESTO.search(cab[max(0, m.start() - 160):m.end()]) or CERCA.search(cab[max(0, m.start() - 60):m.end()])
                        or NOMINAL.search(cab[max(0, m.start() - 25):m.end()])):
                    continue
                if i == 1 and re.search(r"warrant", cab[max(0, m.start() - 80):m.start()], re.I):
                    continue                     # "warrants to purchase one share at a price of $11.50" = precio de ejercicio (SPAC)
                if 0.01 <= v < 500:
                    return v, ctx, f"patron{i}"
    return None, None, "ATM" if atm else "sin frase"


MESES = "January|February|March|April|May|June|July|August|September|October|November|December"
FECHA = r"((?:" + MESES + r")\s+\d{1,2},\s+\d{4})"


def mercado(t, t_col):
    """(fecha, precio) del último precio de mercado que cita el folleto ("last reported sale price … on [fecha] was $X")."""
    if not t:
        return None, None, None
    mejor = None
    for m in re.finditer(r"(?:last (?:reported )?sale price|closing (?:sale |bid )?price|last reported (?:closing )?price)", t[:80000], re.I):
        ctx = t[max(0, m.start() - 160):m.end() + 260]
        d = re.search(FECHA, ctx); p = re.search(NUM + r"\s*per (?:share|ADS|ordinary share|American Depositary Share)", ctx[160:], re.I)
        if not (d and p):
            continue
        try:
            fe = pd.to_datetime(d.group(1))
        except Exception:
            continue
        v = float(p.group(1).replace(",", ""))
        dias = (t_col.normalize() - fe).days
        if 0 <= dias <= 60 and v > 0 and (mejor is None or dias < mejor[3]):
            mejor = (fe, v, ctx, dias)
    return (mejor[0], mejor[1], mejor[2]) if mejor else (None, None, None)


if __name__ == "__main__":
    g, C = eventos()
    if sys.argv[1] == "descargar":
        U = C.dropna(subset=["acc"]).drop_duplicates("acc")
        print("folletos:", len(U), flush=True)
        for i, r in enumerate(U.itertuples()):
            texto(r.cik, r.acc, r.doc)
            if i % 50 == 0:
                print(i, r.sym, r.acc, flush=True)
        print("FIN", flush=True)
    elif sys.argv[1] == "extraer":
        out = []
        for r in C.dropna(subset=["acc"]).drop_duplicates("acc").itertuples():
            tx = texto(r.cik, r.acc, r.doc)
            v, frase, como = precio(tx)
            fm, pm, fr_m = mercado(tx, r.t_col)
            out.append(dict(acc=r.acc, sym=r.sym, form=r.form, t_col=r.t_col, precio_col=v, como=como, frase=frase,
                            fecha_mercado=fm, precio_mercado=pm, frase_mercado=fr_m,
                            url=f"https://www.sec.gov/Archives/edgar/data/{int(r.cik)}/{r.acc.replace('-', '')}/{r.doc}"))
        X = pd.DataFrame(out); X.to_csv("res_28_colocaciones.csv", index=False)
        print(X.como.value_counts().to_dict())
    elif sys.argv[1] == "medir":
        X = pd.read_csv("res_28_colocaciones.csv", parse_dates=["t_col"])
        DI = pd.concat([pd.read_parquet(f, columns=["Date", "Close", "sym"]) for f in glob.glob(f"{D}/diario/*.parquet")])
        DI["Date"] = pd.to_datetime(DI.Date); DI = {k: v.set_index("Date").Close.sort_index() for k, v in DI.groupby("sym")}
        X["fecha_mercado"] = pd.to_datetime(X.fecha_mercado)
        M = C.merge(X[["acc", "precio_col", "como", "frase", "url", "fecha_mercado", "precio_mercado"]], on="acc", how="left").merge(
            g[["sym", "date", "open", "precio", "R", "per", "gap"]], on=["sym", "date"])
        def k_de(r):
            if pd.isna(r.precio_col) or pd.isna(r.precio_mercado) or r.sym not in DI:
                return np.nan
            c = DI[r.sym].loc[:r.fecha_mercado].dropna()
            if c.empty or (r.fecha_mercado - c.index[-1]).days > 5:
                return np.nan
            return c.iloc[-1] / r.precio_mercado
        M["k"] = M.apply(k_de, axis=1)
        M.loc[~(M.precio_col / M.precio_mercado).between(0.3, 1.3), "k"] = np.nan    # filtro de calidad del pre-registro
        M["precio_col_aj"] = M.precio_col * M.k
        M["amb_split"] = False
        M["ratio"] = M.open / M.precio_col_aj
        M["grupo"] = np.where(M.acc.isna(), "sin colocación 365 d", np.where(M.amb_split, "split ambiguo",
                     np.where(M.precio_col.isna(), "colocación sin precio (ATM / ilegible)",
                     np.where(M.k.isna(), "con precio, sin precio de mercado comparable", "con precio"))))
        M.to_csv("res_28_e4.csv", index=False)

        def met(v):
            v = v.dropna(); gg, p = v[v > 0], v[v <= 0]
            return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=gg.mean(), perd=p.mean(),
                                  PF=gg.sum() / -p.sum() if p.sum() < 0 else np.nan, dolares=20 * v.sum()))
        print("grupos:\n", M.groupby(["grupo", "per"]).R.apply(met).unstack().round(3).to_string())
        W = M[M.grupo == "con precio"].copy()
        W["tramo"] = pd.cut(W.ratio, [0, 1, 1.5, 2, 4, np.inf], right=False, labels=["< 1", "1-1.5", "1.5-2", "2-4", "≥ 4"])
        print("\ntramos del ratio (apertura ÷ precio de la colocación):\n", W.groupby(["tramo", "per"], observed=True).R.apply(met).unstack().round(3).to_string())
        res = []
        for per in ("DEV 2015-21", "VAL 2022-26"):
            w = W[W.per == per]; a, b = w[w.ratio >= 2].R, w[w.ratio < 1].R
            t = stats.ttest_ind(a, b, equal_var=False)
            rho = stats.spearmanr(w.ratio, w.R)
            res.append(dict(per=per, n_alto=len(a), R_alto=a.mean(), n_bajo=len(b), R_bajo=b.mean(), dif=a.mean() - b.mean(),
                            t=t.statistic, p_t=t.pvalue / 2 if t.statistic > 0 else 1 - t.pvalue / 2,
                            rho=rho.statistic, p_rho=rho.pvalue / 2 if rho.statistic > 0 else 1 - rho.pvalue / 2))
        H = pd.DataFrame(res); print("\n", H.round(4).to_string(index=False))
        v = H.iloc[1]; d = H.iloc[0]
        ps = sorted([("HE4a", v.p_t, v.dif > 0 and d.dif > 0 and v.t > 2), ("HE4b", v.p_rho, v.rho > 0 and d.rho > 0)], key=lambda x: x[1])
        for k, (n, p, cond) in enumerate(ps):
            print(n, "p", round(p, 4), "umbral Holm", round(0.05 / (2 - k), 4), "→", "VALIDADA" if cond and p < 0.05 / (2 - k) else "NO validada")
            if not (cond and p < 0.05 / (2 - k)):
                break

