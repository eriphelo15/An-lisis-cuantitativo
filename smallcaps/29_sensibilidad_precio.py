"""Comprobación (1-oct-2026): ¿cambian las conclusiones de las rondas 5, 11 y 12 si se corrige el "precio real"?
Hallazgo de la ronda 13: la lista de splits de Yahoo omite contra-splits que sí aplica a sus precios (CRIS, SVRE) → el precio real de la
ronda 5 (ajustado × splits de Yahoo) falla en ~6 % de casos recientes. El R NO cambia (es relativo); cambia quién pasa el filtro precio ≥ $1.
Precios: Y = ronda 5 (splits de Yahoo); M = splits de Massive; T = verdad (apertura 9:30 sin ajustar de Massive, solo oct-2024 en adelante).
Variantes: original (Y); corregida (T si existe; si no, Y cuando Y y M coinciden ±3 %; si no coinciden → fuera); con dudosos = M; con dudosos = Y."""
import os
import numpy as np
import pandas as pd
from scipy import stats

D = "/home/user/data/smallcaps"
R = pd.read_csv("res_18_precio_real.csv", parse_dates=["date"])
S = pd.read_parquet(f"{D}/splits_massive.parquet"); S = S[S.execution_date <= "2026-10-01"].copy()
S["ratio"] = S.split_to / S.split_from; S["d"] = pd.to_datetime(S.execution_date)
G = {k: v for k, v in S.groupby("ticker")}
R["precio_M"] = [r.open * (float(G[r.sym][G[r.sym].d > r.date].ratio.prod()) if r.sym in G else 1.0) for r in R.itertuples()]
T = []
for r in R.itertuples():
    f = f"/home/user/data/massive/m1/{r.sym}_{r.date.date()}.parquet"
    v = np.nan
    if r.date >= pd.Timestamp("2024-10-01") and os.path.exists(f):
        x = pd.read_parquet(f)
        if len(x):
            x.index = pd.to_datetime(x.t, unit="ms", utc=True).dt.tz_convert("America/New_York")
            y = x.between_time("09:30", "09:30")
            v = float(y.o.iloc[0]) if len(y) else np.nan
    T.append(v)
R["precio_T"] = T
coinc = (R.precio / R.precio_M - 1).abs() <= .03
R["precio_corr"] = np.where(R.precio_T.notna(), R.precio_T, np.where(coinc, R.precio, np.nan))
R["dudoso"] = R.precio_T.isna() & ~coinc
print(f"casos {len(R)} | con verdad (Massive 1 min) {R.precio_T.notna().sum()} | Y y M coinciden {coinc.sum()} | dudosos {R.dudoso.sum()}")
print("dudosos por periodo:", R[R.dudoso].per.value_counts().to_dict())
if R.precio_T.notna().any():
    t = R[R.precio_T.notna()]
    print(f"donde hay verdad: Y acierta ±3 % {((t.precio / t.precio_T - 1).abs() <= .03).mean():.1%}, M {((t.precio_M / t.precio_T - 1).abs() <= .03).mean():.1%}")
VAR = {"original (Y)": (R.precio, ~R.ambiguo),
       "corregida (dudosos fuera)": (R.precio_corr, R.precio_corr.notna() & (~R.ambiguo | R.precio_T.notna())),
       "corregida, dudosos = M": (R.precio_corr.fillna(R.precio_M), ~R.ambiguo | R.precio_T.notna()),
       "corregida, dudosos = Y": (R.precio_corr.fillna(R.precio), ~R.ambiguo | R.precio_T.notna())}


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return pd.Series(dict(n=len(v), R=v.mean(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(), PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan))


E = pd.read_csv("clasificacion_catalizador.csv").rename(columns={"cat": "tipo"})
filas = []
for nombre, (precio, valido) in VAR.items():
    X = R.assign(precio_v=precio)[valido].copy()
    # --- ronda 12: pesos de DEV, prueba en VAL
    Z = E.merge(X, on=["sym", "fecha"], how="inner")
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
    Z["punt"] = np.searchsorted(ref, Z.pred, side="right") / len(ref) * 100
    Z["tercio"] = pd.cut(Z.punt, [-1, 100 / 3, 200 / 3, 101], labels=["bajo", "medio", "alto"])
    rho, p = stats.spearmanr(Z.loc[Vm, "punt"], Z.loc[Vm, "R"])
    a, b = Z[Vm & (Z.tercio == "alto")].R, Z[Vm & (Z.tercio == "bajo")].R
    a50 = Z[Vm & (Z.tercio == "alto") & (Z.gap >= .5)].R
    # --- ronda 5: humo gap ≥ 50 %, ≥ $1 frente a < $1 (VAL, bruto)
    H = E.merge(X, on=["sym", "fecha"]); H = H[(H.tipo == "H") & (H.gap >= .5) & H.per.str.startswith("VAL")]
    filas.append(dict(variante=nombre, n12=len(Z), n12_VAL=int(Vm.sum()), rho_VAL=rho, p_rho=p,
                      alto_VAL=a.mean(), bajo_VAL=b.mean(), t_alto_bajo=stats.ttest_ind(a, b, equal_var=False).statistic,
                      alto_gap50_VAL=a50.mean(), n_alto_gap50=len(a50), PF_alto_gap50=met(a50).PF,
                      humo50_mayor1=H[H.precio_v >= 1].R.mean(), humo50_menor1=H[H.precio_v < 1].R.mean(),
                      n_h_m1=int((H.precio_v >= 1).sum()), n_h_m0=int((H.precio_v < 1).sum())))
O = pd.DataFrame(filas); pd.set_option("display.width", 250)
print(O.round(3).to_string(index=False))
O.to_csv("res_29_sensibilidad.csv", index=False)
R[["sym", "fecha", "per", "precio", "precio_M", "precio_T", "precio_corr", "dudoso"]].to_csv("res_29_precios.csv", index=False)
