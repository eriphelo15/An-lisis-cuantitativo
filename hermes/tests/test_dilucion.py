from datetime import datetime

from hermes.inteligencia.dilucion import riesgo_dilucion
from hermes.inteligencia.sec.filings import ET
from hermes.inteligencia.sec.financieros import Financieros

APERTURA = datetime(2024, 6, 3, 9, 30, tzinfo=ET)


def financieros(caja=None, quema=None):
    return Financieros(caja=caja, caja_al=None, quema_mensual=quema, acciones=None, acciones_al=None)


def nombres(riesgo):
    return {c.nombre: c.puntos for c in riesgo.componentes}


def test_riesgo_alto_con_atm_shelf_y_poca_caja(filing):
    filings = [
        filing("S-3", "2023-05-01T10:00:00"),
        filing("424B5", "2024-05-20T08:00:00"),
        filing("8-K", "2024-05-20T08:05:00", ("1.01", "3.02")),
    ]
    riesgo = riesgo_dilucion(filings, financieros(caja=2_000_000, quema=1_000_000), APERTURA)
    assert nombres(riesgo) == {"prospecto": 30, "shelf": 20, "financiamiento": 10, "runway": 25}
    assert riesgo.puntaje == 85
    assert riesgo.nivel == "alto"


def test_ignora_filings_posteriores_al_momento(filing):
    filings = [filing("424B5", "2024-06-03T09:45:00"), filing("S-1", "2024-06-04T08:00:00")]
    riesgo = riesgo_dilucion(filings, financieros(caja=100, quema=-1), APERTURA)
    assert riesgo.puntaje == 0
    assert riesgo.nivel == "bajo"


def test_shelf_vencido_o_retirado_no_cuenta(filing):
    vencido = [filing("S-3", "2020-01-01T10:00:00")]
    retirado = [filing("S-3", "2023-01-01T10:00:00"), filing("RW", "2023-06-01T10:00:00")]
    sin_consumo = financieros(caja=100, quema=-1)
    assert "shelf" not in nombres(riesgo_dilucion(vencido, sin_consumo, APERTURA))
    assert "shelf" not in nombres(riesgo_dilucion(retirado, sin_consumo, APERTURA))


def test_prospecto_reciente_pesa_menos_que_inmediato(filing):
    filings = [filing("424B3", "2024-03-01T10:00:00")]
    riesgo = riesgo_dilucion(filings, financieros(caja=100, quema=-1), APERTURA)
    assert nombres(riesgo) == {"prospecto": 20}


def test_runway_por_tramos_y_desconocido():
    assert nombres(riesgo_dilucion([], financieros(), APERTURA)) == {"runway": 10}
    assert nombres(riesgo_dilucion([], financieros(caja=10, quema=1), APERTURA)) == {"runway": 15}
    assert nombres(riesgo_dilucion([], financieros(caja=20, quema=1), APERTURA)) == {"runway": 5}
    assert nombres(riesgo_dilucion([], financieros(caja=30, quema=1), APERTURA)) == {}
