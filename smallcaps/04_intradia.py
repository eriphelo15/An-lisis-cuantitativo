"""Entradas intradía en gappers de small caps (velas 5 min reales, últimos ~60 días, Yahoo). Ejecución conservadora:
si en la misma vela se toca stop y objetivo -> pérdida. Coste 1% ida+vuelta sobre el precio de entrada. Salida final 15:55.
 S0 corto a la apertura, stop +30% (versión con recorrido real del día)
 S1 corto al romper el mínimo de la 1ª vela de 5 min (09:35-11:00), stop = máximo del día hasta la entrada +1%
 S2 corto en la 1ª vela que cierra bajo el VWAP (10:00-12:00), entrada en la apertura siguiente, stop = máximo del día +1%
 S3 largo al romper el máximo de la 1ª vela de 5 min (09:35-11:00), stop = mínimo de la 1ª vela  (gap and go / ORB)
 S3b igual con objetivo 2R"""
import numpy as np, pandas as pd
E = pd.read_parquet("/home/user/data/smallcaps/eventos_recientes.parquet")
COSTO = 0.01

def jugar(b, i0, e, stop, d, tgt=None):
    for i in range(i0, len(b)):
        h, l = b.High.iat[i], b.Low.iat[i]
        if (d < 0 and h >= stop) or (d > 0 and l <= stop): return (stop - e) * d
        if tgt is not None and ((d > 0 and h >= tgt) or (d < 0 and l <= tgt)): return (tgt - e) * d
    return (b.Close.iat[-1] - e) * d

filas = []
for _, ev in E.iterrows():
    try: m = pd.read_parquet(f"/home/user/data/smallcaps/m5/{ev.sym}.parquet")
    except Exception: continue
    b = m[m.index.date == ev.date.date()]
    b = b.between_time("09:30", "15:55")
    if len(b) < 40 or b.index[0].strftime("%H:%M") != "09:30": continue
    t = b.index.strftime("%H:%M")
    o0, h0, l0 = b.Open.iat[0], b.High.iat[0], b.Low.iat[0]
    tp = (b.High + b.Low + b.Close) / 3; vw = (tp * b.Volume).cumsum() / b.Volume.cumsum().replace(0, np.nan)
    res = {}
    # S0
    res["S0 corto apertura, stop +30%"] = (jugar(b, 0, o0, o0 * 1.3, -1), o0 * 0.3, o0)
    # S1
    for i in range(1, len(b)):
        if t[i] > "11:00": break
        if b.Low.iat[i] < l0:
            e = min(l0 - 0.01, b.Open.iat[i]); hod = b.High.iloc[:i + 1].max(); st = hod * 1.01
            res["S1 corto rompe mín. 1ª vela"] = (jugar(b, i, e, st, -1), st - e, e); break
    # S2
    for i in range(1, len(b) - 1):
        if t[i] < "10:00": continue
        if t[i] > "12:00": break
        if b.Close.iat[i] < vw.iat[i]:
            e = b.Open.iat[i + 1]; st = b.High.iloc[:i + 1].max() * 1.01
            res["S2 corto pierde VWAP"] = (jugar(b, i + 1, e, st, -1), st - e, e); break
    # S3
    for i in range(1, len(b)):
        if t[i] > "11:00": break
        if b.High.iat[i] > h0:
            e = max(h0 + 0.01, b.Open.iat[i]); st = l0; r = e - st
            if b.Low.iat[i] <= st: res["S3 largo ORB 5 min"] = (-r, r, e); res["S3b largo ORB 5 min, obj 2R"] = (-r, r, e); break
            res["S3 largo ORB 5 min"] = (jugar(b, i + 1, e, st, 1), r, e)
            res["S3b largo ORB 5 min, obj 2R"] = (jugar(b, i + 1, e, st, 1, e + 2 * r), r, e); break
    for k, (pnl, r, e) in res.items():
        if r > 0: filas.append(dict(sym=ev.sym, fecha=ev.date, est=k, R=(pnl - COSTO * e) / r, pct=100 * (pnl / e - COSTO)))
X = pd.DataFrame(filas); X.to_csv("res_04_intradia.csv", index=False)
g = X.groupby("est")
S = pd.DataFrame(dict(n=g.size(), acierto=g.R.apply(lambda r: (r > 0).mean()), R_medio=g.R.mean(), R_mediana=g.R.median(),
                      pct_medio=g.pct.mean(), t=g.R.apply(lambda r: r.mean() / r.std() * np.sqrt(len(r)))))
print(f"Gappers con velas de 5 min completas: {X.drop_duplicates(['sym','fecha']).shape[0]}")
print(S.round(3).to_string())
