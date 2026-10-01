"""Funciones comunes OBLIGATORIAS para los estudios (PROTOCOLO_ESTUDIOS.md, 1-oct-2026).
Cada una existe porque un estudio se equivocó al hacerlo a mano:
- dia_habil_anterior: pd.offsets.BDay ignora los festivos (GNPX 21-ene-2020 y UUU 2-sep-2025 perdían el 8-K del viernes por la tarde).
- precios_reales: la lista de splits de Yahoo omite contra-splits (CRIS, SVRE) y a veces lista splits recientes que aún no aplica (ALP,
  CPOP, YAAS) → precio exacto de Massive si existe; si no, calibrado por acción; si no, Yahoo (ver res_29/res_30)."""
import numpy as np
import pandas as pd

D = "/home/user/data/smallcaps"
_CAL = None


def calendario():
    global _CAL
    if _CAL is None:
        cal = pd.DatetimeIndex(pd.read_csv(f"{D}/calendario_mercado.csv").iloc[:, 0])   # días con datos (2015 → fin de los datos)
        # después del último día con datos: días laborables menos los festivos de la bolsa del Radar (FERIADOS de lista_diaria)
        import os, sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herramientas"))
        from lista_diaria import FERIADOS
        extra = [d for d in pd.bdate_range(cal.max() + pd.Timedelta(days=1), "2027-12-31") if d.date().isoformat() not in FERIADOS]
        _CAL = cal.append(pd.DatetimeIndex(extra)).sort_values()
    return _CAL


def dia_habil_anterior(fechas):
    """Día de mercado real anterior (con festivos) para una fecha o una serie de fechas."""
    cal = calendario()
    f = pd.to_datetime(fechas)
    if isinstance(f, pd.Timestamp):
        return cal[cal.searchsorted(f) - 1]
    return pd.Series(cal[cal.searchsorted(pd.DatetimeIndex(f)) - 1], index=getattr(fechas, "index", None))


def precios_reales():
    """sym, fecha, precio_real, metodo ('exacto' Massive 1 min / 'calibrado' / 'yahoo'), dudoso, ambiguo (8 604 gappers)."""
    import subprocess, os
    aqui = os.path.dirname(os.path.abspath(__file__))
    X = pd.read_csv(os.path.join(aqui, "res_18_precio_real.csv"))
    P = pd.read_csv(os.path.join(aqui, "res_29_precios.csv"))
    assert (X.sym.values == P.sym.values).all()
    out = X[["sym", "fecha", "ambiguo"]].copy()
    out["precio_T"] = P.precio_T.values
    out["precio_yahoo"] = X.precio.values
    out["dudoso"] = P.dudoso.values
    return out
