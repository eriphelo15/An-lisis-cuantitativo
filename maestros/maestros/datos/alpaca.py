from datetime import datetime, timedelta, timezone

import pandas as pd

from maestros.datos.calendario import ET
from maestros.http import ClienteHTTP
from maestros.informacion.catalizadores import Noticia

URL_BARRAS = "https://data.alpaca.markets/v2/stocks/bars"
URL_NOTICIAS = "https://data.alpaca.markets/v1beta1/news"
LLAMADAS_POR_SEGUNDO = 3  # plan gratuito: 200 por minuto
RETRASO_PLAN_GRATIS = timedelta(minutes=16)  # el plan gratis solo entrega SIP con más de 15 min de antigüedad

COLUMNAS_BARRAS = ["ticker", "hora", "apertura", "maximo", "minimo", "cierre", "volumen", "vwap", "operaciones"]


def _hora(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00")).astimezone(ET)


def _rfc3339(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parsear_barras(datos: dict) -> pd.DataFrame:
    filas = [
        {
            "ticker": ticker,
            "hora": _hora(b["t"]),
            "apertura": b["o"],
            "maximo": b["h"],
            "minimo": b["l"],
            "cierre": b["c"],
            "volumen": b["v"],
            "vwap": b.get("vw"),
            "operaciones": b.get("n"),
        }
        for ticker, barras in (datos.get("bars") or {}).items()
        for b in barras or []
    ]
    return pd.DataFrame(filas, columns=COLUMNAS_BARRAS)


def parsear_noticias(datos: dict) -> list[Noticia]:
    return [
        Noticia(
            id=str(n["id"]),
            tickers=tuple(s.upper() for s in n.get("symbols", [])),
            hora=_hora(n["created_at"]),
            titular=n.get("headline", "") or "",
            resumen=n.get("summary", "") or "",
            fuente=n.get("source", "") or "",
            url=n.get("url", "") or "",
        )
        for n in datos.get("news") or []
    ]


class ClienteAlpaca:
    def __init__(self, http: ClienteHTTP):
        self._http = http

    @staticmethod
    def headers(key_id: str, secret: str) -> dict[str, str]:
        return {"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret}

    def _paginas(self, url: str, params: dict, ttl: float | None):
        token = None
        while True:
            datos = self._http.pedir_json(url, params={**params, **({"page_token": token} if token else {})},
                                          ttl_segundos=ttl)
            yield datos
            token = datos.get("next_page_token")
            if not token:
                return

    def barras_minuto(self, tickers: list[str], desde: datetime, hasta: datetime) -> pd.DataFrame:
        """Barras de 1 minuto sin ajustar, incluyendo premarket y after hours."""
        hasta = min(hasta, datetime.now(ET) - RETRASO_PLAN_GRATIS)
        params = {
            "symbols": ",".join(sorted(set(tickers))),
            "timeframe": "1Min",
            "start": _rfc3339(desde),
            "end": _rfc3339(hasta),
            "adjustment": "raw",
            "feed": "sip",
            "limit": 10000,
            "sort": "asc",
        }
        partes = [parsear_barras(p) for p in self._paginas(URL_BARRAS, params, ttl=None)]
        partes = [p for p in partes if not p.empty]
        return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=COLUMNAS_BARRAS)

    def noticias(self, desde: datetime, hasta: datetime, tickers: list[str] | None = None) -> list[Noticia]:
        params = {"start": _rfc3339(desde), "end": _rfc3339(hasta), "limit": 50, "sort": "asc",
                  "include_content": "false"}
        if tickers:
            params["symbols"] = ",".join(sorted(set(tickers)))
        ttl = None if hasta < datetime.now(ET) - timedelta(days=1) else 0
        return [n for pagina in self._paginas(URL_NOTICIAS, params, ttl) for n in parsear_noticias(pagina)]
