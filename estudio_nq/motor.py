"""Motor de hipótesis: arrays globales, features diarias y registro de TODAS las pruebas
(para corrección por múltiples pruebas)."""
import os, json
import numpy as np, pandas as pd
from lib import load_1m, RES_DIR, COSTO_MKT_RT_PTS, COSTO_LMT_RT_PTS, stats_trades
from sim import simulate, simulate_limit


def hm2s(hm):
    """HHMM (ET) -> minuto de sesión desde 18:00."""
    return ((hm // 100) * 60 + hm % 100 - 18 * 60) % 1440


class Motor:
    def __init__(self, split="dev"):
        df = load_1m(split)
        self.df = df
        self.o = df.open.to_numpy(); self.h = df.high.to_numpy()
        self.l = df.low.to_numpy(); self.c = df.close.to_numpy()
        self.v = df.volume.to_numpy().astype(float)
        self.smin = df.smin.to_numpy().astype(np.int32)
        codes, uniq = pd.factorize(df.tday)
        self.day_id = codes.astype(np.int32); self.days = pd.DatetimeIndex(uniq)
        self.split = split
        self._daily()
        self.registro = []

    # ---------- features diarias (sin mirar al futuro) ----------
    def _daily(self):
        df = self.df
        di = self.day_id
        n = di.max() + 1
        def first_idx(mask):
            out = np.full(n, -1, np.int64)
            idx = np.flatnonzero(mask)
            d = di[idx]
            first = np.unique(d, return_index=True)
            out[first[0]] = idx[first[1]]
            return out
        s = self.smin
        self.i_rth0 = first_idx(s == 930)          # barra 09:30
        rth = (s >= 930) & (s < 1320)
        on = s < 930
        D = pd.DataFrame(index=np.arange(n))
        g = pd.DataFrame({"d": di, "h": self.h, "l": self.l, "c": self.c, "o": self.o, "v": self.v,
                          "seg": df.seg.to_numpy()})
        gr = g[rth].groupby("d"); go = g[on].groupby("d")
        D["rth_o"] = gr.o.first(); D["rth_h"] = gr.h.max(); D["rth_l"] = gr.l.min(); D["rth_c"] = gr.c.last()
        D["rth_n"] = gr.size()
        D["on_h"] = go.h.max(); D["on_l"] = go.l.min(); D["on_o"] = go.o.first()
        D["seg"] = g.groupby("d").seg.last()
        D["full"] = (D.rth_n >= 385) & (self.i_rth0 >= 0)
        # contexto previo (solo días completos; no cruzar roll)
        P = D[D.full].copy()
        same = P.seg == P.seg.shift()
        for a, b in [("prev_c", "rth_c"), ("prev_h", "rth_h"), ("prev_l", "rth_l"), ("prev_o", "rth_o")]:
            P[a] = P[b].shift().where(same)
        P["rng"] = P.rth_h - P.rth_l
        P["atr"] = P.rng.shift().rolling(14).mean()          # rango medio de los 14 días previos
        P["prev_rng"] = P.rng.shift()
        P["nr7"] = P.prev_rng <= P.rng.shift().rolling(7).min()
        P["inside"] = (P.prev_h <= P.prev_h.shift().where(same)) & (P.prev_l >= P.prev_l.shift().where(same))
        P["gap"] = P.rth_o - P.prev_c
        P["date"] = self.days[P.index]
        P["dow"] = P.date.dt.dayofweek
        self.D = P

    # ---------- ejecución y registro ----------
    def run(self, familia, params, sig_idx, direction, stop_pts, tgt_pts, exit_hm, cost=COSTO_MKT_RT_PTS,
            guardar=True):
        sig_idx = np.asarray(sig_idx, np.int64)
        m = len(sig_idx)
        bc = lambda x, t: np.broadcast_to(np.asarray(x, t), (m,)).copy()
        pnl, bars, out = simulate(self.o, self.h, self.l, self.c, self.day_id, self.smin, sig_idx,
                                  bc(direction, np.int8), bc(stop_pts, float), bc(tgt_pts, float),
                                  bc(hm2s(np.asarray(exit_hm)), np.int32), float(cost))
        return self._reg(familia, params, sig_idx, pnl, guardar)

    def run_limit(self, familia, params, sig_idx, direction, limit_px, cancel_hm, stop_pts, tgt_pts, exit_hm,
                  cost=COSTO_LMT_RT_PTS, guardar=True):
        sig_idx = np.asarray(sig_idx, np.int64)
        m = len(sig_idx)
        bc = lambda x, t: np.broadcast_to(np.asarray(x, t), (m,)).copy()
        pnl, out = simulate_limit(self.o, self.h, self.l, self.c, self.day_id, self.smin, sig_idx,
                                  bc(direction, np.int8), bc(limit_px, float), bc(hm2s(np.asarray(cancel_hm)), np.int32),
                                  bc(stop_pts, float), bc(tgt_pts, float), bc(hm2s(np.asarray(exit_hm)), np.int32),
                                  float(cost))
        return self._reg(familia, params, sig_idx, pnl, guardar)

    def _reg(self, familia, params, sig_idx, pnl, guardar):
        ok = ~np.isnan(pnl)
        yrs = self.days[self.day_id[sig_idx[ok]]].year if ok.any() else np.array([])
        st = stats_trades(pnl[ok], familia)
        st["params"] = json.dumps(params, default=str)
        p = pnl[ok]
        for a, b, tag in [(2021, 2022, "A"), (2023, 2024, "B")]:
            mm = (yrs >= a) & (yrs <= b)
            st[f"exp_{tag}"] = p[mm].mean() if mm.any() else np.nan
            st[f"wr_{tag}"] = (p[mm] > 0).mean() if mm.any() else np.nan
            st[f"n_{tag}"] = int(mm.sum())
        if guardar:
            self.registro.append(st)
        st["_pnl"] = p; st["_idx"] = sig_idx[ok]
        return st

    def guardar_registro(self, nombre):
        R = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in self.registro])
        R.to_csv(os.path.join(RES_DIR, nombre), index=False)
        return R
