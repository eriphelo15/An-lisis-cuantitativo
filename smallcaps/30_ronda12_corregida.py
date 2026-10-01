"""Ronda 12 con los datos corregidos tras la verificación independiente (1-oct-2026, VERIFICADOR_ESTUDIOS.md):
(1) precio real: apertura sin ajustar de Massive (1 min) si existe; si no, calibrado por acción desde otro evento posterior con precio
    exacto (× splits de Yahoo entre medias); si no, ajustado × splits de Yahoo (ronda 5). Casos con split en el mismo mes = fuera salvo
    precio exacto o calibrado.
(2) ventana del catalizador con el día hábil REAL anterior (con festivos): antes se usaba BDay sin festivos (GNPX 21-ene-2020 y UUU
    2-sep-2025 perdían un 8-K del viernes por la tarde → 'solo nota de prensa' mal puesto).
Mismos factores, pesos de DEV, prueba en VAL. Se compara con la réplica a ciegas del verificador."""
import glob, json
import numpy as np
import pandas as pd
from scipy import stats

D, S = "/home/user/data/smallcaps", "/home/user/data/sec"
X = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
P = pd.read_csv("res_29_precios.csv")
assert (X.sym.values == P.sym.values).all()
X["precio_T"] = P.precio_T.values
SP = pd.read_parquet(f"{D}/splits.parquet"); SP["t"] = pd.to_datetime(SP.t)
# (1) calibración por acción desde el evento posterior más cercano con precio exacto
X["precio_c"] = np.nan
for sym, g in X.groupby("sym"):
    conT = g[g.precio_T.notna()]
    if conT.empty:
        continue
    sp = SP[SP.sym == sym]
    for i, r in g[g.precio_T.isna()].iterrows():
        post = conT[conT.date > r.date]
        if post.empty:
            continue
        e = post.iloc[0]
        f1 = e.precio_T / e.open
        m0, m1 = r.date.to_period("M").to_timestamp(), e.date.to_period("M").to_timestamp()
        if ((sp.t == m0) | (sp.t == m1)).any():
            continue
        X.loc[i, "precio_c"] = r.open * f1 * sp[(sp.t > m0) & (sp.t <= m1)].ratio.prod()
X["precio_v"] = X.precio_T.fillna(X.precio_c).fillna(X.precio)
X["exacto"] = X.precio_T.notna() | X.precio_c.notna()
X["valido"] = ~X.ambiguo | X.exacto
# (2) solo_pr con el día hábil real anterior
cal = pd.DatetimeIndex(pd.read_csv(f"{D}/calendario_mercado.csv").iloc[:, 0])
tk = json.load(open(f"{S}/tickers.json")); t2c = {v["ticker"].replace(".", "-"): v["cik_str"] for v in tk.values()}
X["prev_real"] = cal[cal.searchsorted(X.date) - 1]
X["prev_bday"] = X.date - pd.offsets.BDay(1)
cambios = 0
for i, r in X[X.prev_real != X.prev_bday].iterrows():
    f = glob.glob(f"{S}/subs/{t2c.get(r.sym)}.parquet")
    if not f:
        continue
    x = pd.read_parquet(f[0]); x["t"] = pd.to_datetime(x.acceptanceDateTime, utc=True, errors="coerce").dt.tz_convert("America/New_York").dt.tz_localize(None)
    k8 = x[(x.t > r.prev_real + pd.Timedelta(hours=16)) & (x.t < r.date + pd.Timedelta(hours=9, minutes=30)) & x.form.isin(["8-K", "8-K/A"])]
    its = [i2.strip() for i2 in ",".join(k8["items"].astype(str)).split(",")]
    nuevo = len(k8) > 0 and all(i2 in ("7.01", "8.01", "9.01", "") for i2 in its)
    if bool(r.solo_pr) != nuevo:
        cambios += 1; X.loc[i, "solo_pr"] = nuevo
print("precio exacto:", int(X.precio_T.notna().sum()), "| calibrado:", int(X.precio_c.notna().sum()), "| solo_pr corregidos:", cambios)

E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
Z = E.merge(X[X.valido], on=["sym", "fecha"], how="inner")
Z = Z[(Z.precio_v >= 1) & ~Z.tipo.isin(["C", "R", "F", "S"])].copy()
F = pd.DataFrame(index=Z.index)
F["gap_50_100"] = ((Z.gap >= .5) & (Z.gap < 1)).astype(float); F["gap_100"] = (Z.gap >= 1).astype(float)
for t in ["H", "B", "K"]:
    F[f"cat_{t}"] = (Z.tipo == t).astype(float)
for c in ["venta90", "s3", "serie", "solo_pr"]:
    F[c] = Z[c].astype(float)
Dm, Vm = Z.per.str.startswith("DEV"), Z.per.str.startswith("VAL")
coef, *_ = np.linalg.lstsq(np.c_[np.ones(Dm.sum()), F[Dm].values], Z.loc[Dm, "R"].values, rcond=None)
Z["pred"] = coef[0] + F.values @ coef[1:]
ref = np.sort(Z.loc[Dm, "pred"].values)
Z["puntuacion"] = np.searchsorted(ref, Z.pred, side="right") / len(ref) * 100
Z["tercio"] = pd.cut(Z.puntuacion, [-1, 100 / 3, 200 / 3, 101], labels=["bajo", "medio", "alto"])


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(), PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan))


pd.set_option("display.width", 200)
print("casos:", len(Z), "| DEV", int(Dm.sum()), "| VAL", int(Vm.sum()))
print("pesos:", dict(zip(["constante"] + list(F.columns), coef.round(4))))
print(Z.groupby(["per", "tercio"], observed=True).R.apply(met).unstack().round(3).to_string())
print("\ngap ≥ 50 %:\n", Z[Z.gap >= .5].groupby(["per", "tercio"], observed=True).R.apply(met).unstack().round(3).to_string())
rho, p = stats.spearmanr(Z.loc[Vm, "puntuacion"], Z.loc[Vm, "R"])
a, b = Z[Vm & (Z.tercio == "alto")].R, Z[Vm & (Z.tercio == "bajo")].R
print(f"\nVAL Spearman rho {rho:.3f} p {p:.4f} | alto−bajo {a.mean() - b.mean():+.3f}R t {stats.ttest_ind(a, b, equal_var=False).statistic:.2f}")
json.dump(dict(pesos=dict(zip(["constante"] + list(F.columns), coef.round(4).tolist())),
               pesos_exactos=dict(zip(["constante"] + list(F.columns), coef.tolist())), ref_dev=list(map(float, ref))),
          open("puntuacion_pesos_corregida.json", "w"))
Z[["sym", "fecha", "per", "gap", "tipo", "R", "puntuacion", "tercio", "precio_v", "exacto", "venta90", "s3", "serie", "solo_pr"]].to_csv("res_30_ronda12_corregida.csv", index=False)
