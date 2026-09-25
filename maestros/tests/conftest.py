from datetime import date, datetime, timedelta

import pandas as pd
import pytest

from maestros.datos.calendario import ET
from maestros.informacion.catalizadores import Noticia
from maestros.informacion.filings import Filing

DIA = date(2024, 6, 4)  # martes hábil


def et(hora: str, dia: date = DIA) -> datetime:
    return datetime.combine(dia, datetime.strptime(hora, "%H:%M").time(), tzinfo=ET)


def hacer_barras(inicio: datetime, velas: list[tuple], ticker: str = "ABCD") -> pd.DataFrame:
    """velas: (apertura, maximo, minimo, cierre, volumen), una por minuto desde `inicio`."""
    return pd.DataFrame([
        {"ticker": ticker, "hora": inicio + timedelta(minutes=i), "apertura": o, "maximo": h, "minimo": l,
         "cierre": c, "volumen": v, "vwap": float("nan"), "operaciones": 10}
        for i, (o, h, l, c, v) in enumerate(velas)
    ])


def crear_noticia(hora: datetime, titular: str = "ABCD announces FDA clearance", tickers=("ABCD",),
                  resumen: str = "") -> Noticia:
    return Noticia(id=str(hora.timestamp()), tickers=tuple(tickers), hora=hora, titular=titular,
                   resumen=resumen, fuente="benzinga", url="")


def crear_filing(forma: str, aceptado: str, items: tuple[str, ...] = ()) -> Filing:
    momento = datetime.fromisoformat(aceptado).replace(tzinfo=ET)
    return Filing(cik=1, forma=forma, acceso=f"x-{momento:%y%m%d%H%M}", fecha=momento.date(), aceptado=momento,
                  items=items, documento="d.htm")


@pytest.fixture
def filing():
    return crear_filing


@pytest.fixture
def noticia():
    return crear_noticia
