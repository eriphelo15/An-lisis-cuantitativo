"""Refinamiento: políticas de bajo riesgo con parada diaria por ganancia, horizonte 250 días, 4000 sims."""
import numpy as np, pandas as pd, itertools, os, time, sys
import opt_fondeada as of
from reglas_tradeify import FONDEADA
of.HOR = 250
RES = of.RES
sizes = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [25, 50]
rows = []; t0 = time.time()
for tipo, tab in FONDEADA.items():
    for size in sizes:
        r = tab[size]; dd = r["dd"]; dmin = r.get("dia_min", 150)
        for R, S, rr, K, gm, lm, res in itertools.product(
                [x * dd for x in [0.01, 0.02, 0.035, 0.05, 0.075, 0.1, 0.15]], [15, 25, 40, 60, 90], [1, 2, 3, 5], [1, 2, 3, 5],
                [1.0, 1.25, 1.75, 2.5, 4], [1.5, 3, 1e6], [0, 500]):
            G = gm * max(dmin, 100); L = lm * R if lm < 1e5 else 1e9
            cob, nret, viv, qb = of.correr(tipo, size, r, R, S, rr, K, G, L, res, ns=1500, seed=21)
            rows.append(dict(tipo=tipo, size=size, R=R, S=S, rr=rr, K=K, G=G, L=L, reserva=res, ev=cob.mean(),
                             p_cobra=(nret > 0).mean(), n_ret=nret.mean(), quiebra=qb.mean(), dias=viv.mean(), p10=np.quantile(cob, .1), p50=np.median(cob), p90=np.quantile(cob, .9)))
        print(tipo, size, f"{time.time()-t0:.0f}s", flush=True)
R = pd.DataFrame(rows)
R.to_csv(os.path.join(RES, f"opt_fondeada_fino_{'_'.join(map(str, sizes))}.csv"), index=False)
# re-evaluar top 15 por tipo/tamaño con 8000 sims y otra semilla (evita el sesgo de elegir el máximo con ruido)
top = R.sort_values("ev", ascending=False).groupby(["tipo", "size"]).head(15)
out = []
for _, t in top.iterrows():
    cob, nret, viv, qb = of.correr(t.tipo, int(t["size"]), FONDEADA[t.tipo][int(t["size"])], t.R, t.S, t.rr, int(t.K), t.G, t.L, t.reserva, ns=8000, seed=999)
    out.append({**t.to_dict(), "ev_val": cob.mean(), "p_cobra_val": (nret > 0).mean(), "n_ret_val": nret.mean(), "dias_val": viv.mean(),
                "p10_val": np.quantile(cob, .1), "p50_val": np.median(cob), "p90_val": np.quantile(cob, .9)})
V = pd.DataFrame(out); V.to_csv(os.path.join(RES, f"opt_fondeada_top_{'_'.join(map(str, sizes))}.csv"), index=False)
pd.set_option("display.width", 250)
cols = ["tipo", "size", "R", "S", "rr", "K", "G", "L", "reserva", "ev", "ev_val", "p_cobra_val", "n_ret_val", "dias_val", "p50_val", "p90_val"]
print(V.sort_values("ev_val", ascending=False).groupby(["tipo", "size"]).head(3)[cols].round(2).to_string(index=False))
