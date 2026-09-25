from dataclasses import dataclass
from datetime import datetime

from maestros.informacion.catalizadores import Noticia
from maestros.informacion.dilucion import RiesgoDilucion, riesgo_dilucion
from maestros.informacion.filings import Filing
from maestros.informacion.financieros import Financieros, financieros_al


@dataclass(frozen=True)
class Ficha:
    """Lo que se sabe de un ticker al inicio del día. Las noticias se filtran por hora en cada instante."""

    ticker: str
    financieros: Financieros
    riesgo_dilucion: RiesgoDilucion | None
    noticias: tuple[Noticia, ...]

    @property
    def float_aprox(self) -> float | None:
        # Sin fuente gratuita del float exacto, se usan las acciones en circulación: es un tope superior del float.
        return self.financieros.acciones

    def noticias_entre(self, desde: datetime, hasta: datetime) -> list[Noticia]:
        return [n for n in self.noticias if desde <= n.hora <= hasta]


def construir_ficha(
    ticker: str,
    inicio_dia: datetime,
    filings: list[Filing],
    companyfacts: dict,
    noticias: list[Noticia],
) -> Ficha:
    financieros = financieros_al(companyfacts, inicio_dia.date())
    return Ficha(
        ticker=ticker.upper(),
        financieros=financieros,
        riesgo_dilucion=riesgo_dilucion(filings, financieros, inicio_dia) if filings or companyfacts else None,
        noticias=tuple(sorted((n for n in noticias if ticker.upper() in n.tickers), key=lambda n: n.hora)),
    )
