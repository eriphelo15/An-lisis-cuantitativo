"""Utilidades comunes del estudio NQ.

Reglas de disciplina estadística:
  * DEV  = 2021-03-15 .. 2024-12-31  -> toda la exploración y selección.
  * HOLD = 2025-01-01 .. 2026-03-13  -> holdout intocable; solo se evalúa al final,
           una vez, con reglas congeladas.
"""
import os
import numpy as np
import pandas as pd

DATA_DIR = os.environ.get("NQ_DATA_DIR", "/home/user/data")
RES_DIR = os.path.join(os.path.dirname(__file__), "resultados")
HOLDOUT_START = pd.Timestamp("2025-01-01")

# Costos NQ (validados: Tradeify $5.76 RT all-in; tick 0.25 = $5; punto = $20)
PUNTO_USD = 20.0
TICK = 0.25
COMISION_RT_PTS = 5.76 / PUNTO_USD            # 0.288 pts
SLIP_TICKS_LADO = 1                            # órdenes a mercado / stop
COSTO_MKT_RT_PTS = COMISION_RT_PTS + 2 * SLIP_TICKS_LADO * TICK   # 0.788 pts
COSTO_LMT_RT_PTS = COMISION_RT_PTS + 1 * SLIP_TICKS_LADO * TICK   # entrada limit, salida mkt
if os.environ.get("BRUTO") == "1":          # modo bruto: el costo se evalúa aparte, en % del ATR
    COSTO_MKT_RT_PTS = COSTO_LMT_RT_PTS = 0.0
# Periodos del estudio de 15 años (DEV explora; VAL1 nunca vista; VAL2 ya usada en el estudio de 5 años)
PERIODOS_15Y = [("DEV", "2010-10-01", "2018-12-31"), ("VAL1", "2019-01-01", "2021-03-12"), ("VAL2", "2021-03-13", "2026-03-13")]


ARCHIVO = os.environ.get("NQ_PARQUET", "nq_1m.parquet")   # nq15_1m.parquet para 15 años


def load_1m(split="dev"):
    """split: 'dev' | 'hold' | 'all' | (inicio, fin) por día de trading."""
    df = pd.read_parquet(os.path.join(DATA_DIR, ARCHIVO))
    # día de trading CME: la sesión que abre 18:00 ET pertenece al día siguiente
    df["tday"] = (df.ts + pd.Timedelta(hours=6)).dt.normalize()
    df["hm"] = df.ts.dt.hour * 100 + df.ts.dt.minute
    df["rth"] = (df.hm >= 930) & (df.hm < 1600)
    # minuto de sesión desde las 18:00 ET (09:30 -> 930, 16:00 -> 1320, 16:59 -> 1379)
    df["smin"] = ((df.ts.dt.hour * 60 + df.ts.dt.minute) - 18 * 60) % 1440
    if isinstance(split, tuple):
        df = df[(df.tday >= pd.Timestamp(split[0])) & (df.tday <= pd.Timestamp(split[1]))]
    elif split == "dev":
        df = df[df.tday < HOLDOUT_START]
    elif split == "hold":
        df = df[df.tday >= HOLDOUT_START]
    return df.reset_index(drop=True)


def daily_table(df):
    """Tabla diaria: sesión overnight (18:00-09:29), RTH (09:30-15:59) y contexto."""
    g = df.groupby("tday")
    on = df[(df.hm < 930) | (df.hm >= 1800)]
    ong = on.groupby("tday")
    r = df[df.rth].groupby("tday")
    d = pd.DataFrame({
        "on_high": ong.high.max(), "on_low": ong.low.min(),
        "on_open": ong.open.first(),
        "rth_open": r.open.first(), "rth_high": r.high.max(), "rth_low": r.low.min(),
        "rth_close": r.close.last(), "rth_vol": r.volume.sum(), "rth_bars": r.size(),
        "seg": g.seg.last(), "symbol": g.symbol.last(),
        "adj_rth_close": df[df.rth].groupby("tday").adj_close.last(),
        "adj_rth_open": df[df.rth].groupby("tday").adj_open.first(),
    })
    d = d[d.rth_bars >= 300]  # descarta días de cierre temprano / incompletos
    d["prev_close"] = d.rth_close.shift()
    d["prev_high"] = d.rth_high.shift(); d["prev_low"] = d.rth_low.shift()
    same = d.seg == d.seg.shift()
    d.loc[~same, ["prev_close", "prev_high", "prev_low"]] = np.nan  # no cruzar rolls con precios raw
    d["gap"] = d.rth_open - d.prev_close
    d["rng"] = d.rth_high - d.rth_low
    return d


def stats_trades(pnl_pts, label="", n_tests=1):
    """Métricas estándar sobre una serie de PnL por trade en puntos (ya neto de costos)."""
    p = np.asarray(pnl_pts, float)
    p = p[~np.isnan(p)]
    n = len(p)
    if n == 0:
        return dict(label=label, n=0)
    w = p[p > 0]; l = p[p <= 0]
    pf = w.sum() / -l.sum() if l.sum() < 0 else np.inf
    t = p.mean() / (p.std(ddof=1) / np.sqrt(n)) if n > 1 and p.std() > 0 else np.nan
    return dict(label=label, n=n, wr=len(w) / n, exp_pts=p.mean(), avg_win=w.mean() if len(w) else 0,
                avg_loss=l.mean() if len(l) else 0, pf=pf, total_pts=p.sum(), t=t,
                max_dd_pts=_maxdd(p.cumsum()))


def _maxdd(eq):
    eq = np.concatenate([[0], eq])
    return float((np.maximum.accumulate(eq) - eq).max())
