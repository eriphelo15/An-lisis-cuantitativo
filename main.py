"""
ARES QUANT — Sistema de trading automatizado para prop firms de futuros.

Uso:
  python main.py --cuenta 25k --simular
  python main.py --cuenta 25k --estrategia reversal --simular
  python main.py --cuenta 25k --optimizar --simular
  python main.py --lista-cuentas

Estrategias: orb | vwap | reversal | todas (default)
Cuentas    : 10k | 25k | 50k | 100k | 150k
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
    parser.add_argument("--cuenta", default="25k", choices=list(TRADEIFY.keys()),
                        help="Tamaño de cuenta Tradeify (default: 25k)")
    parser.add_argument("--ticker", default="NQ=F",
                        help="Ticker yfinance (default: NQ=F)")
    parser.add_argument("--periodo", default="60d",
                        help="Período histórico: 7d, 30d, 60d (default: 60d)")
    parser.add_argument("--intervalo", default="5m", choices=["1m", "2m", "5m", "15m"],
                        help="Intervalo de barras (default: 5m)")
    parser.add_argument("--estrategia", default="todas",
                        choices=["orb", "vwap", "reversal", "todas"],
                        help="Estrategia a usar (default: todas)")
    parser.add_argument("--simular", action="store_true",
                        help="Usar datos simulados (sin internet)")
    parser.add_argument("--optimizar", action="store_true",
                        help="Correr grid search de parámetros en Reversal [EAO]")
    parser.add_argument("--lista-cuentas", action="store_true",
                        help="Mostrar cuentas y reglas de Tradeify")

    args = parser.parse_args()

    if args.lista_cuentas:
        _mostrar_cuentas()
        return

    reglas = TRADEIFY[args.cuenta]
    _banner(reglas, args.estrategia)

    # ── Cargar datos una sola vez ──────────────────────
    from sistema_ares.backtester import Backtester
    bt = Backtester(reglas=reglas, config=BOT_CONFIG, estrategia=args.estrategia)
    datos = bt._cargar_datos(args.ticker, args.periodo, args.intervalo, args.simular)

    # ── Modo optimización ──────────────────────────────
    if args.optimizar:
        from sistema_ares.optimizador import optimizar, imprimir_optimizacion
        print(f"\n[ARES] Optimizando Reversal [EAO] sobre {len(datos)} barras...")
        resultados = optimizar(datos, capital_inicial=reglas.tamano_cuenta)
        imprimir_optimizacion(resultados)
        return

    # ── Modo backtest normal (reusar datos ya cargados) ─
    try:
        bt._ejecutar_simulacion(datos)
        from sistema_ares.backtester import ResultadoBacktest
        resultado = ResultadoBacktest(
            trades=bt.trades,
            equity_curve=bt._equity_curve,
            fechas_equity=bt._fechas_equity,
            reglas=reglas,
            capital_inicial=reglas.tamano_cuenta,
            capital_final=bt.gestor_riesgo.capital_actual,
        )
        imprimir_reporte(resultado)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


def _banner(reglas, estrategia: str):
    est_label = estrategia.upper()
    print(f"""
╔══════════════════════════════════════════════════════╗
║           ARES QUANT — PROP FIRM TRADING BOT         ║
╠══════════════════════════════════════════════════════╣
║  Cuenta    : {reglas.nombre:<39}║
║  Capital   : ${reglas.tamano_cuenta:>8,.0f}                              ║
║  Objetivo  : ${reglas.objetivo_ganancia:>8,.0f}                              ║
║  Lim. diario: ${reglas.limite_perdida_diaria:>7,.0f}                             ║
║  Drawdown  : ${reglas.drawdown_maximo:>8,.0f}                              ║
║  Estrategia: {est_label:<39}║
╚══════════════════════════════════════════════════════╝
""")


def _mostrar_cuentas():
    from tabulate import tabulate
    filas = []
    for key, r in TRADEIFY.items():
        filas.append([key, f"${r.tamano_cuenta:,.0f}", f"${r.objetivo_ganancia:,.0f}",
                      f"${r.limite_perdida_diaria:,.0f}", f"${r.drawdown_maximo:,.0f}",
                      f"{r.profit_split*100:.0f}%"])
    print("\nCuentas Tradeify disponibles:\n")
    print(tabulate(filas,
                   headers=["Cuenta", "Capital", "Objetivo", "Lim. Diario", "DD Máx", "Split"],
                   tablefmt="rounded_outline"))
    print()


if __name__ == "__main__":
    main()
