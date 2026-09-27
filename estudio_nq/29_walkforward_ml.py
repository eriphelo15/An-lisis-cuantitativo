"""Walk-forward anual (2014-2026) con LightGBM sobre el universo. Para cada año: entrena con años previos,
puntúa el año nuevo y selecciona el top X% con umbral calculado SOLO sobre las predicciones de entrenamiento.
Reporta winrate y R neto fuera de muestra, por instrumento y por año. Solo 1 operación por día e instrumento
(la de mayor puntuación que supere el umbral) para no contar operaciones solapadas."""
import numpy as np, pandas as pd, os, lightgbm as lgb, time
RES = os.path.join(os.path.dirname(__file__), "resultados")
X = pd.read_parquet("/home/user/data/universo_ml.parquet")
X["año"] = X.f.dt.year
feats = ["dia_a_favor", "gap_a_favor", "r5", "r15", "r30", "dist_ema20", "dist_ema50", "pend_ema20", "sep_emas", "dist_vwap", "rango_dia",
         "pos_rango", "vol_rel", "atr_rel", "rango_ayer", "ret_ayer_a_favor", "rango_5min", "tend_otro0", "dia_otro0", "tend_otro1", "dia_otro1",
         "min", "dow", "inst"]
params = dict(objective="binary", learning_rate=0.03, num_leaves=31, min_data_in_leaf=300, feature_fraction=0.8, bagging_fraction=0.8,
              bagging_freq=1, lambda_l2=5.0, verbose=-1, seed=1)
res = []; t0 = time.time(); imp = []
for lab in ["y12", "y11"]:
    for Y in range(2014, 2027):
        tr = X[X.año < Y]; te = X[X.año == Y].copy()
        if len(te) == 0: continue
        m = lgb.train(params, lgb.Dataset(tr[feats], (tr[lab] > 0).astype(int)), num_boost_round=400)
        ptr = m.predict(tr[feats]); te["p"] = m.predict(te[feats])
        if lab == "y12": imp.append(pd.Series(m.feature_importance("gain"), index=feats))
        for q in [1.0, 0.2, 0.1, 0.05, 0.02]:
            thr = np.quantile(ptr, 1 - q) if q < 1 else -1
            sel = te[te.p >= thr].sort_values("p", ascending=False).groupby(["sym", "di"]).head(1)
            for sym, g in sel.groupby("sym"):
                res.append(dict(etiqueta=lab, año=Y, top=q, sym=sym, n=len(g), wr=(g[lab] > 0).mean(), R=g[lab].mean(), R_suma=g[lab].sum()))
        print(lab, Y, f"{time.time()-t0:.0f}s", flush=True)
R = pd.DataFrame(res); R.to_csv(os.path.join(RES, "walkforward_ml.csv"), index=False)
pd.set_option("display.width", 220)
tot = R.groupby(["etiqueta", "sym", "top"]).apply(lambda g: pd.Series(dict(trades=g.n.sum(), trades_año=g.n.sum() / g.año.nunique(),
        wr=(g.wr * g.n).sum() / g.n.sum(), R=g.R_suma.sum() / g.n.sum(), años_pos=f"{(g.R > 0).sum()}/{len(g)}")), include_groups=False)
print(tot.round(3).to_string())
I = pd.concat(imp, axis=1).mean(1); print("\nImportancia media (y12):\n", (I / I.sum()).sort_values(ascending=False).round(3).to_string())
