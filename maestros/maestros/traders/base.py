from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

import pandas as pd

from maestros.backtest.modelos import Senal
from maestros.informacion.ficha import Ficha


@dataclass(frozen=True)
class Contexto:
    """Lo que un algoritmo puede ver en un instante. `barras` termina en la barra actual:
    el mismo objeto se arma en backtest y en vivo, así ningún algoritmo puede mirar el futuro."""

    ticker: str
    fecha: date
    barras: pd.DataFrame
    cierre_previo: float
    volumen_normal: pd.Series | None = None  # volumen acumulado típico por minuto desde las 4:00 ET
    ficha: Ficha | None = None

    @property
    def ahora(self) -> datetime:
        return self.barras["hora"].iloc[-1]


class Estrategia(Protocol):
    nombre: str

    def evaluar(self, ctx: Contexto) -> Senal | None: ...
