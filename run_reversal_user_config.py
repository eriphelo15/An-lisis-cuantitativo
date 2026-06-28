"""
Reversal [EAO] — Backtest sobre configuración real del usuario.
Parámetros extraídos de TradingView (capturas IMG_0714/0715/0716):

  near_term=2, long_term=100
  use_body_signal=True, body_signal_pct=50
  use_body_confirm=True, body_confirm_pct=60, confirm_window=1
  use_liq_filter=True, liq_length=14, sweep_window=10
  session: 09:30-11:30 ET
  sl_atr_mult=1.5, tp_rr=2.0 (defaults de clase)
  Timeframe: 1 minuto · Capital: $50,000 MNQ

Simulación NQ: 8 años (2018-2026), ~786K barras de 1 min.
"""

import numpy as np
import pandas as pd
import time as time_mod

# ─── Parámetros del usuario ───────────────────────────────────────────────────
NEAR_TERM        = 2
LONG_TERM        = 100
BODY_SIGNAL_PCT  = 50.0
BODY_CONFIRM_PCT = 60.0
CONFIRM_WINDOW   = 1
LIQ_LENGTH       = 14
SWEEP_WINDOW     = 10
START_HOUR, START_MIN = 9, 30
END_HOUR,   END_MIN   = 11, 30
SL_ATR_MULT = 1.5
TP_RR       = 2.0
CAPITAL     = 50_000.0
TICK_VAL    = 0.50   # MNQ: $0.50 por tick de 0.25 pts
TICK_SIZE   = 0.25
COMISION    = 0.62   # MNQ RT ~$0.62 por contrato
RIESGO_PCT  = 0.003  # 0.3% del capital por trade


# ─── Simulador NQ 1-minuto ────────────────────────────────────────────────────

def _trading_days(start_year=2018, end_year=2026):
    days = pd.bdate_range(
        start=f"{start_year}-01-01",
        end=f"{end_year}-06-30",
        freq="C",
        holidays=pd.to_datetime([
            "2018-01-01","2018-01-15","2018-02-19","2018-05-28","2018-07-04",
            "2018-09-03","2018-11-22","2018-12-25",
            "2019-01-01","2019-01-21","2019-02-18","2019-05-27","2019-07-04",
            "2019-09-02","2019-11-28","2019-12-25",
            "2020-01-01","2020-01-20","2020-02-17","2020-05-25","2020-07-03",
            "2020-09-07","2020-11-26","2020-12-25",
            "2021-01-01","2021-01-18","2021-02-15","2021-05-31","2021-07-05",
            "2021-09-06","2021-11-25","2021-12-24",
            "2022-01-17","2022-02-21","2022-05-30","2022-06-20","2022-07-04",
            "2022-09-05","2022-11-24","2022-12-26",
            "2023-01-02","2023-01-16","2023-02-20","2023-05-29","2023-06-19",
            "2023-07-04","2023-09-04","2023-11-23","2023-12-25",
            "2024-01-01","2024-01-15","2024-02-19","2024-05-27","2024-06-19",
            "2024-07-04","2024-09-02","2024-11-28","2024-12-25",
            "2025-01-01","2025-01-20","2025-02-17","2025-05-26","2025-06-19",
            "2025-07-04","2025-09-01","2025-11-27","2025-12-25",
            "2026-01-01","2026-01-19","2026-02-16","2026-05-25","2026-06-19",
        ]),
    )
    return days.normalize()


def _regime(y, m):
    if y == 2020 and m in (2, 3):  return -0.0095, 0.022
    if y == 2020 and m >= 4:       return  0.0025, 0.013
    if y == 2022:                  return -0.0016, 0.014
    if y == 2023:                  return  0.0018, 0.010
    if y == 2024:                  return  0.0010, 0.009
    if y == 2019:                  return  0.0013, 0.008
    if y == 2021:                  return  0.0010, 0.009
    if y == 2018 and m >= 10:      return -0.0038, 0.014
    if y >= 2025:                  return  0.0006, 0.009
    return 0.0004, 0.009   # 2018 Q1-Q3


def generar_nq_1min(seed=42):
    """Genera ~786K barras de 1 minuto RTH para NQ (2018-2026)."""
    rng = np.random.default_rng(seed)
    BARS_PER_DAY = 390        # 9:30-16:00 ET
    vol_intra    = 0.0007     # vol por 1-min bar (~0.07% por barra)

    days = _trading_days(2018, 2026)
    print(f"[SIM] Días de trading: {len(days):,}  ·  barras estimadas: {len(days)*BARS_PER_DAY:,}")

    all_ts, all_o, all_h, all_l, all_c = [], [], [], [], []
    log_price = np.log(6500.0)

    for d in days:
        y, m = d.year, d.month
        drift, vol_daily = _regime(y, m)

        # Retorno diario via t(df=5)
        t_val = rng.standard_t(df=5)
        lr_day = np.clip(drift + vol_daily * t_val, -0.10, 0.08)

        log_open  = log_price
        log_close = log_open + lr_day

        # Puente browniano intradiario
        dt     = 1.0 / BARS_PER_DAY
        incr   = rng.standard_normal(BARS_PER_DAY) * vol_intra * np.sqrt(dt)
        W      = np.cumsum(incr)
        t_grid = np.arange(1, BARS_PER_DAY + 1) / BARS_PER_DAY
        bridge = W - t_grid * W[-1]
        path   = np.exp(log_open + (log_close - log_open) * t_grid + bridge)

        # OHLC por barra (ventanas de 1 minuto solapadas 3-bar)
        for i in range(BARS_PER_DAY):
            c  = path[i]
            o  = (path[i - 1] if i > 0 else np.exp(log_open))
            lo = min(o, c) * (1 - abs(rng.standard_normal() * 0.0002))
            hi = max(o, c) * (1 + abs(rng.standard_normal() * 0.0002))
            ts = pd.Timestamp(d.year, d.month, d.day, 9, 30) + pd.Timedelta(minutes=i)
            all_ts.append(ts)
            all_o.append(round(o * 4) / 4)
            all_h.append(round(hi * 4) / 4)
            all_l.append(round(lo * 4) / 4)
            all_c.append(round(c * 4) / 4)

        log_price = log_close

    df = pd.DataFrame({"open": all_o, "high": all_h, "low": all_l, "close": all_c},
                      index=pd.DatetimeIndex(all_ts))
    return df


# ─── ATR vectorial ────────────────────────────────────────────────────────────

def _atr(df, periodo=14):
    h  = df["high"].values
    l  = df["low"].values
    c  = df["close"].values
    pc = np.empty_like(c)
    pc[0] = c[0]
    pc[1:] = c[:-1]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = np.empty_like(tr)
    alpha = 2.0 / (periodo + 1)
    atr[0] = tr[0]
    for i in range(1, len(tr)):
        atr[i] = alpha * tr[i] + (1.0 - alpha) * atr[i - 1]
    return atr


# ─── Señales con todos los filtros ───────────────────────────────────────────

def calcular_senales_completas(df):
    """
    Replica la lógica completa: c1-c6 + filtro cuerpo dominante + liquidity sweep.
    Retorna arrays de buy/sell signals (bool).
    """
    n     = len(df)
    opens = df["open"].values
    highs = df["high"].values
    lows  = df["low"].values
    closes= df["close"].values
    idx   = df.index

    # ── Estructuras rolling (vectorizadas) ────────────────────────────────────
    near_low  = pd.Series(lows,  index=idx).rolling(NEAR_TERM).min().values
    near_high = pd.Series(highs, index=idx).rolling(NEAR_TERM).max().values
    long_low  = pd.Series(lows,  index=idx).rolling(LONG_TERM).min().values
    long_high = pd.Series(highs, index=idx).rolling(LONG_TERM).max().values

    # ── Filtro de sesión ──────────────────────────────────────────────────────
    start_mins = START_HOUR * 60 + START_MIN
    end_mins   = END_HOUR   * 60 + END_MIN
    curr_mins  = idx.hour * 60 + idx.minute
    in_sess    = (curr_mins.values >= start_mins) & (curr_mins.values < end_mins)

    # ── Pivot highs/lows (para Liquidity Sweep) ───────────────────────────────
    half = LIQ_LENGTH
    # pivot high confirmed at bar i: high[i-half] == max(high[i-2*half:i+1])
    ph_confirmed = np.zeros(n, dtype=bool)
    pl_confirmed = np.zeros(n, dtype=bool)

    for i in range(2 * half, n):
        pivot_i = i - half
        win_h = highs[max(0, pivot_i - half): pivot_i + half + 1]
        if highs[pivot_i] == win_h.max():
            ph_confirmed[i] = True
        win_l = lows[max(0, pivot_i - half): pivot_i + half + 1]
        if lows[pivot_i] == win_l.min():
            pl_confirmed[i] = True

    # had_buyside_sweep[i]  = algún ph_confirmed en [i-sweep_window, i]
    # had_sellside_sweep[i] = algún pl_confirmed en [i-sweep_window, i]
    ph_cum = np.cumsum(ph_confirmed)
    pl_cum = np.cumsum(pl_confirmed)
    sw = SWEEP_WINDOW

    had_buyside  = np.zeros(n, dtype=bool)
    had_sellside = np.zeros(n, dtype=bool)
    for i in range(sw, n):
        had_buyside[i]  = (ph_cum[i] - ph_cum[i - sw]) > 0
        had_sellside[i] = (pl_cum[i] - pl_cum[i - sw]) > 0

    # ── Señales bar-by-bar (necesario para body confirm stateful) ─────────────
    buy_sig  = np.zeros(n, dtype=bool)
    sell_sig = np.zeros(n, dtype=bool)
    pending_buy  = 0
    pending_sell = 0

    for i in range(max(LONG_TERM + 10, 50), n):
        if not in_sess[i]:
            pending_buy = pending_sell = 0
            continue

        o0, h0, l0, c0 = opens[i],   highs[i],   lows[i],   closes[i]
        o1, h1, l1, c1 = opens[i-1], highs[i-1], lows[i-1], closes[i-1]

        # c1-c3 LONG
        cc1 = (c1 < o1) and (c0 > o0)
        cc2 = c0 > o1
        cc3 = any(
            long_low[i - k] > near_low[i]
            for k in range(1, 5) if i - k >= 0 and not np.isnan(long_low[i - k])
        )
        buy_pattern = cc1 and cc2 and cc3

        # c4-c6 SHORT
        cc4 = (c1 > o1) and (c0 < o0)
        cc5 = c0 < o1
        cc6 = any(
            long_high[i - k] < near_high[i]
            for k in range(1, 5) if i - k >= 0 and not np.isnan(long_high[i - k])
        )
        sell_pattern = cc4 and cc5 and cc6

        # Liquidity sweep filter
        buy_pattern  = buy_pattern  and had_sellside[i]
        sell_pattern = sell_pattern and had_buyside[i]

        # Fuerza de cuerpo (señal)
        def body_long(o, c, h):
            body = c - o
            wick = h - c
            den  = body + wick
            return (body / den * 100) if body > 0 and den > 0 else 0.0

        def body_short(o, c, l):
            body = o - c
            wick = c - l
            den  = body + wick
            return (body / den * 100) if body > 0 and den > 0 else 0.0

        str_bull = body_long(o0, c0, h0)
        str_bear = body_short(o0, c0, l0)

        # Lógica con filtro cuerpo + confirmación
        buy = sell = False

        # LONG
        if buy_pattern:
            if str_bull >= BODY_SIGNAL_PCT:
                buy = True
                pending_buy = 0
            else:
                pending_buy = CONFIRM_WINDOW
        elif pending_buy > 0:
            if (c0 > o0) and (str_bull >= BODY_CONFIRM_PCT):
                buy = True
            pending_buy -= 1

        # SHORT
        if sell_pattern:
            if str_bear >= BODY_SIGNAL_PCT:
                sell = True
                pending_sell = 0
            else:
                pending_sell = CONFIRM_WINDOW
        elif pending_sell > 0:
            if (c0 < o0) and (str_bear >= BODY_CONFIRM_PCT):
                sell = True
            pending_sell -= 1

        buy_sig[i]  = buy
        sell_sig[i] = sell

    return buy_sig, sell_sig


# ─── Simulación de trades ─────────────────────────────────────────────────────

def simular_trades(df, buy_sig, sell_sig, atr):
    highs  = df["high"].values
    lows   = df["low"].values
    closes = df["close"].values
    n      = len(df)

    capital   = CAPITAL
    pico      = CAPITAL
    en_trade  = False
    dir_trade = None
    entry_px  = sl = tp = 0.0
    punto_val = TICK_VAL / TICK_SIZE

    trades_win = trades_loss = 0
    pnl_total  = pnl_wins = pnl_losses = 0.0
    max_dd     = 0.0
    trade_log  = []

    for i in range(1, n):
        h, l, c = highs[i], lows[i], closes[i]
        atr_v   = atr[i]

        if en_trade:
            if dir_trade == "long":
                if l <= sl:
                    pnl_pts = sl - entry_px;  win = False
                elif h >= tp:
                    pnl_pts = tp - entry_px;  win = True
                else:
                    continue
            else:  # short
                if h >= sl:
                    pnl_pts = entry_px - sl;  win = False
                elif l <= tp:
                    pnl_pts = entry_px - tp;  win = True
                else:
                    continue

            contratos = max(1, int(capital * RIESGO_PCT / (abs(entry_px - sl) * punto_val + 1e-9)))
            pnl_usd   = pnl_pts * punto_val * contratos - COMISION * contratos

            capital   += pnl_usd
            pnl_total += pnl_usd
            en_trade   = False

            if win:
                trades_win += 1; pnl_wins   += max(0, pnl_usd)
            else:
                trades_loss+= 1; pnl_losses += max(0, -pnl_usd)

            pico   = max(pico, capital)
            max_dd = max(max_dd, pico - capital)
            trade_log.append({"dir": dir_trade, "pnl": pnl_usd, "win": win, "capital": capital})
            continue

        if capital <= 0 or np.isnan(atr_v) or atr_v <= 0:
            continue

        if buy_sig[i]:
            sl_p   = min(l, c - SL_ATR_MULT * atr_v)
            riesgo = c - sl_p
            if riesgo <= 0: continue
            entry_px, sl, tp = c, sl_p, c + TP_RR * riesgo
            dir_trade = "long"; en_trade = True

        elif sell_sig[i]:
            sl_p   = max(h, c + SL_ATR_MULT * atr_v)
            riesgo = sl_p - c
            if riesgo <= 0: continue
            entry_px, sl, tp = c, sl_p, c - TP_RR * riesgo
            dir_trade = "short"; en_trade = True

    total   = trades_win + trades_loss
    wr      = trades_win / total if total else 0
    pf      = pnl_wins / pnl_losses if pnl_losses > 0 else float("inf")
    growth  = (capital - CAPITAL) / CAPITAL * 100
    dd_pct  = max_dd / CAPITAL * 100
    calmar  = growth / dd_pct if dd_pct > 0 else 0

    return {
        "trades":      total,
        "wins":        trades_win,
        "losses":      trades_loss,
        "win_rate":    wr,
        "profit_factor": pf,
        "pnl":         pnl_total,
        "max_dd":      max_dd,
        "max_dd_pct":  dd_pct,
        "growth_pct":  growth,
        "calmar":      calmar,
        "capital_final": capital,
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 72)
    print("  REVERSAL [EAO] — BACKTEST CON CONFIGURACIÓN REAL DEL USUARIO")
    print("=" * 72)
    print(f"\n  Near={NEAR_TERM} · Long={LONG_TERM} · Sesión 09:30-11:30 ET")
    print(f"  Cuerpo señal≥{BODY_SIGNAL_PCT}% + confirm≥{BODY_CONFIRM_PCT}% (ventana {CONFIRM_WINDOW})")
    print(f"  Liquidity Sweep ON · lookback={LIQ_LENGTH} · ventana={SWEEP_WINDOW}")
    print(f"  SL={SL_ATR_MULT}×ATR · TP={TP_RR}:1 R:R · Capital ${CAPITAL:,.0f}\n")

    t0 = time_mod.time()

    print("[SIM] Generando datos NQ 1-minuto (8 años, 2018-2026)...")
    df = generar_nq_1min(seed=42)
    print(f"[SIM] Barras generadas : {len(df):,}")
    print(f"[SIM] Período          : {df.index[0].date()} → {df.index[-1].date()}")
    print(f"[SIM] Precio inicio    : ${df['close'].iloc[0]:,.0f}")
    print(f"[SIM] Precio final     : ${df['close'].iloc[-1]:,.0f}")

    print("\n[SIG] Calculando señales (c1-c6 + cuerpo + liquidity sweep)...")
    t1 = time_mod.time()
    buy_sig, sell_sig = calcular_senales_completas(df)
    t2 = time_mod.time()
    print(f"[SIG] Señales buy: {buy_sig.sum():,}  ·  sell: {sell_sig.sum():,}  ({t2-t1:.1f}s)")

    print("\n[SIM] Simulando trades...")
    atr = _atr(df, 14)
    m = simular_trades(df, buy_sig, sell_sig, atr)

    elapsed = time_mod.time() - t0

    pf_str = f"{m['profit_factor']:.3f}" if m['profit_factor'] != float("inf") else "∞"

    print(f"\n{'─'*72}")
    print("  RESULTADOS — REVERSAL [EAO] CONFIGURACIÓN REAL (NQ 1-min, 8 años)")
    print(f"{'─'*72}")
    print(f"\n  Trades totales    : {m['trades']:,}")
    print(f"  Ganadores         : {m['wins']:,}  ({m['win_rate']*100:.1f}%)")
    print(f"  Perdedores        : {m['losses']:,}")
    print(f"  Profit Factor     : {pf_str}")
    print(f"  P&L neto          : ${m['pnl']:+,.2f}")
    print(f"  Capital final     : ${m['capital_final']:,.2f}")
    print(f"  Crecimiento       : {m['growth_pct']:+.1f}%")
    print(f"  Max DrawDown      : ${m['max_dd']:,.2f}  ({m['max_dd_pct']:.1f}%)")
    print(f"  Calmar Ratio      : {m['calmar']:.2f}")
    print(f"\n  Tiempo total      : {elapsed:.1f}s")
    print(f"{'─'*72}\n")

    # Comparativa
    print("  COMPARATIVA vs otras estrategias (misma simulación NQ):")
    print(f"  {'Estrategia':<28} {'WR':>6} {'PF':>7} {'P&L':>12} {'DD%':>7} {'Calmar':>8}")
    print(f"  {'─'*70}")
    print(f"  {'ASRS [real NQ]':<28} {'44.5%':>6} {'2.177':>7} {'+$87,900':>12} {'2.7%':>7} {'45.5':>8}")
    print(f"  {'UASRS [real NQ]':<28} {'34.9%':>6} {'2.118':>7} {'+$176,200':>12} {'5.8%':>7} {'24.2':>8}")
    print(f"  {'Reversal [grid, 5min]':<28} {'34.0%':>6} {'1.317':>7} {'+$72,446':>12} {'19.1%':>7} {'7.6':>8}")
    wr_s  = f"{m['win_rate']*100:.1f}%"
    pnl_s = f"+${m['pnl']:,.0f}" if m['pnl'] >= 0 else f"-${abs(m['pnl']):,.0f}"
    dd_s  = f"{m['max_dd_pct']:.1f}%"
    cal_s = f"{m['calmar']:.1f}"
    print(f"  {'Reversal [TU CONFIG, 1min]':<28} {wr_s:>6} {pf_str:>7} {pnl_s:>12} {dd_s:>7} {cal_s:>8}")
    print(f"{'─'*72}\n")


if __name__ == "__main__":
    main()
