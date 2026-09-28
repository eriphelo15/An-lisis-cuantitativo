"""Descarga el texto del catalizador (anexo EX-99 o documento principal) de los 8-K/6-K aceptados antes de la apertura del gap."""
import glob, html, json, os, re, time, urllib.request
import pandas as pd
H = {"User-Agent": "research eriphelo15 contact@example.com"}
OUT = "/home/user/data/sec/pr"
def get(u, texto=True):
    for k in range(5):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read(); time.sleep(0.12)
            return r.decode("utf-8", "ignore") if texto else json.loads(r)
        except Exception:
            time.sleep(2 * (k + 1))
    return None
def limpiar(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))
tk = json.load(open("/home/user/data/sec/tickers.json"))
t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
X = pd.read_csv("smallcaps/res_11_seleccion.csv", parse_dates=["date"])
subs = {}
for f in glob.glob("/home/user/data/sec/subs/*.parquet"):
    x = pd.read_parquet(f)
    x["t"] = pd.to_datetime(x.acceptanceDateTime, utc=True, errors="coerce").dt.tz_convert("America/New_York").dt.tz_localize(None)
    subs[int(x.cik.iloc[0])] = x
n = 0
for r in X.itertuples():
    c = t2c.get(r.sym); x = subs.get(c)
    if x is None:
        continue
    corte = r.date + pd.Timedelta(hours=9, minutes=30); prev = (r.date - pd.offsets.BDay(1)) + pd.Timedelta(hours=16)
    w = x[(x.t > prev) & (x.t < corte) & x.form.isin(["8-K", "8-K/A", "6-K", "6-K/A"])]
    if w.empty:
        continue
    f = f"{OUT}/{r.sym}_{r.date.date()}.txt"
    if os.path.exists(f):
        continue
    textos, items = [], []
    for d in w.itertuples():
        acc = d.accessionNumber.replace("-", "")
        idx = get(f"https://www.sec.gov/Archives/edgar/data/{c}/{acc}/index.json", texto=False)
        docs = [i["name"] for i in (idx or {}).get("directory", {}).get("item", []) if i["name"].lower().endswith((".htm", ".html", ".txt"))]
        ex = [n_ for n_ in docs if re.search(r"ex[-_]?99|ex991|exhibit99|dex99", n_.lower())]
        for n_ in (ex[:2] or [d.primaryDocument]):
            t = get(f"https://www.sec.gov/Archives/edgar/data/{c}/{acc}/{n_}")
            if t:
                textos.append(limpiar(t)[:20000])
        items.append(str(d.items))
    open(f, "w").write("ITEMS: " + ";".join(items) + "\n" + "\n".join(textos))
    n += 1
    if n % 200 == 0:
        print(n, flush=True)
print("listo", n)
