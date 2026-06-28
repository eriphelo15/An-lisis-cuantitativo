"""
ARES QUANT — Sistema de trading automatizado para prop firms de futuros.

Uso:
  python main.py --cuenta 25k --ticker NQ=F --periodo 60d
  python main.py --cuenta 10k --ticker NQ=F --periodo 30d --intervalo 5m
  python main.py --lista-cuentas

Cuentas disponibles: 10k | 25k | 50k | 100k | 150k
"""

import argparse
import sys

from sistema_ares.config import TRADEIFY, BOT_CONFIG
from sistema_ares.backtester import Backtester
from sistema_ares.reporte import imprimir_reporte


def main():
    parser = argparse.ArgumentParser(
        description="ARES QUANT — Trading Bot para Prop Firms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--cuenta", default="25k",
        choices=list(TRADEIFY.keys()),
        help="Tamaño de cuenta Tradeify (default: 25k)",
    )
    parser.add_argument(
        "--ticker", default="NQ=F",
        help="Ticker de yfinance para datos (default: NQ=F)",
    )
    parser.add_argument(
        "--periodo", default="60d",
        help="Período histórico: 7d, 30d, 60d (default: 60d)",
    )
    parser.add_argument(
        "--intervalo", default="5m",
        choices=["1m", "2m", "5m", "15m"],
        help="Intervalo de barras (default: 5m)",
    )
    parser.add_argument(
        "--lista-cuentas", action="store_true",
        help="Mostrar cuentas disponibles y sus reglas",
    )
    parser.add_argument(
        "--simular", action="store_true",
        help="Usar datos simulados (no requiere conexión a internet)",
    )

    args = parser.parse_args()

    if args.lista_cuentas:
        _mostrar_cuentas()
        return

    reglas = TRADEIFY[args.cuenta]

    print(f"""
╔══════════════════════════════════════════════════════╗
║           ARES QUANT — PROP FIRM TRADING BOT         ║
╠══════════════════════════════════════════════════════╣
║  Cuenta    : {reglas.nombre:<39}║
║  Capital   : ${reglas.tamano_cuenta:>8,.0f}                              ║
║  Objetivo  : ${reglas.objetivo_ganancia:>8,.0f}                              ║
║  Lim. diario: ${reglas.limite_perdida_diaria:>7,.0f}                             ║
║  Drawdown  : ${reglas.drawdown_maximo:>8,.0f}                              ║
║  Estrategia: {', '.join(BOT_CONFIG.estrategias_activas):<39}║
╚══════════════════════════════════════════════════════╝
""")

    try:
        backtester = Backtester(reglas=reglas, config=BOT_CONFIG)
        resultado = backtester.ejecutar(
            ticker=args.ticker,
            periodo=args.periodo,
            intervalo=args.intervalo,
            simular=args.simular,
        )
        imprimir_reporte(resultado)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


def _mostrar_cuentas():
    from tabulate import tabulate
    filas = []
    for key, r in TRADEIFY.items():
        filas.append([
            key,
            f"${r.tamano_cuenta:,.0f}",
            f"${r.objetivo_ganancia:,.0f}",
            f"${r.limite_perdida_diaria:,.0f}",
            f"${r.drawdown_maximo:,.0f}",
            f"{r.profit_split*100:.0f}%",
        ])
    print("\nCuentas Tradeify disponibles:\n")
    print(tabulate(
        filas,
        headers=["Cuenta", "Capital", "Objetivo", "Lim. Diario", "DD Máx", "Split"],
        tablefmt="rounded_outline",
    ))
    print()


if __name__ == "__main__":
    main()
