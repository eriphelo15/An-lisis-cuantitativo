from datetime import date, datetime

import pandas as pd

from maestros.backtest.ejecutar import candidatos
from maestros.datos.almacen import Almacen
from maestros.datos.alpaca import parsear_barras, parsear_noticias
from maestros.datos.calendario import (CIERRE, CIERRE_ANTICIPADO, ET, dias_habiles, dias_habiles_previos, es_dia_habil,
                                       feriados, hora_de_cierre)
from maestros.datos.massive import parsear_diario_agrupado
from tests.conftest import crear_noticia, et


def test_feriados_2024_y_2026():
    assert feriados(2024) == {date(2024, 1, 1), date(2024, 1, 15), date(2024, 2, 19), date(2024, 3, 29),
                              date(2024, 5, 27), date(2024, 6, 19), date(2024, 7, 4), date(2024, 9, 2),
                              date(2024, 11, 28), date(2024, 12, 25)}
    assert {date(2026, 4, 3), date(2026, 7, 3), date(2026, 11, 26)} <= feriados(2026)


def test_feriados_observados_y_cierres_especiales():
    assert date(2022, 6, 20) in feriados(2022)  # Juneteenth cayó domingo
    assert date(2022, 12, 26) in feriados(2022)
    assert date(2021, 12, 24) in feriados(2021)
    assert es_dia_habil(date(2021, 12, 31))  # Año Nuevo 2022 cayó sábado: NYSE no cerró el viernes
    assert not es_dia_habil(date(2025, 1, 9))


def test_cierres_anticipados():
    assert hora_de_cierre(date(2024, 7, 3)) == CIERRE_ANTICIPADO
    assert hora_de_cierre(date(2024, 11, 29)) == CIERRE_ANTICIPADO
    assert hora_de_cierre(date(2024, 12, 24)) == CIERRE_ANTICIPADO
    assert hora_de_cierre(date(2024, 6, 4)) == CIERRE


def test_dias_habiles():
    assert dias_habiles(date(2024, 3, 28), date(2024, 4, 2)) == [date(2024, 3, 28), date(2024, 4, 1), date(2024, 4, 2)]
    assert dias_habiles_previos(date(2024, 4, 1), 2) == [date(2024, 3, 27), date(2024, 3, 28)]


def test_parsear_barras_convierte_a_hora_del_este():
    datos = {"bars": {"ABCD": [{"t": "2024-06-04T13:30:00Z", "o": 2, "h": 2.1, "l": 1.9, "c": 2.05, "v": 1000,
                                "vw": 2.01, "n": 12}]}, "next_page_token": None}
    df = parsear_barras(datos)
    assert df.iloc[0]["hora"] == datetime(2024, 6, 4, 9, 30, tzinfo=ET)
    assert df.iloc[0]["ticker"] == "ABCD" and df.iloc[0]["volumen"] == 1000
    assert parsear_barras({"bars": {}}).empty


def test_parsear_noticias():
    datos = {"news": [{"id": 1, "headline": "ABCD gets FDA nod", "summary": "", "created_at": "2024-06-04T11:05:00Z",
                       "symbols": ["abcd", "XYZ"], "source": "benzinga", "url": "u"}]}
    n = parsear_noticias(datos)[0]
    assert n.tickers == ("ABCD", "XYZ") and n.hora == datetime(2024, 6, 4, 7, 5, tzinfo=ET)


def test_almacen_ida_y_vuelta(tmp_path):
    almacen = Almacen(tmp_path)
    barras = pd.DataFrame([{"ticker": "ABCD", "hora": et("09:30"), "apertura": 1.0, "maximo": 1.1, "minimo": 0.9,
                            "cierre": 1.0, "volumen": 10, "vwap": 1.0, "operaciones": 1}])
    almacen.guardar_minutos(date(2024, 6, 4), "ABCD", barras)
    assert almacen.cargar_minutos(date(2024, 6, 4), "ABCD").iloc[0]["hora"] == et("09:30")
    assert almacen.cargar_minutos(date(2024, 6, 5), "ABCD").empty

    noticia = crear_noticia(et("07:00"))
    almacen.guardar_noticias(date(2024, 6, 4), [noticia])
    assert almacen.cargar_noticias(date(2024, 6, 4)) == [noticia]

    almacen.guardar_diario(date(2024, 6, 4), parsear_diario_agrupado({"results": [{"T": "ABCD", "c": 1.0}]}, date(2024, 6, 4)))
    assert len(almacen.cargar_diario(date(2024, 6, 3), date(2024, 6, 5))) == 1


def _diario(ticker, cierres, volumenes, maximos=None):
    fechas = dias_habiles(date(2024, 1, 2), date(2024, 3, 1))[: len(cierres)]
    maximos = maximos or cierres
    return [{"fecha": f, "ticker": ticker, "apertura": c, "maximo": m, "minimo": c, "cierre": c, "volumen": v, "vwap": c}
            for f, c, m, v in zip(fechas, cierres, maximos, volumenes)]


def test_candidatos_prefiltro_diario():
    filas = (
        _diario("A", [2.0] * 25 + [2.5], [100_000] * 25 + [900_000], maximos=[2.0] * 25 + [3.0])
        + _diario("B", [2.0] * 26, [100_000] * 26)
        + _diario("C", [30.0] * 25 + [40.0], [100_000] * 25 + [900_000], maximos=[30.0] * 25 + [40.0])
    )
    lista = candidatos(pd.DataFrame(filas))
    assert list(lista["ticker"]) == ["A"]
    assert lista.iloc[0]["cierre_previo"] == 2.0
