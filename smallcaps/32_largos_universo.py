"""Ronda 15 (lado largo, campo primero): universo U1 de eventos y embudo automático A.
NO mira ningún precio posterior al evento (solo cierre previo y volumen de las 20 sesiones previas).
Datos: /home/user/data/largos (índice EDGAR, submissions, companyfacts, diarios de Massive)."""
import glob, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun

D = "/home/user/data/largos"
INI, FIN = "2024-10-07", "2026-09-25"
ITEMS = {"1.01", "2.01", "2.02", "7.01", "8.01"}
CAL = [str(x)[:10] for x in comun.calendario()]
POS = {d: i for i, d in enumerate(CAL)}


def sesion_siguiente(dia):          # primera sesión ≥ dia
    for d in CAL:
        if d >= dia:
            return d


def sesion_anterior(dia):           # última sesión < dia
    prev = None
    for d in CAL:
        if d >= dia:
            return prev
        prev = d


def sesiones(ts):
    """ts = hora de aceptación en Nueva York → (sesión previa cuyo cierre es anterior, sesión de entrada E1, ventana)."""
    dia, hm = ts.strftime("%Y-%m-%d"), ts.strftime("%H:%M")
    habil = dia in POS
    if habil and hm < "09:30":
        return CAL[POS[dia] - 1], dia, "pre"
    if habil and hm < "16:00":
        return CAL[POS[dia] - 1], CAL[POS[dia] + 1], "sesion"
    if habil:
        return dia, CAL[POS[dia] + 1], "post"
    return sesion_anterior(dia), sesion_siguiente(dia), "festivo"


def cargar_subs():
    fs = glob.glob(f"{D}/subs/*.parquet")
    S = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
    S["t_ny"] = pd.to_datetime(S.acceptanceDateTime, utc=True).dt.tz_convert("America/New_York")
    return S


def diarios(carpeta, desde, hasta):
    fs = sorted(f for f in glob.glob(f"{D}/{carpeta}/*.parquet") if desde <= os.path.basename(f)[:10] <= hasta)
    return pd.concat([pd.read_parquet(f).assign(fecha=os.path.basename(f)[:10]) for f in fs], ignore_index=True)


def eventos(S):
    E = S[S.form.isin(["8-K", "6-K"])].copy()
    E = E[(E.t_ny >= pd.Timestamp(INI, tz="America/New_York")) & (E.t_ny < pd.Timestamp(FIN, tz="America/New_York") + pd.Timedelta(days=1))]
    its = E["items"].fillna("").str.split(",")
    E["items_ok"] = [(f == "6-K") or bool(ITEMS & set(i)) for f, i in zip(E.form, its)]
    E = E[E.items_ok]
    x = E.t_ny.apply(sesiones)
    E["prev"], E["entrada"], E["ventana"] = [a for a, b, c in x], [b for a, b, c in x], [c for a, b, c in x]
    E = E.sort_values("t_ny")
    G = E.groupby(["cik", "entrada"]).agg(t_ny=("t_ny", "first"), prev=("prev", "first"), ventana=("ventana", "first"),
                                          forms=("form", lambda v: ",".join(v)), items=("items", lambda v: ";".join(x or "" for x in v)),
                                          accns=("accessionNumber", lambda v: ",".join(v)), docs=("primaryDocument", lambda v: ",".join(v)),
                                          name=("name", "first"), sic=("sic", "first"), category=("category", "first")).reset_index()
    return G


def asignar_ticker(G, T, DA):
    T = T.assign(cikn=pd.to_numeric(T.cik, errors="coerce")).dropna(subset=["cikn"])
    T = T[T.type.isin(["CS", "ADRC"])]
    porcik = T.groupby(T.cikn.astype(int)).apply(lambda x: list(zip(x.ticker, x.type))).to_dict()
    barra = {(r.T, r.fecha): r for r in DA.itertuples(index=False)}
    out = []
    for r in G.itertuples(index=False):
        mejor = None
        for tk, tipo in porcik.get(r.cik, []):
            b = barra.get((tk, r.prev))
            if b is not None and (mejor is None or b.v * b.vw > mejor[2].v * mejor[2].vw):
                mejor = (tk, tipo, b)
        out.append((mejor[0], mejor[1], mejor[2].c) if mejor else (None, None, np.nan))
    G["ticker"], G["tipo"], G["cierre_prev"] = [o[0] for o in out], [o[1] for o in out], [o[2] for o in out]
    return G


def acciones_previas(G, SP):
    """Acciones del último dato XBRL presentado ANTES del evento, corregidas por splits entre su fecha y la sesión previa."""
    res = []
    cache = {}
    for r in G.itertuples(index=False):
        if r.cik not in cache:
            f = f"{D}/facts/{r.cik}.parquet"
            x = pd.read_parquet(f) if os.path.exists(f) else pd.DataFrame(columns=["var"])
            cache[r.cik] = x[x["var"] == "acciones"] if len(x) else x
        a = cache[r.cik]
        if not len(a):
            res.append((np.nan, None)); continue
        a = a[a.filed < r.t_ny.strftime("%Y-%m-%d")]
        if not len(a):
            res.append((np.nan, None)); continue
        ult = a.sort_values(["end", "filed"]).iloc[-1]
        acc = a[(a.accn == ult.accn) & (a.end == ult.end)].val.sum()
        sp = SP[(SP.ticker == r.ticker) & (SP.execution_date > ult.end) & (SP.execution_date <= r.prev)]
        for s in sp.itertuples(index=False):
            acc = acc * s.split_to / s.split_from
        res.append((acc, ult.end))
    G["acciones"], G["acciones_fecha"] = [x[0] for x in res], [x[1] for x in res]
    G["mcap"] = G.acciones * G.cierre_prev
    return G


def volumen20(G, DA):
    DA = DA.assign(dv=DA.v * DA.vw)
    piv = DA.pivot_table(index="fecha", columns="T", values="dv")
    fechas = list(piv.index)
    pos = {f: i for i, f in enumerate(fechas)}
    out = []
    for r in G.itertuples(index=False):
        if r.ticker is None or r.prev not in pos or r.ticker not in piv.columns:
            out.append(np.nan); continue
        i = pos[r.prev]
        out.append(piv[r.ticker].iloc[max(0, i - 19): i + 1].fillna(0).mean())
    G["dvol20"] = out
    return G


def embudo_A(G, S):
    """A1: sin 424B en 90 días previos. A2: sin 424B/S-1/S-3/F-1/F-3 ni item 3.02 entre el día anterior y el evento.
    A3: caja + inversiones a corto ≥ 12 meses de quema o flujo operativo ≥ 0 (solo datos presentados antes)."""
    S = S.assign(fdate=S.t_ny.dt.strftime("%Y-%m-%d"))
    porcik = dict(tuple(S.groupby("cik")))
    a1, a2, a3, meses = [], [], [], []
    for r in G.itertuples(index=False):
        x = porcik[r.cik]
        t0 = r.t_ny
        ant = x[x.t_ny < t0]
        ventana90 = ant[ant.t_ny >= t0 - pd.Timedelta(days=90)]
        a1.append(not ventana90.form.str.startswith("424B").any())
        cerca = x[(x.t_ny >= t0 - pd.Timedelta(days=1)) & (x.t_ny <= t0 + pd.Timedelta(minutes=1))]
        reg = cerca.form.str.startswith("424B") | cerca.form.isin(["S-1", "S-3", "F-1", "F-3", "S-1/A", "S-3/A", "F-1/A", "F-3/A"])
        it302 = cerca["items"].fillna("").str.contains("3.02", regex=False).any() or ("3.02" in (r.items or ""))
        a2.append(not (reg.any() or it302))
        ok, m = caja_meses(r.cik, t0.strftime("%Y-%m-%d"))
        a3.append(ok); meses.append(m)
    G["A1"], G["A2"], G["A3"], G["meses_caja"] = a1, a2, a3, meses
    G["pasa_A"] = G.A1 & G.A2 & G.A3
    return G


_F = {}


def caja_meses(cik, dia):
    if cik not in _F:
        f = f"{D}/facts/{cik}.parquet"
        _F[cik] = pd.read_parquet(f) if os.path.exists(f) else pd.DataFrame(columns=["var", "val", "start", "end", "filed", "unidad"])
    x = _F[cik]
    x = x[(x.filed < dia) & (x.unidad.isin(["USD"]))]
    if not len(x):
        return False, np.nan
    fco = x[x["var"].isin(["fco", "fco2"]) & x.start.notna()].copy()
    if not len(fco):
        return False, np.nan
    fco["dias"] = (pd.to_datetime(fco.end) - pd.to_datetime(fco.start)).dt.days
    fco = fco[fco.dias.between(80, 380)].sort_values(["end", "filed", "dias"])
    if not len(fco):
        return False, np.nan
    u = fco.iloc[-1]
    quema_mes = -u.val / (u.dias / 30.44)
    if quema_mes <= 0:
        return True, np.inf
    c = x[x["var"].isin(["caja", "caja2", "caja_restr"]) & (x.end == u.end)]
    if not len(c):
        c = x[x["var"].isin(["caja", "caja2", "caja_restr"]) & (x.end <= u.end)].sort_values("end").tail(1)
        if not len(c) or c.end.iloc[-1] < (pd.Timestamp(u.end) - pd.Timedelta(days=100)).strftime("%Y-%m-%d"):
            return False, np.nan
        fin = c.end.iloc[-1]
    else:
        fin = u.end
    cc = x[x["var"].isin(["caja", "caja2"]) & (x.end == fin)]
    caja = cc.val.max() if len(cc) else x[x["var"].eq("caja_restr") & (x.end == fin)].val.max()
    inv = x[x["var"].isin(["inv_cp", "inv_cp2", "inv_cp3"]) & (x.end == fin)].groupby("var").val.max().max()
    total = caja + (inv if pd.notna(inv) else 0)
    m = total / quema_mes
    return bool(m >= 12), m


if __name__ == "__main__":
    S = cargar_subs()
    G = eventos(S)
    print("eventos 8-K/6-K agrupados:", len(G))
    DA = diarios("diario_sa", "2024-09-01", FIN)
    T = pd.read_parquet(f"{D}/tickers_cik.parquet")
    G = asignar_ticker(G, T, DA)
    print("con acción cotizando la sesión previa:", G.ticker.notna().sum())
    G = G[G.ticker.notna()].copy()
    SP = pd.read_parquet("/home/user/data/smallcaps/splits_massive.parquet")
    SP["execution_date"] = SP.execution_date.astype(str)
    G = acciones_previas(G, SP)
    G = volumen20(G, DA)
    G["filtro_tipo"] = G.tipo.eq("CS")
    G["filtro_precio"] = G.cierre_prev >= 1
    G["filtro_mcap"] = G.mcap < 300e6
    G["filtro_liq"] = G.dvol20 >= 50_000
    for k in ["filtro_tipo", "filtro_precio", "filtro_mcap", "filtro_liq"]:
        print(k, int(G[k].sum()))
    G["U1"] = G.filtro_tipo & G.filtro_precio & G.filtro_mcap & G.filtro_liq
    print("U1:", int(G.U1.sum()), "| sin dato de acciones:", int(G.acciones.isna().sum()))
    U = G[G.U1].copy()
    U = embudo_A(U, S)
    print("A1", int(U.A1.sum()), "A2", int(U.A2.sum()), "A3", int(U.A3.sum()), "pasa A", int(U.pasa_A.sum()))
    G.to_parquet(f"{D}/eventos_todos.parquet")
    U.to_parquet(f"{D}/universo_U1.parquet")
