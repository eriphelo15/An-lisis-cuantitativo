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
@caso("Puntuación en vivo = histórico en los 1 222 casos (30-sep: hasta 4.8 puntos de diferencia por pesos redondeados)", red=False)
def _():
    import pandas as pd
    S = os.path.join(RAIZ, "smallcaps")
    X = pd.read_csv(os.path.join(S, "res_18_precio_real.csv"), parse_dates=["date"])
    E = pd.read_csv(os.path.join(S, "clasificacion_catalizador.csv")).rename(columns={"cat": "tipo"})
    Z = E.merge(X, on=["sym", "fecha"])
    Z = Z[~Z.ambiguo & (Z.precio >= 1) & ~Z.tipo.isin(["C", "R", "F", "S"])]
    Z = Z.merge(pd.read_csv(os.path.join(S, "res_27_puntuacion.csv"))[["sym", "fecha", "puntuacion", "tercio"]], on=["sym", "fecha"])
    assert len(Z) == 1222, len(Z)
    peor, ter = 0, 0
    for r in Z.itertuples():
        items = "7.01,9.01" if r.solo_pr else ("1.01" if not r.cat.startswith("sin") else "")
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


@caso("Universo completo: NASDAQ + NYSE/NYSE American (SLND 29-sep se perdió por faltar un fichero)")
def _():
    U = l.universo()
    # vale con cualquiera de las dos fuentes completas (1-oct: nasdaqtrader nos bloqueó; la SEC cubre Nasdaq + NYSE + NYSE American)
    assert len(U) >= 5000 and (not l.universo.faltan or l.universo.fuentes.get("sec", 0) >= 6000), (len(U), l.universo.faltan, l.universo.fuentes)
    for s in ("SLND", "CNTB", "SOAR", "WHLR"):          # NYSE American, Nasdaq, NYSE y un caso de contra-splits
        assert s in U, s


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
    sys.exit(1 if fallos else 0)
