"""E1 (anuncio de listado spot), E3 (anuncio de perpetuo), E4 (anuncio de retiro).
Velas de 1 hora: Binance (perpetuo/spot) u OKX cuando la moneda aún no estaba en Binance.
Entrada conservadora: cierre de la vela horaria que contiene el anuncio (el salto de los primeros minutos NO se cuenta)."""
import glob, json, os, re
import numpy as np
import pandas as pd
import eco_base as e

DIR = e.DIR
C = 0.001
HOR = [1, 4, 24, 72, 168]
_cache = {}


def serie_binance(sym, mercado):
    k = (sym, mercado)
    if k not in _cache:
        pref = "spot_monthly_klines_" if mercado == "spot" else "futures_um_monthly_klines_"
        fs = sorted(glob.glob(f"{DIR}/k/{pref}{sym}_1h_*.zip"))
        ps = [x for x in (e._zip(f) for f in fs) if x is not None]
        _cache[k] = pd.concat(ps).drop_duplicates("t").set_index("t").sort_index()["c"] if ps else None
    return _cache[k]


def serie_okx(tk, ts):
    f = f"{DIR}/okx/{tk}_{ts}.json"
    if not os.path.exists(f):
        return None
    d = json.load(open(f))
    if not d:
        return None
    s = pd.Series([float(x[4]) for x in d], index=pd.to_datetime([int(x[0]) for x in d], unit="ms", utc=True)).sort_index()
    return s[~s.index.duplicated()]


def perp_de(tk):
    for c in [tk + "USDT", "1000" + tk + "USDT", "1000000" + tk + "USDT"]:
        if glob.glob(f"{DIR}/k/futures_um_monthly_klines_{c}_1h_*"):
            return c


def estudiar(tk, ts, fuentes):
    """ts: pd.Timestamp del anuncio. Devuelve retornos desde el cierre de la vela del anuncio."""
    t_bar = ts.floor("1h")
    for nombre, s in fuentes:
        if s is None or t_bar not in s.index or (t_bar - pd.Timedelta("2h")) not in s.index:
            continue
        p0 = s.loc[t_bar]                           # cierre de la vela que contiene el anuncio
        r = dict(tk=tk, ts=ts, fuente=nombre,
                 pre24=p0 / s.asof(t_bar - pd.Timedelta("24h")) - 1 if (t_bar - pd.Timedelta("24h")) >= s.index[0] else np.nan,
                 salto=p0 / s.loc[t_bar - pd.Timedelta("1h")] - 1)          # incluye la reacción que no se puede capturar
        for h in HOR:
            t1 = t_bar + pd.Timedelta(hours=h)
            r[f"r{h}"] = s.asof(t1) / p0 - 1 if t1 <= s.index[-1] + pd.Timedelta("1h") else np.nan
        return r


def resumen(nombre, R, signo=1):
    R = R.copy()
    R["per"] = np.where(R.ts <= pd.Timestamp("2022-12-31", tz="UTC"), "DEV", "VAL")
    print(f"\n=== {nombre}  (n total {len(R)}; fuentes {R.fuente.value_counts().to_dict()})")
    print(f"   reacción en la hora del anuncio (no capturable): media {R.salto.mean():+.1%}, mediana {R.salto.median():+.1%}"
          f" | 24 h ANTES del anuncio (¿filtración?): media {R.pre24.mean():+.1%}, mediana {R.pre24.median():+.1%}")
    for p in ["DEV", "VAL"]:
        x = R[R.per == p]
        lin = f"   {p} n={len(x):3d}"
        for h in HOR:
            v = signo * x[f"r{h}"].dropna() - 2 * C
            if len(v) > 2:
                lin += f" | {h}h {'largo' if signo > 0 else 'corto'} {v.mean():+.1%} t{v.mean()/v.std(ddof=1)*np.sqrt(len(v)):+.1f} WR{(v>0).mean():.0%}"
        print(lin)


if __name__ == "__main__":
    # ---------- E1 listados spot
    ev = pd.read_pickle(f"{DIR}/ev_listado.pkl")
    ev["ts"] = pd.to_datetime(ev.ts, unit="ms", utc=True)
    filas = []
    for r in ev.itertuples():
        p = perp_de(r.tk)
        o = estudiar(r.tk, r.ts, [("binance perp", serie_binance(p, "fut") if p else None), ("okx", serie_okx(r.tk, int(r.ts.value // 10**6)))])
        if o:
            o.update(tipo=r.tipo, seed=r.seed, meme=r.tk in e.MEMES)
            filas.append(o)
    R1 = pd.DataFrame(filas)
    R1.to_csv("res_eco_anuncio_listado.csv", index=False)
    print(f"E1: {len(ev)} anuncios de listado, {len(R1)} con precio previo en otro mercado")
    resumen("E1 anuncio de listado spot en Binance -> COMPRAR", R1)
    resumen("E1 ... solo HODLer/Launchpool", R1[R1.tipo != "list"])
    resumen("E1 ... solo 'Binance Will List'", R1[R1.tipo == "list"])

    # ---------- E3 lanzamiento de perpetuo (moneda ya en spot Binance)
    a = json.load(open(f"{DIR}/anuncios.json"))
    ev3 = []
    for x in a:
        t = x["title"]
        if x["cat"] == 48 and re.match(r"^Binance Futures Will (Launch|List)", t) and "Pre-" not in t:
            tks = set(m[1] for m in re.findall(r"\b(1000|1000000)?([A-Z0-9]{2,15})USDT\b", t))
            tks |= set(re.findall(r"USDⓈ-M ([A-Z0-9]{2,15}) (?:and [A-Z0-9]{2,15} )?Perpetual", t))
            for tk in tks:
                ev3.append((tk, pd.to_datetime(x["releaseDate"], unit="ms", utc=True)))
    filas = []
    for tk, ts in ev3:
        o = estudiar(tk, ts, [("binance spot", serie_binance(tk + "USDT", "spot"))])
        if o:
            filas.append(o)
    R3 = pd.DataFrame(filas)
    R3.to_csv("res_eco_anuncio_perp.csv", index=False)
    print(f"\nE3: {len(ev3)} anuncios de perpetuo, {len(R3)} con spot previo en Binance")
    resumen("E3 anuncio de perpetuo -> COMPRAR spot", R3)

    # ---------- E4 retiros
    ev4 = pd.read_pickle(f"{DIR}/eventos.pkl")
    ev4 = ev4[ev4.tipo == "spot_delist"]
    filas = []
    for r in ev4.itertuples():
        p = perp_de(r.tk)
        o = estudiar(r.tk, r.ts, [("binance perp", serie_binance(p, "fut") if p else None), ("binance spot", serie_binance(r.tk + "USDT", "spot"))])
        if o:
            filas.append(o)
    R4 = pd.DataFrame(filas)
    R4.to_csv("res_eco_anuncio_retiro.csv", index=False)
    print(f"\nE4: {len(ev4)} monedas anunciadas para retiro, {len(R4)} con precio")
    resumen("E4 anuncio de retiro -> CORTO (en perpetuo si existe)", R4, signo=-1)
    resumen("E4 ... solo con perpetuo (operable en corto)", R4[R4.fuente == "binance perp"], signo=-1)
