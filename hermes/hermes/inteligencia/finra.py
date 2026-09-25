from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from hermes.http import ClienteHTTP

URL_SHORT_INTEREST = "https://api.finra.org/data/group/otcMarket/name/EquityShortInterest"
URL_VOLUMEN_CORTO = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{fecha:%Y%m%d}.txt"

# FINRA publica el short interest varios días hábiles después de la fecha de liquidación.
# Para no usar datos que todavía no existían, solo se toma lo liquidado hace al menos 12 días.
RETRASO_PUBLICACION = timedelta(days=12)
UN_DIA = 24 * 3600


@dataclass(frozen=True)
class ShortInterest:
    liquidacion: date
    posicion: float
    volumen_diario_promedio: float | None
    dias_para_cubrir: float | None


def _numero(valor) -> float | None:
    return None if valor in (None, "") else float(valor)


def parsear_short_interest(filas: list[dict]) -> list[ShortInterest]:
    registros = [
        ShortInterest(
            liquidacion=date.fromisoformat(f["settlementDate"][:10]),
            posicion=float(f["currentShortPositionQuantity"]),
            volumen_diario_promedio=_numero(f.get("averageDailyVolumeQuantity")),
            dias_para_cubrir=_numero(f.get("daysToCoverQuantity")),
        )
        for f in filas
        if f.get("settlementDate") and f.get("currentShortPositionQuantity") not in (None, "")
    ]
    return sorted(registros, key=lambda r: r.liquidacion)


def short_interest(http: ClienteHTTP, ticker: str, al: date | None = None) -> list[ShortInterest]:
    cuerpo = {
        "compareFilters": [{"compareType": "EQUAL", "fieldName": "symbolCode", "fieldValue": ticker.upper()}],
        "limit": 500,
    }
    filas = http.pedir_json(URL_SHORT_INTEREST, metodo="POST", cuerpo_json=cuerpo, ttl_segundos=UN_DIA)
    registros = parsear_short_interest(filas)
    if al is not None:
        registros = [r for r in registros if r.liquidacion <= al - RETRASO_PUBLICACION]
    return registros


def parsear_volumen_corto(texto: str) -> pd.DataFrame:
    filas = []
    for linea in texto.splitlines()[1:]:
        partes = linea.strip().split("|")
        if len(partes) < 5 or not partes[0].isdigit():
            continue
        corto, total = float(partes[2]), float(partes[4])
        filas.append({
            "fecha": pd.Timestamp(partes[0]).date(),
            "ticker": partes[1],
            "volumen_corto": corto,
            "volumen_total": total,
            "pct_corto": corto / total if total else None,
        })
    return pd.DataFrame(filas, columns=["fecha", "ticker", "volumen_corto", "volumen_total", "pct_corto"])


def volumen_corto(http: ClienteHTTP, fecha: date) -> pd.DataFrame:
    """Volumen en corto reportado a FINRA ese día (se publica al cierre de la sesión)."""
    return parsear_volumen_corto(http.pedir_texto(URL_VOLUMEN_CORTO.format(fecha=fecha), ttl_segundos=None))
