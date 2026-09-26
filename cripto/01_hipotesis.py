"""H1-H7 y H9 del pre-registro (HIPOTESIS_CRIPTO.md). Resultados netos de 0.05% por lado."""
import sys
import numpy as np
import pandas as pd
import base_cripto as b

C = b.COSTO
filas = []


def reg(sym, h, var, per, r):
    s = b.resumen(r)
    filas.append(dict(sym=sym, h=h, var=var, per=per, **s))


def por_periodo(sym, h, var, fechas, r):
    fechas = pd.DatetimeIndex(fechas)
    for nom, a, z in b.PER:
        m = (fechas >= pd.Timestamp(a, tz="UTC")) & (fechas <= pd.Timestamp(z + " 23:59", tz="UTC"))
        reg(sym, h, var, nom, np.asarray(r)[m])


def dev_mask(fechas):
    return pd.DatetimeIndex(fechas) <= pd.Timestamp(b.PER[0][2] + " 23:59", tz="UTC")


for sym in ["BTCUSDT", "ETHUSDT"]:
    df = b.cargar(sym)
    A, fechas = b.matriz_dias(df)
    fechas = fechas.tz_localize("UTC") if fechas.tz is None else fechas
    O, H, L, Cl = A[..., 0], A[..., 1], A[..., 2], A[..., 3]
    dev = dev_mask(fechas)

    # ---------- H1 estacionalidad horaria
    prev = np.concatenate([[np.nan], Cl[:-1, -1]])
    cierre_h = Cl[:, 59::60]                                  # (dias,24)
    base_h = np.column_stack([prev, cierre_h[:, :-1]])
    rh = np.log(cierre_h / base_h)
    signos = np.sign(np.nanmean(rh[dev], axis=0))
    tdev = np.nanmean(rh[dev], 0) / np.nanstd(rh[dev], 0) * np.sqrt(dev.sum())
    for h in range(24):
        por_periodo(sym, "H1", f"hora {h:02d} UTC (signo DEV {int(signos[h]):+d}, tDEV {tdev[h]:.1f})", fechas,
                    signos[h] * rh[:, h] - 2 * C)
    sel = np.abs(tdev) > 2
    por_periodo(sym, "H1", f"horas con |tDEV|>2: {list(np.where(sel)[0])}", fechas,
                np.nanmean(np.where(sel, signos * rh - 2 * C, np.nan), axis=1) if sel.any() else np.full(len(fechas), np.nan))

    # ---------- H7 día de la semana (retorno diario 00-24 UTC, sin costo: descriptivo) y fin de semana
    rd = np.log(Cl[:, -1] / prev)
    dow = fechas.dayofweek
    for d, n in enumerate(["lun", "mar", "mie", "jue", "vie", "sab", "dom"]):
        por_periodo(sym, "H7", f"retorno diario {n} (bruto, largo)", fechas, np.where(dow == d, rd, np.nan))

    # ---------- H4 momentum intradía
    r_prim = np.log(Cl[:, 29] / prev)
    r_resto = np.log(Cl[:, 1409] / prev)
    r_ult = np.log(Cl[:, 1439] / Cl[:, 1409])
    por_periodo(sym, "H4", "signo 1a media hora -> ultima media hora", fechas, np.sign(r_prim) * r_ult - 2 * C)
    por_periodo(sym, "H4", "signo 00:00-23:30 -> ultima media hora", fechas, np.sign(r_resto) * r_ult - 2 * C)

    # ---------- H5 momentum diario (costo por rotación)
    px = pd.Series(Cl[:, -1], index=fechas)
    rnext = np.log(px.shift(-1) / px).values
    for N in [1, 7, 14, 28]:
        pos = np.sign(np.log(px / px.shift(N))).fillna(0).values
        cost = C * np.abs(np.diff(np.concatenate([[0], pos])))
        por_periodo(sym, "H5", f"TSMOM {N} dias largo/corto", fechas, pos * rnext - cost)
        posl = (pos > 0).astype(float)
        costl = C * np.abs(np.diff(np.concatenate([[0], posl])))
        por_periodo(sym, "H5", f"TSMOM {N} dias solo largo (vs 0)", fechas, np.where(True, posl * rnext - costl, np.nan))
    por_periodo(sym, "H5", "comprar y mantener (referencia)", fechas, rnext)

    # ---------- H2 / H3 funding
    fr = b.funding(sym)
    fr = fr[fr.index.minute == 0]
    c1 = df["c"]
    ts = fr.index[(fr.index >= df.index[0] + pd.Timedelta("2h")) & (fr.index <= df.index[-1] - pd.Timedelta("25h"))]
    fr = fr.loc[ts]
    cT = c1.reindex(ts).values
    pre = np.log(cT / c1.reindex(ts - pd.Timedelta("60min")).values)
    post = np.log(c1.reindex(ts + pd.Timedelta("60min")).values / cT)
    f8 = np.log(c1.reindex(ts + pd.Timedelta("8h")).values / cT)
    f24 = np.log(c1.reindex(ts + pd.Timedelta("24h")).values / cT)
    fv = fr.values
    devf = dev_mask(ts)
    for nom, r in [("60 min antes", pre), ("60 min despues", post)]:
        for sgn, m in [("funding>0", fv > 0), ("funding<=0", fv <= 0)]:
            d = np.sign(np.nanmean(r[m & devf]))
            por_periodo(sym, "H2", f"{nom}, {sgn}, direccion DEV {int(d):+d}", ts, np.where(m, d * r - 2 * C, np.nan))
    q_hi, q_lo = np.quantile(fv[devf], 0.9), np.quantile(fv[devf], 0.1)
    for nom, r in [("8h", f8), ("24h", f24)]:
        por_periodo(sym, "H3", f"funding >= p90 DEV ({q_hi:.5f}) -> corto {nom}", ts, np.where(fv >= q_hi, -r - 2 * C, np.nan))
        por_periodo(sym, "H3", f"funding <= p10 DEV ({q_lo:.5f}) -> largo {nom}", ts, np.where(fv <= q_lo, r - 2 * C, np.nan))

    # ---------- H6 reversión tras movimientos bruscos de 5 minutos
    c5 = c1.resample("5min").last()
    r5 = np.log(c5 / c5.shift(1))
    vol = r5.rolling(288).std().shift(1)
    z = (r5 / vol).values
    c5v = c5.values
    idx5 = c5.index
    for k in [4, 6, 8]:
        for hor in [6, 12]:            # 30 y 60 min
            res, fe = [], []
            ult = -10**9
            for i in np.where(np.abs(z) > k)[0]:
                if i - ult < 12 or i + hor >= len(c5v):
                    continue
                ult = i
                res.append(-np.sign(z[i]) * np.log(c5v[i + hor] / c5v[i]) - 2 * C)
                fe.append(idx5[i])
            por_periodo(sym, "H6", f"|mov 5m| > {k} sigma, contra {hor*5} min", fe, res)

    # ---------- H9 gap CME
    chi = df.index.tz_convert("America/Chicago")
    loc = pd.Series(np.arange(len(df)), index=chi)
    res, fe, llen, tam = [], [], [], []
    viernes = pd.date_range(chi[0].normalize(), chi[-1].normalize(), freq="W-FRI")
    Hh, Ll, Cc = df["h"].values, df["l"].values, df["c"].values
    for vf in viernes:
        t_close = vf + pd.Timedelta("15h59min")
        t_open = vf + pd.Timedelta("2D17h")
        t_fin = vf + pd.Timedelta("7D15h59min")
        try:
            i_c, i_o, i_f = loc[t_close], loc[t_open], loc[t_fin]
        except KeyError:
            continue
        pf, p0 = Cc[i_c], Cc[i_o]
        g = p0 - pf
        if abs(g) / pf < 0.001:
            continue
        d = -np.sign(g)                  # hacia el cierre del viernes
        tp, sl = pf, p0 + np.sign(g) * abs(g)
        r = np.log(Cc[i_f] / p0) * d
        lleno = False
        for j in range(i_o + 1, i_f + 1):
            toca_sl = Hh[j] >= sl if g > 0 else Ll[j] <= sl
            toca_tp = Ll[j] <= tp if g > 0 else Hh[j] >= tp
            if toca_sl:                  # conservador: stop primero
                r = -abs(g) / p0
                break
            if toca_tp:
                r = abs(g) / p0
                lleno = True
                break
        res.append(r - 2 * C)
        fe.append(df.index[i_o])
        llen.append(lleno)
        tam.append(abs(g) / pf)
    res, tam, llen = np.array(res), np.array(tam), np.array(llen)
    por_periodo(sym, "H9", "gap CME 1:1 hacia cierre viernes (todos >0.1%)", fe, res)
    por_periodo(sym, "H9", "gap CME >1%", fe, np.where(tam > 0.01, res, np.nan))
    print(sym, "H9: gaps", len(res), "llenado antes del stop 1:1:", llen.mean().round(3), "(azar ~0.5)", flush=True)

out = pd.DataFrame(filas)
out.to_csv("res_01_hipotesis.csv", index=False)
pd.set_option("display.width", 250, "display.max_rows", 500, "display.max_colwidth", 70)
w = out.pivot_table(index=["h", "var"], columns=["sym", "per"], values=["bp", "t"], aggfunc="first")
print(w.round(1).to_string())
