from dataclasses import dataclass
from datetime import datetime, timedelta

from hermes.inteligencia.sec.filings import Categoria, Filing, clasificar, conocidos_en
from hermes.inteligencia.sec.financieros import Financieros

VIGENCIA_SHELF = timedelta(days=3 * 365)
VENTANA_RECIENTE = timedelta(days=180)
VENTANA_INMEDIATA = timedelta(days=30)

# Pesos del puntaje (suman 100). Son reglas explícitas y auditables, no un modelo entrenado:
# el Laboratorio decide después si este puntaje predice algo.
PUNTOS_PROSPECTO_INMEDIATO = 30
PUNTOS_PROSPECTO_RECIENTE = 20
PUNTOS_SHELF_VIGENTE = 20
PUNTOS_S1_RECIENTE = 15
PUNTOS_FINANCIAMIENTO = 10
PUNTOS_RUNWAY_CRITICO = 25  # < 6 meses
PUNTOS_RUNWAY_BAJO = 15  # < 12 meses
PUNTOS_RUNWAY_MEDIO = 5  # < 24 meses
PUNTOS_RUNWAY_DESCONOCIDO = 10

UMBRAL_ALTO = 60
UMBRAL_MEDIO = 30


@dataclass(frozen=True)
class Componente:
    nombre: str
    puntos: int
    detalle: str


@dataclass(frozen=True)
class RiesgoDilucion:
    componentes: tuple[Componente, ...]

    @property
    def puntaje(self) -> int:
        return sum(c.puntos for c in self.componentes)

    @property
    def nivel(self) -> str:
        if self.puntaje >= UMBRAL_ALTO:
            return "alto"
        if self.puntaje >= UMBRAL_MEDIO:
            return "medio"
        return "bajo"


def _ultimo(filings: list[Filing], categoria: Categoria) -> Filing | None:
    candidatos = [f for f in filings if categoria in clasificar(f)]
    return max(candidatos, key=lambda f: f.aceptado) if candidatos else None


def _dias(desde: datetime, hasta: datetime) -> int:
    return (hasta - desde).days


def riesgo_dilucion(filings: list[Filing], financieros: Financieros, momento: datetime) -> RiesgoDilucion:
    conocidos = conocidos_en(filings, momento)
    componentes: list[Componente] = []

    prospecto = _ultimo(conocidos, Categoria.PROSPECTO)
    if prospecto and momento - prospecto.aceptado <= VENTANA_INMEDIATA:
        componentes.append(Componente("prospecto", PUNTOS_PROSPECTO_INMEDIATO,
                                      f"{prospecto.forma} hace {_dias(prospecto.aceptado, momento)} días"))
    elif prospecto and momento - prospecto.aceptado <= VENTANA_RECIENTE:
        componentes.append(Componente("prospecto", PUNTOS_PROSPECTO_RECIENTE,
                                      f"{prospecto.forma} hace {_dias(prospecto.aceptado, momento)} días"))

    shelf = _ultimo(conocidos, Categoria.SHELF)
    retiro = _ultimo(conocidos, Categoria.RETIRO)
    shelf_retirado = retiro is not None and shelf is not None and retiro.aceptado > shelf.aceptado
    if shelf and momento - shelf.aceptado <= VIGENCIA_SHELF and not shelf_retirado:
        componentes.append(Componente("shelf", PUNTOS_SHELF_VIGENTE,
                                      f"{shelf.forma} del {shelf.fecha.isoformat()}"))

    s1 = _ultimo(conocidos, Categoria.S1)
    if s1 and momento - s1.aceptado <= VENTANA_RECIENTE:
        componentes.append(Componente("s1", PUNTOS_S1_RECIENTE, f"{s1.forma} hace {_dias(s1.aceptado, momento)} días"))

    acuerdo = _ultimo(conocidos, Categoria.ACUERDO_FINANCIAMIENTO)
    if acuerdo and momento - acuerdo.aceptado <= VENTANA_RECIENTE:
        componentes.append(Componente("financiamiento", PUNTOS_FINANCIAMIENTO,
                                      f"8-K items {','.join(acuerdo.items)} hace {_dias(acuerdo.aceptado, momento)} días"))

    runway = financieros.runway_meses
    if runway is None:
        componentes.append(Componente("runway", PUNTOS_RUNWAY_DESCONOCIDO, "sin datos de caja o consumo"))
    elif runway < 6:
        componentes.append(Componente("runway", PUNTOS_RUNWAY_CRITICO, f"{runway:.1f} meses de caja"))
    elif runway < 12:
        componentes.append(Componente("runway", PUNTOS_RUNWAY_BAJO, f"{runway:.1f} meses de caja"))
    elif runway < 24:
        componentes.append(Componente("runway", PUNTOS_RUNWAY_MEDIO, f"{runway:.1f} meses de caja"))

    return RiesgoDilucion(tuple(componentes))
