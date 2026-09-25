import math
from datetime import date

import pytest

from hermes.inteligencia.sec.financieros import DIAS_POR_MES, financieros_al


def test_solo_usa_lo_publicado_antes_de_la_fecha(companyfacts):
    fin = financieros_al(companyfacts, date(2024, 8, 1))
    assert fin.caja == 5_000_000
    assert fin.caja_al == date(2024, 3, 31)
    assert fin.acciones == 10_000_000
    assert fin.quema_mensual == pytest.approx(3_000_000 / (90 / DIAS_POR_MES))
    assert fin.runway_meses == pytest.approx(5_000_000 / (3_000_000 / (90 / DIAS_POR_MES)))


def test_lo_publicado_el_mismo_dia_todavia_no_cuenta(companyfacts):
    assert financieros_al(companyfacts, date(2024, 8, 12)).caja == 5_000_000
    assert financieros_al(companyfacts, date(2024, 8, 13)).caja == 3_000_000


def test_usa_el_periodo_mas_corto_del_ultimo_cierre(companyfacts):
    fin = financieros_al(companyfacts, date(2024, 9, 1))
    assert fin.quema_mensual == pytest.approx(3_000_000 / (90 / DIAS_POR_MES))
    assert fin.acciones == 20_000_000


def test_empresa_que_genera_caja_tiene_runway_infinito(companyfacts):
    for r in companyfacts["facts"]["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"]["units"]["USD"]:
        r["val"] = abs(r["val"])
    assert math.isinf(financieros_al(companyfacts, date(2024, 9, 1)).runway_meses)


def test_sin_datos():
    fin = financieros_al({}, date(2024, 9, 1))
    assert fin.caja is None and fin.acciones is None and fin.runway_meses is None
