"""
Configuración central del sistema ARES para prop firms de futuros.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ReglasCompania:
    nombre: str
    tamano_cuenta: float
    limite_perdida_diaria: float
    drawdown_maximo: float
    objetivo_ganancia: float
    dias_minimos_trading: int
    instrumentos: List[str]
    plataforma: str
    profit_split: float = 0.90


# Configuraciones reales de Tradeify Express
TRADEIFY: Dict[str, ReglasCompania] = {
    "10k": ReglasCompania(
        nombre="Tradeify $10K",
        tamano_cuenta=10_000,
        limite_perdida_diaria=500,
        drawdown_maximo=600,
        objetivo_ganancia=800,
        dias_minimos_trading=5,
        instrumentos=["MNQ", "MES", "MYM"],
        plataforma="Rithmic",
    ),
    "25k": ReglasCompania(
        nombre="Tradeify $25K",
        tamano_cuenta=25_000,
        limite_perdida_diaria=1_500,
        drawdown_maximo=1_500,
        objetivo_ganancia=2_000,
        dias_minimos_trading=5,
        instrumentos=["MNQ", "MES", "MYM"],
        plataforma="Rithmic",
    ),
    "50k": ReglasCompania(
        nombre="Tradeify $50K",
        tamano_cuenta=50_000,
        limite_perdida_diaria=2_500,
        drawdown_maximo=3_000,
        objetivo_ganancia=4_000,
        dias_minimos_trading=5,
        instrumentos=["MNQ", "MES", "MYM", "NQ", "ES"],
        plataforma="Rithmic",
    ),
    "100k": ReglasCompania(
        nombre="Tradeify $100K",
        tamano_cuenta=100_000,
        limite_perdida_diaria=5_000,
        drawdown_maximo=6_000,
        objetivo_ganancia=6_000,
        dias_minimos_trading=5,
        instrumentos=["MNQ", "MES", "NQ", "ES"],
        plataforma="Rithmic",
    ),
    "150k": ReglasCompania(
        nombre="Tradeify $150K",
        tamano_cuenta=150_000,
        limite_perdida_diaria=5_000,
        drawdown_maximo=9_000,
        objetivo_ganancia=9_000,
        dias_minimos_trading=5,
        instrumentos=["MNQ", "MES", "NQ", "ES"],
        plataforma="Rithmic",
    ),
}


@dataclass
class ConfigBot:
    # Riesgo por trade
    riesgo_por_trade_pct: float = 0.003       # 0.3% del capital por trade

    # Buffers de seguridad sobre los límites reales de la prop firm
    buffer_limite_diario: float = 0.80        # Detenerse al 80% del límite
    buffer_drawdown: float = 0.85             # Detenerse al 85% del drawdown

    # Reglas de racha perdedora
    max_perdidas_consecutivas: int = 3
    reducir_size_tras_n_perdidas: int = 2
    factor_reduccion_size: float = 0.50

    # Límite de operaciones por día
    max_trades_dia: int = 3

    # Horario de trading (Eastern Time)
    zona_horaria: str = "America/New_York"
    hora_apertura: str = "09:30"
    hora_cierre_trading: str = "15:45"

    # Datos para backtest (yfinance)
    ticker_backtest: str = "NQ=F"
    intervalo_backtest: str = "5m"

    # Costos de operación (MNQ - Micro Nasdaq)
    tick_size: float = 0.25           # 0.25 puntos por tick
    tick_valor_mnq: float = 0.50      # $0.50 por tick en MNQ
    tick_valor_nq: float = 5.00       # $5.00 por tick en NQ (grande)
    comision_ida_vuelta: float = 1.24  # $1.24 comisión total por contrato

    # Estrategias activas
    estrategias_activas: List[str] = field(
        default_factory=lambda: ["ORB", "VWAP"]
    )


BOT_CONFIG = ConfigBot()
