"""Lista operación por operación del VI del usuario (NQ, ene-mar 2026) para comparar contra el replay de Tradovate.
Precios reales del contrato, hora de Nueva York. Marca si pasa el filtro 'recorrido al TP >= 0.03 ATR'."""
import sys, importlib
import numpy as np, pandas as pd
sys.path.insert(0, "../estudio_nq")
vi = importlib.import_module("22_vi_usuario")
correr = importlib.import_module("21_vi_filtro_usuario").correr
A, E20, E50, F, atr = vi.dias_con_ema("NQ")
R = pd.DataFrame(correr(A, E20, E50, 120, 0, 5, 0.25), columns=["di", "n", "d", "res", "mot", "rec", "r_ema", "r_vela", "r_ext"])
R["fecha"] = F[R.di.astype(int)]; R = R[R.fecha >= "2026-01-01"].copy()
R["hora_señal"] = [(pd.Timestamp("2000-01-01 09:30") + pd.Timedelta(minutes=int(n))).strftime("%H:%M") for n in R.n]
R["entrada"] = [A[int(d), int(n), 3] for d, n in zip(R.di, R.n)]
R["dirección"] = np.where(R.d > 0, "COMPRA", "VENTA")
R["TP"] = R.entrada + R.d * R.rec
R["salida"] = R.mot.map({1: "TP", 2: "cierre tras EMA20", 3: "5 minutos"})
R["resultado_pts"] = R.res.round(2)
R["neto_usd_1NQ"] = (R.res * 20 - 5.76 - np.where(R.mot == 1, 5, 10)).round(0)
R["pasa_filtro_TP_grande"] = R.rec >= 0.03 * atr[R.di.astype(int)]
out = R[["fecha", "hora_señal", "dirección", "entrada", "TP", "salida", "resultado_pts", "neto_usd_1NQ", "pasa_filtro_TP_grande"]]
out["fecha"] = out.fecha.dt.strftime("%Y-%m-%d")
out.to_csv("vi_operaciones_2026.csv", index=False)
print(out.head(25).to_string(index=False))
print("\nTotal:", len(out), "| acierto:", f"{(out.resultado_pts>0).mean():.0%}", "| suma neta $:", out.neto_usd_1NQ.sum())
g = out.resultado_pts
print("Ganancias: media", round(g[g>0].mean(),1), "pts | Pérdidas: media", round(g[g<=0].mean(),1), "pts | pérdidas > 20 pts:", (g < -20).sum(), "| mayor pérdida:", g.min())
f = out[out.pasa_filtro_TP_grande]
print("Con filtro:", len(f), "ops | acierto", f"{(f.resultado_pts>0).mean():.0%}", "| suma neta $", f.neto_usd_1NQ.sum())
by = out.groupby("fecha").neto_usd_1NQ.sum(); print("días positivos:", (by>0).sum(), "de", len(by))
