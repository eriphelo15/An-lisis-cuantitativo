from dataclasses import dataclass

from maestros.http import ClienteHTTP, NoEncontrado
from maestros.informacion.filings import Filing, parsear_bloque

URL_TICKERS = "https://www.sec.gov/files/company_tickers.json"
URL_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
URL_SUBMISSIONS_PAGINA = "https://data.sec.gov/submissions/{nombre}"
URL_COMPANYFACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

LLAMADAS_POR_SEGUNDO = 8  # la SEC permite 10/s
UNA_HORA = 3600
UN_DIA = 24 * UNA_HORA


@dataclass(frozen=True)
class Empresa:
    cik: int
    nombre: str
    filings: tuple[Filing, ...]


class ClienteSEC:
    def __init__(self, http: ClienteHTTP):
        self._http = http

    def mapa_tickers(self) -> dict[str, int]:
        """Solo tickers activos hoy; un ticker antiguo puede pertenecer hoy a otra empresa."""
        datos = self._http.pedir_json(URL_TICKERS, ttl_segundos=UN_DIA)
        return {fila["ticker"].upper(): int(fila["cik_str"]) for fila in datos.values()}

    def empresa(self, cik: int) -> Empresa:
        datos = self._http.pedir_json(URL_SUBMISSIONS.format(cik=cik), ttl_segundos=UNA_HORA)
        filings = parsear_bloque(datos["filings"]["recent"], cik)
        for pagina in datos["filings"].get("files", []):
            bloque = self._http.pedir_json(URL_SUBMISSIONS_PAGINA.format(nombre=pagina["name"]), ttl_segundos=None)
            filings.extend(parsear_bloque(bloque, cik))
        return Empresa(cik, datos.get("name", ""), tuple(sorted(filings, key=lambda f: f.aceptado)))

    def companyfacts(self, cik: int) -> dict:
        try:
            return self._http.pedir_json(URL_COMPANYFACTS.format(cik=cik), ttl_segundos=UN_DIA)
        except NoEncontrado:
            return {}
