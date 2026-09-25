import math
from collections.abc import Callable
from datetime import date, datetime, time, timedelta

import pandas as pd
import requests

from hermes.http import NoEncontrado
from hermes.inteligencia.dilucion import riesgo_dilucion
from hermes.inteligencia.sec.cliente import ClienteSEC, Empresa
from hermes.inteligencia.sec.filings import ET, Categoria, clasificar
from hermes.inteligencia.sec.financieros import financieros_al

APERTURA = time(9, 30)
VENTANA_OFERTA = timedelta(days=7)  # ~5 sesiones

ResolverCik = Callable[[str, date], int | None]


def _oferta_posterior(empresa: Empresa, momento: datetime) -> bool:
    return any(
        momento <= f.aceptado < momento + VENTANA_OFERTA and Categoria.PROSPECTO in clasificar(f)
        for f in empresa.filings
    )


def evaluar_dilucion(
    runners: pd.DataFrame,
    sec: ClienteSEC,
    resolver_cik: ResolverCik,
    progreso: Callable[[str], None] = lambda _: None,
) -> pd.DataFrame:
    """Calcula, para cada runner, el riesgo de dilución conocido antes de la apertura de ese día
    y si la empresa presentó un prospecto (oferta) en la semana siguiente."""
    empresas: dict[int, tuple[Empresa, dict] | None] = {}
    filas = []
    total = len(runners)

    for i, ev in enumerate(runners.itertuples(index=False), start=1):
        if i % 25 == 0 or i == total:
            progreso(f"  evaluando {i}/{total}")
        momento = datetime.combine(ev.fecha, APERTURA, tzinfo=ET)
        fila = {"ticker": ev.ticker, "fecha": ev.fecha, "cik": None, "puntaje_dilucion": None,
                "nivel_dilucion": "sin_cik", "runway_meses": None, "componentes": "", "oferta_5d": None}

        cik = resolver_cik(ev.ticker, ev.fecha)
        if cik is None:
            filas.append(fila)
            continue
        fila["cik"] = cik

        if cik not in empresas:
            try:
                empresas[cik] = (sec.empresa(cik), sec.companyfacts(cik))
            except (requests.RequestException, NoEncontrado) as error:
                progreso(f"  error con {ev.ticker} (CIK {cik}): {error}")
                empresas[cik] = None
        if empresas[cik] is None:
            fila["nivel_dilucion"] = "error"
            filas.append(fila)
            continue

        empresa, facts = empresas[cik]
        financieros = financieros_al(facts, ev.fecha)
        riesgo = riesgo_dilucion(list(empresa.filings), financieros, momento)
        runway = financieros.runway_meses
        fila.update({
            "puntaje_dilucion": riesgo.puntaje,
            "nivel_dilucion": riesgo.nivel,
            "runway_meses": None if runway is None or math.isinf(runway) else runway,
            "componentes": "; ".join(f"{c.nombre}: {c.detalle}" for c in riesgo.componentes),
            "oferta_5d": _oferta_posterior(empresa, momento),
        })
        filas.append(fila)

    return runners.merge(pd.DataFrame(filas), on=["ticker", "fecha"], how="left")
