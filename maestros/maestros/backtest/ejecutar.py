from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

import pandas as pd

from maestros.backtest.costos import ModeloCostos
from maestros.backtest.modelos import Trade
from maestros.backtest.motor import ReglasSimulacion, simular_dia
from maestros.datos.almacen import Almacen
from maestros.datos.calendario import dias_habiles_previos
from maestros.informacion.ficha import Ficha
from maestros.traders.base import Contexto, Estrategia
from maestros.traders.indicadores import volumen_normal_acumulado


@dataclass(frozen=True)
class FiltroCandidatos:
    """Prefiltro con barras diarias para no descargar minutos de todo el mercado.

    Es más amplio que cualquier algoritmo: su único trabajo es no dejar fuera días que podrían calificar.
    """

    precio_min: float = 1.0
    precio_max: float = 20.0
    alza_maxima_min: float = 0.10  # máximo del día vs. cierre previo
    volumen_relativo_min: float = 2.0
    ventana_volumen: int = 20
    gap_max_sin_split: float = 4.0  # en datos sin ajustar, un reverse split parece un gap enorme


def candidatos(diario: pd.DataFrame, filtro: FiltroCandidatos = FiltroCandidatos()) -> pd.DataFrame:
    df = diario.sort_values(["ticker", "fecha"]).copy()
    grupo = df.groupby("ticker", sort=False)
    df["cierre_previo"] = grupo["cierre"].shift(1)
    df["volumen_promedio"] = grupo["volumen"].transform(
        lambda v: v.shift(1).rolling(filtro.ventana_volumen, min_periods=filtro.ventana_volumen // 2).mean())
    elegido = (
        df["cierre_previo"].between(filtro.precio_min, filtro.precio_max)
        & (df["maximo"] / df["cierre_previo"] - 1 >= filtro.alza_maxima_min)
        & (df["volumen"] >= filtro.volumen_relativo_min * df["volumen_promedio"])
        & (df["apertura"] / df["cierre_previo"] - 1 <= filtro.gap_max_sin_split)
    )
    return df.loc[elegido, ["fecha", "ticker", "cierre_previo", "volumen_promedio"]].reset_index(drop=True)


def _motivo_sin_trade(estrategia: Estrategia, ticker: str, fecha: date, barras: pd.DataFrame, cierre_previo: float,
                      normal: pd.Series | None, ficha: Ficha | None) -> str:
    """Qué pilar falló en el momento más prometedor del día (el máximo de precio)."""
    revisar = getattr(estrategia, "revisar_pilares", None)
    if revisar is None:
        return "sin_senal"
    barras = barras.sort_values("hora").reset_index(drop=True)
    i = int(barras["maximo"].to_numpy().argmax())
    fallo = revisar(Contexto(ticker, fecha, barras.iloc[: i + 1], cierre_previo, normal, ficha))
    return f"pilar_{fallo}" if fallo else "pilares_ok_sin_setup"


def ejecutar_backtest(
    estrategia: Estrategia,
    lista_candidatos: pd.DataFrame,
    almacen: Almacen,
    obtener_ficha: Callable[[str, date], Ficha | None],
    costos: ModeloCostos = ModeloCostos(),
    reglas: ReglasSimulacion = ReglasSimulacion(),
    dias_volumen_normal: int = 20,
    progreso: Callable[[str], None] = lambda _: None,
) -> tuple[list[Trade], Counter]:
    trades: list[Trade] = []
    cobertura: Counter = Counter()
    total = len(lista_candidatos)
    for i, fila in enumerate(lista_candidatos.itertuples(index=False), start=1):
        if i % 50 == 0 or i == total:
            progreso(f"  {i}/{total} días simulados")
        barras = almacen.cargar_minutos(fila.fecha, fila.ticker)
        if barras.empty:
            cobertura["sin_minutos"] += 1
            continue
        previas = [almacen.cargar_minutos(d, fila.ticker) for d in dias_habiles_previos(fila.fecha, dias_volumen_normal)]
        previas = [p for p in previas if not p.empty]
        normal = volumen_normal_acumulado(pd.concat(previas, ignore_index=True)) if previas else None
        if normal is None:
            cobertura["sin_volumen_normal"] += 1
        ficha = obtener_ficha(fila.ticker, fila.fecha)
        if ficha is None:
            cobertura["sin_ficha"] += 1
        cobertura["simulados"] += 1
        cierre_previo = float(fila.cierre_previo)
        del_dia = simular_dia(estrategia, fila.ticker, fila.fecha, barras, cierre_previo, costos, reglas, normal, ficha)
        if not del_dia:
            cobertura[f"sin_trade:{_motivo_sin_trade(estrategia, fila.ticker, fila.fecha, barras, cierre_previo, normal, ficha)}"] += 1
        trades.extend(del_dia)
    return trades, cobertura
