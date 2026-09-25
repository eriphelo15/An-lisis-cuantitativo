from datetime import date

import pandas as pd

from maestros.http import ClienteHTTP

LLAMADAS_POR_SEGUNDO_GRATIS = 5 / 60
COLUMNAS_DIARIO = ["fecha", "ticker", "apertura", "maximo", "minimo", "cierre", "volumen", "vwap"]


def parsear_diario_agrupado(datos: dict, fecha: date) -> pd.DataFrame:
    filas = [
        {"fecha": fecha, "ticker": r["T"], "apertura": r.get("o"), "maximo": r.get("h"), "minimo": r.get("l"),
         "cierre": r.get("c"), "volumen": r.get("v"), "vwap": r.get("vw")}
        for r in datos.get("results") or []
    ]
    return pd.DataFrame(filas, columns=COLUMNAS_DIARIO)


class ClienteMassive:
    def __init__(self, http: ClienteHTTP, api_key: str, base_url: str):
        self._http = http
        self._api_key = api_key
        self._base = base_url

    def diario_agrupado(self, fecha: date) -> pd.DataFrame:
        """Todas las acciones que operaron ese día, sin ajustar por splits."""
        datos = self._http.pedir_json(
            f"{self._base}/v2/aggs/grouped/locale/us/market/stocks/{fecha.isoformat()}",
            params={"adjusted": "false", "apiKey": self._api_key},
            ttl_segundos=None if fecha < date.today() else 0,
        )
        return parsear_diario_agrupado(datos, fecha)
