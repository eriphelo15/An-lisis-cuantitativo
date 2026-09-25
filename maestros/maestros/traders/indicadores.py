import math
from datetime import datetime

import pandas as pd

MINUTOS_SESION_EXTENDIDA = 16 * 60  # de 4:00 a 20:00 ET


def minuto_del_dia(hora: datetime) -> int:
    """Minutos desde las 4:00 ET (inicio del premarket)."""
    return min(max(hora.hour * 60 + hora.minute - 4 * 60, 0), MINUTOS_SESION_EXTENDIDA - 1)


def vwap(barras: pd.DataFrame) -> pd.Series:
    precio = barras["vwap"].where(barras["vwap"].notna(), (barras["maximo"] + barras["minimo"] + barras["cierre"]) / 3)
    volumen = barras["volumen"].astype(float)
    return (precio * volumen).cumsum() / volumen.cumsum()


def volumen_normal_acumulado(barras_previas: pd.DataFrame) -> pd.Series | None:
    """Volumen acumulado promedio a cada minuto del día, calculado con días anteriores.

    Es la base del volumen relativo "a esta hora": 5x a las 8:00 significa 5 veces lo que normalmente
    se habría negociado hasta las 8:00, no 5 veces el volumen de un día completo.
    """
    if barras_previas.empty:
        return None
    df = barras_previas.assign(
        dia=[h.date() for h in barras_previas["hora"]],
        minuto=[minuto_del_dia(h) for h in barras_previas["hora"]],
    )
    por_minuto = df.groupby(["dia", "minuto"])["volumen"].sum().unstack("minuto")
    por_minuto = por_minuto.reindex(columns=range(MINUTOS_SESION_EXTENDIDA), fill_value=0).fillna(0)
    return por_minuto.cumsum(axis=1).mean(axis=0)


def volumen_relativo(barras_hoy: pd.DataFrame, volumen_normal: pd.Series | None) -> float | None:
    if volumen_normal is None or barras_hoy.empty:
        return None
    esperado = float(volumen_normal.iloc[minuto_del_dia(barras_hoy["hora"].iloc[-1])])
    actual = float(barras_hoy["volumen"].sum())
    if esperado <= 0:
        # En small caps es normal no tener volumen en premarket: cualquier volumen hoy es "infinitamente" relativo.
        return math.inf if actual > 0 else None
    return actual / esperado
