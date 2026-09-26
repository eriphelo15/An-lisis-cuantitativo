"""VI original con añadidos (igual que el indicador vi_original.pine) sobre el último mes de NQ (Yahoo, 1 min, sesión completa).
Mismo motor que 26_vi_segundo_vi.py (modo 1 = añadir; salida por cierre al otro lado de cualquier EMA)."""
import importlib
import numpy as np, pandas as pd
M = importlib.import_module("26_vi_segundo_vi") if False else None
from numba import njit
src = open("26_vi_segundo_vi.py").read().split("A, E20, E50, F, atr = vi.dias_con_ema")[0]
D = pd.read_parquet("/home/user/data/nq_yahoo_1m_reciente.parquet")
D["e20"] = D.Close.ewm(span=20, adjust=False).mean(); D["e50"] = D.Close.ewm(span=50, adjust=False).mean()
r = D.between_time("09:30", "15:59"); r = r.assign(dia=r.index.normalize())
dias, A, E20, E50 = [], [], [], []
for d, g in r.groupby("dia"):
    if len(g) < 380: continue
    k = ((g.index.hour * 60 + g.index.minute) - 570).to_numpy()
    a = np.full((390, 6), np.nan); a[k] = g[["Open", "High", "Low", "Close", "e20", "e50"]].to_numpy()
    a = pd.DataFrame(a).ffill().bfill().to_numpy()
    A.append(a[:, :4]); E20.append(a[:, 4]); E50.append(a[:, 5]); dias.append(d)
A, E20, E50 = np.stack(A), np.stack(E20), np.stack(E50)
exec(src.replace("@njit(cache=True)", "@njit").split("import sys, importlib")[0] + "\n" + "\n".join(src.split("\n")[src.split("\n").index("@njit(cache=True)"):]).replace("@njit(cache=True)", "@njit"))
tick = 0.25; atr = np.ones(len(A))
filas = []
for modo, nom in [(0, "sin añadir"), (1, "con añadidos (tu ejecución)")]:
    R = pd.DataFrame(correr(A, E20, E50, atr, 1.0, 120, modo, 0.0, tick), columns=["di", "k", "d", "nc", "pts", "mot"])
    R["fecha"] = [dias[int(i)].strftime("%Y-%m-%d") for i in R.di]
    R["hora_salida"] = [(pd.Timestamp("2000-01-01 09:30") + pd.Timedelta(minutes=int(k))).strftime("%H:%M") for k in R.k]
    R["usd"] = (R.pts - R.nc * np.where(R.mot == 1, 1, 2) * tick) * 20 - R.nc * 5.76
    w = R.usd[R.usd > 0]; lo = R.usd[R.usd <= 0]
    print(f"\n== {nom}: {len(dias)} días, {len(R)} operaciones | acierto {100*(R.usd>0).mean():.1f}% | ganancia media ${w.mean():.0f} | pérdida media ${lo.mean():.0f} | "
          f"media ${R.usd.mean():+.1f} | total ${R.usd.sum():+,.0f} | peor ${R.usd.min():,.0f} | añadidos {int((R.nc-1).sum())}")
    dd = R.groupby("fecha").usd.agg(["size", "sum"]).rename(columns={"size": "ops", "sum": "usd"})
    print("   días positivos:", (dd.usd > 0).sum(), "de", len(dd), "| por día:", dd.usd.round(0).astype(int).to_dict())
    R.to_csv(f"vi_mes_reciente_{modo}.csv", index=False)
