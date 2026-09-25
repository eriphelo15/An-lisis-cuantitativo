from datetime import date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

INICIO_PREMERCADO = time(4, 0)
APERTURA = time(9, 30)
CIERRE = time(16, 0)
CIERRE_ANTICIPADO = time(13, 0)
FIN_POSTMERCADO = time(20, 0)

# Cierres extraordinarios de NYSE (huracán Sandy, funerales de Estado).
CIERRES_ESPECIALES = {date(2012, 10, 29), date(2012, 10, 30), date(2018, 12, 5), date(2025, 1, 9)}

LUNES, JUEVES = 0, 3


def _domingo_de_pascua(anio: int) -> date:
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(anio, mes, dia)


def _nesimo(anio: int, mes: int, dia_semana: int, n: int) -> date:
    primero = date(anio, mes, 1)
    return primero + timedelta(days=(dia_semana - primero.weekday()) % 7 + 7 * (n - 1))


def _ultimo(anio: int, mes: int, dia_semana: int) -> date:
    siguiente = date(anio + (mes == 12), mes % 12 + 1, 1)
    ultimo_dia = siguiente - timedelta(days=1)
    return ultimo_dia - timedelta(days=(ultimo_dia.weekday() - dia_semana) % 7)


def _observado(dia: date) -> date:
    if dia.weekday() == 5:
        return dia - timedelta(days=1)
    if dia.weekday() == 6:
        return dia + timedelta(days=1)
    return dia


@lru_cache(maxsize=64)
def feriados(anio: int) -> frozenset[date]:
    dias = set()
    anio_nuevo = date(anio, 1, 1)
    # NYSE no cierra el viernes previo cuando el 1 de enero cae sábado.
    if anio_nuevo.weekday() == 6:
        dias.add(date(anio, 1, 2))
    elif anio_nuevo.weekday() != 5:
        dias.add(anio_nuevo)
    dias.add(_nesimo(anio, 1, LUNES, 3))
    dias.add(_nesimo(anio, 2, LUNES, 3))
    dias.add(_domingo_de_pascua(anio) - timedelta(days=2))
    dias.add(_ultimo(anio, 5, LUNES))
    if anio >= 2022:
        dias.add(_observado(date(anio, 6, 19)))
    dias.add(_observado(date(anio, 7, 4)))
    dias.add(_nesimo(anio, 9, LUNES, 1))
    dias.add(_nesimo(anio, 11, JUEVES, 4))
    dias.add(_observado(date(anio, 12, 25)))
    dias |= {d for d in CIERRES_ESPECIALES if d.year == anio}
    return frozenset(dias)


def es_dia_habil(dia: date) -> bool:
    return dia.weekday() < 5 and dia not in feriados(dia.year)


def hora_de_cierre(dia: date) -> time:
    anticipado = {
        _nesimo(dia.year, 11, JUEVES, 4) + timedelta(days=1),
        date(dia.year, 7, 3),
        date(dia.year, 12, 24),
    }
    return CIERRE_ANTICIPADO if dia in anticipado and es_dia_habil(dia) else CIERRE


def dias_habiles(desde: date, hasta: date) -> list[date]:
    return [desde + timedelta(days=i) for i in range((hasta - desde).days + 1) if es_dia_habil(desde + timedelta(days=i))]


def dias_habiles_previos(dia: date, cantidad: int) -> list[date]:
    previos, actual = [], dia
    while len(previos) < cantidad:
        actual -= timedelta(days=1)
        if es_dia_habil(actual):
            previos.append(actual)
    return sorted(previos)


def en_et(dia: date, hora: time) -> datetime:
    return datetime.combine(dia, hora, tzinfo=ET)
