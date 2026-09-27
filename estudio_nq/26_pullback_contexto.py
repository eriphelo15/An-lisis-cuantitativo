"""Parte 2 — ¿Se puede agrandar la ventaja del pullback VI filtrando por contexto?
Para cada señal (NQ, 1 min, 09:30-11:30, stop EMA50, objetivo 2R) se calculan variables de contexto conocidas
en el momento de entrar, y se mide el resultado (en R, neto a costo de hoy) por tramos de cada variable,
separado en DEV (2010-18) / VAL1 (2019-21) / VAL2 (2021-26). Un filtro 'real' debe funcionar en los tres."""
import numpy as np, pandas as pd, os, importlib
from numba import njit
from hougaard import INSTR, PERIODOS
vi = importlib.import_module("22_vi_usuario")
RES = os.path.join(os.path.dirname(__file__), "resultados")

@njit(cache=True)
def señales(A, E20, E50, atr, t_fin, Robj, tick):
    out = []
    for di in range(A.shape[0]):
        if np.isnan(atr[di]): continue
        n = 1; libre = 0; k_prev_res = 0.0; num = 0
        while n < t_fin:
            if n < libre: n += 1; continue
            o1 = A[di, n - 1, 0]; c1 = A[di, n - 1, 3]; o = A[di, n, 0]; h = A[di, n, 1]; l = A[di, n, 2]; c = A[di, n, 3]
            h1 = A[di, n - 1, 1]; l1 = A[di, n - 1, 2]
            up = c > E20[di, n] and c > E50[di, n] and E20[di, n] > E50[di, n]
            dn = c < E20[di, n] and c < E50[di, n] and E20[di, n] < E50[di, n]
            d = 0.0
            if up and max(o, c) < min(o1, c1) and h >= l1: d = 1.0
            elif dn and min(o, c) > max(o1, c1) and l <= h1: d = -1.0
            if d == 0.0: n += 1; continue
            e = c; stop = E50[di, n] - d * 2 * tick; rk = d * (e - stop)
            if rk < 4 * tick or rk > 0.25 * atr[di]: n += 1; continue
            tgt = e + d * Robj * rk
            k = n + 1; res = 0.0
            while k <= 385:
                ok_ = A[di, k, 0]; hh = A[di, k, 1]; ll = A[di, k, 2]; cc = A[di, k, 3]
                if (ll <= stop) if d > 0 else (hh >= stop):
                    px = stop
                    if (d > 0 and ok_ < stop) or (d < 0 and ok_ > stop): px = ok_
                    res = d * (px - e); break
                if (hh >= tgt) if d > 0 else (ll <= tgt):
                    res = d * (tgt - e); break
                if k == 385: res = d * (cc - e)
                k += 1
            gap_vi = abs(min(o1, c1) - max(o, c)) if d > 0 else abs(min(o, c) - max(o1, c1))
            out.append((di, n, d, res, rk, gap_vi, h - l, E20[di, n] - E20[di, max(n - 10, 0)], num, k_prev_res))
            num += 1; k_prev_res = res / rk
            libre = k + 1; n = k + 1
    return out

if __name__ == "__main__":
    A, E20, E50, F, atr = vi.dias_con_ema("NQ"); I = INSTR["NQ"]
    Aes, E20es, E50es, Fes, _ = vi.dias_con_ema("ES")
    costo_hoy_atr = (I["com"] / I["usd"] + 2 * I["tick"]) / np.nanmean(atr[-60:])
    S = pd.DataFrame(np.array(señales(A, E20, E50, atr, 120, 2.0, 0.25)),
                     columns=["di", "n", "d", "res", "rk", "gap_vi", "rango_vela", "pend20", "num_señal_dia", "prev_R"])
    di = S.di.astype(int).to_numpy(); n = S.n.astype(int).to_numpy(); d = S.d.to_numpy()
    at = atr[di]
    S["f"] = F[di]
    S["R_neto"] = S.res / S.rk - costo_hoy_atr * at / S.rk                 # en R, a costo de hoy
    # contexto conocido al entrar
    o930 = A[di, 0, 0]; c_prev = np.r_[np.nan, A[:-1, 385, 3]][di]
    S["min_desde_apertura"] = n
    S["mov_apertura_a_favor"] = d * (A[di, n, 3] - o930) / at               # cuánto ha ido el día en la dirección del trade
    S["gap_a_favor"] = d * (o930 - c_prev) / at
    S["mov15_a_favor"] = d * (A[di, 15, 3] - o930) / at * np.where(n >= 15, 1, np.nan)
    S["dist_ema50_R"] = S.rk / at                                           # tamaño del stop en ATR
    S["pend20_a_favor"] = d * S.pend20 / at
    S["gap_vi_atr"] = S.gap_vi / at
    S["rango_vela_atr"] = S.rango_vela / at
    rango_hasta = np.array([A[i, :m + 1, 1].max() - A[i, :m + 1, 2].min() for i, m in zip(di, n)])
    S["rango_dia_hasta_atr"] = rango_hasta / at
    S["atr_rel"] = (pd.Series(atr) / pd.Series(atr).rolling(100, min_periods=40).mean()).to_numpy()[di]
    S["dow"] = S.f.dt.dayofweek
    # ES alineado: ¿ES también está en tendencia en la misma dirección en ese minuto?
    mapa = {f: i for i, f in enumerate(Fes)}
    es_ok = []
    for i, m, dd, ff in zip(di, n, d, S.f):
        j = mapa.get(ff)
        if j is None: es_ok.append(np.nan); continue
        c = Aes[j, m, 3]; up = c > E20es[j, m] and c > E50es[j, m] and E20es[j, m] > E50es[j, m]
        dn = c < E20es[j, m] and c < E50es[j, m] and E20es[j, m] < E50es[j, m]
        es_ok.append(1.0 if (dd > 0 and up) or (dd < 0 and dn) else 0.0)
    S["ES_confirma"] = es_ok
    S.to_parquet(os.path.join("/home/user/data", "pullback_señales_nq.parquet"))
    feats = ["min_desde_apertura", "mov_apertura_a_favor", "gap_a_favor", "mov15_a_favor", "dist_ema50_R", "pend20_a_favor", "gap_vi_atr",
             "rango_vela_atr", "rango_dia_hasta_atr", "atr_rel", "num_señal_dia", "prev_R", "ES_confirma", "dow"]
    filas = []
    for fe in feats:
        x = S[fe]
        if x.nunique() <= 7:
            tr = x
        else:
            tr = pd.qcut(x.rank(method="first"), 4, labels=["Q1 bajo", "Q2", "Q3", "Q4 alto"])
        for q, g in S.groupby(tr, observed=True):
            fila = dict(variable=fe, tramo=str(q), n=len(g), R_medio=g.R_neto.mean(), wr=(g.R_neto > 0).mean())
            for tag, a, b in PERIODOS:
                y = g[(g.f >= a) & (g.f <= b)].R_neto
                fila[f"{tag}_R"] = y.mean(); fila[f"{tag}_t"] = y.mean() / (y.std() / np.sqrt(len(y))) if len(y) > 5 else np.nan
            filas.append(fila)
    T = pd.DataFrame(filas); T.to_csv(os.path.join(RES, "pullback_contexto.csv"), index=False)
    pd.set_option("display.width", 220)
    print("Base (todas las señales): R medio", round(S.R_neto.mean(), 3), "n", len(S))
    print(T.round(3).to_string(index=False))
