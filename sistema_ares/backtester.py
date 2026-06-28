"""
Motor de backtesting para el sistema ARES.
Simula la ejecución trade por trade sobre datos históricos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import pandas as pd
import numpy as np
import yfinance as yf

from .config import ReglasCompania, ConfigBot, BOT_CONFIG
from .risk_manager import GestorRiesgo
from .estrategias.base import Senal, DireccionTrade
from .estrategias.orb import EstrategiaORB
from .estrategias.vwap import EstrategiaVWAP


@dataclass
class Trade:
    id: int
    estrategia: str
    direccion: DireccionTrade
    fecha_entrada: datetime
    precio_entrada: float
    stop_loss: float
    take_profit: float
    contratos: int
    confianza: float
    etiqueta: str = ""

    fecha_salida: Optional[datetime] = None
    precio_salida: Optional[float] = None
    pnl_puntos: float = 0.0
    pnl_usd: float = 0.0
    resultado: str = "abierto"   # "win" | "loss" | "breakeven"

    @property
    def riesgo_puntos(self) -> float:
        return abs(self.precio_entrada - self.stop_loss)

    @property
    def recompensa_puntos(self) -> float:
        return abs(self.take_profit - self.precio_entrada)


class Backtester:
    def __init__(
        self,
        reglas: ReglasCompania,
        config: ConfigBot = BOT_CONFIG,
        ventana_datos: int = 100,
    ):
        self.reglas = reglas
        self.config = config
        self.ventana = ventana_datos

        self.gestor_riesgo = GestorRiesgo(reglas, config)
        self.estrategias = self._inicializar_estrategias()

        self.trades: List[Trade] = []
        self._trade_abierto: Optional[Trade] = None
        self._id_counter: int = 0
        self._equity_curve: List[float] = []
        self._fechas_equity: List[datetime] = []

    def ejecutar(
        self,
        ticker: str,
        periodo: str = "60d",
        intervalo: str = "5m",
        simular: bool = False,
    ) -> "ResultadoBacktest":
        datos_raw = self._cargar_datos(ticker, periodo, intervalo, simular)

        self._ejecutar_simulacion(datos_raw)

        return ResultadoBacktest(
            trades=self.trades,
            equity_curve=self._equity_curve,
            fechas_equity=self._fechas_equity,
            reglas=self.reglas,
            capital_inicial=self.reglas.tamano_cuenta,
            capital_final=self.gestor_riesgo.capital_actual,
        )

    def _ejecutar_simulacion(self, datos: pd.DataFrame):
        fecha_actual = None

        for i in range(self.ventana, len(datos)):
            ventana = datos.iloc[i - self.ventana: i + 1]
            barra = datos.iloc[i]
            ts = barra.name
            fecha = ts.date()

            # Nuevo día
            if fecha != fecha_actual:
                fecha_actual = fecha
                self.gestor_riesgo.iniciar_dia(fecha)
                for est in self.estrategias:
                    est.reiniciar_dia()

            # Registrar equity
            self._equity_curve.append(self.gestor_riesgo.capital_actual)
            self._fechas_equity.append(ts)

            # Gestionar trade abierto
            if self._trade_abierto:
                self._verificar_cierre(barra)
                continue

            # Verificar si se puede operar
            puede, razon = self.gestor_riesgo.puede_operar()
            if not puede:
                continue

            # Buscar señal en cada estrategia activa
            for estrategia in self.estrategias:
                if estrategia.nombre not in self.config.estrategias_activas:
                    continue

                senal = estrategia.calcular_senal(ventana)
                if senal:
                    self._abrir_trade(senal, ts)
                    break   # Solo un trade a la vez

    def _abrir_trade(self, senal: Senal, ts: datetime):
        contratos = self.gestor_riesgo.calcular_contratos(
            senal.precio_entrada, senal.stop_loss
        )
        if contratos == 0:
            return

        self._id_counter += 1
        self._trade_abierto = Trade(
            id=self._id_counter,
            estrategia=senal.estrategia,
            direccion=senal.direccion,
            fecha_entrada=ts,
            precio_entrada=senal.precio_entrada,
            stop_loss=senal.stop_loss,
            take_profit=senal.take_profit,
            contratos=contratos,
            confianza=senal.confianza,
            etiqueta=senal.etiqueta,
        )

    def _verificar_cierre(self, barra):
        t = self._trade_abierto
        if t is None:
            return

        precio_salida = None
        resultado = None

        if t.direccion == DireccionTrade.LONG:
            if barra["low"] <= t.stop_loss:
                precio_salida = t.stop_loss
                resultado = "loss"
            elif barra["high"] >= t.take_profit:
                precio_salida = t.take_profit
                resultado = "win"
        else:
            if barra["high"] >= t.stop_loss:
                precio_salida = t.stop_loss
                resultado = "loss"
            elif barra["low"] <= t.take_profit:
                precio_salida = t.take_profit
                resultado = "win"

        if precio_salida is not None:
            self._cerrar_trade(precio_salida, resultado, barra.name)

    def _cerrar_trade(self, precio_salida: float, resultado: str, ts: datetime):
        t = self._trade_abierto
        t.fecha_salida = ts
        t.precio_salida = precio_salida
        t.resultado = resultado

        if t.direccion == DireccionTrade.LONG:
            t.pnl_puntos = precio_salida - t.precio_entrada
        else:
            t.pnl_puntos = t.precio_entrada - precio_salida

        # Convertir a USD para MNQ
        valor_por_punto = self.config.tick_valor_mnq / self.config.tick_size
        t.pnl_usd = (
            t.pnl_puntos * valor_por_punto * t.contratos
            - self.config.comision_ida_vuelta * t.contratos
        )

        self.gestor_riesgo.registrar_resultado(t.pnl_usd)
        self.trades.append(t)
        self._trade_abierto = None

    def _cargar_datos(
        self, ticker: str, periodo: str, intervalo: str, simular: bool
    ) -> pd.DataFrame:
        if simular:
            from .datos_simulados import generar_nq_simulado
            dias = int(periodo.replace("d", "")) if periodo.endswith("d") else 30
            intervalo_min = int(intervalo.replace("m", "")) if intervalo.endswith("m") else 5
            print(f"\n[ARES] Generando datos simulados: NQ | {dias}d | {intervalo_min}min")
            df = generar_nq_simulado(dias=dias, intervalo_min=intervalo_min)
            print(f"[ARES] {len(df)} barras simuladas | "
                  f"{df.index[0].date()} → {df.index[-1].date()}")
            return df

        print(f"\n[ARES] Descargando datos: {ticker} | {periodo} | {intervalo}")
        datos_raw = yf.download(ticker, period=periodo, interval=intervalo, progress=False)

        if datos_raw.empty:
            raise ValueError(f"No se pudieron obtener datos para {ticker}")

        datos_raw.columns = [c.lower() for c in datos_raw.columns]
        if "adj close" in datos_raw.columns:
            datos_raw = datos_raw.drop(columns=["adj close"])
        datos_raw.index = pd.to_datetime(datos_raw.index)

        if datos_raw.index.tz is None:
            datos_raw.index = datos_raw.index.tz_localize("UTC")
        datos_raw.index = datos_raw.index.tz_convert(self.config.zona_horaria)

        print(f"[ARES] {len(datos_raw)} barras cargadas | "
              f"{datos_raw.index[0].date()} → {datos_raw.index[-1].date()}")
        return datos_raw

    def _inicializar_estrategias(self):
        return [
            EstrategiaORB(multiplicador_tp=2.0, min_rango_puntos=5, max_rango_puntos=150),
            EstrategiaVWAP(sd_entrada=2.0, rsi_sobrecompra=70, rsi_sobreventa=30),
        ]


@dataclass
class ResultadoBacktest:
    trades: List[Trade]
    equity_curve: List[float]
    fechas_equity: List[datetime]
    reglas: ReglasCompania
    capital_inicial: float
    capital_final: float

    @property
    def pnl_total(self) -> float:
        return self.capital_final - self.capital_inicial

    @property
    def trades_cerrados(self) -> List[Trade]:
        return [t for t in self.trades if t.resultado != "abierto"]

    @property
    def wins(self) -> List[Trade]:
        return [t for t in self.trades_cerrados if t.resultado == "win"]

    @property
    def losses(self) -> List[Trade]:
        return [t for t in self.trades_cerrados if t.resultado == "loss"]

    @property
    def win_rate(self) -> float:
        total = len(self.trades_cerrados)
        if total == 0:
            return 0.0
        return len(self.wins) / total

    @property
    def profit_factor(self) -> float:
        ganancia = sum(t.pnl_usd for t in self.wins)
        perdida = abs(sum(t.pnl_usd for t in self.losses))
        if perdida == 0:
            return float("inf")
        return ganancia / perdida

    @property
    def max_drawdown(self) -> float:
        if not self.equity_curve:
            return 0.0
        curva = np.array(self.equity_curve)
        picos = np.maximum.accumulate(curva)
        dd = picos - curva
        return float(dd.max())

    @property
    def sharpe_ratio(self) -> float:
        if len(self.trades_cerrados) < 2:
            return 0.0
        pnls = [t.pnl_usd for t in self.trades_cerrados]
        if np.std(pnls) == 0:
            return 0.0
        return float(np.mean(pnls) / np.std(pnls) * np.sqrt(252))

    @property
    def promedio_rr(self) -> float:
        rrs = [t.recompensa_puntos / t.riesgo_puntos for t in self.trades_cerrados
               if t.riesgo_puntos > 0]
        if not rrs:
            return 0.0
        return float(np.mean(rrs))
