"""Fase 2g — Machine learning (LightGBM) como detector de estructura no lineal.
Puntos de decisión cada 5 min en RTH (10:00-15:25). Objetivo: signo del retorno a 30 min.
Validación walk-forward anual dentro de DEV (train años previos -> test año siguiente)."""
import numpy as np, pandas as pd, os, sys
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
from motor import Motor, hm2s
from lib import RES_DIR, COSTO_MKT_RT_PTS

def features(split):
    M = Motor(split); D = M.D.dropna(subset=["atr", "prev_c"]); s = M.smin; di = M.day_id
    c, h, l, v = M.c, M.h, M.l, M.v
    rth = (s >= 930) & (s < 1320)
    key = np.where(rth, di, -1)
    tp = (h + l + c) / 3
    vwap = pd.Series(tp * v).groupby(key).cumsum().to_numpy() / pd.Series(v).groupby(key).cumsum().to_numpy()
    hi_so_far = pd.Series(h).groupby(key).cummax().to_numpy(); lo_so_far = pd.Series(l).groupby(key).cummin().to_numpy()
    vol30 = pd.Series(v).rolling(30).sum().to_numpy()
    pts = np.flatnonzero(rth & (s >= hm2s(1000)) & (s <= hm2s(1525)) & ((s - 930) % 5 == 4))
    pts = pts[np.isin(di[pts], D.index)]
    pts = pts[(pts + 31 < len(c))]
    pts = pts[di[pts + 30] == di[pts]]
    d = di[pts]; Dd = D.loc[d]
    atr = Dd.atr.to_numpy()
    F = pd.DataFrame(index=pts)
    for k in [1, 5, 15, 30, 60]:
        back = np.maximum(pts - k, 0)
        F[f"r{k}"] = (c[pts] - c[back]) / atr
    F["vwap_z"] = (c[pts] - vwap[pts]) / atr
    F["from_open"] = (c[pts] - Dd.rth_o.to_numpy()) / atr
    F["from_prevc"] = (c[pts] - Dd.prev_c.to_numpy()) / atr
    for col in ["on_h", "on_l", "prev_h", "prev_l"]:
        F["d_" + col] = (c[pts] - Dd[col].to_numpy()) / atr
    F["rng_so_far"] = (hi_so_far[pts] - lo_so_far[pts]) / atr
    F["pos_in_rng"] = (c[pts] - lo_so_far[pts]) / np.maximum(hi_so_far[pts] - lo_so_far[pts], 0.25)
    F["gap"] = Dd.gap.to_numpy() / atr
    F["prev_ret"] = (Dd.prev_c - Dd.prev_o).to_numpy() / atr
    F["atr_rel"] = atr / Dd.atr.rolling(50, min_periods=10).mean().to_numpy()
    F["vol_rel"] = vol30[pts] / pd.Series(vol30[pts]).groupby(s[pts]).transform(lambda x: x.expanding().mean().shift()).to_numpy()
    F["tod"] = s[pts]; F["dow"] = Dd.dow.to_numpy()
    fwd = c[pts + 30] - M.o[pts + 1]
    F["fwd_pts"] = fwd; F["fwd_atr"] = fwd / atr
    F["year"] = M.days[d].year; F["day"] = d
    return F

if __name__ == "__main__":
    F = features("dev")
    X_cols = [c for c in F.columns if c not in ("fwd_pts", "fwd_atr", "year", "day")]
    print("muestras:", len(F), " features:", len(X_cols))
    params = dict(objective="binary", learning_rate=0.02, num_leaves=15, min_data_in_leaf=400, feature_fraction=0.7,
                  bagging_fraction=0.7, bagging_freq=1, lambda_l2=10, verbose=-1, seed=7)
    rows = []; imp = []
    for test_y in [2022, 2023, 2024]:
        tr = F[F.year < test_y]; te = F[F.year == test_y]
        m = lgb.train(params, lgb.Dataset(tr[X_cols], (tr.fwd_pts > 0).astype(int)), num_boost_round=300)
        p = m.predict(te[X_cols]); auc = roc_auc_score(te.fwd_pts > 0, p)
        imp.append(pd.Series(m.feature_importance("gain"), index=X_cols, name=test_y))
        for q in [0.1, 0.05, 0.02]:
            hi = p >= np.quantile(p, 1 - q); lo = p <= np.quantile(p, q)
            pnl = np.concatenate([te.fwd_pts[hi] - COSTO_MKT_RT_PTS, -te.fwd_pts[lo] - COSTO_MKT_RT_PTS])
            rows.append(dict(test=test_y, auc=auc, cola=q, n=len(pnl), wr=(pnl > 0).mean(), exp=pnl.mean(),
                             t=pnl.mean() / (pnl.std() / np.sqrt(len(pnl)))))
    R = pd.DataFrame(rows); print(R.round(4).to_string(index=False))
    I = pd.concat(imp, axis=1); I = I.div(I.sum()); print("\nImportancia (gain, normalizada):\n", I.mean(1).sort_values(ascending=False).round(3).to_string())
    R.to_csv(os.path.join(RES_DIR, "f2g_ml_walkforward_dev.csv"), index=False)
