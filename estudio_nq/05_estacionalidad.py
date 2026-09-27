"""Fase 2c — Estacionalidad intradía y de calendario (DEV)."""
import numpy as np, pandas as pd, os
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS
M = Motor("dev")
df = M.df
# retornos en PUNTOS por slot de 30 min dentro de un mismo día/segmento
df["slot"] = M.smin // 30
g = df.groupby(["tday", "slot"])
S = pd.DataFrame({"o": g.open.first(), "c": g.close.last(), "seg": g.seg.first(), "segl": g.seg.last(), "n": g.size()})
S = S[(S.seg == S.segl) & (S.n >= 25)]
S["pts"] = S.c - S.o
S["bp"] = np.log(S.c / S.o) * 1e4
S = S.reset_index(); S["year"] = S.tday.dt.year
def lab(sl):
    m = (sl * 30 + 18 * 60) % 1440; return f"{m//60:02d}:{m%60:02d}"
T = S.groupby("slot").agg(mean_pts=("pts", "mean"), sd=("pts", "std"), n=("pts", "size"), up=("pts", lambda x: (x > 0).mean()), mean_bp=("bp", "mean"))
T["t"] = T.mean_pts / (T.sd / np.sqrt(T.n))
Y = S.pivot_table(index="slot", columns="year", values="bp", aggfunc="mean")
T = T.join(Y.add_prefix("bp_"))
T["años_mismo_signo"] = (np.sign(Y).eq(np.sign(T.mean_bp), axis=0)).sum(1)
T.index = [lab(i) for i in T.index]
pd.set_option("display.width", 220)
print("Slots de 30 min (hora ET de inicio): media pts, t, % up, bp por año")
print(T.round(3).to_string())
T.to_csv(os.path.join(RES_DIR, "f2c_slots30.csv"))
print("\nSlots con |t|>2:", T[T.t.abs() > 2].index.tolist(), "  (esperados por azar con 46 slots: ~2.3)")

# ---- Calendario (retorno RTH 09:30->16:00 en bp) ----
D = M.D.copy()
D["ret"] = np.log(D.rth_c / D.rth_o) * 1e4
D["ret_on"] = np.log(D.rth_o / D.prev_c) * 1e4
dates = D.date
# turn of month: últimos 1 y primeros 3 días hábiles
D["tdm"] = D.groupby([dates.dt.year, dates.dt.month]).cumcount() + 1
D["tdm_rev"] = D.groupby([dates.dt.year, dates.dt.month]).cumcount(ascending=False) + 1
# OPEX: tercer viernes
D["opex"] = (dates.dt.dayofweek == 4) & dates.dt.day.between(15, 21)
fomc = pd.to_datetime(["2021-03-17","2021-04-28","2021-06-16","2021-07-28","2021-09-22","2021-11-03","2021-12-15",
 "2022-01-26","2022-03-16","2022-05-04","2022-06-15","2022-07-27","2022-09-21","2022-11-02","2022-12-14",
 "2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
 "2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18"])
D["fomc"] = dates.isin(fomc)
D["pre_fomc"] = dates.isin(fomc - pd.offsets.BDay(1))
def test(mask, name, col="ret"):
    x = D.loc[mask, col].dropna(); y = D.loc[~mask, col].dropna()
    t = x.mean() / (x.std() / np.sqrt(len(x)))
    print(f"  {name:<28} n={len(x):4d}  media={x.mean():+7.1f}bp  up={(x>0).mean():.3f}  t={t:+.2f}   (resto {y.mean():+.1f})")
print("\nCalendario — retorno RTH:")
for k in range(5): test(D.dow == k, f"dow={['Lun','Mar','Mié','Jue','Vie'][k]}")
test(D.tdm_rev == 1, "último día del mes"); test(D.tdm <= 3, "primeros 3 días del mes")
test(D.opex, "OPEX (3er viernes)"); test(D.fomc, "día FOMC"); test(D.pre_fomc, "día previo FOMC")
print("Calendario — retorno overnight (cierre previo -> apertura):")
for k in range(5): test(D.dow == k, f"dow={['Lun','Mar','Mié','Jue','Vie'][k]}", "ret_on")
test(D.tdm <= 3, "primeros 3 días del mes", "ret_on"); test(D.fomc, "día FOMC", "ret_on")
