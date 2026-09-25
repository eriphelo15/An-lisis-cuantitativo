from datetime import date, datetime

import pandas as pd

from hermes.inteligencia.finra import parsear_short_interest, parsear_volumen_corto, short_interest
from hermes.inteligencia.halts import parsear_halts
from hermes.inteligencia.sec.filings import ET

FILAS_SHORT_INTEREST = [
    {"settlementDate": "2024-05-31", "symbolCode": "ABCD", "currentShortPositionQuantity": 1_500_000,
     "averageDailyVolumeQuantity": 500_000, "daysToCoverQuantity": 3.0},
    {"settlementDate": "2024-05-15", "symbolCode": "ABCD", "currentShortPositionQuantity": 1_000_000,
     "averageDailyVolumeQuantity": "", "daysToCoverQuantity": None},
]


class HttpFalso:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = []

    def pedir_json(self, url, **kwargs):
        self.llamadas.append((url, kwargs))
        return self.respuesta


def test_parsear_short_interest_ordena_por_fecha():
    registros = parsear_short_interest(FILAS_SHORT_INTEREST)
    assert [r.liquidacion for r in registros] == [date(2024, 5, 15), date(2024, 5, 31)]
    assert registros[0].volumen_diario_promedio is None
    assert registros[1].dias_para_cubrir == 3.0


def test_short_interest_respeta_el_retraso_de_publicacion():
    http = HttpFalso(FILAS_SHORT_INTEREST)
    registros = short_interest(http, "abcd", al=date(2024, 6, 5))
    assert [r.liquidacion for r in registros] == [date(2024, 5, 15)]
    filtro = http.llamadas[0][1]["cuerpo_json"]["compareFilters"][0]
    assert filtro["fieldValue"] == "ABCD"


def test_parsear_volumen_corto():
    texto = (
        "Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market\n"
        "20240603|ABCD|1000|0|4000|B,Q,N\n"
        "20240603|EFGH|0|0|0|Q\n"
        "2\n"
    )
    df = parsear_volumen_corto(texto)
    assert list(df["ticker"]) == ["ABCD", "EFGH"]
    assert df.loc[0, "pct_corto"] == 0.25
    assert pd.isna(df.loc[1, "pct_corto"])


RSS_HALTS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:ndaq="http://www.nasdaqtrader.com/">
  <channel>
    <item>
      <title>ABCD</title>
      <ndaq:HaltDate>06/03/2024</ndaq:HaltDate>
      <ndaq:HaltTime>09:41:07</ndaq:HaltTime>
      <ndaq:IssueSymbol>ABCD</ndaq:IssueSymbol>
      <ndaq:IssueName>Abcd Therapeutics Inc</ndaq:IssueName>
      <ndaq:Market>NASDAQ</ndaq:Market>
      <ndaq:ReasonCode>LUDP</ndaq:ReasonCode>
      <ndaq:PauseThresholdPrice>3.45</ndaq:PauseThresholdPrice>
      <ndaq:ResumptionDate>06/03/2024</ndaq:ResumptionDate>
      <ndaq:ResumptionQuoteTime>09:46:07</ndaq:ResumptionQuoteTime>
      <ndaq:ResumptionTradeTime>09:46:07</ndaq:ResumptionTradeTime>
    </item>
    <item>
      <title>WXYZ</title>
      <ndaq:HaltDate>06/03/2024</ndaq:HaltDate>
      <ndaq:HaltTime>10:02:00</ndaq:HaltTime>
      <ndaq:IssueSymbol>WXYZ</ndaq:IssueSymbol>
      <ndaq:IssueName>Wxyz Corp</ndaq:IssueName>
      <ndaq:Market>NASDAQ</ndaq:Market>
      <ndaq:ReasonCode>T1</ndaq:ReasonCode>
      <ndaq:ResumptionDate></ndaq:ResumptionDate>
      <ndaq:ResumptionQuoteTime></ndaq:ResumptionQuoteTime>
      <ndaq:ResumptionTradeTime></ndaq:ResumptionTradeTime>
    </item>
  </channel>
</rss>"""


def test_parsear_halts():
    luld, noticia = parsear_halts(RSS_HALTS)
    assert luld.ticker == "ABCD" and luld.es_luld and not luld.activo
    assert luld.inicio == datetime(2024, 6, 3, 9, 41, 7, tzinfo=ET)
    assert luld.reanudacion_trading == datetime(2024, 6, 3, 9, 46, 7, tzinfo=ET)
    assert noticia.es_noticia and noticia.activo
