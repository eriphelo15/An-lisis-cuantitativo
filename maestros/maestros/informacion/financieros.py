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
DURACION_MINIMA_DIAS = 80


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
    quema_mensual: float | None  # positivo = consume caja
    acciones: float | None

    @property
    def runway_meses(self) -> float | None:
        if self.caja is None or self.quema_mensual is None:
            return None
        if self.quema_mensual <= 0:
            return math.inf
        return self.caja / self.quema_mensual


def _hechos(facts: dict, taxonomia: str, concepto: str, unidad: str, al: date) -> list[Hecho]:
    registros = facts.get("facts", {}).get(taxonomia, {}).get(concepto, {}).get("units", {}).get(unidad, [])
    hechos = [
        Hecho(float(r["val"]), date.fromisoformat(r["start"]) if r.get("start") else None,
              date.fromisoformat(r["end"]), date.fromisoformat(r["filed"]))
        for r in registros
    ]
    return [h for h in hechos if h.publicado < al]


def financieros_al(facts: dict, al: date) -> Financieros:
    """Solo usa datos publicados antes del día `al`."""
    cajas = [
        (h, prioridad)
        for prioridad, concepto in enumerate(CONCEPTOS_CAJA)
        for h in _hechos(facts, "us-gaap", concepto, "USD", al)
        if h.inicio is None
    ]
    caja = max(cajas, key=lambda c: (c[0].fin, -c[1], c[0].publicado))[0].valor if cajas else None

    flujos = [h for h in _hechos(facts, "us-gaap", CONCEPTO_FLUJO_OPERATIVO, "USD", al)
              if h.duracion_dias and h.duracion_dias >= DURACION_MINIMA_DIAS]
    quema = None
    if flujos:
        ultimo_fin = max(h.fin for h in flujos)
        # con el mismo cierre, el periodo más corto refleja mejor el ritmo actual
        h = min((h for h in flujos if h.fin == ultimo_fin), key=lambda h: h.duracion_dias)
        quema = -h.valor / (h.duracion_dias / DIAS_POR_MES)

    acciones_h = (_hechos(facts, "dei", "EntityCommonStockSharesOutstanding", "shares", al)
                  or _hechos(facts, "us-gaap", "CommonStockSharesOutstanding", "shares", al))
    acciones = max(acciones_h, key=lambda h: (h.fin, h.publicado)).valor if acciones_h else None
    return Financieros(caja=caja, quema_mensual=quema, acciones=acciones)
