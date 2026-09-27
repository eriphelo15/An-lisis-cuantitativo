"""Evalúa la versión 'dejar correr' con el COSTO ACTUAL expresado en % del ATR (nivel de precio de hoy),
por periodo e instrumento, y por régimen de volatilidad (ATR 14d relativo a su media de 100 días, conocido al abrir)."""
import numpy as np, pandas as pd, os, itertools, importlib
from hougaard import INSTR, PERIODOS
vi = importlib.import_module("22_vi_usuario"); pb = importlib.import_module("23_pullback_tendencia")
RES = os.path.join(os.path.dirname(__file__), "resultados")
filas = []; reg = []
for sym in ["NQ", "ES", "YM"]:
    A, E20, E50, F, atr = vi.dias_con_ema(sym); I = INSTR[sym]; tick = I["tick"]
    costo_pts = I["com"] / I["usd"] + 2 * tick
    atr_hoy = np.nanmean(atr[-60:]); costo_hoy_atr = costo_pts / atr_hoy * 100
    atr_rel = pd.Series(atr) / pd.Series(atr).rolling(100, min_periods=40).mean()
    for sm, Robj in itertools.product([0, 2], [2.0, 3.0, 0.0]):
        R = pd.DataFrame(np.array(pb.correr(A, E20, E50, atr, 120, sm, Robj, False, tick, True)), columns=["di", "d", "res", "riesgo", "mot"])
        R["f"] = F[R.di.astype(int)]; R["bruto_atr"] = R.res / atr[R.di.astype(int)] * 100
        R["neto_hoy_atr"] = R.bruto_atr - costo_hoy_atr
        R["regimen"] = pd.cut(atr_rel.to_numpy()[R.di.astype(int)], [0, 0.85, 1.15, 10], labels=["vol baja", "vol normal", "vol alta"])
        lab = dict(sym=sym, stop=["EMA50", "", "0.1 ATR"][sm], objetivo=("%.0fR" % Robj) if Robj else "cierre del día", costo_hoy_pct_atr=costo_hoy_atr)
        x = R.neto_hoy_atr
        fila = dict(lab, trades=len(R), wr=(x > 0).mean(), neto_hoy_atr=x.mean(), neto_hoy_usd=x.mean() / 100 * atr_hoy * I["usd"],
                    t=x.mean() / (x.std() / np.sqrt(len(x))))
        for tag, a, b in PERIODOS:
            y = R[(R.f >= a) & (R.f <= b)].neto_hoy_atr
            fila[f"{tag}_usd_hoy"] = y.mean() / 100 * atr_hoy * I["usd"]; fila[f"{tag}_t"] = y.mean() / (y.std() / np.sqrt(len(y)))
        fila["años_positivos"] = int((R.groupby(R.f.dt.year).neto_hoy_atr.mean() > 0).sum()); fila["años"] = R.f.dt.year.nunique()
        filas.append(fila)
        for rg, g in R.groupby("regimen", observed=True):
            for tag, a, b in PERIODOS:
                y = g[(g.f >= a) & (g.f <= b)].neto_hoy_atr
                reg.append(dict(lab, regimen=rg, periodo=tag, trades=len(y), usd_hoy=y.mean() / 100 * atr_hoy * I["usd"], t=y.mean() / (y.std() / np.sqrt(len(y)))))
T = pd.DataFrame(filas); G = pd.DataFrame(reg)
T.to_csv(os.path.join(RES, "pullback_costo_actual.csv"), index=False); G.to_csv(os.path.join(RES, "pullback_regimen.csv"), index=False)
pd.set_option("display.width", 250)
print("Con COSTO DE HOY (en % del ATR actual), USD por operación a precio de hoy:")
print(T.round(2).to_string(index=False))
print("\nPor régimen de volatilidad (USD por operación a precio de hoy / t):")
P = G.pivot_table(index=["sym", "stop", "objetivo", "regimen"], columns="periodo", values=["usd_hoy", "t"], observed=True)
print(P.round(1).to_string())
