"""Optimiza la política de la cuenta FONDEADA (maximizar USD netos cobrados en 120 días hábiles)."""
import numpy as np, pandas as pd, itertools, os, time, sys
from motor_fondeo import fondeada
from reglas_tradeify import FONDEADA
D = np.load("/home/user/data/dias_rth.npy")
RES = os.path.join(os.path.dirname(__file__), "resultados")
TIPO = {"growth": 0, "select_flex": 1, "select_daily": 2, "lightning": 3}
sizes = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["25", "50"])]
NS = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
HOR = 120
def correr(tipo, size, r, R, S, rr, K, G, L, res, ns=NS, seed=5):
    return fondeada(D, ns, TIPO[tipo], float(size), float(r["dd"]), float(r.get("dll") or 0.0), float(r.get("dia_min", 0.0)),
                    float(r.get("saldo_min", 0.0)), float(r.get("cons", 0.0) if not isinstance(r.get("cons"), tuple) else 0.0),
                    float(r.get("pmin", 250.0)), float(r["pmax"][0] if isinstance(r["pmax"], tuple) else r["pmax"]),
                    float(r["pmax"][1] if isinstance(r["pmax"], tuple) else r["pmax"]), float(r.get("frac", 0.0)),
                    float(r.get("buffer", 0.0)), float(r["goal"][0] if "goal" in r else 0.0), float(r["goal"][1] if "goal" in r else 0.0),
                    float(R), float(S), float(S * rr), K, float(G), float(L), r["max_mini"] * 10, float(res), HOR, seed)
if __name__ == "__main__":
    rows = []; t0 = time.time()
    for tipo, tab in FONDEADA.items():
        for size in sizes:
            r = tab[size]; dd = r["dd"]; dmin = r.get("dia_min", 150)
            for fr, S, rr, K, gm, lm, res in itertools.product([0.05, 0.1, 0.2, 0.35], [10, 20, 40], [0.5, 1, 2, 3], [1, 2, 3],
                                                              [1, 2, 4, 1e6], [1, 2, 1e6], [0, 500]):
                R = fr * dd
                G = gm * max(dmin, 100) if gm < 1e5 else 1e9
                L = lm * R if lm < 1e5 else 1e9
                cob, nret, viv, qb = correr(tipo, size, r, R, S, rr, K, G, L, res)
                rows.append(dict(tipo=tipo, size=size, fr=fr, R=R, S=S, rr=rr, K=K, G=G, L=L, reserva=res, ev=cob.mean(),
                                 p_cobra=(nret > 0).mean(), n_ret=nret.mean(), quiebra=qb.mean(), dias=viv.mean(), sd=cob.std()))
            print(tipo, size, f"{time.time()-t0:.0f}s", flush=True)
    R = pd.DataFrame(rows); R.to_csv(os.path.join(RES, f"opt_fondeada_grid_{'_'.join(map(str,sizes))}.csv"), index=False)
    pd.set_option("display.width", 220)
    print(R.sort_values("ev", ascending=False).groupby(["tipo", "size"]).head(3).sort_values(["tipo", "size", "ev"], ascending=[True, True, False]).round(2).to_string(index=False))
