from datetime import date, datetime

import pandas as pd
import pytest

from hermes.inteligencia.ficha import construir_ficha, formatear
from hermes.inteligencia.sec.cliente import Empresa
from hermes.inteligencia.sec.filings import ET
from hermes.laboratorio.costos import ModeloCostos
from hermes.laboratorio.estudio import agregar_costos, agregar_retornos, resumir, tasa_ofertas
from hermes.laboratorio.pipeline import evaluar_dilucion


def test_costos_por_tramo_y_iliquidez():
    modelo = ModeloCostos()
    assert modelo.costo_ida_vuelta(1.5, 5_000_000) == pytest.approx(0.015 + 0.002)
    assert modelo.costo_ida_vuelta(1.5, 500_000) == pytest.approx(0.015 * 1.5 + 0.002)
    assert modelo.costo_ida_vuelta(12.0, 5_000_000) == pytest.approx(0.003 + 0.002)


def diario_simple():
    fechas = [date(2024, 6, d) for d in (3, 4, 5, 6, 7, 10)]
    cierres = [5.0, 4.0, 3.5, 3.0, 3.2, 2.5]
    return pd.DataFrame({"ticker": "A", "fecha": fechas, "cierre": cierres})


def test_retornos_desde_la_apertura_y_el_cierre_del_evento():
    eventos = pd.DataFrame({"ticker": ["A"], "fecha": [date(2024, 6, 3)], "apertura": [4.0], "cierre": [5.0]})
    ev = agregar_retornos(eventos, diario_simple()).iloc[0]
    assert ev["ret_intradia"] == pytest.approx(0.25)
    assert ev["ret_1d"] == pytest.approx(-0.2)
    assert ev["ret_3d"] == pytest.approx(-0.4)
    assert ev["ret_5d"] == pytest.approx(-0.5)


def test_resumir_calcula_ganancia_del_corto_neta_de_costos():
    eventos = pd.DataFrame({
        "nivel_dilucion": ["alto", "alto", "bajo"],
        "apertura": [5.0, 5.0, 5.0],
        "dolar_volumen": [5e6, 5e6, 5e6],
        "ret_intradia": [-0.10, -0.20, 0.05],
        "ret_1d": [-0.1, None, 0.0],
        "ret_3d": [None, None, None],
        "ret_5d": [0.0, 0.0, 0.0],
        "oferta_5d": [True, False, False],
    })
    eventos = agregar_costos(eventos, ModeloCostos())
    resumen = resumir(eventos, ["nivel_dilucion"])
    alto = resumen[(resumen["nivel_dilucion"] == "alto") & (resumen["horizonte"] == "intradia")].iloc[0]
    costo = ModeloCostos().costo_ida_vuelta(5.0, 5e6)
    assert alto["n"] == 2
    assert alto["pct_bajistas"] == 1.0
    assert alto["corto_neto_medio"] == pytest.approx(0.15 - costo)
    assert resumen[(resumen["nivel_dilucion"] == "alto") & (resumen["horizonte"] == "1d")].iloc[0]["n"] == 1

    ofertas = tasa_ofertas(eventos, ["nivel_dilucion"]).set_index("nivel_dilucion")
    assert ofertas.loc["alto", "tasa"] == 0.5 and ofertas.loc["bajo", "tasa"] == 0.0


class SecFalso:
    def __init__(self, empresas):
        self.empresas = empresas
        self.consultas = 0

    def empresa(self, cik):
        self.consultas += 1
        return self.empresas[cik]

    def companyfacts(self, cik):
        return {}


def test_pipeline_evalua_con_datos_previos_y_detecta_oferta_posterior(filing):
    empresa = Empresa(cik=1, nombre="Abcd Inc", tickers=("ABCD",), filings=(
        filing("S-3", "2023-06-01T10:00:00", cik=1),
        filing("424B5", "2024-06-05T07:00:00", cik=1),
    ))
    runners = pd.DataFrame({"ticker": ["ABCD", "ABCD", "ZZZZ"],
                            "fecha": [date(2024, 6, 3), date(2024, 6, 20), date(2024, 6, 3)]})
    sec = SecFalso({1: empresa})
    eventos = evaluar_dilucion(runners, sec, lambda t, f: 1 if t == "ABCD" else None)

    primero, segundo, sin_cik = (eventos.iloc[i] for i in range(3))
    assert primero["oferta_5d"]
    assert "prospecto" not in primero["componentes"]
    assert primero["puntaje_dilucion"] == 20 + 10  # shelf + runway desconocido
    assert "prospecto" in segundo["componentes"]
    assert not segundo["oferta_5d"]
    assert sin_cik["nivel_dilucion"] == "sin_cik"
    assert sec.consultas == 1


def test_ficha_se_arma_y_se_formatea(companyfacts, filing):
    empresa = Empresa(cik=1, nombre="Abcd Inc", tickers=("ABCD",), filings=(
        filing("S-3", "2024-01-10T10:00:00", cik=1),
        filing("4", "2024-02-10T10:00:00", cik=1),
        filing("424B5", "2024-09-10T10:00:00", cik=1),
    ))
    momento = datetime(2024, 9, 3, 9, 30, tzinfo=ET)
    ficha = construir_ficha("abcd", empresa, companyfacts, momento)
    assert [f.forma for f in ficha.filings_relevantes] == ["S-3"]
    texto = formatear(ficha)
    assert "ABCD — Abcd Inc" in texto
    assert f"RIESGO DE DILUCIÓN: {ficha.riesgo.puntaje}/100" in texto
    assert "meses" in texto
