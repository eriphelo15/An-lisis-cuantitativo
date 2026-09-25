"""Reglas del mercado que afectan la ejecución: SSR, halts (Nasdaq Trader) y datos en corto (FINRA)."""

import xml.etree.ElementTree as ET_XML
from dataclasses import dataclass
from datetime import date, datetime

import pandas as pd

from maestros.datos.calendario import ET
from maestros.http import ClienteHTTP

UMBRAL_SSR = 0.10  # Regla 201: caída de 10% frente al cierre previo
URL_HALTS_RSS = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"
URL_SHORT_INTEREST = "https://api.finra.org/data/group/otcMarket/name/EquityShortInterest"


def inicio_ssr(barras: pd.DataFrame, cierre_previo: float) -> datetime | None:
    """Hora en que se activa la restricción de venta en corto (dura el resto del día y el día siguiente)."""
    activadas = barras[barras["minimo"] <= cierre_previo * (1 - UMBRAL_SSR)]
    return activadas["hora"].iloc[0] if not activadas.empty else None


def ssr_activo(momento: datetime, inicio_hoy: datetime | None, activado_ayer: bool) -> bool:
    return activado_ayer or (inicio_hoy is not None and momento >= inicio_hoy)


@dataclass(frozen=True)
class Halt:
    ticker: str
    codigo: str
    inicio: datetime
    reanudacion: datetime | None

    @property
    def es_luld(self) -> bool:
        return self.codigo in {"LUDP", "LUDS"}

    @property
    def activo(self) -> bool:
        return self.reanudacion is None


def _fecha_hora(fecha: str, hora: str) -> datetime | None:
    if not fecha.strip() or not hora.strip():
        return None
    return datetime.strptime(f"{fecha.strip()} {hora.strip()}", "%m/%d/%Y %H:%M:%S").replace(tzinfo=ET)


def parsear_halts(xml: str) -> list[Halt]:
    halts = []
    for item in ET_XML.fromstring(xml).iter():
        if item.tag.rsplit("}", 1)[-1] != "item":
            continue
        campos = {hijo.tag.rsplit("}", 1)[-1]: (hijo.text or "").strip() for hijo in item}
        inicio = _fecha_hora(campos.get("HaltDate", ""), campos.get("HaltTime", ""))
        if inicio and campos.get("IssueSymbol"):
            halts.append(Halt(
                ticker=campos["IssueSymbol"].upper(),
                codigo=campos.get("ReasonCode", "").upper(),
                inicio=inicio,
                reanudacion=_fecha_hora(campos.get("ResumptionDate", ""), campos.get("ResumptionTradeTime", "")),
            ))
    return halts


def halts_actuales(http: ClienteHTTP) -> list[Halt]:
    return parsear_halts(http.pedir_texto(URL_HALTS_RSS))


@dataclass(frozen=True)
class ShortInterest:
    liquidacion: date
    posicion: float
    dias_para_cubrir: float | None


def parsear_short_interest(filas: list[dict]) -> list[ShortInterest]:
    return sorted(
        (
            ShortInterest(
                liquidacion=date.fromisoformat(f["settlementDate"][:10]),
                posicion=float(f["currentShortPositionQuantity"]),
                dias_para_cubrir=float(f["daysToCoverQuantity"]) if f.get("daysToCoverQuantity") not in (None, "") else None,
            )
            for f in filas
            if f.get("settlementDate") and f.get("currentShortPositionQuantity") not in (None, "")
        ),
        key=lambda r: r.liquidacion,
    )


URL_VOLUMEN_CORTO = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{fecha:%Y%m%d}.txt"


def parsear_volumen_corto(texto: str) -> pd.DataFrame:
    filas = []
    for linea in texto.splitlines()[1:]:
        partes = linea.strip().split("|")
        if len(partes) < 5 or not partes[0].isdigit():
            continue
        corto, total = float(partes[2]), float(partes[4])
        filas.append({"ticker": partes[1], "volumen_corto": corto, "volumen_total": total,
                      "pct_corto": corto / total if total else None})
    return pd.DataFrame(filas, columns=["ticker", "volumen_corto", "volumen_total", "pct_corto"])


def volumen_corto(http: ClienteHTTP, fecha: date) -> pd.DataFrame:
    return parsear_volumen_corto(http.pedir_texto(URL_VOLUMEN_CORTO.format(fecha=fecha), ttl_segundos=None))


def short_interest(http: ClienteHTTP, ticker: str) -> list[ShortInterest]:
    cuerpo = {"compareFilters": [{"compareType": "EQUAL", "fieldName": "symbolCode", "fieldValue": ticker.upper()}],
              "limit": 500}
    return parsear_short_interest(http.pedir_json(URL_SHORT_INTEREST, metodo="POST", cuerpo_json=cuerpo,
                                                  ttl_segundos=24 * 3600))
