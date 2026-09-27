"""Cadena completa (examen + fondeada) y cartera con presupuesto. Cifras conservadoras (días 2011-2020)
y optimistas (2021-2026). Precio con 30% de descuento típico."""
import numpy as np, pandas as pd, os, re
import opt_fondeada as of
from motor_fondeo import examen
from reglas_tradeify import FONDEADA, EXAMEN, PRECIO_LISTA, DESCUENTO_TIPICO
from cartera import cartera
V = pd.read_csv(os.path.join(of.RES, "validacion_politicas.csv"))
D = {"cons": np.load("/home/user/data/dias_rth_2011_2020.npy"), "opt": np.load("/home/user/data/dias_rth.npy")}
of.HOR = 250
def parse(p):
    d = dict(re.findall(r"(\w+)=([\d.]+)", p.replace("%", "").replace("$", "")))
    return {k: float(v) for k, v in d.items()}
rows = []; dist = {}
combos = [("select", "select_flex"), ("growth", "growth"), ("lightning", "lightning")]
for ex_plan, f_plan in combos:
    for size in [25, 50, 100, 150]:
        precio = PRECIO_LISTA[(ex_plan, size)] * (1 - DESCUENTO_TIPICO)
        fp = parse(V[(V.fase == "fondeada") & (V.plan == f_plan) & (V["size"] == size)].politica.iloc[0])
        for esc, Dx in D.items():
            if ex_plan == "lightning":
                pp = 1.0
            else:
                r = EXAMEN[ex_plan][size]; ep = parse(V[(V.fase == "examen") & (V.plan == ex_plan) & (V["size"] == size)].politica.iloc[0])
                G = 1e9 if not r["consist"] else r["consist"] * r["target"] * 0.8
                ok, _ = examen(Dx, 20000, float(r["target"]), float(r["dd"]), float(r["dll"] or 0), float(r["consist"] or 0), r["min_dias"],
                               ep["R"] / 100 * r["dd"], ep["S"], ep["T"], int(ep["K"]), float(G), 1e9, r["max_mini"] * 10, 60, 123)
                pp = ok.mean()
            of.D = Dx
            cob, nret, viv, qb = of.correr(f_plan, size, FONDEADA[f_plan][size], fp["R"], fp["S"], fp["T"] / fp["S"], int(fp["K"]), fp["G"], 1e9, 0, ns=8000, seed=555)
            dist[(ex_plan, size, esc)] = (pp, cob, precio)
            ev1 = pp * cob.mean() - precio
            P = cartera(pp, cob, precio, 1000, 5, n=20000, copiadas=False)
            Pc = cartera(pp, cob, precio, 1000, 5, n=20000, copiadas=True)
            rows.append(dict(plan=ex_plan + ("" if ex_plan == "lightning" else f"→{f_plan}"), size=size, escenario=esc, precio=round(precio),
                             p_aprobar=pp, ev_fondeada=cob.mean(), p_cobra_fondeada=(nret > 0).mean(), ev_por_cuota=ev1, roi_cuota=ev1 / precio,
                             cart_ev=P["ev"], cart_p_ganar=P["p_ganar"], cart_p10=P["p10"], cart_p50=P["p50"], cart_p90=P["p90"],
                             cart_examenes=P["examenes"], cart_fondeadas=P["fondeadas"],
                             copia_ev=Pc["ev"], copia_p_ganar=Pc["p_ganar"], copia_p50=Pc["p50"]))
            print(rows[-1]["plan"], size, esc, round(ev1), round(P["ev"]), flush=True)
R = pd.DataFrame(rows); R.to_csv(os.path.join(of.RES, "comparacion_planes.csv"), index=False)
pd.set_option("display.width", 250)
print(R.round(3).to_string(index=False))
