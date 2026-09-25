import math
from dataclasses import asdict

import pandas as pd

from maestros.backtest.modelos import Trade


def a_tabla(trades: list[Trade]) -> pd.DataFrame:
    filas = [{**asdict(t), "r_bruto": t.r_bruto, "r_neto": t.r_neto, "pnl_neto": t.pnl_neto} for t in trades]
    df = pd.DataFrame(filas)
    if not df.empty:
        df["anio"] = [h.year for h in df["hora_entrada"]]
    return df


def _drawdown_maximo(r: pd.Series) -> float:
    acumulado = r.cumsum()
    return float((acumulado.cummax() - acumulado).max()) if len(r) else 0.0


def _estadisticas(grupo: pd.DataFrame) -> dict:
    r = grupo.sort_values("hora_entrada")["r_neto"]
    n = len(r)
    desviacion = r.std(ddof=1) if n > 1 else math.nan
    return {
        "trades": n,
        "tasa_acierto": float((r > 0).mean()) if n else math.nan,
        "r_medio_neto": float(r.mean()) if n else math.nan,
        "t_estadistico": float(r.mean() / (desviacion / math.sqrt(n))) if n > 1 and desviacion > 0 else math.nan,
        "r_total_neto": float(r.sum()),
        "drawdown_max_r": _drawdown_maximo(r),
    }


def resumen(tabla: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Métricas en R (múltiplos del riesgo inicial), ya descontados los costos.

    t_estadistico > 2 sugiere que el resultado medio no es ruido.
    """
    if tabla.empty:
        return pd.DataFrame()
    filas = []
    for clave, grupo in tabla.groupby(por, dropna=False):
        clave = clave if isinstance(clave, tuple) else (clave,)
        filas.append({**dict(zip(por, clave)), **_estadisticas(grupo)})
    return pd.DataFrame(filas)
