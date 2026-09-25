"""Hermes — línea de comandos.

  python -m hermes ficha SNDL [--fecha 2025-03-14]
  python -m hermes descargar --desde 2024-10-01 --hasta 2026-09-24
  python -m hermes runners --desde 2024-10-01 --hasta 2026-09-24
  python -m hermes estudio --desde 2024-10-01 --hasta 2026-09-24
  python -m hermes halts
"""

import argparse
import sys
from datetime import date, datetime, time
from pathlib import Path

import requests

from hermes.config import Config, cargar_config
from hermes.http import ClienteHTTP, NoEncontrado
from hermes.inteligencia import finra
from hermes.inteligencia.ficha import construir_ficha, formatear
from hermes.inteligencia.halts import halts_actuales
from hermes.inteligencia.sec.cliente import LLAMADAS_POR_SEGUNDO, ClienteSEC
from hermes.inteligencia.sec.filings import ET
from hermes.laboratorio.costos import ModeloCostos
from hermes.laboratorio.estudio import agregar_costos, agregar_retornos, resumir, tasa_ofertas
from hermes.laboratorio.pipeline import evaluar_dilucion
from hermes.universo.almacen import cargar_diario, dias_habiles, existe_diario, guardar_diario
from hermes.universo.massive import LLAMADAS_POR_SEGUNDO_GRATIS, ClienteMassive
from hermes.universo.runners import CriteriosRunner, detectar_runners


def _cache(config: Config, nombre: str) -> Path:
    return config.directorio_datos / "cache" / nombre


def _cliente_sec(config: Config) -> ClienteSEC:
    return ClienteSEC(ClienteHTTP(config.exigir_sec(), LLAMADAS_POR_SEGUNDO, _cache(config, "sec")))


def _cliente_massive(config: Config) -> ClienteMassive:
    http = ClienteHTTP("hermes", LLAMADAS_POR_SEGUNDO_GRATIS, _cache(config, "massive"))
    return ClienteMassive(http, config.exigir_massive(), config.massive_base_url)


def _http_publico(config: Config, nombre: str) -> ClienteHTTP:
    return ClienteHTTP(config.sec_user_agent or "hermes", 2, _cache(config, nombre))


def _fecha(texto: str) -> date:
    return date.fromisoformat(texto)


def cmd_ficha(args, config: Config) -> None:
    sec = _cliente_sec(config)
    ticker = args.ticker.upper()
    momento = datetime.combine(args.fecha, time(9, 30), tzinfo=ET) if args.fecha else datetime.now(ET)

    cik = None
    if args.fecha and config.massive_api_key:
        cik = _cliente_massive(config).cik_de_ticker(ticker, args.fecha)
    cik = cik or sec.mapa_tickers().get(ticker)
    if cik is None:
        sys.exit(f"No encontré el CIK de {ticker}. Si está deslistada, usa --fecha y configura MASSIVE_API_KEY.")

    try:
        short = finra.short_interest(_http_publico(config, "finra"), ticker, momento.date())
    except (requests.RequestException, NoEncontrado, ValueError) as error:
        print(f"(sin short interest de FINRA: {error})\n")
        short = None

    ficha = construir_ficha(ticker, sec.empresa(cik), sec.companyfacts(cik), momento, short)
    print(formatear(ficha))


def cmd_descargar(args, config: Config) -> None:
    massive = _cliente_massive(config)
    pendientes = [d for d in dias_habiles(args.desde, args.hasta) if not existe_diario(config.directorio_datos, d)]
    print(f"{len(pendientes)} días por descargar (plan gratuito: ~12 s por día).")
    for i, dia in enumerate(pendientes, start=1):
        df = massive.diario_agrupado(dia)
        guardar_diario(config.directorio_datos, dia, df)
        print(f"  {dia}  {len(df):>6} acciones  ({i}/{len(pendientes)})")


def _runners(args, config: Config):
    diario = cargar_diario(config.directorio_datos, args.desde, args.hasta)
    if diario.empty:
        sys.exit("No hay datos diarios en ese rango. Corre primero: python -m hermes descargar")
    return diario, detectar_runners(diario, CriteriosRunner())


def cmd_runners(args, config: Config) -> None:
    _, runners = _runners(args, config)
    salida = config.directorio_datos / "resultados" / f"runners_{args.desde}_{args.hasta}.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)
    runners.to_csv(salida, index=False)
    print(f"{len(runners)} runners detectados ({runners['ticker'].nunique()} tickers). Guardado en {salida}")


def cmd_estudio(args, config: Config) -> None:
    diario, runners = _runners(args, config)
    sec = _cliente_sec(config)
    mapa_sec = sec.mapa_tickers()
    massive = _cliente_massive(config) if config.massive_api_key else None

    def resolver_cik(ticker: str, fecha: date) -> int | None:
        # primero por fecha (Massive): un ticker actual puede pertenecer hoy a otra empresa
        if massive:
            cik = massive.cik_de_ticker(ticker, fecha)
            if cik:
                return cik
        return mapa_sec.get(ticker)

    print(f"{len(runners)} runners. Evaluando dilución con datos conocidos antes de cada apertura...")
    eventos = evaluar_dilucion(runners, sec, resolver_cik, progreso=print)
    eventos = agregar_costos(agregar_retornos(eventos, diario), ModeloCostos())
    eventos["anio"] = [f.year for f in eventos["fecha"]]

    evaluados = eventos[eventos["nivel_dilucion"].isin(["bajo", "medio", "alto"])]
    por_nivel = resumir(evaluados, ["nivel_dilucion"])
    por_anio = resumir(evaluados, ["anio", "nivel_dilucion"])
    ofertas = tasa_ofertas(evaluados, ["nivel_dilucion"])

    carpeta = config.directorio_datos / "resultados" / f"estudio_{args.desde}_{args.hasta}"
    carpeta.mkdir(parents=True, exist_ok=True)
    eventos.to_csv(carpeta / "eventos.csv", index=False)
    por_nivel.to_csv(carpeta / "resumen_por_nivel.csv", index=False)
    por_anio.to_csv(carpeta / "resumen_por_anio.csv", index=False)
    ofertas.to_csv(carpeta / "ofertas.csv", index=False)

    cobertura = eventos["nivel_dilucion"].value_counts().to_string()
    informe = "\n\n".join([
        f"ESTUDIO: runners de small caps vs. riesgo de dilución ({args.desde} a {args.hasta})",
        f"Cobertura de eventos por nivel:\n{cobertura}",
        "¿Ofrecieron acciones en la semana siguiente?\n" + ofertas.to_string(index=False),
        "Retornos por nivel (corto_neto_medio = ganancia de un corto después de costos; "
        "|t| > 2 sugiere un efecto que no es ruido)\n" + por_nivel.round(4).to_string(index=False),
        "Por año (estabilidad del efecto)\n" + por_anio.round(4).to_string(index=False),
    ])
    (carpeta / "informe.txt").write_text(informe, encoding="utf-8")
    print("\n" + informe + f"\n\nArchivos en {carpeta}")


def cmd_halts(args, config: Config) -> None:
    halts = halts_actuales(_http_publico(config, "nasdaq"))
    if not halts:
        print("No hay halts publicados ahora.")
    for h in halts:
        estado = "ACTIVO" if h.activo else f"reanudó {h.reanudacion_trading:%H:%M:%S}"
        print(f"{h.inicio:%Y-%m-%d %H:%M:%S}  {h.ticker:<6} {h.codigo:<5} {estado:<18} {h.nombre}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="hermes", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("ficha", help="Ficha de inteligencia de un ticker")
    p.add_argument("ticker")
    p.add_argument("--fecha", type=_fecha, help="Ficha tal como se conocía antes de la apertura de ese día")
    p.set_defaults(fn=cmd_ficha)

    for nombre, fn, ayuda in [
        ("descargar", cmd_descargar, "Descarga barras diarias de todo el mercado (Massive)"),
        ("runners", cmd_runners, "Detecta runners en los datos descargados"),
        ("estudio", cmd_estudio, "Estudio: ¿los runners con dilución pendiente se comportan distinto?"),
    ]:
        p = sub.add_parser(nombre, help=ayuda)
        p.add_argument("--desde", type=_fecha, required=True)
        p.add_argument("--hasta", type=_fecha, required=True)
        p.set_defaults(fn=fn)

    p = sub.add_parser("halts", help="Halts publicados hoy por Nasdaq")
    p.set_defaults(fn=cmd_halts)

    args = parser.parse_args()
    try:
        args.fn(args, cargar_config())
    except RuntimeError as error:
        sys.exit(f"Error: {error}")


if __name__ == "__main__":
    main()
