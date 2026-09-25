import math
from dataclasses import dataclass, replace
from datetime import date, datetime, time

import pandas as pd

from maestros.backtest.costos import ModeloCostos
from maestros.backtest.modelos import Direccion, Senal, Trade
from maestros.informacion.ficha import Ficha
from maestros.traders.base import Contexto, Estrategia


@dataclass(frozen=True)
class ReglasSimulacion:
    riesgo_por_trade: float = 50.0
    max_trades_dia: int = 5
    perdida_max_dia_r: float = 3.0  # sin trades nuevos tras perder 3R en el día
    vigencia_senal_barras: int = 3  # si la entrada no se dispara en N barras, la orden se cancela
    participacion_max: float = 0.05  # máximo % del volumen de las últimas 5 barras
    salida_forzada: time = time(15, 55)


@dataclass
class _Posicion:
    senal: Senal
    hora_entrada: datetime
    precio_entrada: float
    acciones: int
    costo_pct: float


def _disparo(senal: Senal, barra) -> float | None:
    """Precio de entrada si la barra toca el disparo; si abre más allá (gap), se llena en la apertura."""
    if senal.direccion is Direccion.LARGO and barra.maximo >= senal.entrada:
        return max(senal.entrada, barra.apertura)
    if senal.direccion is Direccion.CORTO and barra.minimo <= senal.entrada:
        return min(senal.entrada, barra.apertura)
    return None


def _toca_stop(senal: Senal, barra) -> float | None:
    if senal.direccion is Direccion.LARGO and barra.minimo <= senal.stop:
        return min(senal.stop, barra.apertura)
    if senal.direccion is Direccion.CORTO and barra.maximo >= senal.stop:
        return max(senal.stop, barra.apertura)
    return None


def _toca_objetivo(senal: Senal, barra) -> float | None:
    if senal.direccion is Direccion.LARGO and barra.maximo >= senal.objetivo:
        return max(senal.objetivo, barra.apertura)
    if senal.direccion is Direccion.CORTO and barra.minimo <= senal.objetivo:
        return min(senal.objetivo, barra.apertura)
    return None


def simular_dia(
    estrategia: Estrategia,
    ticker: str,
    fecha: date,
    barras: pd.DataFrame,
    cierre_previo: float,
    costos: ModeloCostos,
    reglas: ReglasSimulacion = ReglasSimulacion(),
    volumen_normal: pd.Series | None = None,
    ficha: Ficha | None = None,
) -> list[Trade]:
    """Recorre las barras de 1 minuto de un día en orden, como pasaría en vivo.

    Reglas conservadoras: si en la misma barra se tocan stop y objetivo, gana el stop; si la barra que
    dispara la entrada también toca el stop, el trade se cuenta como perdido; los gaps (incluidos los
    halts) llenan el stop en la apertura de la barra siguiente, no en el precio del stop.
    """
    barras = barras.sort_values("hora").reset_index(drop=True)
    trades: list[Trade] = []
    posicion: _Posicion | None = None
    pendiente: Senal | None = None
    barras_restantes = 0

    def cerrar(barra, precio: float, motivo: str) -> None:
        nonlocal posicion
        trades.append(Trade(
            ticker=ticker, setup=posicion.senal.setup, direccion=posicion.senal.direccion,
            hora_senal=posicion.senal.hora, hora_entrada=posicion.hora_entrada,
            precio_entrada=posicion.precio_entrada, stop=posicion.senal.stop, objetivo=posicion.senal.objetivo,
            hora_salida=barra.hora, precio_salida=precio, motivo_salida=motivo,
            acciones=posicion.acciones, costo_pct=posicion.costo_pct,
        ))
        posicion = None

    for i, barra in enumerate(barras.itertuples(index=False)):
        if posicion is not None:
            if (precio := _toca_stop(posicion.senal, barra)) is not None:
                cerrar(barra, precio, "stop")
            elif (precio := _toca_objetivo(posicion.senal, barra)) is not None:
                cerrar(barra, precio, "objetivo")
            elif barra.hora.time() >= reglas.salida_forzada:
                cerrar(barra, barra.cierre, "tiempo")
            continue

        if pendiente is not None:
            precio = _disparo(pendiente, barra)
            if precio is not None:
                previas = barras.iloc[max(0, i - 5):i]
                limite = reglas.participacion_max * previas["volumen"].mean() if len(previas) else 0
                acciones = min(math.floor(reglas.riesgo_por_trade / pendiente.riesgo_por_accion), math.floor(limite))
                if acciones >= 1:
                    dolar_volumen = float((barras.iloc[: i + 1]["volumen"] * barras.iloc[: i + 1]["cierre"]).sum())
                    # el stop se mantiene en su precio original aunque la entrada se llene con gap
                    posicion = _Posicion(pendiente, barra.hora, precio, acciones,
                                         costos.costo_ida_vuelta(precio, dolar_volumen))
                    if (salida := _toca_stop(pendiente, barra)) is not None:
                        cerrar(barra, salida, "stop")
                pendiente = None
                continue
            barras_restantes -= 1
            if barras_restantes <= 0 or _toca_stop(pendiente, barra) is not None:
                pendiente = None
            continue

        if (len(trades) >= reglas.max_trades_dia or barra.hora.time() >= reglas.salida_forzada
                or sum(t.r_neto for t in trades) <= -reglas.perdida_max_dia_r):
            continue
        ctx = Contexto(ticker, fecha, barras.iloc[: i + 1], cierre_previo, volumen_normal, ficha)
        senal = estrategia.evaluar(ctx)
        if senal is not None and senal.es_valida:
            pendiente = replace(senal, hora=barra.hora)
            barras_restantes = reglas.vigencia_senal_barras

    if posicion is not None:
        cerrar(barras.iloc[-1], float(barras.iloc[-1]["cierre"]), "fin_datos")
    return trades
