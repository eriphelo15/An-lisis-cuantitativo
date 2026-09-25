from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from maestros.datos.calendario import ET


@dataclass(frozen=True)
class Filing:
    cik: int
    forma: str
    acceso: str
    fecha: date
    aceptado: datetime
    items: tuple[str, ...]
    documento: str


class Categoria(StrEnum):
    SHELF = "shelf"
    PROSPECTO = "prospecto"
    S1 = "s1"
    ACUERDO_FINANCIAMIENTO = "acuerdo_financiamiento"
    AVISO_LISTADO = "aviso_listado"
    CAMBIO_ESTATUTOS = "cambio_estatutos"
    FINANCIERO = "financiero"
    RETIRO = "retiro"
    OTRO = "otro"


FORMAS_SHELF = {"S-3", "F-3", "S-3ASR", "F-3ASR"}
FORMAS_S1 = {"S-1", "F-1", "S-1MEF", "F-1MEF"}
FORMAS_FINANCIERAS = {"10-Q", "10-K", "20-F", "40-F", "10-KT", "10-QT"}
FORMAS_EVENTO = {"8-K", "6-K"}


def parsear_aceptacion(texto: str) -> datetime:
    # EDGAR publica acceptanceDateTime en hora del Este aunque el texto termine en "Z":
    # un filing aceptado después de las 17:30 ET lleva fecha del día hábil siguiente.
    return datetime.strptime(texto[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=ET)


def parsear_bloque(bloque: dict, cik: int) -> list[Filing]:
    n = len(bloque.get("accessionNumber", []))
    items = bloque.get("items") or [""] * n
    documentos = bloque.get("primaryDocument") or [""] * n
    return [
        Filing(
            cik=cik,
            forma=bloque["form"][i].strip().upper(),
            acceso=bloque["accessionNumber"][i],
            fecha=date.fromisoformat(bloque["filingDate"][i]),
            aceptado=parsear_aceptacion(bloque["acceptanceDateTime"][i]),
            items=tuple(x.strip() for x in (items[i] or "").split(",") if x.strip()),
            documento=documentos[i] or "",
        )
        for i in range(n)
    ]


def clasificar(filing: Filing) -> set[Categoria]:
    base = filing.forma.split("/")[0].strip()
    if base in FORMAS_SHELF:
        return {Categoria.SHELF}
    if base.startswith("424B"):
        return {Categoria.PROSPECTO}
    if base in FORMAS_S1:
        return {Categoria.S1}
    if base == "RW":
        return {Categoria.RETIRO}
    if base in FORMAS_FINANCIERAS:
        return {Categoria.FINANCIERO}
    if base in FORMAS_EVENTO:
        categorias = set()
        if {"1.01", "3.02"} & set(filing.items):
            categorias.add(Categoria.ACUERDO_FINANCIAMIENTO)
        if "3.01" in filing.items:
            categorias.add(Categoria.AVISO_LISTADO)
        if "5.03" in filing.items:
            categorias.add(Categoria.CAMBIO_ESTATUTOS)
        return categorias or {Categoria.OTRO}
    return {Categoria.OTRO}


def conocidos_en(filings: list[Filing], momento: datetime) -> list[Filing]:
    return [f for f in filings if f.aceptado < momento]
