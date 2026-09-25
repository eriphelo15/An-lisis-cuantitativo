import math
from dataclasses import dataclass
from datetime import date

CONCEPTOS_CAJA = (
    "CashAndCashEquivalentsAtCarryingValue",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "Cash",
)
CONCEPTO_FLUJO_OPERATIVO = "NetCashProvidedByUsedInOperatingActivities"
DIAS_POR_MES = 30.4375
DURACION_MINIMA_DIAS = 80  # un trimestre; evita periodos parciales raros


@dataclass(frozen=True)
class Hecho:
    valor: float
    inicio: date | None
    fin: date
    publicado: date

    @property
    def duracion_dias(self) -> int | None:
        return (self.fin - self.inicio).days if self.inicio else None


@dataclass(frozen=True)
class Financieros:
    caja: float | None
    caja_al: date | None
    quema_mensual: float | None  # positivo = la empresa consume caja
    acciones: float | None
    acciones_al: date | None

    @property
    def runway_meses(self) -> float | None:
        if self.caja is None or self.quema_mensual is None:
            return None
        if self.quema_mensual <= 0:
            return math.inf
        return self.caja / self.quema_mensual


def _hechos(facts: dict, taxonomia: str, concepto: str, unidad: str) -> list[Hecho]:
    registros = facts.get("facts", {}).get(taxonomia, {}).get(concepto, {}).get("units", {}).get(unidad, [])
    return [
        Hecho(
            valor=float(r["val"]),
            inicio=date.fromisoformat(r["start"]) if r.get("start") else None,
            fin=date.fromisoformat(r["end"]),
            publicado=date.fromisoformat(r["filed"]),
        )
        for r in registros
    ]


def _conocidos(hechos: list[Hecho], al: date) -> list[Hecho]:
    return [h for h in hechos if h.publicado < al]


def _caja(facts: dict, al: date) -> Hecho | None:
    candidatos = [
        (h, prioridad)
        for prioridad, concepto in enumerate(CONCEPTOS_CAJA)
        for h in _conocidos(_hechos(facts, "us-gaap", concepto, "USD"), al)
        if h.inicio is None
    ]
    if not candidatos:
        return None
    return max(candidatos, key=lambda c: (c[0].fin, -c[1], c[0].publicado))[0]


def _quema_mensual(facts: dict, al: date) -> float | None:
    hechos = [
        h
        for h in _conocidos(_hechos(facts, "us-gaap", CONCEPTO_FLUJO_OPERATIVO, "USD"), al)
        if h.duracion_dias and h.duracion_dias >= DURACION_MINIMA_DIAS
    ]
    if not hechos:
        return None
    ultimo_fin = max(h.fin for h in hechos)
    # con el mismo cierre, el periodo más corto refleja mejor el ritmo actual de consumo
    hecho = min((h for h in hechos if h.fin == ultimo_fin), key=lambda h: (h.duracion_dias, -h.publicado.toordinal()))
    return -hecho.valor / (hecho.duracion_dias / DIAS_POR_MES)


def _acciones(facts: dict, al: date) -> Hecho | None:
    hechos = _conocidos(_hechos(facts, "dei", "EntityCommonStockSharesOutstanding", "shares"), al)
    if not hechos:
        hechos = _conocidos(_hechos(facts, "us-gaap", "CommonStockSharesOutstanding", "shares"), al)
    if not hechos:
        return None
    return max(hechos, key=lambda h: (h.fin, h.publicado))


def financieros_al(facts: dict, al: date) -> Financieros:
    """Solo usa datos publicados antes del día `al`, para no mirar el futuro."""
    caja = _caja(facts, al)
    acciones = _acciones(facts, al)
    return Financieros(
        caja=caja.valor if caja else None,
        caja_al=caja.fin if caja else None,
        quema_mensual=_quema_mensual(facts, al),
        acciones=acciones.valor if acciones else None,
        acciones_al=acciones.fin if acciones else None,
    )
