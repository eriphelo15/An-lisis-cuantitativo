import pandas as pd
import pytest

from maestros.backtest.ejecutar import ejecutar_backtest
from maestros.datos.almacen import Almacen
from maestros.datos.calendario import dias_habiles_previos
from maestros.informacion.ficha import Ficha
from maestros.traders.cameron import CameronLiteral
from tests.conftest import DIA, crear_noticia, et, hacer_barras
from tests.test_cameron import ficha, impulso, premercado_plano


def test_backtest_de_punta_a_punta_con_dias_previos_sin_premarket(tmp_path):
    almacen = Almacen(tmp_path)
    velas = premercado_plano() + impulso() + [(2.40, 2.39, 2.33, 2.34, 20_000), (2.35, 2.45, 2.34, 2.44, 60_000),
                                              (2.44, 2.60, 2.43, 2.58, 80_000)]
    for ticker in ("ABCD", "EFGH"):
        # días normales: solo negocian en horario regular, sin nada de volumen en premarket
        for d in dias_habiles_previos(DIA, 20):
            almacen.guardar_minutos(d, ticker, hacer_barras(et("09:30", d), [(1.8, 1.8, 1.8, 1.8, 500)] * 60, ticker))
        almacen.guardar_minutos(DIA, ticker, hacer_barras(et("07:00"), velas, ticker))

    noticias = [crear_noticia(et("06:30"))]  # solo ABCD tiene catalizador

    def obtener_ficha(ticker, fecha) -> Ficha:
        base = ficha(noticias=noticias)
        return Ficha(ticker, base.financieros, None, tuple(n for n in noticias if ticker in n.tickers))

    lista = pd.DataFrame({"fecha": [DIA, DIA], "ticker": ["ABCD", "EFGH"], "cierre_previo": [1.80, 1.80],
                          "volumen_promedio": [30_000, 30_000]})
    trades, cobertura = ejecutar_backtest(CameronLiteral(), lista, almacen, obtener_ficha)

    assert [t.ticker for t in trades] == ["ABCD"]
    assert trades[0].r_bruto == pytest.approx(2.0)
    assert cobertura["simulados"] == 2
    assert cobertura["sin_trade:pilar_catalizador"] == 1


def test_backtest_cuenta_dias_sin_datos(tmp_path):
    lista = pd.DataFrame({"fecha": [DIA], "ticker": ["ZZZZ"], "cierre_previo": [2.0], "volumen_promedio": [1.0]})
    trades, cobertura = ejecutar_backtest(CameronLiteral(), lista, Almacen(tmp_path), lambda t, f: None)
    assert trades == [] and cobertura["sin_minutos"] == 1
