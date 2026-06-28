"""
Indicadores técnicos optimizados para futuros de índices (NQ/ES).
Todos operan sobre DataFrames de pandas con columnas OHLCV.
"""

import numpy as np
import pandas as pd


def vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP que se reinicia cada sesión (agrupado por fecha)."""
    precio_tipico = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"].replace(0, np.nan)

    # Acumulados por día de sesión
    pv_acum = (precio_tipico * vol).groupby(df.index.date).cumsum()
    vol_acum = vol.groupby(df.index.date).cumsum()

    return pv_acum / vol_acum


def vwap_bandas(df: pd.DataFrame, desviaciones: list[float] = [1.0, 2.0, 3.0]):
    """
    VWAP con bandas de desviación estándar ponderadas por volumen.
    Retorna dict con 'vwap', 'sup_1', 'inf_1', 'sup_2', etc.
    """
    precio_tipico = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"].replace(0, np.nan)

    pv_acum = (precio_tipico * vol).groupby(df.index.date).cumsum()
    pv2_acum = (precio_tipico ** 2 * vol).groupby(df.index.date).cumsum()
    vol_acum = vol.groupby(df.index.date).cumsum()

    vwap_vals = pv_acum / vol_acum
    varianza = (pv2_acum / vol_acum) - vwap_vals ** 2
    varianza = varianza.clip(lower=0)
    std = np.sqrt(varianza)

    resultado = {"vwap": vwap_vals}
    for n in desviaciones:
        resultado[f"sup_{n}"] = vwap_vals + n * std
        resultado[f"inf_{n}"] = vwap_vals - n * std

    return resultado


def atr(df: pd.DataFrame, periodo: int = 14) -> pd.Series:
    """Average True Range."""
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    return tr.ewm(span=periodo, adjust=False).mean()


def ema(serie: pd.Series, periodo: int) -> pd.Series:
    """Exponential Moving Average."""
    return serie.ewm(span=periodo, adjust=False).mean()


def rsi(serie: pd.Series, periodo: int = 14) -> pd.Series:
    """RSI clásico de Wilder."""
    delta = serie.diff()
    ganancias = delta.clip(lower=0)
    perdidas = (-delta).clip(lower=0)

    avg_gain = ganancias.ewm(alpha=1 / periodo, adjust=False).mean()
    avg_loss = perdidas.ewm(alpha=1 / periodo, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def rango_apertura(df: pd.DataFrame, minutos: int = 30) -> pd.DataFrame:
    """
    Calcula el alto y bajo del rango de apertura para cada día.
    Retorna DataFrame con columnas ['or_high', 'or_low', 'or_size']
    indexado por fecha.
    """
    inicio = pd.Timedelta(hours=9, minutes=30)
    fin = pd.Timedelta(hours=9, minutes=30) + pd.Timedelta(minutes=minutos)

    resultados = []
    for fecha, grupo in df.groupby(df.index.date):
        # Filtrar solo las barras del rango de apertura
        hora_barras = grupo.index - grupo.index.normalize()
        mascara = (hora_barras >= inicio) & (hora_barras < fin)
        rango = grupo[mascara]

        if len(rango) == 0:
            continue

        or_high = rango["high"].max()
        or_low = rango["low"].min()
        resultados.append({
            "fecha": pd.Timestamp(fecha),
            "or_high": or_high,
            "or_low": or_low,
            "or_size": or_high - or_low,
            "or_vol_medio": rango["volume"].mean() if "volume" in rango.columns else np.nan,
        })

    if not resultados:
        return pd.DataFrame()

    return pd.DataFrame(resultados).set_index("fecha")


def detectar_tendencia_sesion(df: pd.DataFrame, ventana: int = 20) -> pd.Series:
    """
    Tendencia simple: +1 alcista, -1 bajista, 0 lateral.
    Basado en la pendiente de la EMA de cierre.
    """
    ema_vals = ema(df["close"], ventana)
    pendiente = ema_vals.diff(5)
    umbral = atr(df, 14) * 0.1

    tendencia = pd.Series(0, index=df.index)
    tendencia[pendiente > umbral] = 1
    tendencia[pendiente < -umbral] = -1
    return tendencia
