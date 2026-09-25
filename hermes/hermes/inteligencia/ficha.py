import math
from dataclasses import dataclass
from datetime import datetime

from hermes.inteligencia.dilucion import RiesgoDilucion, riesgo_dilucion
from hermes.inteligencia.finra import ShortInterest
from hermes.inteligencia.sec.cliente import Empresa
from hermes.inteligencia.sec.filings import Categoria, Filing, clasificar, conocidos_en
from hermes.inteligencia.sec.financieros import Financieros, financieros_al

CATEGORIAS_RELEVANTES = {
    Categoria.SHELF, Categoria.PROSPECTO, Categoria.S1, Categoria.EFECTIVIDAD,
    Categoria.ACUERDO_FINANCIAMIENTO, Categoria.AVISO_LISTADO, Categoria.CAMBIO_ESTATUTOS,
    Categoria.PARTICIPACION, Categoria.RETIRO, Categoria.FINANCIERO,
}


@dataclass(frozen=True)
class Ficha:
    ticker: str
    empresa: Empresa
    momento: datetime
    financieros: Financieros
    riesgo: RiesgoDilucion
    filings_relevantes: tuple[Filing, ...]
    short_interest: ShortInterest | None


def construir_ficha(
    ticker: str,
    empresa: Empresa,
    companyfacts: dict,
    momento: datetime,
    short_interest: list[ShortInterest] | None = None,
    max_filings: int = 12,
) -> Ficha:
    conocidos = conocidos_en(list(empresa.filings), momento)
    financieros = financieros_al(companyfacts, momento.date())
    relevantes = [f for f in conocidos if clasificar(f) & CATEGORIAS_RELEVANTES]
    return Ficha(
        ticker=ticker.upper(),
        empresa=empresa,
        momento=momento,
        financieros=financieros,
        riesgo=riesgo_dilucion(conocidos, financieros, momento),
        filings_relevantes=tuple(sorted(relevantes, key=lambda f: f.aceptado, reverse=True)[:max_filings]),
        short_interest=short_interest[-1] if short_interest else None,
    )


def _millones(valor: float | None) -> str:
    return "—" if valor is None else f"{valor / 1e6:,.1f} M"


def formatear(ficha: Ficha) -> str:
    fin = ficha.financieros
    runway = fin.runway_meses
    if runway is None:
        texto_runway = "sin datos"
    elif math.isinf(runway):
        texto_runway = "la operación genera caja"
    else:
        texto_runway = f"{runway:.1f} meses"

    lineas = [
        f"{ficha.ticker} — {ficha.empresa.nombre} (CIK {ficha.empresa.cik})",
        f"Datos conocidos al {ficha.momento:%Y-%m-%d %H:%M} ET",
        "",
        f"RIESGO DE DILUCIÓN: {ficha.riesgo.puntaje}/100 ({ficha.riesgo.nivel})",
    ]
    lineas += [f"  +{c.puntos:>2}  {c.nombre}: {c.detalle}" for c in ficha.riesgo.componentes]
    lineas += [
        "",
        "CAJA",
        f"  Caja:            {_millones(fin.caja)} USD" + (f" (al {fin.caja_al})" if fin.caja_al else ""),
        f"  Consumo mensual: {_millones(fin.quema_mensual)} USD",
        f"  Runway:          {texto_runway}",
        f"  Acciones:        {_millones(fin.acciones)}" + (f" (al {fin.acciones_al})" if fin.acciones_al else ""),
    ]
    if ficha.short_interest:
        si = ficha.short_interest
        porcentaje = f" ({si.posicion / fin.acciones:.1%} de las acciones)" if fin.acciones else ""
        lineas += [
            "",
            "SHORT INTEREST (FINRA)",
            f"  {si.posicion:,.0f} acciones al {si.liquidacion}{porcentaje}",
            f"  Días para cubrir: {si.dias_para_cubrir if si.dias_para_cubrir is not None else '—'}",
        ]
    lineas += ["", "FILINGS RELEVANTES"]
    lineas += [
        f"  {f.fecha}  {f.forma:<10} {', '.join(sorted(c.value for c in clasificar(f)))}"
        + (f" (items {','.join(f.items)})" if f.items else "")
        for f in ficha.filings_relevantes
    ] or ["  ninguno"]
    return "\n".join(lineas)
