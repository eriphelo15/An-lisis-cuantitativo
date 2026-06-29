"""
Optimizador de parámetros para la estrategia Reversal [EAO].
Usa señales vectorizadas (fast path) + simulación simplificada de trades.
"""

import itertools
import numpy as np
import pandas as pd
from dataclasses import dataclass
from tabulate import tabulate
from typing import List


# ──────────────────────────────────────────────────────────
# Señales vectorizadas (sin bar-by-bar, mucho más rápido)
# ──────────────────────────────────────────────────────────

def _atr_vectorial(df: pd.DataFrame, periodo: int = 14) -> pd.Series:
    h, l, pc = df["high"], df["low"], df["close"].shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(span=periodo, adjust=False).mean()


def calcular_senales(
    df: pd.DataFrame,
    near_term: int,
    long_term: int,
    use_time: bool,
    start_hour: int,
    start_min: int,
    end_hour: int,
    end_min: int,
    use_body: bool,
    body_pct: float,
    long_only: bool,
) -> tuple[pd.Series, pd.Series]:
    """
    Computa buy_signals y sell_signals como Series booleanas sobre el DataFrame completo.
    Replica la lógica Pine Script c1-c6 de forma vectorizada.
    """
    close = df["close"]
    open_ = df["open"]
    high  = df["high"]
    low   = df["low"]

    # Indicadores de estructura
    near_low  = low.rolling(near_term).min()
    near_high = high.rolling(near_term).max()
    long_low  = low.rolling(long_term).min()
    long_high = high.rolling(long_term).max()

    # Patrón base LONG
    c1 = (close.shift(1) < open_.shift(1)) & (close > open_)
    c2 = close > open_.shift(1)
    c3 = (
        (long_low.shift(1) > near_low) |
        (long_low.shift(2) > near_low) |
        (long_low.shift(3) > near_low) |
        (long_low.shift(4) > near_low)
    )
    buy_base = c1 & c2 & c3

    # Patrón base SHORT
    c4 = (close.shift(1) > open_.shift(1)) & (close < open_)
    c5 = close < open_.shift(1)
    c6 = (
        (long_high.shift(1) < near_high) |
        (long_high.shift(2) < near_high) |
        (long_high.shift(3) < near_high) |
        (long_high.shift(4) < near_high)
    )
    sell_base = c4 & c5 & c6

    # Filtro de sesión
    if use_time:
        start_mins = start_hour * 60 + start_min
        end_mins   = end_hour   * 60 + end_min
        curr_mins  = df.index.hour * 60 + df.index.minute
        in_sess    = (curr_mins >= start_mins) & (curr_mins < end_mins)
        buy_base   = buy_base  & in_sess
        sell_base  = sell_base & in_sess

    # Filtro de cuerpo dominante
    if use_body:
        body_bull = (close - open_).clip(lower=0)
        wick_bull = (high - close).clip(lower=0)
        den_bull  = body_bull + wick_bull
        str_bull  = np.where(den_bull > 0, body_bull / den_bull * 100, 0)

        body_bear = (open_ - close).clip(lower=0)
        wick_bear = (close - low).clip(lower=0)
        den_bear  = body_bear + wick_bear
        str_bear  = np.where(den_bear > 0, body_bear / den_bear * 100, 0)

        buy_base  = buy_base  & (pd.Series(str_bull, index=df.index) >= body_pct)
        sell_base = sell_base & (pd.Series(str_bear, index=df.index) >= body_pct)

    if long_only:
        sell_base = pd.Series(False, index=df.index)

    return buy_base.fillna(False), sell_base.fillna(False)


# ──────────────────────────────────────────────────────────
# Simulación rápida de trades
# ──────────────────────────────────────────────────────────

def simular_trades(
    df: pd.DataFrame,
    buy_signals: pd.Series,
    sell_signals: pd.Series,
    sl_atr_mult: float,
    tp_rr: float,
    riesgo_por_trade: float = 0.003,
    capital_inicial: float = 25_000,
    tick_valor: float = 0.50,
    tick_size: float = 0.25,
    comision: float = 1.24,
) -> dict:
    atr = _atr_vectorial(df, 14)
    capital = capital_inicial
    pico    = capital_inicial

    trades_win  = 0
    trades_loss = 0
    pnl_total   = 0.0
    max_dd      = 0.0
    pnl_wins    = 0.0
    pnl_losses  = 0.0

    en_trade = False
    dir_trade = None
    sl = tp = 0.0

    for i in range(1, len(df)):
        bar = df.iloc[i]

        # Gestionar trade abierto
        if en_trade:
            if dir_trade == "long":
                if bar["low"] <= sl:
                    pnl = sl - df["close"].iloc[i - 1]
                    hit = "loss"
                elif bar["high"] >= tp:
                    pnl = tp - df["close"].iloc[i - 1]
                    hit = "win"
                else:
                    continue
            else:
                if bar["high"] >= sl:
                    pnl = df["close"].iloc[i - 1] - sl
                    hit = "loss"
                elif bar["low"] <= tp:
                    pnl = df["close"].iloc[i - 1] - tp
                    hit = "win"
                else:
                    continue

            valor_punto = tick_valor / tick_size
            contratos   = max(1, int(capital * riesgo_por_trade / (abs(df["close"].iloc[i - 1] - sl) * valor_punto)))
            pnl_usd     = pnl * valor_punto * contratos - comision * contratos

            capital    += pnl_usd
            pnl_total  += pnl_usd
            en_trade    = False

            if pnl_usd > 0:
                trades_win += 1
                pnl_wins   += pnl_usd
            else:
                trades_loss += 1
                pnl_losses  += abs(pnl_usd)

            pico   = max(pico, capital)
            max_dd = max(max_dd, pico - capital)
            continue

        if capital <= 0:
            break

        # Nueva señal
        idx = df.index[i]
        precio  = bar["close"]
        atr_val = atr.iloc[i]
        if pd.isna(atr_val) or atr_val == 0:
            continue

        if buy_signals.get(idx, False):
            sl_price = min(bar["low"], precio - sl_atr_mult * atr_val)
            riesgo   = precio - sl_price
            if riesgo <= 0:
                continue
            sl = sl_price
            tp = precio + tp_rr * riesgo
            dir_trade = "long"
            en_trade  = True

        elif sell_signals.get(idx, False):
            sl_price = max(bar["high"], precio + sl_atr_mult * atr_val)
            riesgo   = sl_price - precio
            if riesgo <= 0:
                continue
            sl = sl_price
            tp = precio - tp_rr * riesgo
            dir_trade = "short"
            en_trade  = True

    total_trades = trades_win + trades_loss
    win_rate     = trades_win / total_trades if total_trades else 0
    profit_factor = pnl_wins / pnl_losses if pnl_losses > 0 else float("inf")

    return {
        "pnl":          pnl_total,
        "trades":       total_trades,
        "win_rate":     win_rate,
        "profit_factor": profit_factor,
        "max_drawdown": max_dd,
        "capital_final": capital,
    }


# ──────────────────────────────────────────────────────────
# Grid Search
# ──────────────────────────────────────────────────────────

@dataclass
class ResultadoOptimizacion:
    params: dict
    metricas: dict
    score: float


def optimizar(
    df: pd.DataFrame,
    capital_inicial: float = 25_000,
    top_n: int = 10,
) -> List[ResultadoOptimizacion]:
    """
    Corre grid search sobre los parámetros principales de la estrategia.
    Retorna los top_n mejores conjuntos de parámetros.
    """
    grid = {
        "near_term":  [2, 3, 5],
        "long_term":  [20, 35, 50, 75],
        "end_hour":   [10, 11, 12],
        "end_min":    [0, 30],
        "use_body":   [False, True],
        "body_pct":   [60, 70],
        "sl_atr_mult": [1.0, 1.5, 2.0],
        "tp_rr":      [1.5, 2.0, 2.5],
    }

    combinaciones = list(itertools.product(*grid.values()))
    claves = list(grid.keys())
    total  = len(combinaciones)
    resultados: List[ResultadoOptimizacion] = []

    print(f"\n[OPT] Evaluando {total:,} combinaciones de parámetros...")

    for k, combo in enumerate(combinaciones):
        params = dict(zip(claves, combo))

        # Saltar si body_pct pero use_body=False (parámetro irrelevante, reducir duplicados)
        if not params["use_body"] and params["body_pct"] != 60:
            continue

        try:
            buy_sig, sell_sig = calcular_senales(
                df,
                near_term  = params["near_term"],
                long_term  = params["long_term"],
                use_time   = True,
                start_hour = 9,
                start_min  = 30,
                end_hour   = params["end_hour"],
                end_min    = params["end_min"],
                use_body   = params["use_body"],
                body_pct   = params["body_pct"],
                long_only  = False,
            )

            metricas = simular_trades(
                df, buy_sig, sell_sig,
                sl_atr_mult   = params["sl_atr_mult"],
                tp_rr         = params["tp_rr"],
                capital_inicial = capital_inicial,
            )

            # Score compuesto: premia PF alto, WR alto, drawdown bajo, mínimo 5 trades
            if metricas["trades"] < 5:
                continue

            pf  = min(metricas["profit_factor"], 5.0)  # cap para no inflar
            wr  = metricas["win_rate"]
            dd  = max(metricas["max_drawdown"], 1)
            pnl = metricas["pnl"]

            score = (pf * 0.35 + wr * 0.30 + (pnl / capital_inicial) * 0.25
                     - (dd / capital_inicial) * 0.10)

            resultados.append(ResultadoOptimizacion(
                params=params, metricas=metricas, score=score
            ))

        except Exception:
            continue

        if (k + 1) % 100 == 0:
            print(f"[OPT]   {k + 1}/{total} procesadas...", end="\r")

    resultados.sort(key=lambda x: x.score, reverse=True)
    print(f"\n[OPT] Completado. {len(resultados):,} combinaciones válidas.")
    return resultados[:top_n]


def imprimir_optimizacion(resultados: List[ResultadoOptimizacion]):
    print("\n" + "─" * 80)
    print("  REVERSAL [EAO] — TOP CONFIGURACIONES POR SCORE COMPUESTO")
    print("─" * 80)
    print("  Score = 35%×PF + 30%×WR + 25%×ROI − 10%×DD/Capital\n")

    filas = []
    for i, r in enumerate(resultados, 1):
        p  = r.params
        m  = r.metricas
        pf = m["profit_factor"]
        filas.append([
            i,
            p["near_term"],
            p["long_term"],
            f"{p['end_hour']:02d}:{p['end_min']:02d}",
            "Sí" if p["use_body"] else "No",
            f"{p['body_pct']:.0f}%" if p["use_body"] else "—",
            p["sl_atr_mult"],
            p["tp_rr"],
            m["trades"],
            f"{m['win_rate'] * 100:.1f}%",
            f"{pf:.2f}" if pf != float('inf') else "∞",
            f"${m['pnl']:+,.0f}",
            f"${m['max_drawdown']:,.0f}",
            f"{r.score:.3f}",
        ])

    print(tabulate(
        filas,
        headers=[
            "#", "Near", "Long", "Fin Ses", "Cuerpo", "Body%",
            "SL×ATR", "TP:R", "Trades", "WR%", "PF",
            "P&L", "MaxDD", "Score"
        ],
        tablefmt="rounded_outline",
    ))

    # Destacar la mejor
    best = resultados[0]
    bp   = best.params
    bm   = best.metricas
    print(f"""
  ★  MEJOR CONFIGURACIÓN
     · nearTerm   = {bp['near_term']}
     · longTerm   = {bp['long_term']}
     · Sesión     = 09:30 → {bp['end_hour']:02d}:{bp['end_min']:02d} ET
     · Filtro cuerpo = {'Sí (' + str(bp['body_pct']) + '%)' if bp['use_body'] else 'No'}
     · SL         = {bp['sl_atr_mult']}× ATR
     · TP         = {bp['tp_rr']}:1 R:R
     · Trades     = {bm['trades']}
     · Win Rate   = {bm['win_rate'] * 100:.1f}%
     · P&L        = ${bm['pnl']:+,.0f}
     · Max DD     = ${bm['max_drawdown']:,.0f}
""")
    print("─" * 80)
