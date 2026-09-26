"""Carga de datos cripto (Binance USDT-M perpetuos, 1 minuto) y utilidades comunes."""
import glob, io, os, zipfile
import numpy as np
import pandas as pd

DIR = "/home/user/data/cripto"
COSTO = 0.0005          # 0.05% por lado (taker Binance / aprox. micro BTC CME con deslizamiento)
PER = [("DEV 2020-2022", "2020-01-01", "2022-12-31"),
       ("VAL 2023-2026", "2023-01-01", "2026-08-31")]


def _leer_zip(f):
    with zipfile.ZipFile(f) as z:
        raw = z.read(z.namelist()[0])
    df = pd.read_csv(io.BytesIO(raw), header=None, usecols=[0, 1, 2, 3, 4, 5, 9])
    if not str(df.iloc[0, 0]).isdigit():
        df = df.iloc[1:]
    df.columns = ["t", "o", "h", "l", "c", "v", "vb"]
    return df.astype(float)


def cargar(sym="BTCUSDT"):
    """DataFrame 1m indexado por tiempo UTC, rejilla completa (huecos rellenados con el close previo)."""
    cache = f"{DIR}/{sym}_1m.parquet"
    if os.path.exists(cache):
        return pd.read_parquet(cache)
    df = pd.concat([_leer_zip(f) for f in sorted(glob.glob(f"{DIR}/{sym}-1m-*.zip"))])
    df["t"] = pd.to_datetime(df["t"].astype("int64"), unit="ms", utc=True)
    df = df.drop_duplicates("t").set_index("t").sort_index()
    rej = pd.date_range(df.index[0], df.index[-1], freq="1min", tz="UTC")
    df = df.reindex(rej)
    df["c"] = df["c"].ffill()
    for k in ["o", "h", "l"]:
        df[k] = df[k].fillna(df["c"])
    df[["v", "vb"]] = df[["v", "vb"]].fillna(0)
    df.to_parquet(cache)
    return df


def matriz_dias(df):
    """Array (dias, 1440, 4) OHLC por día UTC, solo días completos."""
    n = len(df) // 1440 * 1440
    inicio = df.index[0].normalize()
    assert df.index[0] == inicio
    A = df[["o", "h", "l", "c"]].values[:n].reshape(-1, 1440, 4)
    fechas = pd.date_range(inicio, periods=A.shape[0], freq="D")
    return A, fechas


def funding(sym="BTCUSDT"):
    fs = sorted(glob.glob(f"{DIR}/funding/{sym}-fundingRate-*.zip"))
    df = pd.concat([pd.read_csv(zipfile.ZipFile(f).open(zipfile.ZipFile(f).namelist()[0])) for f in fs])
    df["t"] = pd.to_datetime(df["calc_time"], unit="ms", utc=True).dt.round("1min")
    return df.set_index("t")["last_funding_rate"].sort_index()


def resumen(r, fechas=None):
    """r: retornos netos por operación (fracción). Devuelve dict con n, media bp, t, WR."""
    r = np.asarray(r, float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return dict(n=len(r), bp=np.nan, t=np.nan, wr=np.nan)
    return dict(n=len(r), bp=r.mean() * 1e4, t=r.mean() / r.std(ddof=1) * np.sqrt(len(r)), wr=(r > 0).mean())
