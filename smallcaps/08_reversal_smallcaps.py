"""¿Sirve el indicador 'Reversal' del usuario para shortear gappers? (misma lógica que brechas/15_reversal_eao.py:
near=2, long=20; señal de venta = vela anterior alcista, actual bajista que cierra bajo la apertura de la anterior,
tras barrer el máximo de las últimas `long` velas).
Estilo del usuario ("reciclaje"): corto en cada señal de venta, cubrir en la siguiente señal de compra, volver a entrar en la
siguiente venta. Stop: máximo barrido (máximo de las últimas `near` velas) + 0.5 %. Salida forzosa 15:55. Coste 1 % ida y vuelta.
Comparación: entradas AL AZAR en el mismo día y acción, con la misma regla de salida y stop (para saber si la señal aporta algo)."""
import glob, sys
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
COSTE = 0.01
NEAR, LONG = 2, 20
tf = sys.argv[1] if len(sys.argv) > 1 else "m5"          # m5 (60 días) o m1 (septiembre)
E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
E["date"] = pd.to_datetime(E["date"])


def senales(b):
    o, h, l, c = b.Open.values, b.High.values, b.Low.values, b.Close.values
    n = len(b)
    buy = np.zeros(n, bool); sell = np.zeros(n, bool)
    for j in range(LONG + 5, n):
        nl = l[j - NEAR + 1:j + 1].min(); nh = h[j - NEAR + 1:j + 1].max()
        c3 = any(l[j - k - LONG + 1:j - k + 1].min() > nl for k in range(1, 5))
        c6 = any(h[j - k - LONG + 1:j - k + 1].max() < nh for k in range(1, 5))
        buy[j] = c[j - 1] < o[j - 1] and c[j] > o[j] and c[j] > o[j - 1] and c3
        sell[j] = c[j - 1] > o[j - 1] and c[j] < o[j] and c[j] < o[j - 1] and c6
    return buy, sell


def simular(b, entradas, buy, i0):
    """Corto en cada índice de 'entradas' (cierre de la vela), salida en la siguiente señal de compra, stop o 15:55."""
    h, c = b.High.values, b.Close.values
    res = []
    libre = 0
    for j in entradas:
        if j < libre or j < i0 or j >= len(b) - 1:
            continue
        e = c[j]; st = h[max(0, j - NEAR + 1):j + 1].max() * 1.005
        if st <= e:
            continue
        sal, k = c[-1], len(b) - 1
        for k in range(j + 1, len(b)):
            if h[k] >= st:
                sal = st; break
            if buy[k]:
                sal = c[k]; break
        res.append(((e - sal - COSTE * e) / (st - e), (e - sal) / e - COSTE))
        libre = k + 1
    return res


filas = []
for f in glob.glob(f"/home/user/data/smallcaps/{tf}/*.parquet"):
    sym = f.split("/")[-1][:-8]
    m = pd.read_parquet(f)
    if hasattr(m.columns, "levels"):
        m.columns = m.columns.get_level_values(0)
    if m.index.tz is None:
        m.index = m.index.tz_localize("UTC")
    m.index = m.index.tz_convert("America/New_York")
    for r in E[E.sym == sym].itertuples():
        dia = m[m.index.date == r.date.date()]
        b = dia.between_time("09:00", "15:55")            # 30 min previos para que el indicador tenga historia
        if len(b) < 60:
            continue
        i0 = int((b.index < b.index[0].normalize() + pd.Timedelta("9h30min")).sum())   # primera vela de la sesión
        buy, sell = senales(b)
        idx_sell = np.where(sell)[0]
        for R, pct in simular(b, idx_sell, buy, i0):
            filas.append(dict(sym=sym, date=r.date, gap=r.gap, tipo="Reversal (señal de venta)", R=R, pct=pct))
        # azar: mismo número de entradas, en velas aleatorias de la sesión
        cand = np.arange(max(i0, LONG + 5), len(b) - 1)
        if len(idx_sell) and len(cand):
            azar = np.sort(rng.choice(cand, size=min(len(cand), max(1, len(idx_sell))), replace=False))
            for R, pct in simular(b, azar, buy, i0):
                filas.append(dict(sym=sym, date=r.date, gap=r.gap, tipo="Entradas al azar (control)", R=R, pct=pct))
X = pd.DataFrame(filas)
X = X[np.isfinite(X.R)]
X.to_csv(f"res_08_reversal_{tf}.csv", index=False)
print(f"Velas: {tf} | días de gapper: {X[['sym','date']].drop_duplicates().shape[0]}")
for nom, msk in [("todos (gap >= 20 %)", X.gap >= 0.2), ("gap >= 50 %", X.gap >= 0.5)]:
    print(f"\n-- {nom}")
    g = X[msk].groupby("tipo")
    print(pd.DataFrame(dict(operaciones=g.size(), pct_ganadoras=g.R.apply(lambda v: (v > 0).mean()),
                            R_medio=g.R.mean(), R_mediana=g.R.median(), pct_medio=g.pct.mean() * 100,
                            t=g.R.apply(lambda v: v.mean() / v.std() * np.sqrt(len(v))))).round(3).to_string())
    # por día (como opera el usuario: suma de todas las operaciones del día)
    dia = X[msk].groupby(["tipo", "sym", "date"]).R.sum().groupby("tipo")
    print("   R por DÍA (suma del reciclaje): media", dia.mean().round(2).to_dict(), "| % días positivos", dia.apply(lambda v: (v > 0).mean()).round(2).to_dict())
