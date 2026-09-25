"""Maestros — línea de comandos.

Orden recomendado para el primer backtest:
  python -m maestros verificar-noticias
  python -m maestros descargar-diario    --desde 2024-10-01 --hasta 2026-09-24
  python -m maestros candidatos          --desde 2024-10-01 --hasta 2026-09-24
  python -m maestros descargar-minutos   --desde 2024-10-01 --hasta 2026-09-24
  python -m maestros descargar-noticias  --desde 2024-10-01 --hasta 2026-09-24
  python -m maestros backtest            --desde 2024-10-01 --hasta 2026-09-24
  python -m maestros halts
"""

import argparse
import sys
from datetime import date, datetime

import pandas as pd

from maestros.backtest.costos import ModeloCostos
from maestros.backtest.ejecutar import candidatos, ejecutar_backtest
from maestros.backtest.reporte import a_tabla, resumen
from maestros.config import Config, cargar_config
from maestros.datos import alpaca as alpaca_mod
from maestros.datos.almacen import Almacen
from maestros.datos.alpaca import ClienteAlpaca
from maestros.datos.calendario import CIERRE, FIN_POSTMERCADO, INICIO_PREMERCADO, dias_habiles, dias_habiles_previos, en_et
from maestros.datos.massive import LLAMADAS_POR_SEGUNDO_GRATIS, ClienteMassive
from maestros.http import ClienteHTTP, NoEncontrado
from maestros.informacion.ficha import Ficha, construir_ficha
from maestros.informacion.financieros import Financieros
from maestros.informacion.mercado import halts_actuales
from maestros.informacion.sec import LLAMADAS_POR_SEGUNDO as SEC_POR_SEGUNDO
from maestros.informacion.sec import ClienteSEC
from maestros.traders.cameron import CameronLiteral

DIAS_VOLUMEN_NORMAL = 20
ESTRATEGIAS = {"cameron": CameronLiteral}


def _cache(config: Config, nombre: str):
    return config.directorio_datos / "cache" / nombre


def _alpaca(config: Config) -> ClienteAlpaca:
    key, secret = config.exigir_alpaca()
    http = ClienteHTTP("maestros", alpaca_mod.LLAMADAS_POR_SEGUNDO, _cache(config, "alpaca"),
                       headers_extra=ClienteAlpaca.headers(key, secret))
    return ClienteAlpaca(http)


def _candidatos(almacen: Almacen, desde: date, hasta: date) -> pd.DataFrame:
    # se cargan días extra antes de `desde` para calcular el cierre previo y el volumen promedio
    diario = almacen.cargar_diario(dias_habiles_previos(desde, 30)[0], hasta)
    if diario.empty:
        sys.exit("No hay barras diarias en ese rango. Corre primero: python -m maestros descargar-diario")
    lista = candidatos(diario)
    return lista[(lista["fecha"] >= desde) & (lista["fecha"] <= hasta)].reset_index(drop=True)


def cmd_descargar_diario(args, config: Config, almacen: Almacen) -> None:
    http = ClienteHTTP("maestros", LLAMADAS_POR_SEGUNDO_GRATIS, _cache(config, "massive"))
    massive = ClienteMassive(http, config.exigir_massive(), config.massive_base_url)
    # 30 días hábiles extra antes de --desde para tener cierre previo y promedios desde el primer día
    pendientes = [d for d in dias_habiles(dias_habiles_previos(args.desde, 30)[0], args.hasta)
                  if not almacen.tiene_diario(d)]
    print(f"{len(pendientes)} días por descargar (plan gratuito: ~12 s por día).")
    for i, dia in enumerate(pendientes, start=1):
        df = massive.diario_agrupado(dia)
        almacen.guardar_diario(dia, df)
        print(f"  {dia}  {len(df):>6} acciones  ({i}/{len(pendientes)})")


def cmd_candidatos(args, config: Config, almacen: Almacen) -> None:
    lista = _candidatos(almacen, args.desde, args.hasta)
    salida = almacen.carpeta_resultados("candidatos") / f"{args.desde}_{args.hasta}.csv"
    lista.to_csv(salida, index=False)
    print(f"{len(lista)} días candidatos ({lista['ticker'].nunique()} tickers). Guardado en {salida}")


def cmd_descargar_minutos(args, config: Config, almacen: Almacen) -> None:
    alpaca = _alpaca(config)
    lista = _candidatos(almacen, args.desde, args.hasta)
    print(f"{len(lista)} candidatos: se descargan su día y los {DIAS_VOLUMEN_NORMAL} días hábiles previos.")
    for i, fila in enumerate(lista.itertuples(index=False), start=1):
        dias = dias_habiles_previos(fila.fecha, DIAS_VOLUMEN_NORMAL) + [fila.fecha]
        faltan = [d for d in dias if not almacen.tiene_minutos(d, fila.ticker)]
        if not faltan:
            continue
        barras = alpaca.barras_minuto([fila.ticker], en_et(faltan[0], INICIO_PREMERCADO),
                                      en_et(faltan[-1], FIN_POSTMERCADO))
        por_dia = {d: g for d, g in barras.groupby([h.date() for h in barras["hora"]])} if not barras.empty else {}
        for dia in faltan:
            almacen.guardar_minutos(dia, fila.ticker, por_dia.get(dia, barras.iloc[0:0]))
        print(f"  {fila.fecha} {fila.ticker:<6} {len(barras):>6} barras  ({i}/{len(lista)})")


def cmd_descargar_noticias(args, config: Config, almacen: Almacen) -> None:
    alpaca = _alpaca(config)
    lista = _candidatos(almacen, args.desde, args.hasta)
    for fecha, grupo in lista.groupby("fecha"):
        if almacen.tiene_noticias(fecha):
            continue
        desde = en_et(dias_habiles_previos(fecha, 1)[0], CIERRE)
        noticias = alpaca.noticias(desde, en_et(fecha, CIERRE), sorted(grupo["ticker"].unique()))
        almacen.guardar_noticias(fecha, noticias)
        print(f"  {fecha}  {len(noticias):>4} noticias para {grupo['ticker'].nunique()} tickers")


def cmd_verificar_noticias(args, config: Config, almacen: Almacen) -> None:
    """Sin noticias históricas no se puede probar el pilar de catalizador: esto se verifica primero."""
    alpaca = _alpaca(config)
    print("Noticias de AAPL en la primera semana hábil de enero de cada año:")
    for anio in range(2015, datetime.now().year + 1):
        n = len(alpaca.noticias(en_et(date(anio, 1, 5), INICIO_PREMERCADO), en_et(date(anio, 1, 9), CIERRE), ["AAPL"]))
        print(f"  {anio}: {n} noticias")


def _fichas(config: Config, almacen: Almacen):
    sec = ClienteSEC(ClienteHTTP(config.exigir_sec(), SEC_POR_SEGUNDO, _cache(config, "sec")))
    mapa = sec.mapa_tickers()
    empresas: dict[int, tuple] = {}
    noticias_por_fecha: dict[date, list] = {}
    sin_cik: set[str] = set()

    def obtener(ticker: str, fecha: date) -> Ficha | None:
        if fecha not in noticias_por_fecha:
            noticias_por_fecha[fecha] = almacen.cargar_noticias(fecha)
        noticias = noticias_por_fecha[fecha]
        cik = mapa.get(ticker)
        if cik is None:
            sin_cik.add(ticker)
            return Ficha(ticker, Financieros(None, None, None), None, tuple(n for n in noticias if ticker in n.tickers))
        if cik not in empresas:
            try:
                empresas[cik] = (list(sec.empresa(cik).filings), sec.companyfacts(cik))
            except NoEncontrado:
                empresas[cik] = ([], {})
        filings, facts = empresas[cik]
        return construir_ficha(ticker, en_et(fecha, INICIO_PREMERCADO), filings, facts, noticias)

    return obtener, sin_cik


def cmd_backtest(args, config: Config, almacen: Almacen) -> None:
    estrategia = ESTRATEGIAS[args.estrategia]()
    lista = _candidatos(almacen, args.desde, args.hasta)
    obtener_ficha, sin_cik = _fichas(config, almacen)
    print(f"Backtest de {estrategia.nombre} sobre {len(lista)} días candidatos...")
    trades, cobertura = ejecutar_backtest(estrategia, lista, almacen, obtener_ficha, ModeloCostos(),
                                          dias_volumen_normal=DIAS_VOLUMEN_NORMAL, progreso=print)
    tabla = a_tabla(trades)
    carpeta = almacen.carpeta_resultados(f"backtest_{estrategia.nombre}_{args.desde}_{args.hasta}")
    tabla.to_csv(carpeta / "trades.csv", index=False)

    secciones = [
        f"BACKTEST {estrategia.nombre} ({args.desde} a {args.hasta})",
        "Cobertura de datos:\n" + "\n".join(f"  {k}: {v}" for k, v in sorted(cobertura.items()))
        + f"\n  tickers sin CIK en la SEC (probablemente deslistados; float desconocido): {len(sin_cik)}",
    ]
    if tabla.empty:
        secciones.append("Ningún trade. Revisa la cobertura: sin minutos, sin volumen normal o sin ficha no hay pilares.")
    else:
        por_setup, por_anio = resumen(tabla, ["setup"]), resumen(tabla, ["anio", "setup"])
        por_setup.to_csv(carpeta / "resumen_por_setup.csv", index=False)
        por_anio.to_csv(carpeta / "resumen_por_anio.csv", index=False)
        secciones += [
            "Resultados en R, netos de costos (t > 2 sugiere que no es ruido):\n"
            + resumen(tabla, ["direccion"]).round(3).to_string(index=False),
            "Por setup:\n" + por_setup.round(3).to_string(index=False),
            "Por año (estabilidad):\n" + por_anio.round(3).to_string(index=False),
        ]
    informe = "\n\n".join(secciones)
    (carpeta / "informe.txt").write_text(informe, encoding="utf-8")
    print("\n" + informe + f"\n\nArchivos en {carpeta}")


def cmd_halts(args, config: Config, almacen: Almacen) -> None:
    halts = halts_actuales(ClienteHTTP("maestros", 1))
    if not halts:
        print("No hay halts publicados ahora.")
    for h in halts:
        estado = "ACTIVO" if h.activo else f"reanudó {h.reanudacion:%H:%M:%S}"
        print(f"{h.inicio:%Y-%m-%d %H:%M:%S}  {h.ticker:<6} {h.codigo:<5} {estado}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="maestros", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    for nombre, fn in [("descargar-diario", cmd_descargar_diario), ("candidatos", cmd_candidatos),
                       ("descargar-minutos", cmd_descargar_minutos), ("descargar-noticias", cmd_descargar_noticias),
                       ("backtest", cmd_backtest)]:
        p = sub.add_parser(nombre)
        p.add_argument("--desde", type=date.fromisoformat, required=True)
        p.add_argument("--hasta", type=date.fromisoformat, required=True)
        if nombre == "backtest":
            p.add_argument("--estrategia", choices=sorted(ESTRATEGIAS), default="cameron")
        p.set_defaults(fn=fn)
    sub.add_parser("verificar-noticias").set_defaults(fn=cmd_verificar_noticias)
    sub.add_parser("halts").set_defaults(fn=cmd_halts)

    args = parser.parse_args()
    config = cargar_config()
    try:
        args.fn(args, config, Almacen(config.directorio_datos))
    except RuntimeError as error:
        sys.exit(f"Error: {error}")


if __name__ == "__main__":
    main()
