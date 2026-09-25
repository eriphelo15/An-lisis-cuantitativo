from dataclasses import dataclass
from datetime import datetime, timedelta

from maestros.informacion.filings import Categoria, Filing, clasificar, conocidos_en
from maestros.informacion.financieros import Financieros

VIGENCIA_SHELF = timedelta(days=3 * 365)
VENTANA_RECIENTE = timedelta(days=180)
VENTANA_INMEDIATA = timedelta(days=30)

# Pesos explícitos (suman 100). El backtest decide si el puntaje predice algo.
PUNTOS = {
    "prospecto_inmediato": 30,
    "prospecto_reciente": 20,
    "shelf": 20,
    "s1": 15,
    "financiamiento": 10,
    "runway_critico": 25,  # < 6 meses
    "runway_bajo": 15,  # < 12 meses
    "runway_medio": 5,  # < 24 meses
    "runway_desconocido": 10,
}


@dataclass(frozen=True)
class RiesgoDilucion:
    componentes: tuple[tuple[str, int, str], ...]

    @property
    def puntaje(self) -> int:
        return sum(p for _, p, _ in self.componentes)

    @property
    def nivel(self) -> str:
        return "alto" if self.puntaje >= 60 else "medio" if self.puntaje >= 30 else "bajo"


def _ultimo(filings: list[Filing], categoria: Categoria) -> Filing | None:
    candidatos = [f for f in filings if categoria in clasificar(f)]
    return max(candidatos, key=lambda f: f.aceptado) if candidatos else None


def riesgo_dilucion(filings: list[Filing], financieros: Financieros, momento: datetime) -> RiesgoDilucion:
    conocidos = conocidos_en(filings, momento)
    componentes = []

    def agregar(clave: str, detalle: str) -> None:
        componentes.append((clave, PUNTOS[clave], detalle))

    prospecto = _ultimo(conocidos, Categoria.PROSPECTO)
    if prospecto and momento - prospecto.aceptado <= VENTANA_INMEDIATA:
        agregar("prospecto_inmediato", f"{prospecto.forma} del {prospecto.fecha}")
    elif prospecto and momento - prospecto.aceptado <= VENTANA_RECIENTE:
        agregar("prospecto_reciente", f"{prospecto.forma} del {prospecto.fecha}")

    shelf = _ultimo(conocidos, Categoria.SHELF)
    retiro = _ultimo(conocidos, Categoria.RETIRO)
    if shelf and momento - shelf.aceptado <= VIGENCIA_SHELF and not (retiro and retiro.aceptado > shelf.aceptado):
        agregar("shelf", f"{shelf.forma} del {shelf.fecha}")

    s1 = _ultimo(conocidos, Categoria.S1)
    if s1 and momento - s1.aceptado <= VENTANA_RECIENTE:
        agregar("s1", f"{s1.forma} del {s1.fecha}")

    acuerdo = _ultimo(conocidos, Categoria.ACUERDO_FINANCIAMIENTO)
    if acuerdo and momento - acuerdo.aceptado <= VENTANA_RECIENTE:
        agregar("financiamiento", f"8-K items {','.join(acuerdo.items)} del {acuerdo.fecha}")

    runway = financieros.runway_meses
    if runway is None:
        agregar("runway_desconocido", "sin datos de caja o consumo")
    elif runway < 6:
        agregar("runway_critico", f"{runway:.1f} meses")
    elif runway < 12:
        agregar("runway_bajo", f"{runway:.1f} meses")
    elif runway < 24:
        agregar("runway_medio", f"{runway:.1f} meses")

    return RiesgoDilucion(tuple(componentes))
