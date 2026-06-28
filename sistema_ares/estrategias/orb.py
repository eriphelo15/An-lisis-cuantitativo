"""
Opening Range Breakout (ORB) — Estrategia principal para futuros.

Lógica:
  1. Los primeros 30 min definen el rango de apertura (9:30–10:00 ET)
  2. Si el precio rompe hacia arriba con volumen → LONG
  3. Si el precio rompe hacia abajo con volumen → SHORT
  4. TP = tamaño del rango × multiplicador (1:2 mínimo)
  5. SL = extremo opuesto del rango
  6. Solo 1 trade por día con esta estrategia

Ventaja estadística:
  En NQ/ES, los primeros 30 min concentran ~35% del volumen diario.
  El breakout de ese rango tiene 60-65% de continuación estadística.
"""

from datetime import time, date
from typing import Optional
import pandas as pd

from .base import EstrategiaBase, Senal, DireccionTrade


class EstrategiaORB(EstrategiaBase):
    def __init__(
        self,
        minutos_rango: int = 30,
        multiplicador_tp: float = 2.0,
        min_rango_puntos: float = 8.0,
        max_rango_puntos: float = 60.0,
        confirmar_volumen: bool = True,
        mult_volumen: float = 1.2,
    ):
        super().__init__("ORB")
        self.minutos_rango = minutos_rango
        self.multiplicador_tp = multiplicador_tp
        self.min_rango_puntos = min_rango_puntos
        self.max_rango_puntos = max_rango_puntos
        self.confirmar_volumen = confirmar_volumen
        self.mult_volumen = mult_volumen

        self._or_high: Optional[float] = None
        self._or_low: Optional[float] = None
        self._or_vol_medio: Optional[float] = None
        self._rango_listo: bool = False
        self._trade_tomado: bool = False
        self._fecha_actual: Optional[date] = None

    def reiniciar_dia(self):
        self._or_high = None
        self._or_low = None
        self._or_vol_medio = None
        self._rango_listo = False
        self._trade_tomado = False

    def calcular_senal(self, datos: pd.DataFrame) -> Optional[Senal]:
        if len(datos) < 2:
            return None

        ultima = datos.iloc[-1]
        ts = ultima.name
        hora = ts.time()
        fecha = ts.date()

        # Reset en día nuevo
        if fecha != self._fecha_actual:
            self._fecha_actual = fecha
            self.reiniciar_dia()

        hora_inicio_or = time(9, 30)
        hora_fin_or = time(10, 0)
        hora_max_entrada = time(15, 30)

        # Construir rango durante los primeros 30 min
        if hora_inicio_or <= hora < hora_fin_or:
            self._construir_rango(datos, hora_inicio_or, fecha)
            return None

        # Sellar el rango justo después del período
        if hora >= hora_fin_or and not self._rango_listo:
            self._construir_rango(datos, hora_inicio_or, fecha)
            self._rango_listo = True

        if not self._rango_listo or self._trade_tomado:
            return None

        if hora > hora_max_entrada:
            return None

        tamano_rango = self._or_high - self._or_low

        # Filtro de rango: ni muy pequeño ni muy volátil
        if not (self.min_rango_puntos <= tamano_rango <= self.max_rango_puntos):
            return None

        precio_close = ultima["close"]
        precio_high = ultima["high"]
        precio_low = ultima["low"]
        volumen = ultima.get("volume", None)
        volumen_ok = True
        if self.confirmar_volumen and volumen and self._or_vol_medio:
            volumen_ok = volumen >= self._or_vol_medio * self.mult_volumen

        # LONG: barra cierra por encima del rango con confirmación
        if precio_high > self._or_high and precio_close > self._or_high and volumen_ok:
            sl = self._or_low
            tp = precio_close + tamano_rango * self.multiplicador_tp
            self._trade_tomado = True
            return Senal(
                direccion=DireccionTrade.LONG,
                precio_entrada=precio_close,
                stop_loss=sl,
                take_profit=tp,
                estrategia=self.nombre,
                confianza=0.75 if volumen_ok else 0.55,
                etiqueta=f"ORB-L rango={tamano_rango:.1f}pts",
            )

        # SHORT: barra cierra por debajo del rango con confirmación
        if precio_low < self._or_low and precio_close < self._or_low and volumen_ok:
            sl = self._or_high
            tp = precio_close - tamano_rango * self.multiplicador_tp
            self._trade_tomado = True
            return Senal(
                direccion=DireccionTrade.SHORT,
                precio_entrada=precio_close,
                stop_loss=sl,
                take_profit=tp,
                estrategia=self.nombre,
                confianza=0.75 if volumen_ok else 0.55,
                etiqueta=f"ORB-S rango={tamano_rango:.1f}pts",
            )

        return None

    def _construir_rango(self, datos: pd.DataFrame, hora_inicio: time, fecha: date):
        mascara = (
            (datos.index.time >= hora_inicio)
            & (datos.index.date == fecha)
        )
        rango = datos[mascara]
        if len(rango) > 0:
            self._or_high = rango["high"].max()
            self._or_low = rango["low"].min()
            if "volume" in rango.columns:
                self._or_vol_medio = rango["volume"].mean()
