from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class Filing:
    cik: int
    forma: str
    acceso: str
    fecha: date
    aceptado: datetime
    items: tuple[str, ...]
    documento: str

    @property
    def url(self) -> str:
        return f"https://www.sec.gov/Archives/edgar/data/{self.cik}/{self.acceso.replace('-', '')}/{self.documento}"


class Categoria(StrEnum):
    SHELF = "shelf"
    PROSPECTO = "prospecto"
    S1 = "s1"
    EFECTIVIDAD = "efectividad"
    ACUERDO_FINANCIAMIENTO = "acuerdo_financiamiento"
    AVISO_LISTADO = "aviso_listado"
    CAMBIO_ESTATUTOS = "cambio_estatutos"
    FINANCIERO = "financiero"
    INSIDER = "insider"
    PARTICIPACION = "participacion"
    PLAN_EMPLEADOS = "plan_empleados"
    PROXY = "proxy"
    RETIRO = "retiro"
    OTRO = "otro"


FORMAS_SHELF = {"S-3", "F-3", "S-3ASR", "F-3ASR"}
FORMAS_S1 = {"S-1", "F-1", "S-1MEF", "F-1MEF"}
FORMAS_FINANCIERAS = {"10-Q", "10-K", "20-F", "40-F", "10-KT", "10-QT"}
FORMAS_INSIDER = {"3", "4", "5"}
FORMAS_PARTICIPACION = {"SC 13D", "SC 13G", "SCHEDULE 13D", "SCHEDULE 13G"}
FORMAS_PROXY = {"DEF 14A", "PRE 14A", "DEF 14C", "PRE 14C"}
FORMAS_EVENTO = {"8-K", "6-K"}

ITEMS_FINANCIAMIENTO = {"1.01", "3.02"}
ITEM_AVISO_LISTADO = "3.01"
ITEM_ESTATUTOS = "5.03"


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
    if base == "EFFECT":
        return {Categoria.EFECTIVIDAD}
    if base in FORMAS_EVENTO:
        categorias = set()
        if ITEMS_FINANCIAMIENTO & set(filing.items):
            categorias.add(Categoria.ACUERDO_FINANCIAMIENTO)
        if ITEM_AVISO_LISTADO in filing.items:
            categorias.add(Categoria.AVISO_LISTADO)
        if ITEM_ESTATUTOS in filing.items:
            categorias.add(Categoria.CAMBIO_ESTATUTOS)
        return categorias or {Categoria.OTRO}
    if base in FORMAS_FINANCIERAS:
        return {Categoria.FINANCIERO}
    if base in FORMAS_INSIDER:
        return {Categoria.INSIDER}
    if base in FORMAS_PARTICIPACION:
        return {Categoria.PARTICIPACION}
    if base == "S-8":
        return {Categoria.PLAN_EMPLEADOS}
    if base in FORMAS_PROXY:
        return {Categoria.PROXY}
    if base == "RW":
        return {Categoria.RETIRO}
    return {Categoria.OTRO}


def conocidos_en(filings: list[Filing], momento: datetime) -> list[Filing]:
    return [f for f in filings if f.aceptado < momento]
