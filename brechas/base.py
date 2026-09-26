"""Base común para la investigación amplia: tabla de tramos horarios por día de trading (NQ, ES, YM, 15 años).
Día de trading CME: 18:00 ET del día anterior -> 17:00 ET. Precios back-ajustados (adj_close) -> diferencias intradía exactas.
Rendimientos en puntos básicos (bp) sobre el precio real (close) para que sean comparables entre eras."""
import os
import numpy as np, pandas as pd

DATA = os.environ.get("NQ_DATA_DIR", "/home/user/data")
SYMS = {"NQ": "nq15_1m.parquet", "ES": "es15_1m.parquet", "YM": "ym15_1m.parquet"}
# costo ida+vuelta en puntos (comisión $5.76 + 1 tick por lado)
COSTO_PTS = {"NQ": 5.76 / 20 + 0.5, "ES": 5.76 / 50 + 0.5, "YM": 5.76 / 5 + 2.0}
USD_PT = {"NQ": 20.0, "ES": 50.0, "YM": 5.0}
PERIODOS = [("DEV", "2010-10-01", "2018-12-31"), ("VAL1", "2019-01-01", "2021-03-12"), ("VAL2", "2021-03-13", "2026-03-13")]
# límites de tramo en minutos desde medianoche ET; el día empieza a las 18:00 del día anterior (=-360)
CORTES = {"t18": -360, "t20": -240, "t00": 0, "t03": 180, "t0830": 510, "t0930": 570, "t10": 600, "t12": 720,
          "t14": 840, "t1530": 930, "t1550": 950, "t16": 960, "t1659": 1019}


def cargar(sym, cols=("ts", "open", "high", "low", "close", "adj_close", "volume")):
    d = pd.read_parquet(os.path.join(DATA, SYMS[sym]), columns=list(cols))
    m = d.ts.dt.hour * 60 + d.ts.dt.minute
    nxt = d.ts.dt.hour >= 18
    fecha = d.ts.dt.normalize() + pd.to_timedelta(nxt.astype(int), unit="D")
    # viernes 18:00+ no existe; sábado -> lunes (por si acaso)
    fecha = fecha + pd.to_timedelta(np.where(fecha.dt.dayofweek == 5, 2, 0), unit="D")
    d["fecha"] = fecha
    d["m"] = np.where(nxt, m - 1440, m)   # minuto relativo al día de trading
    return d


def tramos(sym):
    """Precio (adj) al INICIO de cada corte = open de la primera barra con m >= corte; y close real de referencia."""
    cache = os.path.join(DATA, f"tramos_{sym}.parquet")
    if os.path.exists(cache):
        return pd.read_parquet(cache)
    d = cargar(sym)
    d["off"] = d.adj_close - d.close
    d["aopen"] = d.open + d.off
    out = {}
    g = d.groupby("fecha")
    for k, c in CORTES.items():
        x = d[(d.m >= c) & (d.m < c + 30)]
        out[k] = x.groupby("fecha").aopen.first()
        out[k + "_m"] = x.groupby("fecha").m.first()
    T = pd.DataFrame(out)
    T["ref"] = d[(d.m >= 570) & (d.m < 600)].groupby("fecha").close.first()   # precio real a la apertura
    T["cierre_prev"] = np.nan
    rth = d[(d.m >= 570) & (d.m < 960)]
    gr = rth.groupby("fecha")
    T["rth_h"] = gr.high.max() + gr.off.last(); T["rth_l"] = gr.low.min() + gr.off.last()
    T["rth_c"] = gr.adj_close.last(); T["n_rth"] = gr.size()
    T["vol_rth"] = gr.volume.sum()
    T = T[T.n_rth >= 385]
    T.to_parquet(cache)
    return T


def periodo(fechas):
    p = pd.Series("", index=fechas)
    for tag, a, b in PERIODOS:
        p[(fechas >= a) & (fechas <= b)] = tag
    return p.to_numpy()
