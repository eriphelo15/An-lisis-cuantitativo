"""Tipos base para señales y estrategias."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import pandas as pd


class DireccionTrade(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Senal:
    direccion: DireccionTrade
    precio_entrada: float
    stop_loss: float
    take_profit: float
    estrategia: str
    confianza: float = 1.0
    etiqueta: str = ""

    @property
    def riesgo_puntos(self) -> float:
        return abs(self.precio_entrada - self.stop_loss)

    @property
    def recompensa_puntos(self) -> float:
        return abs(self.take_profit - self.precio_entrada)

    @property
    def ratio_rr(self) -> float:
        if self.riesgo_puntos == 0:
            return 0.0
        return self.recompensa_puntos / self.riesgo_puntos


class EstrategiaBase:
    def __init__(self, nombre: str):
        self.nombre = nombre

    def calcular_senal(self, datos: pd.DataFrame) -> Optional[Senal]:
        raise NotImplementedError

    def reiniciar_dia(self):
        pass
