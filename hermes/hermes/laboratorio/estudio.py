import math

import pandas as pd

from hermes.laboratorio.costos import ModeloCostos

HORIZONTES_DIAS = (1, 3, 5)
COLUMNAS_RETORNO = ("ret_intradia",) + tuple(f"ret_{k}d" for k in HORIZONTES_DIAS)


def agregar_retornos(eventos: pd.DataFrame, diario: pd.DataFrame) -> pd.DataFrame:
    """ret_intradia: de la apertura al cierre del día del evento.
    ret_Nd: del cierre del día del evento al cierre N sesiones después (en las que la acción operó).
    """
    base = diario.sort_values(["ticker", "fecha"])[["ticker", "fecha", "cierre"]].copy()
    cierres = base.groupby("ticker")["cierre"]
    for k in HORIZONTES_DIAS:
        base[f"cierre_{k}d"] = cierres.shift(-k)
    ev = eventos.merge(base.drop(columns="cierre"), on=["ticker", "fecha"], how="left")
    ev["ret_intradia"] = ev["cierre"] / ev["apertura"] - 1
    for k in HORIZONTES_DIAS:
        ev[f"ret_{k}d"] = ev[f"cierre_{k}d"] / ev["cierre"] - 1
    return ev


def agregar_costos(eventos: pd.DataFrame, modelo: ModeloCostos) -> pd.DataFrame:
    ev = eventos.copy()
    ev["costo"] = [modelo.costo_ida_vuelta(p, dv) for p, dv in zip(ev["apertura"], ev["dolar_volumen"])]
    return ev


def _estadisticas(retornos: pd.Series, costos: pd.Series) -> dict:
    validos = retornos.notna()
    r, c = retornos[validos], costos[validos]
    n = len(r)
    corto_neto = -r - c
    desviacion = corto_neto.std(ddof=1) if n > 1 else math.nan
    return {
        "n": n,
        "retorno_medio": r.mean(),
        "retorno_mediano": r.median(),
        "pct_bajistas": (r < 0).mean() if n else math.nan,
        "corto_neto_medio": corto_neto.mean(),
        "t_corto_neto": corto_neto.mean() / (desviacion / math.sqrt(n)) if n > 1 and desviacion > 0 else math.nan,
    }


def resumir(eventos: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Una fila por grupo y horizonte. `corto_neto_medio` es lo que habría ganado un corto, ya descontados costos.

    Requiere la columna `costo` (ver `agregar_costos`).
    """
    filas = []
    for clave, grupo in eventos.groupby(por, dropna=False):
        clave = clave if isinstance(clave, tuple) else (clave,)
        for columna in COLUMNAS_RETORNO:
            filas.append({
                **dict(zip(por, clave)),
                "horizonte": columna.removeprefix("ret_"),
                **_estadisticas(grupo[columna], grupo["costo"]),
            })
    return pd.DataFrame(filas)


def tasa_ofertas(eventos: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    return (
        eventos.groupby(por, dropna=False)["oferta_5d"]
        .agg(n="size", ofertas="sum", tasa="mean")
        .reset_index()
    )
