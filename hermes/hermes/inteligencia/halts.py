import xml.etree.ElementTree as ET_XML
from dataclasses import dataclass
from datetime import datetime

from hermes.http import ClienteHTTP
from hermes.inteligencia.sec.filings import ET

URL_HALTS_RSS = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"
CODIGOS_LULD = {"LUDP", "LUDS"}
CODIGOS_NOTICIA = {"T1", "T2", "T3"}


@dataclass(frozen=True)
class Halt:
    ticker: str
    nombre: str
    mercado: str
    codigo: str
    inicio: datetime
    reanudacion_cotizacion: datetime | None
    reanudacion_trading: datetime | None

    @property
    def es_luld(self) -> bool:
        return self.codigo in CODIGOS_LULD

    @property
    def es_noticia(self) -> bool:
        return self.codigo in CODIGOS_NOTICIA

    @property
    def activo(self) -> bool:
        return self.reanudacion_trading is None


def _local(etiqueta: str) -> str:
    return etiqueta.rsplit("}", 1)[-1]


def _fecha_hora(fecha: str, hora: str) -> datetime | None:
    if not fecha or not hora:
        return None
    return datetime.strptime(f"{fecha.strip()} {hora.strip()}", "%m/%d/%Y %H:%M:%S").replace(tzinfo=ET)


def parsear_halts(xml: str) -> list[Halt]:
    raiz = ET_XML.fromstring(xml)
    halts = []
    for item in raiz.iter():
        if _local(item.tag) != "item":
            continue
        campos = {_local(hijo.tag): (hijo.text or "").strip() for hijo in item}
        inicio = _fecha_hora(campos.get("HaltDate", ""), campos.get("HaltTime", ""))
        if not inicio or not campos.get("IssueSymbol"):
            continue
        fecha_reanudacion = campos.get("ResumptionDate", "")
        halts.append(Halt(
            ticker=campos["IssueSymbol"].upper(),
            nombre=campos.get("IssueName", ""),
            mercado=campos.get("Market", ""),
            codigo=campos.get("ReasonCode", "").upper(),
            inicio=inicio,
            reanudacion_cotizacion=_fecha_hora(fecha_reanudacion, campos.get("ResumptionQuoteTime", "")),
            reanudacion_trading=_fecha_hora(fecha_reanudacion, campos.get("ResumptionTradeTime", "")),
        ))
    return halts


def halts_actuales(http: ClienteHTTP) -> list[Halt]:
    return parsear_halts(http.pedir_texto(URL_HALTS_RSS))
