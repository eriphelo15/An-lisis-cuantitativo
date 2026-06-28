"""
Motor de gestión de riesgo para prop firms.
Este módulo es el guardián del sistema — ninguna orden pasa sin su aprobación.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from .config import ReglasCompania, ConfigBot, BOT_CONFIG


@dataclass
class EstadoRiesgo:
    perdida_diaria: float = 0.0
    ganancia_diaria: float = 0.0
    pnl_total: float = 0.0
    trades_hoy: int = 0
    perdidas_consecutivas: int = 0
    factor_size_actual: float = 1.0
    max_equity: float = 0.0           # Para calcular trailing drawdown
    drawdown_actual: float = 0.0
    dia_actual: Optional[date] = None
    trading_permitido: bool = True
    razon_bloqueo: str = ""
    dias_operados: set = field(default_factory=set)


class GestorRiesgo:
    """
    Implementa todas las reglas de la prop firm más capas adicionales
    de protección propias del sistema.
    """

    def __init__(self, reglas: ReglasCompania, config: ConfigBot = BOT_CONFIG):
        self.reglas = reglas
        self.config = config
        self.capital_inicial = reglas.tamano_cuenta
        self.capital_actual = reglas.tamano_cuenta
        self.estado = EstadoRiesgo(max_equity=reglas.tamano_cuenta)

    # ──────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────

    def iniciar_dia(self, fecha: date) -> bool:
        """Prepara el gestor para un nuevo día de trading."""
        if self.estado.dia_actual == fecha:
            return self.estado.trading_permitido

        self.estado.dia_actual = fecha
        self.estado.perdida_diaria = 0.0
        self.estado.ganancia_diaria = 0.0
        self.estado.trades_hoy = 0
        self.estado.trading_permitido = True
        self.estado.razon_bloqueo = ""

        self._evaluar_condiciones()
        return self.estado.trading_permitido

    def puede_operar(self) -> tuple[bool, str]:
        """Verifica si el sistema puede abrir un nuevo trade ahora."""
        self._evaluar_condiciones()
        return self.estado.trading_permitido, self.estado.razon_bloqueo

    def calcular_contratos(self, precio_entrada: float, stop_loss: float) -> int:
        """
        Calcula el número óptimo de contratos respetando el riesgo máximo.
        Usa sizing dinámico: si hay pérdidas recientes, reduce el tamaño.
        """
        distancia_puntos = abs(precio_entrada - stop_loss)
        if distancia_puntos == 0:
            return 0

        riesgo_max_trade = self.capital_actual * self.config.riesgo_por_trade_pct
        riesgo_max_trade *= self.estado.factor_size_actual

        valor_por_punto = self.config.tick_valor_mnq / self.config.tick_size
        riesgo_por_contrato = distancia_puntos * valor_por_punto

        contratos = int(riesgo_max_trade / riesgo_por_contrato)
        return max(1, contratos)

    def registrar_resultado(self, pnl_usd: float):
        """Registra el resultado de un trade cerrado y actualiza el estado."""
        self.capital_actual += pnl_usd
        self.estado.pnl_total += pnl_usd
        self.estado.trades_hoy += 1

        if self.estado.dia_actual:
            self.estado.dias_operados.add(self.estado.dia_actual)

        if pnl_usd >= 0:
            self.estado.ganancia_diaria += pnl_usd
            self.estado.perdidas_consecutivas = 0
            self.estado.factor_size_actual = min(
                1.0,
                self.estado.factor_size_actual + 0.25
            )
        else:
            self.estado.perdida_diaria += abs(pnl_usd)
            self.estado.perdidas_consecutivas += 1
            self._ajustar_size_por_racha()

        self._actualizar_drawdown()
        self._evaluar_condiciones()

    # ──────────────────────────────────────────────
    # Propiedades de estado
    # ──────────────────────────────────────────────

    @property
    def limite_perdida_diaria_efectivo(self) -> float:
        return self.reglas.limite_perdida_diaria * self.config.buffer_limite_diario

    @property
    def drawdown_maximo_efectivo(self) -> float:
        return self.reglas.drawdown_maximo * self.config.buffer_drawdown

    @property
    def progreso_objetivo(self) -> float:
        return min(1.0, max(0.0, self.estado.pnl_total / self.reglas.objetivo_ganancia))

    @property
    def dias_trading_completados(self) -> int:
        return len(self.estado.dias_operados)

    @property
    def challenge_completado(self) -> bool:
        return (
            self.estado.pnl_total >= self.reglas.objetivo_ganancia
            and self.dias_trading_completados >= self.reglas.dias_minimos_trading
        )

    @property
    def challenge_fallido(self) -> bool:
        return self.estado.drawdown_actual >= self.reglas.drawdown_maximo

    # ──────────────────────────────────────────────
    # Lógica interna
    # ──────────────────────────────────────────────

    def _evaluar_condiciones(self):
        bloqueos = []

        if self.estado.perdida_diaria >= self.limite_perdida_diaria_efectivo:
            bloqueos.append(
                f"Límite diario alcanzado: ${self.estado.perdida_diaria:.0f} "
                f"/ ${self.limite_perdida_diaria_efectivo:.0f}"
            )

        if self.estado.drawdown_actual >= self.drawdown_maximo_efectivo:
            bloqueos.append(
                f"Drawdown máximo alcanzado: ${self.estado.drawdown_actual:.0f}"
            )

        if self.estado.perdidas_consecutivas >= self.config.max_perdidas_consecutivas:
            bloqueos.append(
                f"{self.estado.perdidas_consecutivas} pérdidas consecutivas"
            )

        if self.estado.trades_hoy >= self.config.max_trades_dia:
            bloqueos.append(
                f"Máximo de trades diarios alcanzado: {self.config.max_trades_dia}"
            )

        if bloqueos:
            self.estado.trading_permitido = False
            self.estado.razon_bloqueo = " | ".join(bloqueos)
        else:
            self.estado.trading_permitido = True
            self.estado.razon_bloqueo = ""

    def _ajustar_size_por_racha(self):
        n = self.config.reducir_size_tras_n_perdidas
        if self.estado.perdidas_consecutivas >= n:
            self.estado.factor_size_actual = self.config.factor_reduccion_size
        else:
            self.estado.factor_size_actual = 1.0

    def _actualizar_drawdown(self):
        if self.capital_actual > self.estado.max_equity:
            self.estado.max_equity = self.capital_actual
        self.estado.drawdown_actual = self.estado.max_equity - self.capital_actual

    def resumen(self) -> dict:
        return {
            "capital_actual": self.capital_actual,
            "pnl_total": self.estado.pnl_total,
            "perdida_diaria": self.estado.perdida_diaria,
            "drawdown_actual": self.estado.drawdown_actual,
            "drawdown_maximo_permitido": self.reglas.drawdown_maximo,
            "objetivo_ganancia": self.reglas.objetivo_ganancia,
            "progreso_pct": self.progreso_objetivo * 100,
            "trades_hoy": self.estado.trades_hoy,
            "dias_operados": self.dias_trading_completados,
            "dias_requeridos": self.reglas.dias_minimos_trading,
            "perdidas_consecutivas": self.estado.perdidas_consecutivas,
            "factor_size": self.estado.factor_size_actual,
            "trading_permitido": self.estado.trading_permitido,
            "challenge_completado": self.challenge_completado,
            "challenge_fallido": self.challenge_fallido,
        }
