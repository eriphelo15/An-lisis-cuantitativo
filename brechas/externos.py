"""Datos diarios externos (FRED/CBOE) alineados SIN mirar el futuro: para el día de trading D se usa el cierre del día hábil anterior."""
import os
import numpy as np, pandas as pd
EXT = "/home/user/data/ext"


def _cboe(n):
    d = pd.read_csv(os.path.join(EXT, f"{n}_cboe.csv")); d.columns = [c.upper() for c in d.columns]
    d["DATE"] = pd.to_datetime(d.DATE); col = "CLOSE" if "CLOSE" in d else d.columns[-1]
    return d.set_index("DATE")[col].astype(float).rename(n)


def _fred(n):
    d = pd.read_csv(os.path.join(EXT, f"{n}.csv")); d.columns = ["DATE", n]
    d["DATE"] = pd.to_datetime(d.DATE); d[n] = pd.to_numeric(d[n], errors="coerce")
    return d.set_index("DATE")[n]


def externos(fechas):
    X = pd.concat([_cboe("VIX"), _cboe("VIX9D"), _cboe("VIX3M"), _cboe("VVIX"), _fred("VXNCLS"), _fred("DGS10"), _fred("DGS2"),
                   _fred("DTWEXBGS")], axis=1).sort_index().ffill()
    X["ratio_9d"] = X.VIX9D / X.VIX; X["ratio_3m"] = X.VIX / X.VIX3M
    X["dvix"] = X.VIX.pct_change(); X["vix_pct252"] = X.VIX.rolling(252).rank(pct=True)
    X["vix_z20"] = (X.VIX - X.VIX.rolling(20).mean()) / X.VIX.rolling(20).std()
    X["d10y"] = X.DGS10.diff(); X["d2y"] = X.DGS2.diff(); X["dusd"] = X.DTWEXBGS.pct_change()
    # alinear: valor conocido antes del día D = último dato con fecha < D
    f = pd.DatetimeIndex(fechas)
    idx = X.index.searchsorted(f, side="left") - 1
    out = X.iloc[np.clip(idx, 0, None)].copy(); out.index = f
    out[idx < 0] = np.nan
    return out
