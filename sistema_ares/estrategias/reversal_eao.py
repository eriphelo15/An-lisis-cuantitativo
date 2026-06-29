"""
Reversal [EAO] — Reversión por engulfing + barrido de liquidez.

Lógica original: Dead Simple Reversal (@paidtofade)
Personalización [EAO]: sesión, Long Bias, Liquidity Sweep, filtro de cuerpo dominante.

CONDICIÓN LONG (todas deben cumplirse):
  c1: Vela anterior bajista  + vela actual alcista   (candle flip)
  c2: Cierre actual > apertura anterior              (engulfing)
  c3: En alguna de las 4 velas previas, el mínimo de largo plazo (longTerm)
      era MAYOR que el mínimo de corto plazo actual (nearTerm)
      → el precio acaba de barrer liquidez bajo la estructura de largo plazo

CONDICIÓN SHORT (simétrica):
  c4 + c5 + c6: espejo de c1/c2/c3 pero en máximos

FILTROS OPCIONALES:
  · Sesión horaria (ET) — por defecto 9:30–11:30
  · Cuerpo dominante — la vela señal debe tener un % de cuerpo mínimo
  · Ventana de confirmación — si la vela es débil, esperar N velas
  · Liquidity Sweep de pivotes (pivot high/low explícitos)
"""

from datetime import time, date
from typing import Optional
import numpy as np
import pandas as pd

from .base import EstrategiaBase, Senal, DireccionTrade
from ..indicadores import atr as calcular_atr


class EstrategiaReversalEAO(EstrategiaBase):

    def __init__(
        self,
        # Estructura
        near_term: int = 3,
        long_term: int = 50,
        # Sesgo
        long_only: bool = False,
        # Sesión (ET)
        use_time: bool = True,
        start_hour: int = 9,
        start_min: int = 30,
        end_hour: int = 11,
        end_min: int = 30,
        # Filtro cuerpo dominante
        use_body_signal: bool = False,
        body_signal_pct: float = 70.0,
        use_body_confirm: bool = False,
        body_confirm_pct: float = 70.0,
        confirm_window: int = 1,
        # Filtro Liquidity Sweep (pivotes)
        use_liq_filter: bool = False,
        liq_length: int = 14,
        sweep_window: int = 2,
        # Salida
        sl_atr_mult: float = 1.5,
        tp_rr: float = 2.0,
        atr_periodo: int = 14,
    ):
        super().__init__("Reversal_EAO")
        self.near_term = near_term
        self.long_term = long_term
        self.long_only = long_only
        self.use_time = use_time
        self.start_hour = start_hour
        self.start_min = start_min
        self.end_hour = end_hour
        self.end_min = end_min
        self.use_body_signal = use_body_signal
        self.body_signal_pct = body_signal_pct
        self.use_body_confirm = use_body_confirm
        self.body_confirm_pct = body_confirm_pct
        self.confirm_window = confirm_window
        self.use_liq_filter = use_liq_filter
        self.liq_length = liq_length
        self.sweep_window = sweep_window
        self.sl_atr_mult = sl_atr_mult
        self.tp_rr = tp_rr
        self.atr_periodo = atr_periodo

        # Estado de confirmación pendiente (persiste entre barras)
        self._pending_buy: int = 0
        self._pending_sell: int = 0
        self._ultima_sesion: Optional[time] = None

        # Pivotes registrados para liquidity sweep
        self._ph_prices: list[float] = []   # pivot highs
        self._pl_prices: list[float] = []   # pivot lows
        self._ph_bar: list[int] = []        # bar index cuando se detectó
        self._pl_bar: list[int] = []
        self._bar_global: int = 0

    def reiniciar_dia(self):
        # Los pivotes y la estructura no se resetean entre días
        pass

    # ──────────────────────────────────────────────────────
    # Señal principal
    # ──────────────────────────────────────────────────────

    def calcular_senal(self, datos: pd.DataFrame) -> Optional[Senal]:
        min_barras = max(self.long_term + 10, self.atr_periodo + 5, self.liq_length * 2 + 5)
        if len(datos) < min_barras:
            return None

        self._bar_global += 1
        ultima = datos.iloc[-1]
        ts = ultima.name

        # ── Filtro de sesión ──────────────────────────────
        if self.use_time:
            hora = ts.time()
            inicio = time(self.start_hour, self.start_min)
            fin = time(self.end_hour, self.end_min)
            if not (inicio <= hora < fin):
                self._pending_buy = 0
                self._pending_sell = 0
                return None

        close = datos["close"]
        open_ = datos["open"]
        high  = datos["high"]
        low   = datos["low"]

        # ── Indicadores de estructura ──────────────────────
        near_low  = low.rolling(self.near_term).min()
        near_high = high.rolling(self.near_term).max()
        long_low  = low.rolling(self.long_term).min()
        long_high = high.rolling(self.long_term).max()

        nl = near_low.iloc[-1]
        nh = near_high.iloc[-1]

        # ── Patrón base ───────────────────────────────────
        # LONG: engulfing alcista
        c1 = (close.iloc[-2] < open_.iloc[-2]) and (close.iloc[-1] > open_.iloc[-1])
        c2 = close.iloc[-1] > open_.iloc[-2]
        # c3: el mínimo de corto plazo (hoy) rompió bajo el mínimo de largo plazo de 1-4 velas atrás
        c3 = any(
            long_low.iloc[-(i + 2)] > nl
            for i in range(4)
            if len(datos) > i + 2
        )
        buy_pattern = c1 and c2 and c3

        # SHORT: engulfing bajista
        c4 = (close.iloc[-2] > open_.iloc[-2]) and (close.iloc[-1] < open_.iloc[-1])
        c5 = close.iloc[-1] < open_.iloc[-2]
        c6 = any(
            long_high.iloc[-(i + 2)] < nh
            for i in range(4)
            if len(datos) > i + 2
        )
        sell_pattern = c4 and c5 and c6 and not self.long_only

        # ── Filtro de cuerpo dominante ────────────────────
        str_long  = self._body_strength_long(open_.iloc[-1], close.iloc[-1], high.iloc[-1])
        str_short = self._body_strength_short(open_.iloc[-1], close.iloc[-1], low.iloc[-1])
        strong_bull = (close.iloc[-1] > open_.iloc[-1]) and (str_long  >= self.body_signal_pct)
        strong_bear = (close.iloc[-1] < open_.iloc[-1]) and (str_short >= self.body_signal_pct)

        buy = sell = False

        if not self.use_body_signal:
            buy  = buy_pattern
            sell = sell_pattern
        else:
            # LONG con filtro de cuerpo
            if buy_pattern:
                if strong_bull:
                    buy = True
                elif self.use_body_confirm:
                    self._pending_buy = self.confirm_window
            if self._pending_buy > 0 and not buy_pattern:
                confirm_bull = (close.iloc[-1] > open_.iloc[-1]) and (str_long >= self.body_confirm_pct)
                if confirm_bull:
                    buy = True
                    self._pending_buy = 0
                else:
                    self._pending_buy -= 1

            # SHORT con filtro de cuerpo
            if sell_pattern:
                if strong_bear:
                    sell = True
                elif self.use_body_confirm:
                    self._pending_sell = self.confirm_window
            if self._pending_sell > 0 and not sell_pattern:
                confirm_bear = (close.iloc[-1] < open_.iloc[-1]) and (str_short >= self.body_confirm_pct)
                if confirm_bear:
                    sell = True
                    self._pending_sell = 0
                else:
                    self._pending_sell -= 1

        if self.long_only:
            sell = False

        # ── Filtro de Liquidity Sweep (pivotes) ───────────
        if self.use_liq_filter:
            self._actualizar_pivotes(high, low)
            recent_buyside  = self._hubo_sweep_buyside()
            recent_sellside = self._hubo_sweep_sellside()
            buy  = buy  and recent_sellside
            sell = sell and recent_buyside

        if not (buy or sell):
            return None

        # ── Stop Loss y Take Profit ───────────────────────
        atr_vals = calcular_atr(datos, self.atr_periodo)
        atr_val  = atr_vals.iloc[-1]
        if pd.isna(atr_val) or atr_val == 0:
            return None

        precio = close.iloc[-1]

        if buy:
            sl = min(low.iloc[-1], precio - self.sl_atr_mult * atr_val)
            riesgo = precio - sl
            if riesgo <= 0:
                return None
            tp = precio + self.tp_rr * riesgo
            return Senal(
                direccion=DireccionTrade.LONG,
                precio_entrada=precio,
                stop_loss=sl,
                take_profit=tp,
                estrategia=self.nombre,
                confianza=0.72,
                etiqueta=f"REV-L c3={'✓'} body={str_long:.0f}%",
            )

        # sell
        sl = max(high.iloc[-1], precio + self.sl_atr_mult * atr_val)
        riesgo = sl - precio
        if riesgo <= 0:
            return None
        tp = precio - self.tp_rr * riesgo
        return Senal(
            direccion=DireccionTrade.SHORT,
            precio_entrada=precio,
            stop_loss=sl,
            take_profit=tp,
            estrategia=self.nombre,
            confianza=0.72,
            etiqueta=f"REV-S c6={'✓'} body={str_short:.0f}%",
        )

    # ──────────────────────────────────────────────────────
    # Pivotes para Liquidity Sweep
    # ──────────────────────────────────────────────────────

    def _actualizar_pivotes(self, high: pd.Series, low: pd.Series):
        n = len(high)
        half = self.liq_length
        if n < half * 2 + 1:
            return

        pivot_idx = n - 1 - half
        ph_candidate = high.iloc[pivot_idx]
        is_ph = ph_candidate == high.iloc[max(0, pivot_idx - half): pivot_idx + half + 1].max()
        if is_ph and (not self._ph_prices or abs(ph_candidate - self._ph_prices[-1]) > 0.01):
            self._ph_prices.append(ph_candidate)
            self._ph_bar.append(self._bar_global)

        pl_candidate = low.iloc[pivot_idx]
        is_pl = pl_candidate == low.iloc[max(0, pivot_idx - half): pivot_idx + half + 1].min()
        if is_pl and (not self._pl_prices or abs(pl_candidate - self._pl_prices[-1]) > 0.01):
            self._pl_prices.append(pl_candidate)
            self._pl_bar.append(self._bar_global)

        # Mantener solo los últimos 200 pivotes
        if len(self._ph_prices) > 200:
            self._ph_prices.pop(0); self._ph_bar.pop(0)
        if len(self._pl_prices) > 200:
            self._pl_prices.pop(0); self._pl_bar.pop(0)

    def _hubo_sweep_buyside(self) -> bool:
        """¿El precio barrió un pivot high en las últimas sweepWindow barras?"""
        ventana = self.sweep_window
        for i, bar in enumerate(reversed(self._ph_bar)):
            if self._bar_global - bar > ventana + 1:
                break
            if i < len(self._ph_prices):
                return True
        return False

    def _hubo_sweep_sellside(self) -> bool:
        for i, bar in enumerate(reversed(self._pl_bar)):
            if self._bar_global - bar > self.sweep_window + 1:
                break
            if i < len(self._pl_prices):
                return True
        return False

    # ──────────────────────────────────────────────────────
    # Fuerza de cuerpo (replicación exacta del Pine Script)
    # ──────────────────────────────────────────────────────

    @staticmethod
    def _body_strength_short(o: float, c: float, l: float) -> float:
        """cuerpo=(open-close), mecha=(close-low), fuerza=cuerpo/(cuerpo+mecha)×100"""
        body = o - c
        wick = c - l
        den  = body + wick
        return (body / den) * 100 if body > 0 and den > 0 else 0.0

    @staticmethod
    def _body_strength_long(o: float, c: float, h: float) -> float:
        """cuerpo=(close-open), mecha=(high-close), fuerza=cuerpo/(cuerpo+mecha)×100"""
        body = c - o
        wick = h - c
        den  = body + wick
        return (body / den) * 100 if body > 0 and den > 0 else 0.0
