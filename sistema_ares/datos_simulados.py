"""
Generador de datos de futuros NQ simulados con propiedades estadísticas
similares a las del mercado real.
Útil para testing cuando no hay conexión a datos en vivo.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz


def generar_nq_simulado(
    dias: int = 30,
    intervalo_min: int = 5,
    precio_inicial: float = 21_000.0,
    volatilidad_diaria: float = 0.007,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Genera barras OHLCV de NQ con:
    - Apertura con gap aleatorio
    - Sesión NY 9:30 - 16:00 ET
    - Volatilidad intraday realista (mayor al open y close)
    - Volumen proporcional a la volatilidad
    """
    rng = np.random.default_rng(seed)
    et = pytz.timezone("America/New_York")

    barras = []
    precio_cierre_anterior = precio_inicial

    fecha_inicio = datetime.now(et).replace(
        hour=9, minute=30, second=0, microsecond=0
    ) - timedelta(days=dias)

    # Avanzar al lunes si cae en fin de semana
    while fecha_inicio.weekday() >= 5:
        fecha_inicio += timedelta(days=1)

    fecha_actual = fecha_inicio

    while (datetime.now(et) - fecha_actual).days > 0:
        if fecha_actual.weekday() >= 5:
            fecha_actual += timedelta(days=1)
            continue

        # Gap de apertura
        gap_pct = rng.normal(0, 0.002)
        precio_open_dia = precio_cierre_anterior * (1 + gap_pct)

        # Tendencia intradía del día (+1 alcista, -1 bajista)
        tendencia_dia = rng.choice([1, -1, 0], p=[0.45, 0.40, 0.15])
        drift_dia = tendencia_dia * volatilidad_diaria * 0.5

        # Volatilidad intraday: mayor en open y close
        horas_sesion = 6.5  # 9:30 a 16:00
        n_barras = int(horas_sesion * 60 / intervalo_min)

        precio_actual = precio_open_dia
        hora_barra = fecha_actual.replace(hour=9, minute=30)

        for i in range(n_barras):
            # Volatilidad varía por hora (U-shape: alta al open y close)
            progreso = i / n_barras
            factor_vol = 1.5 if progreso < 0.15 or progreso > 0.85 else 0.8

            vol_barra = volatilidad_diaria * factor_vol / np.sqrt(n_barras)
            retorno = rng.normal(drift_dia / n_barras, vol_barra)

            open_b = precio_actual
            close_b = open_b * (1 + retorno)

            # High y Low alrededor de open/close
            rango_b = abs(close_b - open_b) * rng.uniform(1.5, 3.0)
            high_b = max(open_b, close_b) + rango_b * rng.uniform(0.1, 0.5)
            low_b = min(open_b, close_b) - rango_b * rng.uniform(0.1, 0.5)

            # Volumen: correlacionado con volatilidad
            vol_base = 5000
            vol_b = int(vol_base * factor_vol * rng.lognormal(0, 0.5))

            barras.append({
                "datetime": hora_barra,
                "open": round(open_b, 2),
                "high": round(high_b, 2),
                "low": round(low_b, 2),
                "close": round(close_b, 2),
                "volume": vol_b,
            })

            precio_actual = close_b
            hora_barra += timedelta(minutes=intervalo_min)

        precio_cierre_anterior = precio_actual
        fecha_actual += timedelta(days=1)

    df = pd.DataFrame(barras).set_index("datetime")
    idx = pd.DatetimeIndex(df.index)
    if idx.tz is None:
        idx = idx.tz_localize("America/New_York")
    df.index = idx
    return df
