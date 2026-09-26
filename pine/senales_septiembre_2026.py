"""Pullback VI filtrado sobre NQ de Yahoo (1 min, 31-ago a 25-sep-2026), mismas reglas que el indicador Pine.
ATR = media del rango RTH de los 14 días anteriores, calculado con velas de 5 min de Yahoo (60 días de historial)."""
import numpy as np, pandas as pd, yfinance as yf
D = pd.read_parquet("/home/user/data/nq_yahoo_1m_reciente.parquet")
D["e20"] = D.Close.ewm(span=20, adjust=False).mean(); D["e50"] = D.Close.ewm(span=50, adjust=False).mean()
m5 = yf.download("NQ=F", period="60d", interval="5m", progress=False, auto_adjust=False, prepost=True)
m5.columns = [c[0] for c in m5.columns]; m5.index = m5.index.tz_convert("America/New_York")
r5 = m5.between_time("09:30", "15:55"); rng = r5.groupby(r5.index.normalize()).apply(lambda g: g.High.max() - g.Low.min())
atr = rng.shift().rolling(14).mean()
tick = 0.25; filas = []
r = D.between_time("09:30", "15:59")
for d, g in r.groupby(r.index.normalize()):
    if len(g) < 380 or d not in atr.index or np.isnan(atr[d]): continue
    k = ((g.index.hour * 60 + g.index.minute) - 570).to_numpy()
    a = np.full((390, 6), np.nan); a[k] = g[["Open", "High", "Low", "Close", "e20", "e50"]].to_numpy(); a = pd.DataFrame(a).ffill().bfill().to_numpy()
    at = atr[d]; o930 = a[0, 0]
    for n in range(10, 120):
        o1, h1, l1, c1 = a[n - 1, :4]; o, h, l, c = a[n, :4]; e20, e50 = a[n, 4], a[n, 5]; pend = e20 - a[n - 10, 4]
        dd = 0
        if e20 > e50 and c > e20 and c > e50 and max(o, c) < min(o1, c1) and h >= l1: dd = 1
        elif e20 < e50 and c < e20 and c < e50 and min(o, c) > max(o1, c1) and l <= h1: dd = -1
        if dd == 0: continue
        stop = e50 - dd * 2 * tick; rr = dd * (c - stop)
        if not (dd * (c - o930) > 0.158 * at and dd * pend > 0.074 * at and max(0.069 * at, 4 * tick) <= rr <= 0.25 * at): continue
        tgt = c + dd * 2 * rr; res = None
        for j in range(n + 1, 386):
            oo, hh, ll, cc = a[j, :4]
            if (dd > 0 and ll <= stop) or (dd < 0 and hh >= stop):
                px = oo if (dd > 0 and oo < stop) or (dd < 0 and oo > stop) else stop; res = dd * (px - c) / rr; mot = "STOP"; hs = j; break
            if (dd > 0 and hh >= tgt) or (dd < 0 and ll <= tgt): res = 2.0; mot = "OBJETIVO"; hs = j; break
        if res is None: res = dd * (a[385, 3] - c) / rr; mot = "15:55"; hs = 385
        ctos = int(250 // (rr * 2 + 2.82))
        filas.append(dict(fecha=d.strftime("%Y-%m-%d"), hora=(pd.Timestamp("2000-01-01 09:30") + pd.Timedelta(minutes=n)).strftime("%H:%M"),
                          dir="COMPRA" if dd > 0 else "VENTA", entrada=c, stop=round(stop, 2), objetivo=round(tgt, 2), stop_pts=round(rr, 2),
                          ATR=round(at, 1), salida=mot, hora_salida=(pd.Timestamp("2000-01-01 09:30") + pd.Timedelta(minutes=hs)).strftime("%H:%M"),
                          R=round(res, 2), MNQ_con_250=ctos, usd_MNQ=round(ctos * (res * rr * 2) - ctos * 2.82)))
        break
X = pd.DataFrame(filas); X.to_csv("senales_septiembre_2026.csv", index=False)
pd.set_option("display.width", 250); print(X.to_string(index=False))
print(f"\nDías analizados: {r.index.normalize().nunique()} | operaciones: {len(X)} | acierto {100*(X.R>0).mean():.0f}% | R medio {X.R.mean():+.2f} | R total {X.R.sum():+.2f} | $ con riesgo $250 en MNQ: {X.usd_MNQ.sum():+,}")
