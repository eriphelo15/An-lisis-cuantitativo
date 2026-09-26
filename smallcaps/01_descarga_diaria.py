"""Descarga OHLCV diario (sin ajustar por dividendos; sí por splits, como da Yahoo) 2015-2026 de todo el universo de acciones comunes
de EE. UU. listadas HOY (NASDAQ/NYSE/AMEX). Sesgo de supervivencia: faltan las empresas deslistadas (en small caps, muchas)."""
import os, time
import pandas as pd, yfinance as yf
D = "/home/user/data/smallcaps"; os.makedirs(f"{D}/diario", exist_ok=True)
syms = pd.read_csv(f"{D}/universo.csv").Symbol.tolist()
lote = 100
for i in range(0, len(syms), lote):
    out = f"{D}/diario/lote_{i:05d}.parquet"
    if os.path.exists(out): continue
    grupo = [s.replace(".", "-") for s in syms[i:i + lote]]
    for intento in range(4):
        try:
            d = yf.download(grupo, start="2015-01-01", end="2026-09-26", progress=False, auto_adjust=False, threads=True, group_by="ticker")
            break
        except Exception as e:
            print("reintento", e); time.sleep(10 * (intento + 1))
    filas = []
    for s in grupo:
        if s not in d.columns.get_level_values(0): continue
        x = d[s].dropna(subset=["Open", "Close"]).copy()
        if len(x) == 0: continue
        x["sym"] = s; filas.append(x.reset_index())
    if filas:
        pd.concat(filas).to_parquet(out)
    print(i, len(filas), flush=True); time.sleep(1)
