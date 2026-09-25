from datetime import date, datetime

import pandas as pd
import pytest

from maestros.datos.calendario import ET
from maestros.informacion.catalizadores import TipoCatalizador, clasificar_tipo, evaluar_catalizador, monto_mayor
from maestros.informacion.dilucion import riesgo_dilucion
from maestros.informacion.ficha import construir_ficha
from maestros.informacion.filings import Categoria, clasificar, parsear_aceptacion
from maestros.informacion.financieros import DIAS_POR_MES, Financieros, financieros_al
from maestros.informacion.mercado import (inicio_ssr, parsear_halts, parsear_short_interest, parsear_volumen_corto,
                                          ssr_activo)
from tests.conftest import et, hacer_barras

APERTURA = datetime(2024, 6, 3, 9, 30, tzinfo=ET)


def test_aceptacion_en_hora_del_este():
    assert parsear_aceptacion("2023-11-02T18:08:27.000Z") == datetime(2023, 11, 2, 18, 8, 27, tzinfo=ET)


def test_clasificar_filings(filing):
    assert clasificar(filing("S-3/A", "2024-01-02T10:00:00")) == {Categoria.SHELF}
    assert clasificar(filing("424B5", "2024-01-02T10:00:00")) == {Categoria.PROSPECTO}
    assert clasificar(filing("8-K", "2024-01-02T10:00:00", ("1.01", "3.02"))) == {Categoria.ACUERDO_FINANCIAMIENTO}
    assert clasificar(filing("8-K", "2024-01-02T10:00:00", ("3.01",))) == {Categoria.AVISO_LISTADO}
    assert clasificar(filing("8-K", "2024-01-02T10:00:00", ("2.02",))) == {Categoria.OTRO}


def _hecho(val, end, filed, start=None):
    return {"val": val, "end": end, "filed": filed, **({"start": start} if start else {})}


FACTS = {"facts": {
    "us-gaap": {
        "CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [
            _hecho(5_000_000, "2024-03-31", "2024-05-10"), _hecho(3_000_000, "2024-06-30", "2024-08-12")]}},
        "NetCashProvidedByUsedInOperatingActivities": {"units": {"USD": [
            _hecho(-3_000_000, "2024-03-31", "2024-05-10", "2024-01-01"),
            _hecho(-6_000_000, "2024-06-30", "2024-08-12", "2024-01-01"),
            _hecho(-3_000_000, "2024-06-30", "2024-08-12", "2024-04-01")]}},
    },
    "dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": [
        _hecho(10_000_000, "2024-05-08", "2024-05-10"), _hecho(20_000_000, "2024-08-09", "2024-08-12")]}}},
}}


def test_financieros_point_in_time():
    antes = financieros_al(FACTS, date(2024, 8, 12))
    assert antes.caja == 5_000_000 and antes.acciones == 10_000_000
    assert antes.runway_meses == pytest.approx(5_000_000 / (3_000_000 / (90 / DIAS_POR_MES)))
    despues = financieros_al(FACTS, date(2024, 8, 13))
    assert despues.caja == 3_000_000 and despues.acciones == 20_000_000
    assert financieros_al({}, date(2024, 8, 13)).runway_meses is None


def test_riesgo_dilucion(filing):
    filings = [filing("S-3", "2023-05-01T10:00:00"), filing("424B5", "2024-05-20T08:00:00"),
               filing("S-1", "2024-06-03T09:45:00")]
    riesgo = riesgo_dilucion(filings, Financieros(2_000_000, 1_000_000, None), APERTURA)
    assert {c for c, _, _ in riesgo.componentes} == {"prospecto_inmediato", "shelf", "runway_critico"}
    assert riesgo.puntaje == 75 and riesgo.nivel == "alto"


def test_shelf_retirado_no_cuenta(filing):
    filings = [filing("S-3", "2023-01-01T10:00:00"), filing("RW", "2023-06-01T10:00:00")]
    riesgo = riesgo_dilucion(filings, Financieros(100, -1, None), APERTURA)
    assert riesgo.puntaje == 0


@pytest.mark.parametrize("titular,tipo", [
    ("ABCD Announces Pricing of $5 Million Registered Direct Offering", TipoCatalizador.OFERTA),
    ("ABCD announces 1-for-10 reverse stock split", TipoCatalizador.REVERSE_SPLIT),
    ("ABCD receives FDA 510(k) clearance for its device", TipoCatalizador.FDA),
    ("ABCD reports positive topline Phase 2 data", TipoCatalizador.ENSAYO),
    ("ABCD awarded $12 million contract by US Army", TipoCatalizador.CONTRATO),
    ("ABCD enters into definitive agreement to be acquired", TipoCatalizador.FUSION),
    ("ABCD partners with major retailer", TipoCatalizador.ALIANZA),
    ("ABCD launches bitcoin treasury strategy", TipoCatalizador.TEMATICO),
    ("ABCD to present at investor conference", TipoCatalizador.OTRO),
])
def test_clasificar_tipo(noticia, titular, tipo):
    assert clasificar_tipo(noticia(et("07:00"), titular)) == tipo


def test_puntaje_de_calidad(noticia):
    contrato = noticia(et("07:00"), "ABCD awarded $12 million contract, signed with US Army")
    assert monto_mayor(contrato.texto) == 12_000_000
    grande = evaluar_catalizador(contrato, capitalizacion=20_000_000)
    assert grande.puntaje == 55 + 20 + 5
    chico = evaluar_catalizador(contrato, capitalizacion=2_000_000_000)
    assert chico.puntaje == 55 - 10 + 5
    humo = evaluar_catalizador(noticia(et("07:00"), "ABCD signs letter of intent for revolutionary, "
                                                    "game-changing partnership"))
    assert humo.puntaje == 40 - 15 - 10
    oferta = evaluar_catalizador(noticia(et("07:00"), "ABCD prices $3 million public offering"))
    assert oferta.puntaje == 0
    assert evaluar_catalizador(contrato, 20_000_000, dilucion_alta=True).puntaje == grande.puntaje - 15


def test_ssr():
    barras = hacer_barras(et("09:30"), [(10, 10, 9.5, 9.6, 1), (9.6, 9.6, 8.9, 9.0, 1), (9.0, 9.1, 8.5, 8.7, 1)])
    inicio = inicio_ssr(barras, 10.0)
    assert inicio == et("09:31")
    assert not ssr_activo(et("09:30"), inicio, activado_ayer=False)
    assert ssr_activo(et("09:32"), inicio, activado_ayer=False)
    assert ssr_activo(et("09:30"), None, activado_ayer=True)


def test_halts_short_interest_y_volumen_corto():
    xml = """<rss xmlns:ndaq="http://www.nasdaqtrader.com/"><channel><item>
      <ndaq:HaltDate>06/04/2024</ndaq:HaltDate><ndaq:HaltTime>09:41:07</ndaq:HaltTime>
      <ndaq:IssueSymbol>ABCD</ndaq:IssueSymbol><ndaq:ReasonCode>LUDP</ndaq:ReasonCode>
      <ndaq:ResumptionDate>06/04/2024</ndaq:ResumptionDate><ndaq:ResumptionTradeTime>09:46:07</ndaq:ResumptionTradeTime>
    </item></channel></rss>"""
    halt = parsear_halts(xml)[0]
    assert halt.es_luld and not halt.activo and halt.inicio == et("09:41").replace(second=7)

    si = parsear_short_interest([{"settlementDate": "2024-05-31", "currentShortPositionQuantity": 1500,
                                  "daysToCoverQuantity": ""}])
    assert si[0].posicion == 1500 and si[0].dias_para_cubrir is None

    vc = parsear_volumen_corto("Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market\n"
                               "20240604|ABCD|1000|0|4000|Q\n20240604|X|0|0|0|Q\n2\n")
    assert list(vc["ticker"]) == ["ABCD", "X"] and vc.iloc[0]["pct_corto"] == 0.25
    assert pd.isna(vc.iloc[1]["pct_corto"])


def test_ficha_filtra_noticias_del_ticker(noticia, filing):
    propia = noticia(et("07:00"))
    ajena = noticia(et("07:05"), tickers=("ZZZ",))
    ficha = construir_ficha("abcd", et("04:00"), [filing("S-3", "2024-01-02T10:00:00")], FACTS, [ajena, propia])
    assert ficha.noticias == (propia,)
    assert ficha.float_aprox == 10_000_000
    assert ficha.noticias_entre(et("06:00"), et("06:59")) == []
    assert ficha.riesgo_dilucion.nivel in {"bajo", "medio", "alto"}
