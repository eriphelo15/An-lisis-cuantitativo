"""Descarga el historial completo de documentos EDGAR (con hora de aceptación) de las empresas de los gappers."""
import json, os, time, urllib.request
import pandas as pd
H = {"User-Agent": "research eriphelo15 contact@example.com"}
OUT = "/home/user/data/sec/subs"
def get(u):
    for k in range(5):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read(); time.sleep(0.12); return json.loads(r)
        except Exception:
            time.sleep(2 * (k + 1))
    return None
tk = json.load(open("/home/user/data/sec/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
ciks = sorted({t2c[s] for s in E.sym.unique() if s in t2c})
print("empresas:", len(ciks))
cols = ["accessionNumber", "filingDate", "acceptanceDateTime", "form", "items", "primaryDocument"]
for i, c in enumerate(ciks):
    f = f"{OUT}/{c}.parquet"
    if os.path.exists(f):
        continue
    d = get(f"https://data.sec.gov/submissions/CIK{c:010d}.json")
    if not d:
        continue
    partes = [pd.DataFrame({k: d["filings"]["recent"].get(k, []) for k in cols})]
    for extra in d["filings"].get("files", []):
        x = get("https://data.sec.gov/submissions/" + extra["name"])
        if x:
            partes.append(pd.DataFrame({k: x.get(k, []) for k in cols}))
    df = pd.concat(partes)
    df["sic"] = d.get("sic", ""); df["cik"] = c; df["name"] = d.get("name", "")
    df.to_parquet(f)
    if i % 200 == 0:
        print(i, flush=True)
print("listo")
