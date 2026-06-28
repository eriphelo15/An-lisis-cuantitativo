"""
Generador de reportes de performance para el sistema ARES.
Incluye análisis específico de progreso en el challenge de prop firms.
"""

import numpy as np
from tabulate import tabulate
from .backtester import ResultadoBacktest


def imprimir_reporte(resultado: ResultadoBacktest):
    r = resultado
    trades = r.trades_cerrados

    _separador()
    print("  ARES QUANT — REPORTE DE PERFORMANCE")
    _separador()

    # ── Métricas generales ──────────────────────────
    print("\n  MÉTRICAS GENERALES\n")
    metricas = [
        ["Capital inicial",     f"${r.capital_inicial:,.0f}"],
        ["Capital final",       f"${r.capital_final:,.0f}"],
        ["P&L total",           _fmt_pnl(r.pnl_total)],
        ["Total trades",        len(trades)],
        ["Win rate",            f"{r.win_rate * 100:.1f}%"],
        ["Profit factor",       f"{r.profit_factor:.2f}"],
        ["Sharpe ratio",        f"{r.sharpe_ratio:.2f}"],
        ["Max drawdown",        f"${r.max_drawdown:,.0f}"],
        ["R:R promedio",        f"1:{r.promedio_rr:.2f}"],
    ]
    print(tabulate(metricas, tablefmt="simple"))

    # ── Análisis por estrategia ──────────────────────
    print("\n\n  BREAKDOWN POR ESTRATEGIA\n")
    estrategias = {}
    for t in trades:
        if t.estrategia not in estrategias:
            estrategias[t.estrategia] = {"trades": [], "wins": 0, "pnl": 0.0}
        estrategias[t.estrategia]["trades"].append(t)
        if t.resultado == "win":
            estrategias[t.estrategia]["wins"] += 1
        estrategias[t.estrategia]["pnl"] += t.pnl_usd

    rows_est = []
    for nombre, data in estrategias.items():
        total = len(data["trades"])
        wr = data["wins"] / total if total > 0 else 0
        rows_est.append([
            nombre,
            total,
            f"{wr * 100:.1f}%",
            _fmt_pnl(data["pnl"]),
        ])

    print(tabulate(rows_est, headers=["Estrategia", "Trades", "Win%", "P&L"],
                   tablefmt="simple"))

    # ── Estado del challenge ─────────────────────────
    print("\n\n  ESTADO DEL CHALLENGE PROP FIRM\n")
    reglas = r.reglas
    pnl = r.pnl_total
    obj = reglas.objetivo_ganancia
    dd_max = reglas.drawdown_maximo
    dd_actual = r.max_drawdown
    progreso = min(100.0, (pnl / obj) * 100) if obj > 0 else 0

    estado_challenge = "EN PROGRESO"
    if pnl >= obj:
        estado_challenge = "✓ CHALLENGE SUPERADO"
    elif dd_actual >= dd_max:
        estado_challenge = "✗ CHALLENGE FALLIDO (drawdown)"

    challenge = [
        ["Compañía",                reglas.nombre],
        ["Estado",                  estado_challenge],
        ["Objetivo de ganancia",    f"${obj:,.0f}"],
        ["P&L actual",              _fmt_pnl(pnl)],
        ["Progreso",                f"{progreso:.1f}%  {'█' * int(progreso/10)}{'░' * (10 - int(progreso/10))}"],
        ["Drawdown actual",         f"${dd_actual:,.0f}"],
        ["Límite drawdown",         f"${dd_max:,.0f}"],
        ["Margen drawdown restante",f"${dd_max - dd_actual:,.0f}"],
    ]
    print(tabulate(challenge, tablefmt="simple"))

    # ── Top 5 trades ────────────────────────────────
    if trades:
        print("\n\n  ÚLTIMOS 10 TRADES\n")
        rows_t = []
        for t in trades[-10:]:
            rows_t.append([
                t.id,
                t.estrategia,
                t.direccion.value,
                t.fecha_entrada.strftime("%m/%d %H:%M"),
                f"{t.precio_entrada:,.2f}",
                f"{t.precio_salida:,.2f}" if t.precio_salida else "-",
                _fmt_pnl(t.pnl_usd),
                t.resultado.upper(),
            ])
        print(tabulate(
            rows_t,
            headers=["ID", "Estrategia", "Dir", "Entrada", "Px En", "Px Sal", "P&L", "Res"],
            tablefmt="simple",
        ))

    # ── Proyección ──────────────────────────────────
    if len(trades) >= 5:
        print("\n\n  PROYECCIÓN ESTADÍSTICA\n")
        dias_totales = len(set(t.fecha_entrada.date() for t in trades))
        if dias_totales > 0:
            pnl_por_dia = pnl / dias_totales
            dias_para_objetivo = (
                (obj - pnl) / pnl_por_dia if pnl_por_dia > 0 else float("inf")
            )
            prob_exito = _monte_carlo(trades, obj, dd_max)
            proyeccion = [
                ["P&L promedio por día",   _fmt_pnl(pnl_por_dia)],
                ["Días para completar obj",f"{dias_para_objetivo:.0f} días" if dias_para_objetivo != float('inf') else "N/A"],
                ["Prob. de éxito (1000 sim)",f"{prob_exito * 100:.1f}%"],
            ]
            print(tabulate(proyeccion, tablefmt="simple"))

    _separador()
    print()


def _monte_carlo(trades, objetivo: float, drawdown_max: float, simulaciones: int = 1000) -> float:
    """Simulación Monte Carlo para estimar probabilidad de superar el challenge."""
    pnls = [t.pnl_usd for t in trades]
    if not pnls:
        return 0.0

    exitos = 0
    for _ in range(simulaciones):
        equity = 0.0
        pico = 0.0
        for _ in range(len(pnls) * 3):  # simular 3x más trades
            muestra = np.random.choice(pnls)
            equity += muestra
            pico = max(pico, equity)
            dd = pico - equity
            if dd >= drawdown_max:
                break
            if equity >= objetivo:
                exitos += 1
                break

    return exitos / simulaciones


def _fmt_pnl(valor: float) -> str:
    signo = "+" if valor >= 0 else ""
    return f"{signo}${valor:,.2f}"


def _separador():
    print("─" * 60)
