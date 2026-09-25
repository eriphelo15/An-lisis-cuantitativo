from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Direccion(StrEnum):
    LARGO = "largo"
    CORTO = "corto"


@dataclass(frozen=True)
class Senal:
    """Orden bracket propuesta: entrada por ruptura del precio `entrada`, con stop y objetivo."""

    setup: str
    direccion: Direccion
    entrada: float
    stop: float
    objetivo: float
    hora: datetime
    motivo: str = ""

    @property
    def riesgo_por_accion(self) -> float:
        return abs(self.entrada - self.stop)

    @property
    def es_valida(self) -> bool:
        if self.riesgo_por_accion <= 0:
            return False
        if self.direccion is Direccion.LARGO:
            return self.stop < self.entrada < self.objetivo
        return self.objetivo < self.entrada < self.stop


@dataclass(frozen=True)
class Trade:
    ticker: str
    setup: str
    direccion: Direccion
    hora_senal: datetime
    hora_entrada: datetime
    precio_entrada: float
    stop: float
    objetivo: float
    hora_salida: datetime
    precio_salida: float
    motivo_salida: str
    acciones: int
    costo_pct: float

    @property
    def riesgo_por_accion(self) -> float:
        return abs(self.precio_entrada - self.stop)

    @property
    def r_bruto(self) -> float:
        signo = 1 if self.direccion is Direccion.LARGO else -1
        return signo * (self.precio_salida - self.precio_entrada) / self.riesgo_por_accion

    @property
    def r_neto(self) -> float:
        return self.r_bruto - self.costo_pct * self.precio_entrada / self.riesgo_por_accion

    @property
    def pnl_neto(self) -> float:
        return self.r_neto * self.riesgo_por_accion * self.acciones
