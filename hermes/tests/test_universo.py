from datetime import date, timedelta

import pandas as pd
import pytest

from hermes.universo.almacen import cargar_diario, dias_habiles, guardar_diario
from hermes.universo.massive import parsear_diario_agrupado
from hermes.universo.runners import CriteriosRunner, detectar_runners, enriquecer

INICIO = date(2024, 1, 1)


def serie(ticker, precios, volumenes, inicio=INICIO):
    filas, dia = [], inicio
    for (apertura, maximo, cierre), volumen in zip(precios, volumenes):
        while dia.weekday() >= 5:
            dia += timedelta(days=1)
        filas.append({"fecha": dia, "ticker": ticker, "apertura": apertura, "maximo": maximo,
                      "minimo": min(apertura, cierre), "cierre": cierre, "volumen": volumen,
                      "vwap": cierre, "operaciones": 100})
        dia += timedelta(days=1)
    return filas


def construir_diario():
    tranquilo = [(2.0, 2.05, 2.0)] * 25
    filas = []
    # A: runner real (gap +50%, 20x volumen)
    filas += serie("A", tranquilo + [(3.0, 4.0, 2.6)], [100_000] * 25 + [2_000_000])
    # B: reverse split 1:10 en datos sin ajustar (gap +900%)
    filas += serie("B", [(1.5, 1.55, 1.5)] * 25 + [(15.0, 16.0, 15.2)], [1_000_000] * 25 + [5_000_000])
    # C: gap fuerte sin volumen
    filas += serie("C", tranquilo + [(2.8, 2.9, 2.7)], [1_000_000] * 26)
    # D: penny stock (precio previo < $1)
    filas += serie("D", [(0.5, 0.52, 0.5)] * 25 + [(0.8, 1.0, 0.9)], [100_000] * 25 + [20_000_000])
    return pd.DataFrame(filas)


def test_volumen_promedio_excluye_el_dia_del_evento():
    df = enriquecer(construir_diario())
    ultimo_a = df[df["ticker"] == "A"].iloc[-1]
    assert ultimo_a["volumen_promedio"] == pytest.approx(100_000)
    assert ultimo_a["volumen_relativo"] == pytest.approx(20)
    assert ultimo_a["gap"] == pytest.approx(0.5)
    assert ultimo_a["extension"] == pytest.approx(1.0)


def test_detectar_runners_filtra_split_volumen_y_precio():
    runners = detectar_runners(construir_diario(), CriteriosRunner())
    assert list(runners["ticker"]) == ["A"]


def test_parsear_diario_agrupado():
    datos = {"results": [{"T": "ABCD", "o": 1, "h": 2, "l": 0.9, "c": 1.5, "v": 1000, "vw": 1.4, "n": 10}]}
    df = parsear_diario_agrupado(datos, date(2024, 6, 3))
    assert df.iloc[0]["ticker"] == "ABCD" and df.iloc[0]["cierre"] == 1.5
    assert parsear_diario_agrupado({"resultsCount": 0}, date(2024, 6, 3)).empty


def test_guardar_y_cargar_diario(tmp_path):
    dia = date(2024, 6, 3)
    df = parsear_diario_agrupado({"results": [{"T": "ABCD", "o": 1, "h": 2, "l": 0.9, "c": 1.5, "v": 1000}]}, dia)
    guardar_diario(tmp_path, dia, df)
    guardar_diario(tmp_path, date(2024, 6, 4), df.iloc[0:0])
    cargado = cargar_diario(tmp_path, date(2024, 6, 1), date(2024, 6, 7))
    assert len(cargado) == 1 and cargado.iloc[0]["fecha"] == dia


def test_dias_habiles_omite_fines_de_semana():
    assert dias_habiles(date(2024, 6, 1), date(2024, 6, 4)) == [date(2024, 6, 3), date(2024, 6, 4)]
