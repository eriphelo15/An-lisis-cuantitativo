import pandas as pd
import pytest

from maestros.backtest.costos import ModeloCostos
from maestros.backtest.motor import simular_dia
from maestros.informacion.ficha import Ficha
from maestros.informacion.financieros import Financieros
from maestros.traders.base import Contexto
from maestros.traders.cameron import CameronLiteral, ParametrosCameron
from maestros.traders.indicadores import MINUTOS_SESION_EXTENDIDA, volumen_normal_acumulado, volumen_relativo
from tests.conftest import DIA, crear_noticia, et, hacer_barras

CIERRE_PREVIO = 1.80
VOLUMEN_NORMAL = pd.Series([100.0 * m for m in range(MINUTOS_SESION_EXTENDIDA)])


def ficha(float_aprox=5_000_000, noticias=None):
    noticias = (crear_noticia(et("06:30")),) if noticias is None else tuple(noticias)
    return Ficha("ABCD", Financieros(None, None, float_aprox), None, noticias)


def premercado_plano(desde="07:00", minutos=60, precio=2.00, maximo=None):
    return [(precio, maximo or precio, precio - 0.005, precio, 20_000)] * minutos


def impulso(desde=2.00, paso=0.04, velas=10):
    return [(desde + paso * i, desde + paso * (i + 1), desde + paso * i - 0.005, desde + paso * (i + 1), 50_000)
            for i in range(velas)]


def dia_micro_pullback():
    velas = premercado_plano() + impulso() + [(2.40, 2.39, 2.33, 2.34, 20_000)]
    return hacer_barras(et("07:00"), velas)


def ctx(barras, ficha_=None, cierre_previo=CIERRE_PREVIO):
    return Contexto("ABCD", DIA, barras, cierre_previo, VOLUMEN_NORMAL, ficha() if ficha_ is None else ficha_)


def test_micro_pullback():
    senal = CameronLiteral().evaluar(ctx(dia_micro_pullback()))
    assert senal.setup == "micro_pullback"
    assert senal.entrada == pytest.approx(2.40) and senal.stop == pytest.approx(2.32)
    assert senal.objetivo == pytest.approx(2.56)


def test_ninguna_senal_durante_el_impulso():
    barras = dia_micro_pullback()
    cameron = CameronLiteral()
    assert all(cameron.evaluar(ctx(barras.iloc[: i + 1])) is None for i in range(len(barras) - 1))


@pytest.mark.parametrize("cambio,pilar", [
    ({"ficha_": ficha(float_aprox=50_000_000)}, "float"),
    ({"ficha_": ficha(float_aprox=None)}, "float"),
    ({"ficha_": ficha(noticias=[])}, "catalizador"),
    ({"ficha_": ficha(noticias=[crear_noticia(et("09:00"))])}, "catalizador"),
    ({"cierre_previo": 2.30}, "alza"),
])
def test_cada_pilar_bloquea_la_senal(cambio, pilar):
    contexto = ctx(dia_micro_pullback(), **cambio)
    cameron = CameronLiteral()
    assert cameron.revisar_pilares(contexto) == pilar
    assert cameron.evaluar(contexto) is None


def test_volumen_relativo_insuficiente():
    contexto = Contexto("ABCD", DIA, dia_micro_pullback(), CIERRE_PREVIO, VOLUMEN_NORMAL * 1000, ficha())
    assert CameronLiteral().revisar_pilares(contexto) == "volumen_relativo"
    sin_historia = Contexto("ABCD", DIA, dia_micro_pullback(), CIERRE_PREVIO, None, ficha())
    assert CameronLiteral().revisar_pilares(sin_historia) == "volumen_relativo"


def test_fuera_del_horario_no_opera():
    velas = premercado_plano(minutos=10) + impulso() + [(2.40, 2.39, 2.33, 2.34, 20_000)]
    barras = hacer_barras(et("10:40"), velas)
    assert CameronLiteral().evaluar(ctx(barras)) is None


def test_bull_flag():
    bandera = [(2.40, 2.39, 2.34, 2.36, 15_000), (2.36, 2.38, 2.34, 2.37, 15_000), (2.37, 2.385, 2.35, 2.38, 15_000)]
    barras = hacer_barras(et("07:00"), premercado_plano() + impulso() + bandera)
    senal = CameronLiteral().evaluar(ctx(barras))
    assert senal.setup == "bull_flag"
    assert senal.entrada == pytest.approx(2.395) and senal.stop == pytest.approx(2.33)


def test_bandera_con_volumen_creciente_no_es_bull_flag():
    bandera = [(2.40, 2.39, 2.34, 2.36, 90_000), (2.36, 2.38, 2.34, 2.37, 90_000), (2.37, 2.385, 2.35, 2.38, 90_000)]
    barras = hacer_barras(et("07:00"), premercado_plano() + impulso() + bandera)
    assert CameronLiteral().evaluar(ctx(barras)) is None


def test_gap_and_go():
    velas = premercado_plano(minutos=150, maximo=2.10) + [(2.05, 2.08, 2.03, 2.07, 100_000)]
    barras = hacer_barras(et("07:00"), velas)
    senal = CameronLiteral().evaluar(ctx(barras))
    assert senal.setup == "gap_and_go"
    assert senal.entrada == pytest.approx(2.11) and senal.stop == pytest.approx(2.02)


def test_gap_and_go_no_repite_si_ya_rompio_el_maximo():
    velas = premercado_plano(minutos=150, maximo=2.10) + [(2.05, 2.15, 2.03, 2.07, 100_000)]
    senal = CameronLiteral().evaluar(ctx(hacer_barras(et("07:00"), velas)))
    assert senal is None or senal.setup != "gap_and_go"


def test_riesgo_demasiado_grande_se_descarta():
    params = ParametrosCameron(riesgo_max_pct=0.01)
    assert CameronLiteral(params).evaluar(ctx(dia_micro_pullback())) is None


def test_de_punta_a_punta_con_el_motor():
    continuacion = [(2.35, 2.45, 2.34, 2.44, 60_000), (2.44, 2.60, 2.43, 2.58, 80_000)]
    velas = premercado_plano() + impulso() + [(2.40, 2.39, 2.33, 2.34, 20_000)] + continuacion
    barras = hacer_barras(et("07:00"), velas)
    sin_costos = ModeloCostos(tramos_spread=((float("inf"), 0.0),), slippage_por_lado=0.0)
    trades = simular_dia(CameronLiteral(), "ABCD", DIA, barras, CIERRE_PREVIO, sin_costos,
                         volumen_normal=VOLUMEN_NORMAL, ficha=ficha())
    assert len(trades) == 1
    t = trades[0]
    assert t.setup == "micro_pullback" and t.motivo_salida == "objetivo"
    assert t.r_bruto == pytest.approx(2.0)


def test_volumen_normal_y_relativo():
    dia1 = hacer_barras(et("09:30"), [(1, 1, 1, 1, 100), (1, 1, 1, 1, 100)])
    dia2 = hacer_barras(et("09:30").replace(day=5), [(1, 1, 1, 1, 300), (1, 1, 1, 1, 300)])
    normal = volumen_normal_acumulado(pd.concat([dia1, dia2]))
    minuto_0930 = 5 * 60 + 30
    assert normal.iloc[minuto_0930] == 200 and normal.iloc[minuto_0930 + 1] == 400
    assert normal.iloc[minuto_0930 - 1] == 0 and normal.iloc[-1] == 400
    hoy = hacer_barras(et("09:30"), [(1, 1, 1, 1, 1000)])
    assert volumen_relativo(hoy, normal) == 5.0


def test_volumen_en_premarket_sin_historia_de_premarket_es_infinito():
    normal = volumen_normal_acumulado(hacer_barras(et("09:30").replace(day=3), [(1, 1, 1, 1, 100)]))
    assert volumen_relativo(hacer_barras(et("08:00"), [(1, 1, 1, 1, 50)]), normal) == float("inf")
    assert volumen_relativo(hacer_barras(et("08:00"), [(1, 1, 1, 1, 0)]), normal) is None
