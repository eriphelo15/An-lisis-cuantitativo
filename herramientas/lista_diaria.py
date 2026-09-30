"""Lista diaria de cortos en small caps (gappers del premarket).

Pasos (cada mañana, día hábil de EE. UU.):
  1) python3 herramientas/lista_diaria.py escanear            → listas/datos/AAAA-MM-DD_candidatos.json
     (premarket Yahoo + EDGAR desde el cierre anterior + noticias Finviz/Yahoo + munición + historial)
  2) Claude lee cada catalizador y escribe listas/datos/AAAA-MM-DD_clasif.json:
     {"TICKER": {"tipo": "H|K|B|R|F|S|C|O|N", "frase_en": "...", "frase_es": "...", "cifra": "...", "nota": "..."}}
     (definiciones: smallcaps/HIPOTESIS_SELECCION.md, ronda 2b; N = no se encontró ninguna noticia)
  3) python3 herramientas/lista_diaria.py finalizar           → listas/datos/AAAA-MM-DD.json (nivel, plan, estadística)
  4) python3 herramientas/lista_diaria.py resultados --fecha D → resultado real (setup A) de la lista del día D

Prueba con días pasados: añadir --replay --fecha AAAA-MM-DD (usa la apertura real como "premarket", EDGAR hasta las 9:10
y ninguna noticia de agencias, porque no hay histórico gratuito).
Solo criterios validados con datos (smallcaps/INFORME_SELECCION.md). Todo automático: confirmar en los enlaces.
"""
import argparse, datetime as dt, html, json, math, os, re, sys, time
import urllib.parse, urllib.request
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DATOS = os.path.join(RAIZ, "listas", "datos")
UA_SEC = {"User-Agent": "research eriphelo15 contact@example.com"}
UA_WEB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
FERIADOS = {  # NYSE, cerrado todo el día
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18",
    "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"}
GAP_LISTA, GAP_VIGILAR, PRECIO_MIN = 0.50, 0.20, 0.30
GAP_A, PRECIO_OPERABLE = 1.00, 1.00      # ronda 5: A = gap ≥ 100 %; < $1 no operable (el locate en centavos se come la ventaja)
STOP, DESL, COSTE = 0.30, 0.05, 0.01
RIESGO_ACCION = (1 + STOP) * (1 + DESL) - 1 + COSTE          # ≈ 0.375 del precio de entrada si salta el stop con deslizamiento

# Estadística histórica por nivel (setup A: corto a la apertura, stop +30 %, 5 % desliz., coste 1 %). Fuente: INFORME_SELECCION.md
ESTAD = {
    "A": dict(R=0.45, WR=0.75, gan=0.94, perd=-1.03, PF=2.74, n=56, squeeze=0.09,
              fuente="base mecánica, humo + gap ≥100 % + precio ≥ $1 · VAL 2022-26 (DEV 2015-21: +0.42R, 18 casos) · corte provisional (ronda 5)"),
    "B": dict(R=-0.02, WR=0.60, gan=0.67, perd=-1.05, PF=0.96, n=60, squeeze=0.18,
              fuente="base mecánica, humo + gap 50-100 % + precio ≥ $1 · VAL 2022-26 (DEV: +0.01R, 47 casos) · la ventaja depende de la ejecución"),
    "H20": dict(R=0.09, WR=0.65, gan=0.57, perd=-0.76, PF=1.35, n=138, squeeze=0.10,
                fuente="base mecánica, humo + gap 20-50 % + precio ≥ $1 · VAL 2022-26 (DEV: +0.02R, 99 casos) · base pequeña (ronda 6)"),
    "H<1": dict(R=0.26, WR=0.70, gan=0.90, perd=-1.25, PF=1.68, n=40, squeeze=0.28,
                fuente="base mecánica, humo + gap ≥50 % + precio < $1 · VAL 2022-26 · ANTES del locate: con $0.02 por acción queda en −0.14R (ronda 5)"),
    "VIGILAR": dict(R=0.01, WR=0.60, gan=None, perd=None, PF=1.05, n=None, squeeze=None, fuente="contrato real / FDA / otros ≈ 0R"),
    "NO": dict(R=-0.12, WR=0.49, gan=None, perd=None, PF=0.65, n=None, squeeze=None, fuente="resultados / financiación / avisos de bolsa: PF 0.6-0.7"),
    "NUNCA": dict(R=-0.04, WR=0.08, gan=None, perd=None, PF=0.23, n=13, squeeze=0.0, fuente="compra en efectivo: el precio queda anclado"),
}
TIPOS = {"H": "Humo / cosmético", "K": "Contrato real con cifra", "B": "Biotech real (FDA / datos)", "R": "Resultados",
         "F": "Financiación", "S": "Corporativo / bolsa", "C": "Compra en efectivo", "O": "Otros", "N": "Sin noticia"}
ITEMS = {"1.01": "acuerdo firmado", "1.02": "fin de acuerdo", "2.01": "compra/venta de activos", "2.02": "resultados",
         "2.03": "deuda nueva", "3.01": "aviso de bolsa", "3.02": "venta privada de acciones", "3.03": "cambio de derechos",
         "5.02": "directivos", "5.03": "estatutos (contra-split)", "5.07": "votación", "7.01": "nota de prensa",
         "8.01": "otros hechos", "9.01": "anexos"}


# ------------------------------------------------------------------ red
def get(url, sec=False, js=False, tries=3, timeout=25):
    for k in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA_SEC if sec else UA_WEB), timeout=timeout).read()
            if sec:
                time.sleep(0.12)
            t = r.decode("utf-8", "ignore")
            return json.loads(t) if js else t
        except Exception:
            time.sleep(1.5 * (k + 1))
    return None


def limpiar(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h or "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def resumen_doc(t, n=1600):
    """Texto útil de un 8-K/6-K o anexo EX-99 (salta la portada de la SEC)."""
    t = t.strip()
    if "SECURITIES AND EXCHANGE COMMISSION" in t[:800].upper():
        cab = t[:6000]
        ini = max(cab.rfind("☐"), cab.rfind("☒"), cab.rfind("Form 40-F"), cab.rfind("240.13e-4(c))"), 0)
        t = t[ini:]
        m = re.search(r"Item\s*\d\.\d\d", t[:3000])
        t = t[m.start():] if m else t[1:]
    t = re.sub(r"^(EX-99\S*\s+\d+\s+\S+\s*)", "", t)
    for _ in range(4):
        t = re.sub(r"^(EX-99\S*|Exhibit\s*99\S*|PRESS RELEASE|FOR IMMEDIATE RELEASE|News Release)\s*", "", t, flags=re.I)
    return t[:n]


# ------------------------------------------------------------------ calendario
def dia_habil_anterior(d):
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5 or d.isoformat() in FERIADOS:
        d -= dt.timedelta(days=1)
    return d


def es_habil(d):
    return d.weekday() < 5 and d.isoformat() not in FERIADOS


# ------------------------------------------------------------------ universo y premarket
def universo():
    syms = set()
    universo.faltan = []
    for u, col_etf, col_test in [("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", 6, 3),
                                 ("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", 4, 6)]:
        # 29-sep-2026: el fichero de NYSE/NYSE American (otherlisted) no se descargó y el Radar perdió SLND → más reintentos y control
        t = get(u, tries=6, timeout=40) or ""
        if len(t.splitlines()) < 1000:
            universo.faltan.append(u.rsplit("/", 1)[-1])
        for ln in t.splitlines()[1:]:
            c = ln.split("|")
            if len(c) < 7 or c[col_etf] == "Y" or c[col_test] == "Y":
                continue
            s = c[0].strip()
            if not s or not re.fullmatch(r"[A-Z]{1,5}", s):      # fuera warrants/unidades/preferentes con sufijos raros
                continue
            nombre = c[1].lower()
            if any(w in nombre for w in (" warrant", " unit", " right", "preferred", " notes")) and "ordinary" not in nombre:
                continue
            syms.add(s)          # las ADS (acciones extranjeras, p. ej. chinas: NAMI) SÍ entran; las de preferentes ya caen por "preferred"
    # fuera warrants/derechos/unidades de 5 letras cuya raíz de 4 letras también cotiza (RGTIW, ABCDR, ABCDU)
    return sorted(s for s in syms if not (len(s) == 5 and s[-1] in "WRU" and s[:4] in syms))


class Yahoo:
    def __init__(self):
        import requests
        self.s = requests.Session(); self.s.headers.update(UA_WEB)
        self.s.get("https://fc.yahoo.com", timeout=15)
        self.crumb = self.s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=15).text

    def cotizaciones(self, syms):
        out = []
        for i in range(0, len(syms), 150):
            for k in range(3):
                try:
                    r = self.s.get("https://query1.finance.yahoo.com/v7/finance/quote",
                                   params={"symbols": ",".join(syms[i:i + 150]), "crumb": self.crumb}, timeout=20).json()
                    out += r["quoteResponse"]["result"]; break
                except Exception:
                    time.sleep(2)
        return out


def cierre_ultima_sesion(s, sym, hoy):
    """Cierre oficial de la última sesión completa ANTERIOR a hoy (histórico diario de Yahoo) y último precio (incl. premarket)."""
    try:
        r = s.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                  params=dict(range="5d", interval="1m", includePrePost="true"), timeout=20).json()["chart"]["result"][0]
        d = s.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                  params=dict(range="10d", interval="1d"), timeout=20).json()["chart"]["result"][0]
        dias = [dt.datetime.fromtimestamp(x, NY).date() for x in d["timestamp"]]
        cierres = d["indicators"]["quote"][0]["close"]
        prev = next(c for f, c in sorted(zip(dias, cierres), reverse=True) if f < hoy and c)
        ult = [c for c in r["indicators"]["quote"][0]["close"] if c]
        return prev, (ult[-1] if ult else None)
    except Exception:
        return None, None


def massive_cierres(dia):
    """Cierre oficial de TODAS las acciones en `dia` (Massive, antes Polygon; plan gratis, 1 consulta; la credencial la añade el
    entorno). Fuente complementaria a Yahoo (añadida el 29-sep-2026 a petición del usuario). Devuelve {} si no está disponible."""
    import requests
    for k in range(8):
        try:
            r = requests.get(f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{dia}",
                             params=dict(adjusted="false"), timeout=(15, 60))
            if r.status_code == 429 or "exceeded" in r.text[:300]:
                time.sleep(15); continue
            return {x["T"]: x["c"] for x in (r.json().get("results") or []) if x.get("c")}
        except Exception:
            time.sleep(10)
    return {}


def tradingview_premarket(minimo=15):
    """Segunda fuente de gappers del premarket (escáner público de TradingView, añadido el 29-sep-2026 tras perder SLND).
    Devuelve {ticker: (precio_premarket, cambio_%)} de acciones de NASDAQ/NYSE/AMEX con cambio premarket ≥ `minimo` %."""
    import requests
    body = {"filter": [{"left": "type", "operation": "equal", "right": "stock"},
                       {"left": "exchange", "operation": "in_range", "right": ["NASDAQ", "NYSE", "AMEX"]},
                       {"left": "premarket_change", "operation": "greater", "right": minimo}],
            "columns": ["name", "premarket_close", "premarket_change"],
            "sort": {"sortBy": "premarket_change", "sortOrder": "desc"}, "range": [0, 300]}
    for k in range(3):
        try:
            r = requests.post("https://scanner.tradingview.com/america/scan", json=body, timeout=20).json()
            return {x["d"][0]: (x["d"][1], x["d"][2]) for x in r.get("data", []) if x["d"][1]}
        except Exception:
            time.sleep(5)
    return None


def escanear_vivo():
    y = Yahoo()
    U = universo()
    cot = y.cotizaciones(U)
    escanear_vivo.cobertura = dict(universo=len(U), cotizadas=len(cot), pct=round(len(cot) / max(len(U), 1), 4),
                                   ficheros_faltan=list(universo.faltan))
    hoy = dt.datetime.now(NY).date()
    MS = massive_cierres(dia_habil_anterior(hoy))
    escanear_vivo.cobertura["massive"] = len(MS)
    cand = []
    for q in cot:
        estado = q.get("marketState")
        pre = estado in ("PRE", "PREPRE")
        px = q.get("preMarketPrice") if pre else q.get("regularMarketOpen") or q.get("regularMarketPrice")
        # 1) red amplia: antes de la apertura Yahoo pone el cierre de AYER en regularMarketPrice y el de ANTEAYER en
        #    regularMarketPreviousClose (29-sep: KOD +171 % contra el viernes y estaba −2.5 %), pero no siempre de forma
        #    fiable (SLND 29-sep: +58 % real y quedó fuera) → se usan los dos campos y se verifica en el paso 2.
        refs = [x for x in (q.get("regularMarketPrice") if pre else None, q.get("regularMarketPreviousClose"),
                            MS.get(q["symbol"])) if x]
        if not px or px < PRECIO_MIN or not refs or max(px / r - 1 for r in refs) < GAP_VIGILAR - 0.05:
            continue
        # 2) verificación con el cierre oficial de la última sesión (histórico diario) y el último precio real
        prev, ult = cierre_ultima_sesion(y.s, q["symbol"], hoy)
        if prev is None:
            prev = refs[0]
        if pre and ult:
            px = ult
        cm = MS.get(q["symbol"])
        # split efectivo hoy (29-sep: CDT, AGRZ, ONMD, TRUG, VRME salían +900-2400 %): el histórico y Massive dan el cierre SIN
        # ajustar; la cotización de Yahoo sí lo ajusta → si difieren ×2 o más, se usa el factor entero del split
        # antes de la apertura solo regularMarketPrice (= cierre de AYER); regularMarketPreviousClose es el de ANTEAYER y un día de
        # +86 % parecía un split (30-sep: BKYI y SDEV salían +77 % / +71 % y en realidad bajaban −11 % / −15 %)
        qref = [x for x in ((q.get("regularMarketPrice"),) if pre else (q.get("regularMarketPreviousClose"),)) if x]
        split = None
        for r in qref:
            f = r / prev
            if (f >= 1.9 or f <= 0.55) and (not cm or abs(cm / prev - 1) < 0.02):
                split = round(f) if f >= 1.9 else round(1 / f)
                prev, cm = (prev * split, cm * split if cm else cm) if f >= 1.9 else (prev / split, cm / split if cm else cm)
                break
        gap = px / prev - 1
        if (gap >= GAP_VIGILAR or (cm and px / cm - 1 >= GAP_VIGILAR)) and px >= PRECIO_MIN:
            cand.append(dict(sym=q["symbol"], nombre=q.get("longName") or q.get("shortName") or "", precio=round(px, 4),
                             cierre_prev=prev, cierre_massive=cm, gap=round(gap, 4), cap=q.get("marketCap"),
                             vol_pre=q.get("preMarketVolume") or q.get("regularMarketVolume"), acciones=q.get("sharesOutstanding"),
                             bolsa=q.get("fullExchangeName"), estado=estado, split_hoy=split))
    # 3) segunda fuente de gappers: TradingView. Lo que TradingView ve con ≥ 20 % y el escáner no, se verifica y se añade.
    TV = tradingview_premarket()
    escanear_vivo.cobertura["tradingview"] = None if TV is None else len(TV)
    solo_tv = []
    ya = {c["sym"] for c in cand}
    qd = {q["symbol"]: q for q in cot}
    for sym, (ptv, chg) in (TV or {}).items():
        if chg < GAP_VIGILAR * 100 or sym in ya:
            continue
        q = qd.get(sym)
        if q is None:
            motivo = "sin cotización de Yahoo" if sym in U else "fuera del universo: ETF, warrant, preferente o no listada"
            solo_tv.append(f"{sym} +{chg:.0f} % ({motivo}) → revisar a mano")
            continue
        prev, ult = cierre_ultima_sesion(y.s, sym, hoy)
        px = ult or ptv
        cm = MS.get(sym)
        prev = prev or cm
        if not prev or px < PRECIO_MIN:
            solo_tv.append(f"{sym} +{chg:.0f} % (sin cierre anterior o precio < ${PRECIO_MIN})"); continue
        gap = px / prev - 1
        if gap < GAP_VIGILAR:
            solo_tv.append(f"{sym} +{chg:.0f} % en TradingView pero {gap:+.0%} con el cierre oficial"); continue
        cand.append(dict(sym=sym, nombre=q.get("longName") or q.get("shortName") or "", precio=round(px, 4),
                         cierre_prev=prev, cierre_massive=cm, gap=round(gap, 4), cap=q.get("marketCap"),
                         vol_pre=q.get("preMarketVolume") or q.get("regularMarketVolume"), acciones=q.get("sharesOutstanding"),
                         bolsa=q.get("fullExchangeName"), estado=q.get("marketState"), fuente="TradingView"))
        solo_tv.append(f"{sym} +{gap:.0%}: AÑADIDA (solo la veía TradingView; revisar por qué Yahoo no)")
    escanear_vivo.cobertura["solo_tradingview"] = solo_tv
    return cand


def escanear_replay(fecha):
    import pandas as pd
    E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
    E = E[E.date == pd.Timestamp(fecha)]
    f = {s: factor_split(s, fecha) for s in E.sym}          # Yahoo ajusta por splits posteriores → precio real del día
    return [dict(sym=r.sym, nombre="", precio=round(float(r.open) * f[r.sym], 4), cierre_prev=float(r.pc) * f[r.sym], gap=round(float(r.gap), 4),
                 cap=None, vol_pre=None, bolsa="", estado="REPLAY") for r in E.itertuples() if r.open * f[r.sym] >= PRECIO_MIN]


def factor_split(sym, fecha):
    """Producto de los ratios de los splits posteriores al mes de `fecha` (splits.parquet trae la fecha como día 1 del mes)."""
    import pandas as pd
    global _SP
    if "_SP" not in globals():
        _SP = pd.read_parquet("/home/user/data/smallcaps/splits.parquet"); _SP["t"] = pd.to_datetime(_SP.t)
    d = pd.Timestamp(fecha); g = _SP[_SP.sym == sym]
    return float(g[g.t > pd.Timestamp(d.year, d.month, 1)].ratio.prod())


# ------------------------------------------------------------------ SEC
_TK = None


def cik_de(sym):
    global _TK
    if _TK is None:
        _TK = {v["ticker"].upper(): (v["cik_str"], v["title"]) for v in (get("https://www.sec.gov/files/company_tickers.json", sec=True, js=True) or {}).values()}
    return _TK.get(sym.upper().replace("-", "."), _TK.get(sym.upper(), (None, None)))


def presentaciones(cik):
    d = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", sec=True, js=True) or {}
    r = d.get("filings", {}).get("recent", {})
    out = []
    for i in range(len(r.get("form", []))):
        t = r["acceptanceDateTime"][i]
        try:
            hora = dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(NY)
        except Exception:
            continue
        acc = r["accessionNumber"][i].replace("-", "")
        out.append(dict(form=r["form"][i], hora=hora, fecha=r["filingDate"][i], items=r.get("items", [""] * 99999)[i] or "",
                        acc=acc, doc=r["primaryDocument"][i],
                        url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{r['primaryDocument'][i]}"))
    return out, d.get("name", ""), d.get("sicDescription", ""), d.get("stateOfIncorporation", "")


def texto_catalizador(cik, p):
    idx = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/index.json", sec=True, js=True) or {}
    docs = [i["name"] for i in idx.get("directory", {}).get("item", []) if i["name"].lower().endswith((".htm", ".html", ".txt"))]
    ex = [n for n in docs if re.search(r"ex[-_]?99|ex991|exhibit99|dex99", n.lower())]
    partes = []
    for n in (ex[:2] or [p["doc"]]):
        t = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/{n}", sec=True)
        if t:
            partes.append(dict(archivo=n, url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/{n}",
                               texto=resumen_doc(limpiar(t))))
    return partes


def municion(cik, pres, desde, sym, precio):
    hoy = desde.date()
    ant = [p for p in pres if p["hora"] < desde]
    dias = lambda p: (hoy - p["hora"].date()).days
    m = dict(venta90=any(p["form"].startswith("424B") and dias(p) <= 90 for p in ant),
             s3=next((p["fecha"] for p in ant if p["form"] in ("S-3", "S-3/A", "F-3", "F-3/A", "S-3ASR") and dias(p) <= 3 * 365), None),
             s1=next((p["fecha"] for p in ant if p["form"] in ("S-1", "S-1/A", "F-1", "F-1/A") and dias(p) <= 365), None),
             ventas_12m=sum(1 for p in ant if p["form"] in ("424B4", "424B5") and dias(p) <= 365),
             aviso_bolsa=any("3.01" in p["items"] for p in ant if dias(p) <= 365),
             contrasplits_2a=sum(1 for p in ant if "5.03" in p["items"] and dias(p) <= 730))
    m["ultimas_ventas"] = [dict(form=p["form"], fecha=p["fecha"], url=p["url"]) for p in ant if p["form"] in ("424B4", "424B5")][:4]
    # último 10-Q/10-K: ATM, convertible tóxica, going concern, warrants (texto)
    per = [p for p in ant if p["form"] in ("10-Q", "10-K", "10-Q/A", "10-K/A", "20-F")]
    m.update(atm=False, toxica=False, going_concern=False, warrants=[])
    if per:
        t = limpiar(get(per[0]["url"], sec=True) or "")
        m["informe"] = dict(form=per[0]["form"], fecha=per[0]["fecha"], url=per[0]["url"])
        m["atm"] = bool(re.search(r"at-the-market|at the market offering|equity distribution agreement", t, re.I))
        m["eloc"] = bool(re.search(r"equity line|equity purchase agreement|standby equity|purchase agreement with (lincoln park|yorkville|ya ii)", t, re.I))
        m["toxica"] = bool(re.search(r"not determinable|variable conversion|% of the (average of the )?(three |five )?lowest|lowest (daily )?(vwap|trading price)", t, re.I))
        m["going_concern"] = bool(re.search(r"substantial doubt", t, re.I))
        ej = sorted({round(float(x), 2) for x in re.findall(r"exercise price[^$.]{0,60}\$\s?([0-9]+(?:\.[0-9]+)?)", t, re.I) if 0.01 < float(x) < 10000})
        m["warrants"] = ej[:8]
        m["warrants_en_dinero"] = bool(precio and any(e < precio for e in ej))   # ojo: sin ajustar por contra-splits posteriores
    return m


# ------------------------------------------------------------------ noticias (vivo)
def noticias(sym, desde, hasta=None):
    out = []
    t = get(f"https://finviz.com/quote.ashx?t={sym}&p=d")
    if t:
        dia = None
        i0 = t.find('id="news-table"')
        i1 = t.find("</table>", i0) if i0 >= 0 else -1           # toda la tabla (antes se cortaba a 200 000 caracteres y se perdían noticias)
        for fila in re.findall(r'(?s)<tr[^>]*>(.*?)</tr>', t[i0:i1 if i1 > 0 else None] if i0 >= 0 else ""):
            f = re.search(r'<td[^>]*>\s*([^<]+?)\s*</td>', fila)
            a = re.search(r'<a[^>]*class="tab-link-news"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', fila)
            fuente = re.search(r'<span[^>]*>\(([^)]+)\)</span>', fila)
            if not (f and a):
                continue
            txt = f.group(1).strip()
            m = re.match(r"([A-Za-z]{3}-\d{2}-\d{2})\s+(\d{1,2}:\d{2}[AP]M)", txt)
            if m:
                dia = dt.datetime.strptime(m.group(1), "%b-%d-%y").date(); hh = m.group(2)
            elif txt.lower().startswith("today"):
                dia = desde.date(); hh = txt.split()[-1]
            else:
                hh = txt
            if dia is None:
                continue
            try:
                h = dt.datetime.combine(dia, dt.datetime.strptime(hh, "%I:%M%p").time(), NY)
            except Exception:
                continue
            if h >= desde and (hasta is None or h <= hasta):
                out.append(dict(hora=h.strftime("%Y-%m-%d %H:%M"), titular=html.unescape(a.group(2)).strip(), url=urllib.parse.urljoin("https://finviz.com/", a.group(1)),
                                fuente=fuente.group(1) if fuente else "Finviz"))
    if not out:
        t = get(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={sym}&region=US&lang=en-US") or ""
        for it in re.findall(r"(?s)<item>(.*?)</item>", t):
            ti = re.search(r"<title>(.*?)</title>", it); li = re.search(r"<link>(.*?)</link>", it); pd_ = re.search(r"<pubDate>(.*?)</pubDate>", it)
            try:
                h = dt.datetime.strptime(pd_.group(1), "%a, %d %b %Y %H:%M:%S %z").astimezone(NY)
            except Exception:
                continue
            if h >= desde and (hasta is None or h <= hasta):
                out.append(dict(hora=h.strftime("%Y-%m-%d %H:%M"), titular=html.unescape(ti.group(1)), url=li.group(1), fuente="Yahoo"))
    return out[:15]                                  # (antes [:8] sin límite superior: en días pasados se perdían noticias)


# ------------------------------------------------------------------ pasos
def ruta(fecha, suf=""):
    os.makedirs(DATOS, exist_ok=True)
    return os.path.join(DATOS, f"{fecha}{suf}.json")


def escanear(fecha, replay, corte_hhmm=None):
    d = dt.date.fromisoformat(fecha)
    if not es_habil(d):
        print(f"{fecha}: mercado cerrado (fin de semana o festivo). Sin lista."); return
    desde = dt.datetime.combine(dia_habil_anterior(d), dt.time(16, 0), NY)
    corte = dt.datetime.combine(d, dt.time(9, 10), NY) if replay else dt.datetime.now(NY)
    if corte_hhmm:                                   # rehacer un día en vivo con el corte de documentos de la mañana
        hh, mm = map(int, corte_hhmm.split(":")); corte = dt.datetime.combine(d, dt.time(hh, mm), NY)
    cand = escanear_replay(fecha) if replay else escanear_vivo()
    cand.sort(key=lambda c: -c["gap"])
    print(f"{len(cand)} candidatos con gap ≥ {GAP_VIGILAR:.0%}", flush=True)
    for c in cand:
        cik, titulo = cik_de(c["sym"])
        c["cik"] = cik
        if not c["nombre"]:
            c["nombre"] = titulo or ""
        c["catalizadores"], c["docs_hoy"], c["noticias"] = [], [], []
        if cik:
            pres, nombre, sic, estado = presentaciones(cik)
            c["nombre"] = c["nombre"] or nombre
            c["sector"] = sic
            hoy = [p for p in pres if desde < p["hora"] <= corte]
            c["docs_hoy"] = [dict(form=p["form"], hora=p["hora"].strftime("%Y-%m-%d %H:%M"), items=p["items"], url=p["url"],
                                  items_es="; ".join(f"{i} {ITEMS.get(i, '')}" for i in p["items"].split(",") if i)) for p in hoy]
            profundo = c["gap"] >= GAP_VIGILAR          # desde el 29-sep: análisis completo también para los gappers de 20-50 %
            for p in hoy:
                if p["form"] in ("8-K", "8-K/A", "6-K", "6-K/A") and profundo:
                    c["catalizadores"].append(dict(form=p["form"], hora=p["hora"].strftime("%Y-%m-%d %H:%M"), items=p["items"],
                                                   url=p["url"], partes=texto_catalizador(cik, p)))
            c["venta_hoy"] = any(p["form"].startswith("424B") for p in hoy)
            c["municion"] = municion(cik, pres, desde, c["sym"], c["precio"]) if profundo else {}
            if c.get("cap") is None and profundo:
                fr = get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/dei/EntityCommonStockSharesOutstanding.json", sec=True, js=True)
                try:
                    v = max(fr["units"]["shares"], key=lambda f: f["end"])["val"]; c["cap"] = v * c["precio"]
                except Exception:
                    pass
        if c["gap"] >= GAP_VIGILAR:                    # noticias solo hasta el corte (también en días de prueba)
            c["noticias"] = noticias(c["sym"], desde, corte)
        print(f"  {c['sym']:6} gap {c['gap']:+.0%}  docs hoy {len(c['docs_hoy'])}  catalizadores {len(c['catalizadores'])}  noticias {len(c['noticias'])}", flush=True)
    out = dict(fecha=fecha, generado=dt.datetime.now(NY).strftime("%Y-%m-%d %H:%M"), replay=replay,
               desde=desde.strftime("%Y-%m-%d %H:%M"), corte=corte.strftime("%Y-%m-%d %H:%M"),
               cobertura=None if replay else getattr(escanear_vivo, "cobertura", None), candidatos=cand)
    json.dump(out, open(ruta(fecha, "_candidatos"), "w"), ensure_ascii=False, indent=1, default=str)
    print("→", ruta(fecha, "_candidatos"))


def nivel(c, cl):
    t = cl.get("tipo", "N")
    if c["gap"] < GAP_LISTA:
        return "VIGILAR"
    if t == "C":
        return "NUNCA"
    if t in ("R", "F", "S") or c.get("venta_hoy"):
        return "NO"
    if t == "H":
        if (c.get("precio") or 0) < PRECIO_OPERABLE:
            return "VIGILAR"
        return "A" if c["gap"] >= GAP_A else "B"
    return "VIGILAR"


TIPOS_OK = set("CFRBKHSON")


def auditar(C, CL, replay):
    """Control de calidad antes de publicar. Errores = la lista NO se publica hasta corregirlos."""
    err, av = [], []
    cob = C.get("cobertura")
    if not replay:
        if not cob:
            err.append("Sin dato de cobertura del escáner: repetir 'escanear'")
        elif cob.get("ficheros_faltan") or cob["universo"] < 5000:
            err.append(f"Universo incompleto ({cob['universo']} tickers; faltan {cob.get('ficheros_faltan')}): repetir 'escanear' "
                       "(29-sep: faltó el fichero de NYSE/NYSE American y se perdió SLND)")
        elif cob["pct"] < 0.97:
            err.append(f"Cobertura del escáner {cob['pct']:.1%} ({cob['cotizadas']}/{cob['universo']}): faltan cotizaciones, repetir 'escanear'")
    if not replay and cob and cob.get("tradingview") is None:
        av.append("TradingView no respondió: gappers sin contrastar con la segunda fuente")
    for x in (cob or {}).get("solo_tradingview", []):
        av.append("Segunda fuente (TradingView): " + x)
    if not replay and cob and not cob.get("massive"):
        av.append("Massive no respondió: cierres de ayer sin contrastar con la segunda fuente")
    for c in C["candidatos"]:
        s, cl = c["sym"], CL.get(c["sym"])
        if not cl:
            err.append(f"{s}: gap {c['gap']:+.0%} sin clasificar"); continue
        t = cl.get("tipo")
        if t not in TIPOS_OK:
            err.append(f"{s}: tipo '{t}' no válido")
        fuentes = len(c.get("noticias", [])) + len(c.get("catalizadores", []))
        if t == "N" and fuentes and not cl.get("fuentes_abiertas"):
            err.append(f"{s}: 'sin noticia' pero hay {fuentes} titular(es)/8-K: abrirlos todos y anotar 'fuentes_abiertas'")
        if t != "N" and (not cl.get("frase_en") or not cl.get("frase_es") or not cl.get("cifra")):
            err.append(f"{s}: falta frase original, traducción o cifra con unidad")
        if not replay and not c.get("municion"):
            err.append(f"{s}: sin análisis de munición: repetir 'escanear'")
        if c.get("cap") is None:
            av.append(f"{s}: capitalización desconocida")
        cm = c.get("cierre_massive")
        if not replay and cm and abs(c["cierre_prev"] / cm - 1) > 0.02:
            err.append(f"{s}: cierre anterior Yahoo {c['cierre_prev']} vs Massive {cm} (difieren > 2 %): comprobar cuál es el correcto (¿split?)")
        if not replay and not cm:
            av.append(f"{s}: sin cierre de Massive para contrastar")
        if t == "N" and not replay and not cl.get("fuentes_abiertas"):
            av.append(f"{s}: sin ninguna noticia; confirmar a mano en Finviz/Yahoo")
    return err, av


def finalizar(fecha, replay, forzar=False):
    C = json.load(open(ruta(fecha, "_candidatos")))
    cl_f = ruta(fecha, "_clasif")
    CL = json.load(open(cl_f)) if os.path.exists(cl_f) else {}
    if not replay and C["candidatos"]:                       # precio del premarket actualizado
        try:
            q = {x["symbol"]: x for x in Yahoo().cotizaciones([c["sym"] for c in C["candidatos"]])}
            for c in C["candidatos"]:
                x = q.get(c["sym"], {})
                # con el mercado abierto, el gap es el de la apertura (como en escanear), no el cambio del momento
                px = x.get("preMarketPrice") if x.get("marketState") in ("PRE", "PREPRE") else x.get("regularMarketOpen") or x.get("regularMarketPrice")
                if px:
                    c["precio"] = round(px, 4); c["gap"] = round(px / c["cierre_prev"] - 1, 4)
        except Exception as e:
            print("sin actualizar precios:", e)
    err, av = auditar(C, CL, replay)
    for e in err:
        print("ERROR:", e)
    for a in av:
        print("aviso:", a)
    if err and not forzar:
        sys.exit("Auditoría con errores: lista NO generada. Corregir y repetir (o --forzar si es imposible corregir a tiempo).")
    lista, vigilar = [], []
    orden = {"A": 0, "B": 1, "VIGILAR": 2, "NO": 3, "NUNCA": 4}
    for c in C["candidatos"]:
        cl = CL.get(c["sym"], {})
        t = cl.get("tipo", "N")
        if c["gap"] < GAP_LISTA:     # 20-50 %: ficha completa, nivel solo informativo (NO/Nunca si el catalizador lo indica)
            nv = "NUNCA" if t == "C" else "NO" if (t in ("R", "F", "S") or c.get("venta_hoy")) else "VIGILAR"
        else:
            nv = nivel(c, cl)
        avisos = []
        # (aviso de capitalización < $30 M retirado el 28-sep: era un artefacto de precios ajustados por splits, ronda 5)
        if c.get("venta_hoy"):
            avisos.append("424B presentado HOY: la empresa está vendiendo acciones en esta subida")
        if cl.get("tipo") == "H" and (c.get("precio") or 0) < PRECIO_OPERABLE:
            avisos.append("Precio < $1: con un locate normal ($0.02 por acción) la ventaja histórica pasa a negativa (ronda 5) → no operable")
        if cl.get("tipo") == "H" and not c.get("catalizadores"):
            avisos.append("Humo solo en nota de prensa, sin 8-K/6-K (caso no medido por separado)")
        if cl.get("tipo") == "N":
            avisos.append("Sube sin ninguna noticia encontrada: caso no medido → solo vigilar")
        m = c.get("municion", {})
        if m.get("toxica"):
            avisos.append("Convertible de precio variable (tóxica) en el último informe")
        # avisos informativos de la ronda 11 (29-sep, caso BKYI): NO validados → no cambian el nivel
        acc = c.get("acciones")          # acciones en circulación de Yahoo (sin estimar desde la capitalización: BKYI salía 0.82 M vs 1.44 M)
        if acc and acc < 5e6:
            avisos.append(f"Muy pocas acciones en circulación ({acc / 1e6:.2f} M): cualquier volumen dispara la rotación "
                          "(rotación > 10× = el corto pierde, validado). Como filtro previo NO validado (ronda 11)")
        if m and t not in ("F", "C") and not (m.get("venta90") or m.get("s3") or m.get("atm") or m.get("eloc") or m.get("warrants_en_dinero")):
            avisos.append("Sin munición activa (sin venta 424B en 90 días, sin S-3, ATM, ELOC ni warrants por debajo del precio): "
                          "no hay vendedor de acciones de la empresa. Como filtro NO validado (ronda 11)")
        entrada = c["precio"]
        if c["gap"] < GAP_LISTA:
            est = ESTAD["H20"] if t == "H" and (entrada or 0) >= PRECIO_OPERABLE else ESTAD[nv]
        elif nv == "VIGILAR" and t == "H" and (entrada or 0) < PRECIO_OPERABLE:
            est = ESTAD["H<1"]
        else:
            est = ESTAD[nv]
        (lista if c["gap"] >= GAP_LISTA else vigilar).append(dict(sym=c["sym"], nombre=c["nombre"], sector=c.get("sector", ""), precio=entrada, cierre_prev=c["cierre_prev"],
                          gap=c["gap"], cap=c.get("cap"), acciones=acc, vol_pre=c.get("vol_pre"), nivel=nv, clasif=dict(cl, tipo_es=TIPOS.get(cl.get("tipo", "N"), "")),
                          catalizadores=[dict(form=k["form"], hora=k["hora"], items=k["items"], url=k["url"],
                                              anexos=[dict(archivo=p["archivo"], url=p["url"]) for p in k["partes"]]) for k in c.get("catalizadores", [])],
                          docs_hoy=c.get("docs_hoy", []), noticias=c.get("noticias", []), municion=m, venta_hoy=c.get("venta_hoy", False),
                          # referencia de costes (información de campo, no instrucción de ejecución):
                          # cuánto R de la base mecánica consume cada $0.01 de locate por acción
                          costes=dict(locate_1c_R=round(0.01 / (STOP * entrada), 3) if entrada else None),
                          estad=est, avisos=avisos))
    lista.sort(key=lambda x: (orden[x["nivel"]], -x["gap"]))
    vigilar.sort(key=lambda x: -x["gap"])
    out = dict(fecha=fecha, generado=dt.datetime.now(NY).strftime("%Y-%m-%d %H:%M"), replay=replay, desde=C["desde"], corte=C["corte"],
               reglas=dict(gap_lista=GAP_LISTA, gap_vigilar=GAP_VIGILAR, stop=STOP, deslizamiento=DESL, coste=COSTE, riesgo_accion=RIESGO_ACCION),
               lista=lista, vigilar=vigilar, resultados=None,
               auditoria=dict(errores=err, avisos=av, cobertura=C.get("cobertura"), forzada=bool(err and forzar)))
    json.dump(out, open(ruta(fecha), "w"), ensure_ascii=False, indent=1, default=str)
    print("→", ruta(fecha), "|", ", ".join(f"{x['sym']}:{x['nivel']}" for x in lista), "| vigilar", len(vigilar))


def resultados(fecha):
    """Resultado real de cada acción de la lista (setup A) para validar la lista con el tiempo."""
    import yfinance as yf
    L = json.load(open(ruta(fecha)))
    d = dt.date.fromisoformat(fecha)
    res = {}
    for x in L["lista"] + [v for v in L.get("vigilar", []) if "precio" in v]:
        try:
            h = yf.download(x["sym"], start=d.isoformat(), end=(d + dt.timedelta(days=5)).isoformat(), progress=False, auto_adjust=False)
            if hasattr(h.columns, "levels"):
                h.columns = h.columns.get_level_values(0)
            h = h[h.index.date == d]
            if h.empty:
                continue
            o, hi, lo, cl = (float(h[k].iloc[0]) for k in ("Open", "High", "Low", "Close"))
            stop = o * (1 + STOP)
            R = -((stop * (1 + DESL) - o) / o + COSTE) / STOP if hi >= stop else ((o - cl) / o - COSTE) / STOP
            res[x["sym"]] = dict(apertura=o, maximo=hi, minimo=lo, cierre=cl, R=round(R, 3), subida_max=round(hi / o - 1, 3),
                                 caida_cierre=round(cl / o - 1, 3))
        except Exception as e:
            print(x["sym"], e)
    L["resultados"] = res
    json.dump(L, open(ruta(fecha), "w"), ensure_ascii=False, indent=1, default=str)
    print("resultados", fecha, {k: v["R"] for k, v in res.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("paso", choices=["escanear", "finalizar", "resultados"])
    ap.add_argument("--fecha", default=dt.datetime.now(NY).date().isoformat())
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--corte", help="HH:MM: solo documentos/noticias hasta esa hora (para rehacer un día ya abierto)")
    ap.add_argument("--forzar", action="store_true", help="publicar aunque la auditoría tenga errores (queda anotado)")
    a = ap.parse_args()
    {"escanear": lambda: escanear(a.fecha, a.replay, a.corte), "finalizar": lambda: finalizar(a.fecha, a.replay, a.forzar),
     "resultados": lambda: resultados(a.fecha)}[a.paso]()
