"""Re-optimiza examen y fondeada con entrada de momentum de apertura (09:46, dirección de los primeros 15 min).
Selección por el PROMEDIO de ambas épocas (2011-20 y 2021-26) para no sobreajustar a una."""
import numpy as np, pandas as pd, itertools, os, time
from motor_fondeo import fondeada, examen
from reglas_tradeify import FONDEADA, EXAMEN
RES = os.path.join(os.path.dirname(__file__), "resultados")
LIB = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
M, TI = 2, 16
CUOTAS = {"growth": 93.0, "select": 165 * 0.6}   # Growth ~$93 (dato del usuario); Select con 40%
t0 = time.time(); rows_e = []; rows_f = []
for plan in ["growth", "select"]:
    e = EXAMEN[plan][50]
    for fr, S, rr, K in itertools.product([0.15, 0.3, 0.6, 1.0], [30, 45, 60, 90], [1.5, 2, 3, 4], [1, 2]):
        G = 1e9 if not e["consist"] else e["consist"] * e["target"] * 0.8
        res = {}
        for esc, D in LIB.items():
            ok, d = examen(D, 4000, float(e["target"]), float(e["dd"]), float(e["dll"] or 0), float(e["consist"] or 0), e["min_dias"],
                           float(fr * e["dd"]), float(S), float(S * rr), K, float(G), 1e9, 40, 60, 3, M, TI)
            res[esc] = ok.mean(); res[esc + "_dias"] = np.median(d[ok]) if ok.any() else np.nan
        rows_e.append(dict(plan=plan, fr=fr, S=S, rr=rr, K=K, G=G, **res, prom=(res["cons"] + res["opt"]) / 2))
tipos = {"growth": 0, "select_flex": 1}
for tipo in tipos:
    r = FONDEADA[tipo][50]
    cols = [-1, 2500] if tipo == "growth" else [-1]
    for R, S, rr, K, G, col in itertools.product([100, 150, 250, 400, 600], [30, 45, 60, 90], [1.5, 2, 3], [1, 2], [300, 600, 1e9], cols):
        res = {}
        for esc, D in LIB.items():
            cob, nret, viv, qb = fondeada(D, 1500, tipos[tipo], 50., float(r["dd"]), float(r.get("dll") or 0), float(r["dia_min"]),
                                          float(r.get("saldo_min", 0.)), float(r.get("cons", 0.) or 0.), float(r.get("pmin", 250.)),
                                          float(r["pmax"][0] if isinstance(r["pmax"], tuple) else r["pmax"]), float(r["pmax"][1] if isinstance(r["pmax"], tuple) else r["pmax"]),
                                          float(r.get("frac", 0.)), 0., 0., 0., float(R), float(S), float(S * rr), K, float(G), 1e9, 40, 0., 250, 17, M, TI, float(col))
            res[esc] = cob.mean(); res[esc + "_pcobra"] = (nret > 0).mean(); res[esc + "_dias"] = viv.mean()
        rows_f.append(dict(tipo=tipo, R=R, S=S, rr=rr, K=K, G=G, colchon=col, **res, prom=(res["cons"] + res["opt"]) / 2))
E = pd.DataFrame(rows_e); F = pd.DataFrame(rows_f)
E.to_csv(os.path.join(RES, "mom_examen.csv"), index=False); F.to_csv(os.path.join(RES, "mom_fondeada.csv"), index=False)
pd.set_option("display.width", 220)
print(f"{time.time()-t0:.0f}s\nExamen (mejor por promedio de épocas):")
print(E.sort_values("prom", ascending=False).groupby("plan").head(3).round(3).to_string(index=False))
print("\nFondeada (mejor por promedio de épocas):")
print(F.sort_values("prom", ascending=False).groupby("tipo").head(5).round(2).to_string(index=False))
