from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CriteriosRunner:
    precio_min: float = 1.0
    precio_max: float = 20.0
    gap_min: float = 0.30
    extension_min: float = 0.50
    volumen_relativo_min: float = 5.0
    dolar_volumen_min: float = 1_000_000
    ventana_volumen: int = 20
    max_dias_desde_previo: int = 5
    # En datos sin ajustar, un reverse split aparece como un "gap" gigante (1:10 = +900%).
    gap_max_sin_split: float = 4.0


def enriquecer(diario: pd.DataFrame, ventana_volumen: int = 20) -> pd.DataFrame:
    """Agrega, por ticker, el cierre previo, el volumen promedio previo y las métricas del día.

    El volumen promedio usa solo días anteriores, así el día del evento no se contamina a sí mismo.
    """
    df = diario.sort_values(["ticker", "fecha"]).copy()
    grupo = df.groupby("ticker", sort=False)
    df["cierre_previo"] = grupo["cierre"].shift(1)
    df["fecha_previa"] = grupo["fecha"].shift(1)
    df["volumen_promedio"] = grupo["volumen"].transform(
        lambda v: v.shift(1).rolling(ventana_volumen, min_periods=max(5, ventana_volumen // 2)).mean()
    )
    df["gap"] = df["apertura"] / df["cierre_previo"] - 1
    df["extension"] = df["maximo"] / df["cierre_previo"] - 1
    df["volumen_relativo"] = df["volumen"] / df["volumen_promedio"]
    df["dolar_volumen"] = df["volumen"] * df["vwap"].fillna(df["cierre"])
    df["dias_desde_previo"] = (pd.to_datetime(df["fecha"]) - pd.to_datetime(df["fecha_previa"])).dt.days
    return df


def detectar_runners(diario: pd.DataFrame, criterios: CriteriosRunner = CriteriosRunner()) -> pd.DataFrame:
    df = enriquecer(diario, criterios.ventana_volumen)
    es_runner = (
        df["cierre_previo"].between(criterios.precio_min, criterios.precio_max)
        & ((df["gap"] >= criterios.gap_min) | (df["extension"] >= criterios.extension_min))
        & (df["volumen_relativo"] >= criterios.volumen_relativo_min)
        & (df["dolar_volumen"] >= criterios.dolar_volumen_min)
        & (df["dias_desde_previo"] <= criterios.max_dias_desde_previo)
        & (df["gap"] <= criterios.gap_max_sin_split)
    )
    return df[es_runner].reset_index(drop=True)
