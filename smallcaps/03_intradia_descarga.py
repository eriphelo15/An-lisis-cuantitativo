"""Velas de 5 min (Yahoo, últimos ~60 días) para cada gapper del periodo; una llamada por ticker."""
import os, time
import pandas as pd, yfinance as yf
E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
E["date"] = pd.to_datetime(E.date)
ini = pd.Timestamp.today().normalize() - pd.Timedelta(days=58)
E = E[E.date >= ini]
print("gappers recientes:", len(E), "tickers:", E.sym.nunique())
os.makedirs("/home/user/data/smallcaps/m5", exist_ok=True)
for s in sorted(E.sym.unique()):
    out = f"/home/user/data/smallcaps/m5/{s}.parquet"
    if os.path.exists(out): continue
    try:
        d = yf.download(s, period="60d", interval="5m", progress=False, auto_adjust=False, prepost=False)
        if len(d):
            d.columns = [c[0] if isinstance(c, tuple) else c for c in d.columns]
            d.to_parquet(out)
    except Exception as e:
        print(s, e)
    time.sleep(0.3)
E.to_parquet("/home/user/data/smallcaps/eventos_recientes.parquet")
print("listo")
