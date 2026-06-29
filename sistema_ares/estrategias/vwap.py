"""
VWAP Mean Reversion — Estrategia secundaria de reversión a la media.

Lógica:
  1. Calcular VWAP de la sesión + bandas de desviación estándar
  2. Si precio toca ±2SD Y RSI confirma sobre/sobrecompra → señal contraria
  3. Target: retorno al VWAP o 1SD
  4. Stop: más allá de 3SD

La estadística favorece la reversión cuando el precio se aleja 2+ SD
del VWAP durante sesiones con volumen normal (no eventos de noticias).
Funciona mejor entre 10:00–14:00 ET en días de tendencia débil.
"""

from datetime import time, date
from typing import Optional
import pandas as pd
import numpy as np

from .base import EstrategiaBase, Senal, DireccionTrade
from ..indicadores import vwap_bandas, rsi as calcular_rsi, detectar_tendencia_sesion


class EstrategiaVWAP(EstrategiaBase):
    def __init__(
        self,
        sd_entrada: float = 2.0,
        sd_stop: float = 3.0,
        rsi_sobrecompra: float = 70.0,
        rsi_sobreventa: float = 30.0,
        rsi_periodo: int = 14,
        max_trades_dia: int = 2,
        solo_contratendencia: bool = True,
    ):
        super().__init__("VWAP")
        self.sd_entrada = sd_entrada
        self.sd_stop = sd_stop
        self.rsi_sobrecompra = rsi_sobrecompra
        self.rsi_sobreventa = rsi_sobreventa
        self.rsi_periodo = rsi_periodo
        self.max_trades_dia = max_trades_dia
        self.solo_contratendencia = solo_contratendencia

        self._trades_hoy: int = 0
        self._fecha_actual: Optional[date] = None

    def reiniciar_dia(self):
        self._trades_hoy = 0

    def calcular_senal(self, datos: pd.DataFrame) -> Optional[Senal]:
        # Necesitamos suficiente historia para calcular indicadores
        if len(datos) < max(30, self.rsi_periodo + 5):
            return None

        ultima = datos.iloc[-1]
        ts = ultima.name
        hora = ts.time()
        fecha = ts.date()

        if fecha != self._fecha_actual:
            self._fecha_actual = fecha
            self.reiniciar_dia()

        # Horario permitido: 10:00 - 14:30 ET (mercado más líquido)
        if not (time(10, 0) <= hora <= time(14, 30)):
            return None

        if self._trades_hoy >= self.max_trades_dia:
            return None

        # Calcular indicadores sobre la ventana disponible
        bandas = vwap_bandas(datos)
        rsi_vals = calcular_rsi(datos["close"], self.rsi_periodo)
        tendencia = detectar_tendencia_sesion(datos)

        idx = -1
        precio = datos["close"].iloc[idx]
        vwap_val = bandas["vwap"].iloc[idx]
        sup_entrada = bandas[f"sup_{self.sd_entrada}"].iloc[idx]
        inf_entrada = bandas[f"inf_{self.sd_entrada}"].iloc[idx]
        sup_stop = bandas[f"sup_{self.sd_stop}"].iloc[idx]
        inf_stop = bandas[f"inf_{self.sd_stop}"].iloc[idx]
        rsi_val = rsi_vals.iloc[idx]
        tend = tendencia.iloc[idx]

        if pd.isna(vwap_val) or pd.isna(rsi_val):
            return None

        # SHORT: precio en zona de sobrecompra (sobre 2SD) + RSI alto
        # Solo si la tendencia NO es fuertemente alcista (contratendencia)
        if (
            precio >= sup_entrada
            and rsi_val >= self.rsi_sobrecompra
            and (not self.solo_contratendencia or tend <= 0)
        ):
            sl = max(precio * 1.001, sup_stop)  # Stop más allá del 3SD
            tp = vwap_val                        # Target: VWAP
            self._trades_hoy += 1
            return Senal(
                direccion=DireccionTrade.SHORT,
                precio_entrada=precio,
                stop_loss=sl,
                take_profit=tp,
                estrategia=self.nombre,
                confianza=0.65,
                etiqueta=f"VWAP-S RSI={rsi_val:.0f} +{self.sd_entrada}SD",
            )

        # LONG: precio en zona de sobreventa (bajo -2SD) + RSI bajo
        if (
            precio <= inf_entrada
            and rsi_val <= self.rsi_sobreventa
            and (not self.solo_contratendencia or tend >= 0)
        ):
            sl = min(precio * 0.999, inf_stop)
            tp = vwap_val
            self._trades_hoy += 1
            return Senal(
                direccion=DireccionTrade.LONG,
                precio_entrada=precio,
                stop_loss=sl,
                take_profit=tp,
                estrategia=self.nombre,
                confianza=0.65,
                etiqueta=f"VWAP-L RSI={rsi_val:.0f} -{self.sd_entrada}SD",
            )

        return None
