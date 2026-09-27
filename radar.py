"""
RADAR MEMES — registra tokens nuevos de Solana y mide qué pasa con ellos.

Uso:
  python radar.py ciclo                 # escanear + seguimiento + informe (una vez)
  python radar.py ciclo --cada 300      # repetir cada 5 min (en tu ordenador)
  python radar.py escanear
  python radar.py seguimiento
  python radar.py informe

Los datos se guardan en --datos (por defecto datos_radar/).
"""

import argparse
import time

from radar_memes import analisis, escaner, seguimiento
from radar_memes.almacen import Almacen


def main():
    parser = argparse.ArgumentParser(description="Radar de memecoins de Solana",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__)
    parser.add_argument("accion", choices=["ciclo", "escanear", "seguimiento", "informe"])
    parser.add_argument("--datos", default="datos_radar", help="Carpeta de datos")
    parser.add_argument("--cada", type=int, default=0,
                        help="Repetir cada N segundos (0 = una sola vez)")
    parser.add_argument("--sin-rugcheck", action="store_true")
    args = parser.parse_args()

    almacen = Almacen(args.datos)
    while True:
        if args.accion in ("ciclo", "escanear"):
            escaner.escanear(almacen, con_rugcheck=not args.sin_rugcheck)
        if args.accion in ("ciclo", "seguimiento"):
            seguimiento.seguir(almacen)
        if args.accion in ("ciclo", "informe"):
            analisis.escribir(almacen)
        if not args.cada:
            break
        time.sleep(args.cada)


if __name__ == "__main__":
    main()
