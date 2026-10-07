"""Casos de oro del Radar: cada error real que hemos encontrado se convierte en una prueba permanente con datos reales.

Uso:  python3 tests/casos_oro.py            → todas (≈ 2-3 min, necesita red: SEC, Yahoo)
      python3 tests/casos_oro.py --rapidas  → solo las que no usan la red
Sale con código 1 si alguna falla. La rutina de la mañana (RUTINA.md, paso 1c) NO sigue si falla alguna.
Regla (1-oct-2026, pedida por el usuario): cada error nuevo que encontremos (nosotros o comparando con otros traders)
se añade aquí ANTES de darlo por corregido, con el caso real que lo destapó.
"""
import datetime as dt
import json
import os
import sys
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
import lista_diaria as l  # noqa: E402

CASOS = []


def caso(nombre, red=True):
    def deco(f):
        CASOS.append((nombre, red, f))
        return f
    return deco


def NY(fecha, h=16):
    return dt.datetime.fromisoformat(f"{fecha}T{h:02d}:00").replace(tzinfo=l.NY)


_cache = {}


def cntb():
    if "cntb" not in _cache:
        pres, *_ = l.presentaciones(1835268)
        _cache["cntb"] = (pres, l.municion(1835268, pres, NY("2026-09-29"), "CNTB", 1.83))
    return _cache["cntb"]


# ---------------------------------------------------------------- sin red
@caso("Puntuación en vivo = histórico en todos los casos (30-sep: pesos redondeados; 1-oct: datos corregidos, 1 242 casos)", red=False)
def _():
    import pandas as pd
    Z = pd.read_csv(os.path.join(RAIZ, "smallcaps", "res_30_ronda12_corregida.csv"))
    assert len(Z) == 1242, len(Z)
    peor, ter = 0, 0
    for r in Z.itertuples():
        items = "7.01,9.01" if r.solo_pr else ""
        p = l.puntuar(dict(gap=r.gap, municion=dict(venta90=bool(r.venta90), s3="x" if r.s3 else None, p424_12m=3 if r.serie else 0),
                           docs_hoy=[dict(form="8-K", items=items)] if items else []), dict(tipo=r.tipo))
        peor = max(peor, abs(p["valor"] - r.puntuacion))
        ter += p["tercio"][:3].lower() != {"alto": "alt", "medio": "med", "bajo": "baj"}[r.tercio]
    assert peor <= 0.5 and ter == 0, (peor, ter)


@caso("Catalizador viejo (LGHL 30-sep: financiación del día anterior) → la auditoría exige N", red=False)
def _():
    C = dict(cobertura=None, candidatos=[dict(sym="LGHL", gap=0.58, cierre_prev=4.51, cap=1e6, municion={"x": 1},
                                              noticias=[], catalizadores=[], docs_hoy=[])])
    err, _ = l.auditar(C, {"LGHL": dict(tipo="F", frase_en="x", frase_es="x", cifra="x")}, True)
    assert any("no hay ningún 8-K/6-K ni noticia" in e for e in err), err


@caso("Dato clínico fallido escondido en la presentación → la auditoría exige 'negativos_revisados' (CNTB 30-sep)", red=False)
def _():
    texto = "Key Secondary Endpoint – Post-Bronchodilator FEV1 on Day 7 Not Significant Δ0 mL p - NS"
    neg = l.negativos(texto)
    assert any(n["tipo"] == "dato clínico fallido" for n in neg), neg
    C = dict(cobertura=None, candidatos=[dict(sym="CNTB", gap=0.84, cierre_prev=0.99, cap=6e7, municion={"x": 1}, noticias=[], docs_hoy=[],
                                              catalizadores=[dict(partes=[dict(texto=texto, negativos=neg)])])])
    err, _ = l.auditar(C, {"CNTB": dict(tipo="B", frase_en="x", frase_es="x", cifra="x")}, True)
    assert any("NO fue significativo" in e for e in err), err


@caso("Rendimiento con el gap de la APERTURA (BKYI 29-sep: +71 % a las 9:05, +105 % al abrir)", red=False)
def _():
    L = json.load(open(os.path.join(RAIZ, "listas", "datos", "2026-09-29.json")))
    r = L["resultados"]["BKYI"]
    assert r["gap_apertura"] >= 1.0 and r["tramo_apertura"] == "≥ 50 %", r


# ---------------------------------------------------------------- con red
@caso("Hora oficial de la SEC (el JSON de las presentaciones del mismo día trae la hora NY con una 'Z' falsa; CNTB 8-K = 07:05 NY)")
def _():
    assert l.hora_oficial(1835268, "0001835268-26-000038").strftime("%Y-%m-%d %H:%M") == "2026-09-30 07:05"
    pres, _ = cntb()
    # las antiguas (corregidas por la SEC) siguen bien con la conversión UTC → NY
    p = next(x for x in pres if x["acc"] == "000183526826000028")
    assert p["hora"].strftime("%Y-%m-%d %H:%M") == "2026-08-12 16:16", p["hora"]


@caso("Shelf MIXTA: empresa $200 M + reventa de 50 000 000 acciones en el mismo F-3/A (BIYA 7-oct, verificador; antes solo se veía la reventa y sin número)")
def _():
    o = l.analizar_shelf(dict(form="F-3/A", fecha="2026-08-21", url="https://www.sec.gov/Archives/edgar/data/1944712/000121390026092611/ea0302933-f3a1_baiya.htm"))
    assert o["tipo"] == "reventa" and o.get("acciones_reventa") == 50000000 and o.get("base_usd") == 200e6 and o.get("tambien_empresa"), {k: v for k, v in o.items() if "frase" not in k}


@caso("Reventa con el nombre del inversor antes de «Selling Shareholder» (SXTC 7-oct: F-3/A 28-ago-2026 = reventa de 157 500 000 acciones de Smart Mart, pre-paid purchase a precio variable)")
def _():
    o = l.analizar_shelf(dict(form="F-3/A", fecha="2026-08-28", url="https://www.sec.gov/Archives/edgar/data/1723980/000121390026095149/ea0298922-f3a1_chinasxt.htm"))
    assert o["tipo"] == "reventa" and o.get("acciones_reventa") == 157500000 and o.get("eloc"), {k: v for k, v in o.items() if "frase" not in k}


@caso("ATM AMPLIADA: se toma la más reciente (LPCN 7-oct: 424B5 26-feb-2026 sube la ATM de A.G.P. a $50 M, quedan $39 384 424; antes se leía la de $10.6 M de 2024)")
def _():
    o = l.analizar_shelf(dict(form="424B5", fecha="2026-02-26", url="https://www.sec.gov/Archives/edgar/data/1535955/000149315226008201/form424b5.htm"))
    assert o["atm_usd"] == 50e6 and o.get("atm_restante_usd") == 39384424, o


@caso("ATM en la shelf aunque el 10-Q no la mencione: CNTB $150 M con Cantor Fitzgerald, sin usar")
def _():
    _, m = cntb()
    a = m["atm_shelf"]
    assert m["atm"] and a and a["atm_usd"] == 150e6 and a["atm_agente"] == "Cantor Fitzgerald", a
    assert any(x.get("base_usd") == 300e6 and x["tipo"] == "empresa" for x in m["shelves"])


@caso("Reventa de terceros ≠ shelf de la empresa: CNTB F-3 may-2026 = 6 130 000 acciones de selling securityholders")
def _():
    _, m = cntb()
    x = next(x for x in m["shelves"] if x["fecha"] == "2026-05-15")
    assert x["tipo"] == "reventa" and x["acciones_reventa"] == 6130000, x
    assert m["reventa_acciones"] == 6130000, m["reventa_acciones"]


@caso("Warrants sin precios de OPCIONES de empleados (CNTB $2.14 era el precio medio de opciones)")
def _():
    _, m = cntb()
    assert 2.14 not in m["warrants"], m["warrants"]


@caso("Se leen TODOS los anexos EX-99 por su tipo (CNTB 'a991.htm' y 'a992.htm') y el fallo del secundario aparece")
def _():
    pres, _ = cntb()
    p = next(x for x in pres if x["acc"] == "000183526826000038")
    partes = l.texto_catalizador(1835268, p)
    nombres = [x["archivo"] for x in partes]
    assert "a991.htm" in nombres and "a992.htm" in nombres, nombres
    assert any("Not Significant" in n["frase"] for x in partes for n in x["negativos"] if n["tipo"] == "dato clínico fallido")


@caso("Historial de catalizadores con reacción: CNTB 15-sep −32 % (cierre 1.725 → 1.17)")
def _():
    pres, _ = cntb()
    h = l.historial_catalizadores(1835268, pres, NY("2026-09-29"), "CNTB")
    r = next(x for x in h if x["fecha"].startswith("2026-09-15"))["reaccion"]
    assert -0.34 < r["cierre"] < -0.30, r


@caso("Caja que queda HOY, no a la fecha del informe (CNTB: 5.9 meses al 30-jun → ≈ 2.9 al 30-sep)")
def _():
    c = l.caja(1835268, dt.date(2026, 9, 30))
    assert c["caja"] == 27015000 and c["inversiones"] == 4471000, c
    assert 2.6 <= c["autonomia_hoy"] <= 3.2, c


@caso("Colocación privada con precio (CNTB 30-mar-2026: 6 130 000 acciones a $3.25) — lo vio el verificador, no el Radar")
def _():
    _, m = cntb()
    assert any(c["precio"] == 3.25 and c["acciones"] == 6130000 for c in m["colocaciones"]), m["colocaciones"]


@caso("Baby shelf detectada (CNTB F-3 jun-2025, General Instruction I.B.5) y lo que la empresa DICE de su caja ('at least one year')")
def _():
    _, m = cntb()
    assert any(x.get("baby_shelf") for x in m["shelves"]), [x.get("baby_shelf") for x in m["shelves"]]
    assert m["empresa_dice_caja"] and "at least one year" in m["empresa_dice_caja"], m["empresa_dice_caja"]


@caso("ELOC escondida en una reventa: FFR 55 000 000 'VWAP Shares' de Gold King Arthur")
def _():
    pres, *_ = l.presentaciones(1460702)
    m = l.municion(1460702, pres, NY("2026-09-29"), "FFR", 1.22)
    assert m["eloc"] and any(x.get("acciones_reventa") == 55000000 and x.get("eloc") for x in m["shelves"]), m["shelves"]


@caso("Reventa ajustada por contra-splits posteriores (VBIO: 51 M registradas antes de 1:25 → ~2 M)")
def _():
    cik, _ = l.cik_de("VBIO")
    pres, *_ = l.presentaciones(cik)
    m = l.municion(cik, pres, NY("2026-09-29"), "VBIO", 3.44)
    assert m["reventa_acciones"] < 5e6, m["reventa_acciones"]


@caso("Ticker nuevo sin CIK en la tabla de la SEC (FFR = antes AIXC) → se encuentra igual")
def _():
    assert l.cik_de("FFR")[0] == 1460702


@caso("Enmiendas de la misma reventa no se suman (GYGY: 3 registros de 16 072 730 acciones)")
def _():
    cik, _ = l.cik_de("GYGY")
    pres, *_ = l.presentaciones(cik)
    m = l.municion(cik, pres, NY("2026-09-25"), "GYGY", 1.2)
    assert m["reventa_acciones"] == 16072730, m["reventa_acciones"]


@caso("Registro de reventa presentado DENTRO de la ventana también cuenta (RZAI 30-sep 16:06: F-1 de 19 814 230 acciones)")
def _():
    pres, *_ = l.presentaciones(2075335)
    m = l.municion(2075335, pres, NY("2026-09-30"), "RZAI", 37.5)
    assert any(x.get("tipo") == "reventa" and x.get("acciones_reventa") == 19814230 for x in m["shelves"]), m["shelves"]


@caso("Recién listada sin 10-Q: se lee el folleto (RZAI: preferente Clase C a precio variable = tóxica; warrants a $8.00)")
def _():
    pres, *_ = l.presentaciones(2075335)
    m = l.municion(2075335, pres, NY("2026-09-30"), "RZAI", 37.5)
    assert m["toxica"] and 8.0 in m["warrants"] and m["going_concern"], (m["toxica"], m["warrants"], m["going_concern"])


@caso("Warrants ajustados por contra-split posterior al informe (VEEA: 10-Q 12-ago, contra-split 1:20 el 31-ago → $0.05 = $1.00)")
def _():
    pres, *_ = l.presentaciones(1840317)
    m = l.municion(1840317, pres, NY("2026-09-30"), "VEEA", 3.1)
    assert m.get("ajuste_splits_warrants") == 20 and 1.0 in m["warrants"] and 0.05 not in m["warrants"], (m.get("ajuste_splits_warrants"), m["warrants"])


@caso("Universo completo: NASDAQ + NYSE/NYSE American (SLND 29-sep se perdió por faltar un fichero)")
def _():
    U = l.universo()
    # vale con cualquiera de las dos fuentes completas (1-oct: nasdaqtrader nos bloqueó; la SEC cubre Nasdaq + NYSE + NYSE American)
    assert len(U) >= 5000 and (not l.universo.faltan or l.universo.fuentes.get("sec", 0) >= 6000), (len(U), l.universo.faltan, l.universo.fuentes)
    for s in ("SLND", "CNTB", "SOAR", "WHLR"):          # NYSE American, Nasdaq, NYSE y un caso de contra-splits
        assert s in U, s


@caso("Rehacer una lista publicada (--sin_actualizar) conserva sus precios, gap y premarket (VEEA 1-oct pasaba de 56 % a 44 %)")
def _():
    import shutil, tempfile
    tmp, antes = tempfile.mkdtemp(), l.DATOS
    for suf in ("", "_candidatos", "_clasif", "_verificacion"):
        src = os.path.join(antes, f"2026-10-01{suf}.json")
        if os.path.exists(src):
            shutil.copy(src, tmp)
    L0 = json.load(open(os.path.join(tmp, "2026-10-01.json")))
    try:
        l.DATOS = tmp
        l.finalizar("2026-10-01", False, sin_actualizar=True)
    finally:
        l.DATOS = antes
    L1 = json.load(open(os.path.join(tmp, "2026-10-01.json")))
    a = {x["sym"]: x for x in L0["acciones"] + L0["descartadas"]}
    b = {x["sym"]: x for x in L1["acciones"] + L1["descartadas"]}
    assert set(a) == set(b) and {x["sym"] for x in L0["acciones"]} == {x["sym"] for x in L1["acciones"]}, (sorted(a), sorted(b))
    for s_ in a:
        for k in ("precio", "gap", "premarket"):
            assert a[s_].get(k) == b[s_].get(k), (s_, k, a[s_].get(k), b[s_].get(k))
    assert L1["generado"] == L0["generado"] and L1.get("rehecho"), (L0["generado"], L1["generado"])


@caso("Splits: la lista de Yahoo omite contra-splits → se une con Massive (CRIS 1:20 del 29-sep-2023; SVRE ADS 1:13.33 del 21-feb-2025)")
def _():
    import datetime as _dt
    c = dict(l.splits_de("CRIS")); v = dict(l.splits_de("SVRE"))
    assert any(abs((d - _dt.date(2023, 9, 29)).days) <= 5 and abs(f - 0.05) < 1e-6 for d, f in c.items()), c
    assert any(abs((d - _dt.date(2025, 2, 21)).days) <= 5 and abs(f - 1 / 13.33) < 1e-3 for d, f in v.items()), v
    assert sum(1 for d in c if abs((d - _dt.date(2026, 7, 6)).days) <= 5) == 1, c          # el mismo split no se cuenta dos veces


# ---------------------------------------------------------------- pruebas por MODO del programa (1-oct-2026, mejora 1 del sistema)
# Cada forma de usar lista_diaria.py se ejercita con un día real conocido y se contrasta con una SEGUNDA FUENTE (Massive sin ajustar).
def _copia(fecha, sufijos=("", "_candidatos", "_clasif", "_verificacion")):
    import shutil, tempfile
    tmp = tempfile.mkdtemp()
    for suf in sufijos:
        p = os.path.join(l.DATOS, f"{fecha}{suf}.json")
        if os.path.exists(p):
            shutil.copy(p, tmp)
    return tmp


@caso("Modo días pasados (escanear --replay): precio real del día = apertura SIN ajustar de Massive (21, 22 y 23-sep)")
def _():
    for fecha in ("2026-09-21", "2026-09-22", "2026-09-23"):
        M = l.massive_dia_sin_ajustar(fecha)
        assert M, f"Massive no responde para {fecha}"
        for c in l.escanear_replay(fecha):
            m = M.get(c["sym"])
            if m:
                assert abs(c["precio"] / m["o"] - 1) <= 0.03, (fecha, c["sym"], c["precio"], m["o"])   # ±3 % = redondeo de Yahoo (VTGN 0.39 / 0.3861)
    U = {c["sym"] for c in l.escanear_replay("2026-09-23")}
    assert {"BENF", "WHLR", "HCTI", "MSS", "DCOY"} <= U, U


@caso("Modo días pasados (finalizar --replay) reproduce la lista publicada del 23-sep (acciones, precios, tesis, riesgo, motivos)")
def _():
    tmp, antes = _copia("2026-09-23"), l.DATOS
    L0 = json.load(open(os.path.join(tmp, "2026-09-23.json")))
    try:
        l.DATOS = tmp
        l.finalizar("2026-09-23", True)
    finally:
        l.DATOS = antes
    L1 = json.load(open(os.path.join(tmp, "2026-09-23.json")))
    a = {x["sym"]: x for x in L0["acciones"] + L0["descartadas"]}
    b = {x["sym"]: x for x in L1["acciones"] + L1["descartadas"]}
    assert [x["sym"] for x in L0["acciones"]] == [x["sym"] for x in L1["acciones"]] and set(a) == set(b), (sorted(a), sorted(b))
    for s_ in a:
        for k in ("precio", "gap", "motivo"):
            assert a[s_].get(k) == b[s_].get(k), (s_, k, a[s_].get(k), b[s_].get(k))
        # (la puntuación no se compara: la lista se publicó con los pesos del 30-sep; la vigila su propia prueba)
        assert (a[s_].get("riesgo") or {}).get("nivel") == (b[s_].get("riesgo") or {}).get("nivel"), s_


@caso("Modo resultados: R de cada acción (Yahoo) = R recalculado con Massive sin ajustar (29 y 30-sep, 11 acciones)")
def _():
    for fecha in ("2026-09-29", "2026-09-30"):
        tmp, antes = _copia(fecha, ("",)), l.DATOS
        try:
            l.DATOS = tmp
            l.resultados(fecha)
        finally:
            l.DATOS = antes
        R = json.load(open(os.path.join(tmp, f"{fecha}.json")))["resultados"]
        M = l.massive_dia_sin_ajustar(fecha)
        assert len(R) >= 4 and M, (fecha, len(R))
        for s_, v in R.items():
            m = M[s_]; o, h, c = m["o"], m["h"], m["c"]; st = o * (1 + l.STOP)
            Rm = -((st * (1 + l.DESL) - o) / o + l.COSTE) / l.STOP if h >= st else ((o - c) / o - l.COSTE) / l.STOP
            assert abs(v["R"] - Rm) <= 0.05, (fecha, s_, v["R"], round(Rm, 3))


@caso("Estudios: día hábil anterior CON festivos (GNPX 21-ene-2020 y UUU 2-sep-2025 perdían el 8-K del viernes; lo vio el verificador)", red=False)
def _():
    import pandas as pd
    sys.path.insert(0, os.path.join(RAIZ, "smallcaps"))
    import comun
    assert comun.dia_habil_anterior("2020-01-21") == pd.Timestamp("2020-01-17")
    assert comun.dia_habil_anterior("2025-09-02") == pd.Timestamp("2025-08-29")
    assert comun.dia_habil_anterior("2026-09-29") == pd.Timestamp("2026-09-28")
    Z = pd.read_csv(os.path.join(RAIZ, "smallcaps", "res_30_ronda12_corregida.csv"))
    g = Z[(Z.sym == "GNPX") & (Z.fecha == "2020-01-21")]
    assert len(g) == 1 and not bool(g.solo_pr.iloc[0]), g          # el 8-K del 17-ene (Item 1.01) cuenta → no es 'solo nota'
    import glob
    malos = [f for f in glob.glob(os.path.join(RAIZ, "smallcaps", "2[8-9]_*.py")) + glob.glob(os.path.join(RAIZ, "smallcaps", "3*_*.py"))
             if "offsets.BDay(1)) + pd.Timedelta(hours=16)" in open(f).read()]
    assert not malos, malos                                           # estudios nuevos: nunca BDay para la ventana


@caso("Estudios: precio real verificado (CPOP 10-sep-2025 = $2.10 y YAAS 27-abr-2026 = $1.445, no $0.14 / $0.29)", red=False)
def _():
    import pandas as pd
    P = pd.read_csv(os.path.join(RAIZ, "smallcaps", "res_29_precios.csv"))
    for s_, d, v in (("CPOP", "2025-09-10", 2.10), ("YAAS", "2026-04-27", 1.445)):
        x = P[(P.sym == s_) & (P.fecha == d)]
        assert len(x) == 1 and abs(x.precio_T.iloc[0] / v - 1) < 0.01, (s_, x.to_dict("records"))


@caso("Registro de pasos del trabajo de criterio: la auditoría bloquea si falta algo o si hay fuentes/anexos sin leer (desde el 2-oct)", red=False)
def _():
    C = json.load(open(os.path.join(l.DATOS, "2026-10-01_candidatos.json")))
    CL = json.load(open(os.path.join(l.DATOS, "2026-10-01_clasif.json")))
    C = dict(C, fecha="2026-10-02")                                   # mismas acciones, como si fuera un día con la regla activa
    err, _a = l.auditar(C, CL, False)
    assert sum("pasos." in e for e in err) >= len(C["candidatos"]), err   # sin pasos → bloquea cada acción
    c = next(x for x in C["candidatos"] if x["sym"] == "VEEA")
    partes = sum(len(k.get("partes", [])) for k in c.get("catalizadores", []))
    bien = dict(fuentes=["x"] * (len(c.get("catalizadores", [])) + len(c.get("noticias", []))), anexos_leidos=partes,
                negativos="ninguno, revisado", historial="14-sep fusión potencial −x %", municion="ATM Roth, ELOC", caja="agotada")
    assert l.revisar_pasos(c, dict(pasos=bien)) == []
    assert l.revisar_pasos(c, dict(pasos=dict(bien, fuentes=[]))), "fuentes vacías debe fallar"
    if partes:
        assert l.revisar_pasos(c, dict(pasos=dict(bien, anexos_leidos=partes - 1))), "un anexo sin leer debe fallar"
    if c.get("historial"):
        assert l.revisar_pasos(c, dict(pasos=dict(bien, historial="sin historial"))), "historial ignorado debe fallar"


@caso("Comprobación de citas: la frase en inglés tiene que estar LITERAL en la fuente y la cifra también (Ctrl+F automático, desde el 2-oct)")
def _():
    C = json.load(open(os.path.join(l.DATOS, "2026-09-30_candidatos.json")))
    CL = json.load(open(os.path.join(l.DATOS, "2026-09-30_clasif.json")))
    c = next(x for x in C["candidatos"] if x["sym"] == "CNTB"); cl = CL["CNTB"]
    assert l.comprobar_cita(c, cl) == [], l.comprobar_cita(c, cl)                                   # cita real del 8-K → pasa
    assert l.comprobar_cita(c, dict(cl, frase_en="the company announced a definitive agreement worth $500 million"))   # inventada
    assert l.comprobar_cita(c, dict(cl, cifra="$987 654 321"))                                      # cifra que no está
    assert l.comprobar_cita(c, dict(cl, frase_en=cl["frase_en"].replace("81%", "18%")))             # número cambiado
    C1 = json.load(open(os.path.join(l.DATOS, "2026-10-01_candidatos.json")))
    CL1 = json.load(open(os.path.join(l.DATOS, "2026-10-01_clasif.json")))
    v = next(x for x in C1["candidatos"] if x["sym"] == "VEEA")
    assert l.comprobar_cita(v, CL1["VEEA"]) == []                                                   # nota de prensa (Yahoo) → pasa


@caso("Línea de salud: pruebas, universo, fuentes, verificaciones y citas en el mensaje de cada mañana", red=False)
def _():
    C = json.load(open(os.path.join(l.DATOS, "2026-10-01_candidatos.json")))
    d = l.salud("2026-10-01", C, {}, [], ["x"], [], [], False)
    assert d["linea"].startswith("Salud: ") and "universo 6472" in d["linea"] and "1 avisos" in d["linea"], d["linea"]
    assert d["pruebas"] in ("NO EJECUTADAS HOY",) or "/" in d["pruebas"]


@caso("Catalizador: el cuerpo del 8-K se lee SIEMPRE, también con EX-99 (IPDN 6-oct: el Item 1.01 de $1.177 M solo estaba en el cuerpo)")
def _():
    partes = l.texto_catalizador(1546296, dict(acc="000143774926032105", doc="ipdn20261005_8k.htm"))
    nombres = [x["archivo"] for x in partes]
    assert "ipdn20261005_8k.htm" in nombres and "ex_1022427.htm" in nombres, nombres
    cuerpo = next(x["texto"] for x in partes if x["archivo"] == "ipdn20261005_8k.htm")
    assert "1.177 million" in cuerpo, cuerpo[:300]


@caso("Munición: convertible tóxica en el folleto de REVENTA, no en el 10-Q (OLOX 6-oct: «80% of the lowest closing price», 424B3 7-ene-2026)")
def _():
    desde = dt.datetime(2026, 10, 5, 16, 0, tzinfo=l.NY)
    pres = l.presentaciones(1023994)[0]
    m = l.municion(1023994, pres, desde, "OLOX", 0.88)
    assert m["toxica"] and m.get("toxica_fuente", {}).get("form") == "424B3", m.get("toxica_fuente")


@caso("Catalizador: en 6-K la nota de prensa puede ser EX-1, no EX-99 (AudioCodes 6-nov-2024: tm2427606d1_ex1.htm)")
def _():
    partes = l.texto_catalizador(1086434, dict(acc="000110465924114576", doc="tm2427606d1_6k.htm"))
    nombres = [x["archivo"] for x in partes]
    assert "tm2427606d1_ex1.htm" in nombres and "tm2427606d1_6k.htm" in nombres, nombres


if __name__ == "__main__":
    rapidas = "--rapidas" in sys.argv
    fallos = 0
    for nombre, red, f in CASOS:
        if rapidas and red:
            continue
        try:
            f()
            print("OK    ", nombre, flush=True)
        except Exception as e:
            fallos += 1
            print("FALLA ", nombre, "→", (str(e) or type(e).__name__)[:300], flush=True)
            traceback.print_exc(limit=1)
    print(f"\n{len(CASOS) - fallos if not rapidas else '-'} bien · {fallos} fallos")
    if not rapidas:   # la línea de salud del Radar lee este resultado (1-oct-2026)
        hoy = dt.datetime.now(l.NY)
        json.dump(dict(fecha=hoy.date().isoformat(), hora=hoy.strftime("%H:%M"), total=len(CASOS), fallos=fallos),
                  open(os.path.join(l.DATOS, "_pruebas.json"), "w"))
    sys.exit(1 if fallos else 0)
