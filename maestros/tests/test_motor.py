from datetime import time

import pytest

from maestros.backtest.costos import ModeloCostos
from maestros.backtest.modelos import Direccion, Senal
from maestros.backtest.motor import ReglasSimulacion, simular_dia
from maestros.backtest.reporte import a_tabla, resumen
from tests.conftest import DIA, et, hacer_barras

SIN_COSTOS = ModeloCostos(tramos_spread=((float("inf"), 0.0),), slippage_por_lado=0.0)
VOLUMEN = 100_000


class EstrategiaFija:
    """Emite una señal fija en la barra `en_barra` y registra lo que vio en cada evaluación."""

    nombre = "fija"

    def __init__(self, en_barra: int, entrada=10.0, stop=9.0, objetivo=12.0, direccion=Direccion.LARGO, repetir=False):
        self.en_barra, self.repetir = en_barra, repetir
        self.params = (entrada, stop, objetivo, direccion)
        self.vistas = []

    def evaluar(self, ctx):
        self.vistas.append((len(ctx.barras), ctx.ahora))
        if len(ctx.barras) - 1 == self.en_barra or (self.repetir and len(ctx.barras) - 1 >= self.en_barra):
            entrada, stop, objetivo, direccion = self.params
            return Senal("prueba", direccion, entrada, stop, objetivo, ctx.ahora)
        return None


def simular(velas, estrategia, reglas=ReglasSimulacion(), costos=SIN_COSTOS, inicio="09:30"):
    barras = hacer_barras(et(inicio), velas)
    return simular_dia(estrategia, "ABCD", DIA, barras, 9.0, costos, reglas)


def vela(o, h, l, c, v=VOLUMEN):
    return (o, h, l, c, v)


def test_entrada_por_ruptura_y_salida_en_objetivo():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 9.7, 10.1), vela(10.1, 12.5, 10.0, 12.2)]
    trades = simular(velas, EstrategiaFija(en_barra=5))
    assert len(trades) == 1
    t = trades[0]
    assert t.precio_entrada == 10.0 and t.precio_salida == 12.0 and t.motivo_salida == "objetivo"
    assert t.r_bruto == pytest.approx(2.0) and t.acciones == 50


def test_gap_por_debajo_del_stop_se_llena_en_la_apertura():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 9.7, 10.1), vela(8.0, 8.2, 7.9, 8.1)]
    t = simular(velas, EstrategiaFija(en_barra=5))[0]
    assert t.precio_salida == 8.0 and t.motivo_salida == "stop"
    assert t.r_bruto == pytest.approx(-2.0)


def test_stop_y_objetivo_en_la_misma_barra_gana_el_stop():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 9.7, 10.1), vela(10.1, 12.5, 8.5, 11.0)]
    assert simular(velas, EstrategiaFija(en_barra=5))[0].motivo_salida == "stop"


def test_barra_de_entrada_que_toca_el_stop_se_cuenta_como_perdida():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 8.9, 9.5)]
    t = simular(velas, EstrategiaFija(en_barra=5))[0]
    assert t.motivo_salida == "stop" and t.r_bruto == pytest.approx(-1.0)


def test_senal_invalidada_si_toca_el_stop_antes_de_entrar():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.5, 9.6, 8.9, 9.0), vela(9.8, 10.5, 9.7, 10.4)]
    assert simular(velas, EstrategiaFija(en_barra=5)) == []


def test_senal_vence_si_no_se_dispara():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 10 + [vela(9.8, 10.5, 9.7, 10.4)]
    assert simular(velas, EstrategiaFija(en_barra=5), ReglasSimulacion(vigencia_senal_barras=3)) == []


def test_salida_forzada_al_final_del_dia():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 9.7, 10.1)] + [vela(10.1, 10.3, 9.9, 10.2)] * 5
    t = simular(velas, EstrategiaFija(en_barra=5), inicio="15:48")[0]
    assert t.motivo_salida == "tiempo" and t.hora_salida.time() == time(15, 55)


def test_la_estrategia_nunca_ve_barras_futuras():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 8
    estrategia = EstrategiaFija(en_barra=99)
    simular(velas, estrategia)
    barras = hacer_barras(et("09:30"), velas)
    assert estrategia.vistas == [(i + 1, barras["hora"].iloc[i]) for i in range(8)]


def test_limite_de_participacion_evita_tamanos_irreales():
    velas = [vela(9.5, 9.8, 9.4, 9.7, v=10)] * 6 + [vela(9.8, 10.2, 9.7, 10.1, v=10)]
    assert simular(velas, EstrategiaFija(en_barra=5)) == []


def test_perdida_maxima_diaria_detiene_nuevos_trades():
    perdedora = [vela(9.8, 10.2, 8.9, 9.5)]  # entra y toca el stop en la misma barra: -1R
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + (perdedora + [vela(9.5, 9.8, 9.4, 9.7)]) * 5
    trades = simular(velas, EstrategiaFija(en_barra=5, repetir=True), ReglasSimulacion(perdida_max_dia_r=2.0))
    assert len(trades) == 2


def test_costos_reducen_el_resultado_en_r():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 9.7, 10.1), vela(10.1, 12.5, 10.0, 12.2)]
    t = simular(velas, EstrategiaFija(en_barra=5), costos=ModeloCostos())[0]
    assert t.r_neto < t.r_bruto
    assert t.r_neto == pytest.approx(2.0 - t.costo_pct * 10.0 / 1.0)


def test_corto_simetrico():
    velas = [vela(10.5, 10.6, 10.2, 10.3)] * 6 + [vela(10.2, 10.3, 9.9, 9.95), vela(9.9, 9.95, 7.5, 7.8)]
    t = simular(velas, EstrategiaFija(en_barra=5, entrada=10.0, stop=11.0, objetivo=8.0, direccion=Direccion.CORTO))[0]
    assert t.motivo_salida == "objetivo" and t.r_bruto == pytest.approx(2.0)


def test_resumen_en_r():
    velas = [vela(9.5, 9.8, 9.4, 9.7)] * 6 + [vela(9.8, 10.2, 9.7, 10.1), vela(10.1, 12.5, 10.0, 12.2)]
    tabla = a_tabla(simular(velas, EstrategiaFija(en_barra=5)))
    fila = resumen(tabla, ["setup"]).iloc[0]
    assert fila["trades"] == 1 and fila["tasa_acierto"] == 1.0 and fila["r_total_neto"] == pytest.approx(2.0)
