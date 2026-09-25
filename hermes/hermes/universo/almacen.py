from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from hermes.universo.massive import COLUMNAS_DIARIO


def dias_habiles(desde: date, hasta: date) -> list[date]:
    """Días de lunes a viernes; los feriados simplemente llegan vacíos desde la API."""
    dias, dia = [], desde
    while dia <= hasta:
        if dia.weekday() < 5:
            dias.append(dia)
        dia += timedelta(days=1)
    return dias


def ruta_diario(directorio: Path, fecha: date) -> Path:
    return directorio / "diario" / f"{fecha.isoformat()}.parquet"


def existe_diario(directorio: Path, fecha: date) -> bool:
    return ruta_diario(directorio, fecha).exists()


def guardar_diario(directorio: Path, fecha: date, df: pd.DataFrame) -> None:
    ruta = ruta_diario(directorio, fecha)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ruta, index=False)


def cargar_diario(directorio: Path, desde: date, hasta: date) -> pd.DataFrame:
    partes = [
        pd.read_parquet(ruta_diario(directorio, dia))
        for dia in dias_habiles(desde, hasta)
        if existe_diario(directorio, dia)
    ]
    partes = [p for p in partes if not p.empty]
    if not partes:
        return pd.DataFrame(columns=COLUMNAS_DIARIO)
    df = pd.concat(partes, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df
