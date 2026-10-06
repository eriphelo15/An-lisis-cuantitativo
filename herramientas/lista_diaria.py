"""Lista diaria de cortos en small caps (gappers del premarket).

Pasos (cada mañana, día hábil de EE. UU.):
  1) python3 herramientas/lista_diaria.py escanear            → listas/datos/AAAA-MM-DD_candidatos.json
     (premarket Yahoo + EDGAR desde el cierre anterior + noticias Finviz/Yahoo + munición + historial)
  2) Claude lee cada catalizador y escribe listas/datos/AAAA-MM-DD_clasif.json:
     {"TICKER": {"tipo": "H|K|B|R|F|S|C|O|N", "frase_en": "...", "frase_es": "...", "cifra": "...", "nota": "..."}}
     (definiciones: smallcaps/HIPOTESIS_SELECCION.md, ronda 2b; N = no se encontró ninguna noticia)
  3) python3 herramientas/lista_diaria.py finalizar           → listas/datos/AAAA-MM-DD.json (filtro de campo, puntuación de la
     tesis 0-100 validada en la ronda 12, riesgo estructural aparte, caja, premarket, textos de los 8-K; descartadas con su motivo)
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
PRECIO_OPERABLE = 1.00      # ronda 5: < $1 no operable (el locate en centavos se come la ventaja)
STOP, DESL, COSTE = 0.30, 0.05, 0.01
RIESGO_ACCION = (1 + STOP) * (1 + DESL) - 1 + COSTE          # ≈ 0.375 del precio de entrada si salta el stop con deslizamiento

# (desde el 30-sep-2026 no hay letras A/B/Vigilar: el nivel lo sustituye la puntuación de la tesis, ronda 12, más abajo)
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
    # 1-oct-2026: nasdaqtrader.com bloqueó nuestras descargas (protección anti-bots "Incapsula") → segunda fuente SIEMPRE: la lista
    # oficial de la SEC con la bolsa de cada ticker (Nasdaq / NYSE, incluye NYSE American). Se suman las dos.
    universo.fuentes = {"nasdaqtrader": len(syms)}
    d = get("https://www.sec.gov/files/company_tickers_exchange.json", sec=True, js=True, tries=4) or {}
    n_sec = 0
    for cik_, nombre, tk, bolsa in d.get("data", []):
        if bolsa in ("Nasdaq", "NYSE") and tk and re.fullmatch(r"[A-Z]{1,5}", tk):
            nm = (nombre or "").lower()
            if any(w in nm for w in (" warrant", " unit", " right", "preferred", " notes")) and "ordinary" not in nm:
                continue
            syms.add(tk); n_sec += 1
    universo.fuentes["sec"] = n_sec
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
                                   ficheros_faltan=list(universo.faltan), fuentes_universo=dict(getattr(universo, "fuentes", {})))
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
                             vol_pre=q.get("preMarketVolume") if pre else q.get("regularMarketVolume"),   # (antes de abrir, el de ayer no vale)
                             acciones=q.get("sharesOutstanding"), bolsa=q.get("fullExchangeName"), estado=estado, split_hoy=split))
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
                         vol_pre=q.get("preMarketVolume") if q.get("marketState") in ("PRE", "PREPRE") else q.get("regularMarketVolume"),
                         acciones=q.get("sharesOutstanding"), bolsa=q.get("fullExchangeName"), estado=q.get("marketState"), fuente="TradingView"))
        solo_tv.append(f"{sym} +{gap:.0%}: AÑADIDA (solo la veía TradingView; revisar por qué Yahoo no)")
    escanear_vivo.cobertura["solo_tradingview"] = solo_tv
    return cand


def escanear_replay(fecha):
    import pandas as pd
    E = pd.read_parquet("/home/user/data/smallcaps/eventos_gappers.parquet")
    E = E[E.date == pd.Timestamp(fecha)]
    # Yahoo ajusta por splits posteriores → precio real del día. 1-oct-2026: la lista de splits de Yahoo omite algunos (CRIS, SVRE) →
    # primero la apertura SIN ajustar de Massive (1 consulta para todo el mercado); si no la tiene, ajustado × splits de Yahoo
    M = massive_dia_sin_ajustar(fecha)
    f = {}
    for r in E.itertuples():
        m = M.get(r.sym)
        f[r.sym] = m["o"] / float(r.open) if m and m.get("o") and abs(m["o"] / (float(r.open) * factor_split(r.sym, fecha)) - 1) > 0.03 \
            else factor_split(r.sym, fecha)
    return [dict(sym=r.sym, nombre="", precio=round(float(r.open) * f[r.sym], 4), cierre_prev=float(r.pc) * f[r.sym], gap=round(float(r.gap), 4),
                 cap=None, vol_pre=None, bolsa="", estado="REPLAY") for r in E.itertuples() if r.open * f[r.sym] >= PRECIO_MIN]


def massive_dia_sin_ajustar(dia):
    """{ticker: barra diaria SIN ajustar} de todo el mercado en `dia` (Massive, plan gratis: ~2 años). {} si no está disponible."""
    import requests
    for k in range(6):
        try:
            r = requests.get(f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{dia}", params=dict(adjusted="false"), timeout=(15, 60))
            if r.status_code == 429 or "exceeded" in r.text[:300]:
                time.sleep(13); continue
            return {x["T"]: x for x in r.json().get("results") or []}
        except Exception:
            time.sleep(3)
    return {}


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
    r = _TK.get(sym.upper().replace("-", "."), _TK.get(sym.upper(), (None, None)))
    if r[0] is None:            # 30-sep (FFR = AIXC con ticker nuevo ese día): búsqueda de texto de EDGAR ("Nasdaq: FFR" en su 8-K)
        hoy = dt.date.today()
        for bolsa in ("Nasdaq", "NASDAQ", "NYSE American", "NYSE"):
            q = urllib.parse.quote(f'"{bolsa}: {sym.upper()}"')
            d = get(f"https://efts.sec.gov/LATEST/search-index?q={q}&startdt={hoy - dt.timedelta(days=120)}&enddt={hoy}", sec=True, js=True) or {}
            ciks = {c for h in d.get("hits", {}).get("hits", []) for c in h["_source"].get("ciks", [])}
            if len(ciks) == 1:
                r = (int(ciks.pop()), None); break
    if r[0] is None:            # segunda opción: Massive
        try:
            import requests
            d = requests.get(f"https://api.polygon.io/v3/reference/tickers/{sym}", timeout=(10, 30)).json().get("results") or {}
            if d.get("cik"):
                r = (int(d["cik"]), d.get("name"))
        except Exception:
            pass
    return r


def hora_oficial(cik, acc_guiones):
    """Hora de aceptación oficial (Nueva York) de la cabecera de la presentación: ACCEPTANCE-DATETIME AAAAMMDDhhmmss."""
    a = acc_guiones.replace("-", "")
    h = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{a}/{acc_guiones}-index-headers.html", sec=True) or ""
    m = re.search(r"ACCEPTANCE-DATETIME>\s*(\d{14})", h)
    return dt.datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=NY) if m else None


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
        # 1-oct-2026 (lo destapó el verificador independiente): en las presentaciones del MISMO día (y quizá del anterior) el JSON de la
        # SEC da la hora de Nueva York con una "Z" falsa (CNTB 8-K: JSON 07:05:05Z, oficial 07:05:05 NY); días después la corrige a UTC.
        # Muestra del 30-sep: 5/5 del mismo día mal, 49/49 anteriores bien → para los últimos 3 días se usa la hora oficial de la cabecera.
        if (dt.date.today() - dt.date.fromisoformat(r["filingDate"][i])).days <= 3:
            ho = hora_oficial(cik, r["accessionNumber"][i])
            if ho:
                hora = ho
        out.append(dict(form=r["form"][i], hora=hora, fecha=r["filingDate"][i], items=r.get("items", [""] * 99999)[i] or "",
                        acc=acc, doc=r["primaryDocument"][i],
                        url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{r['primaryDocument'][i]}"))
    return out, d.get("name", ""), d.get("sicDescription", ""), d.get("stateOfIncorporation", "")


def texto_catalizador(cik, p):
    idx = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/index.json", sec=True, js=True) or {}
    docs = [i["name"] for i in idx.get("directory", {}).get("item", []) if i["name"].lower().endswith((".htm", ".html", ".txt"))]
    # 30-sep: el anexo se busca por su TIPO (EX-99.x) en la página índice; por el nombre se perdía (CNTB: 'a991.htm')
    acc_g = f"{p['acc'][:10]}-{p['acc'][10:12]}-{p['acc'][12:]}"
    ih = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/{acc_g}-index.html", sec=True) or ""
    ex = []
    for fila in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", ih):
        a = re.search(r'href="[^"]*/([^"/]+\.html?)"', fila); tp = re.findall(r"<td[^>]*>\s*([^<]*?)\s*</td>", fila)
        if a and any(x.upper().startswith("EX-99") for x in tp):
            ex.append(a.group(1))
    ex = [n for n in ex if n in docs] or [n for n in docs if re.search(r"ex[-_]?99|ex991|exhibit99|dex99|(^|[^0-9])a?99[1-9]?\.htm", n.lower())]
    # 6-oct (estudio de largos, AudioCodes 6-K 6-nov-2024): en 6-K la nota de prensa puede ser "EX-1" (tm…_ex1.htm) → si no hay EX-99,
    # leer los demás .htm de la presentación (sin índices ni tablas XBRL)
    if not ex:
        ex = [n for n in docs if n != p["doc"] and n.lower().endswith((".htm", ".html"))
              and not re.search(r"index|^r\d+\.htm|filingsummary|financial_report", n.lower())]
    partes = []
    # 6-oct (IPDN, lo destapó el verificador): el cuerpo del 8-K/6-K va SIEMPRE, también cuando hay EX-99 — ahí está el Item 1.01
    # (IPDN: arrendamiento + reparto de ingresos + préstamo con Goodwill Labs por $1.177 M que la nota de prensa no contaba)
    nombres = ([p["doc"]] if ex and p["doc"] not in ex[:8] else []) + (ex[:8] or [p["doc"]])   # 6-oct: hasta 8 anexos (PLG: la nota era el EX-99.8)
    for n in nombres:          # 1-oct: TODOS los anexos (CNTB: el fallo del secundario estaba en la presentación EX-99.2)
        t = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/{n}", sec=True)
        if t:
            completo = resumen_doc(limpiar(t), 10 ** 7)
            partes.append(dict(archivo=n, url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{p['acc']}/{n}",
                               texto=completo[:30000], recortado=len(completo) > 30000, negativos=negativos(completo)))
    return partes


# Frases que la empresa no pone en el titular: resultados fallidos, condiciones, acuerdos no vinculantes (1-oct-2026, caso CNTB)
NEGATIVOS = [
    ("dato clínico fallido", r"not statistically significant|did not (?:reach|achieve|meet) (?:statistical )?significance|statistical significance (?:was )?not (?:achieved|reached)|\bNot Significant\b|p\s*[-=]\s*NS\b|did not meet (?:its|the) (?:primary|secondary|key)|failed to (?:meet|achieve|demonstrate)|did not demonstrate|no statistically significant"),
    ("objetivo secundario / clave", r"key secondary|secondary endpoint"),
    ("no vinculante / preliminar", r"non-binding|nonbinding|letter of intent|memorandum of understanding|\bMOU\b|\bLOI\b|subject to (?:the )?(?:execution|negotiation|completion) of (?:a )?definitive"),
    ("cifra 'hasta' / potencial", r"\bup to \$|potential(?:ly)? (?:worth|value|revenue)|could generate|aggregate potential"),
    ("dilución / financiación", r"registered direct|private placement|warrants? to purchase|convertible (?:note|debenture|preferred)|at[- ]the[- ]market|equity line"),
]


def negativos(texto):
    out = []
    for etiqueta, pat in NEGATIVOS:
        for mm in list(re.finditer(pat, texto, re.I))[:3]:
            out.append(dict(tipo=etiqueta, frase=texto[max(0, mm.start() - 220):mm.end() + 220].strip()))
    return out


def historial_catalizadores(cik, pres, desde, sym, dias=120, maximo=6):
    """8-K/6-K de los últimos `dias` antes de hoy con su titular y la reacción del precio ese día (Yahoo diario).
    1-oct-2026: el 15-sep CNTB había caído −32 % con otro dato clínico y no lo miramos."""
    ant = [p for p in pres if p["hora"] < desde and p["form"] in ("8-K", "6-K") and (desde.date() - p["hora"].date()).days <= dias
           and (p["form"] == "6-K" or re.search(r"7\.01|8\.01|1\.01|2\.02", p["items"] or ""))][:maximo]
    if not ant:
        return []
    serie = {}
    try:
        r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1y&interval=1d", js=True)["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        serie = {dt.datetime.fromtimestamp(t, NY).date(): (o, c) for t, o, c in zip(r["timestamp"], q["open"], q["close"]) if c}
    except Exception:
        pass
    dias_ord = sorted(serie)
    out = []
    for p in ant:
        h = p["hora"]
        d = h.date() if h.time() < dt.time(16, 0) else h.date() + dt.timedelta(days=1)
        d = next((x for x in dias_ord if x >= d), None)
        reac = None
        if d and dias_ord.index(d) > 0:
            prev = serie[dias_ord[dias_ord.index(d) - 1]][1]; o, c = serie[d]
            reac = dict(dia=d.isoformat(), apertura=round(o / prev - 1, 4) if o else None, cierre=round(c / prev - 1, 4))
        titular = ""
        try:
            partes = texto_catalizador(cik, p)
            titular = re.sub(r"^(Document\s+)?Exhibit\s*99\.\d\s*", "", (partes[0]["texto"] if partes else ""))[:220]
        except Exception:
            pass
        out.append(dict(form=p["form"], fecha=h.strftime("%Y-%m-%d %H:%M"), items=p["items"], url=p["url"], titular=titular, reaccion=reac))
    return out


# ------------------------------------------------------------------ shelves y ATM (1-oct-2026, caso CNTB: la ATM de $150 M con Cantor
# estaba en el F-3 de junio de 2025 y el Radar decía "sin ATM" porque solo miraba el último 10-Q; y el F-3 de mayo de 2026 era una
# REVENTA de terceros que contábamos como shelf de la empresa)
AGENTES = r"(Cantor Fitzgerald|H\.C\. Wainwright|Maxim Group|Jefferies|TD Cowen|Cowen and Company|Leerink|B\. Riley|Roth Capital|ThinkEquity|A\.G\.P\.|Ladenburg|EF Hutton|Aegis Capital|BTIG|Oppenheimer|Piper Sandler|Mizuho|Stifel|Canaccord|Lake Street|Dawson James|Craig-Hallum|Spartan Capital|Univest|D\. Boral|Virtu|Guggenheim|Evercore|Raymond James|JonesTrading|Wedbush|Titan Partners|Rodman|Chardan|Alliance Global|Laidlaw|Benchmark|Northland|Needham|Truist|Citizens JMP|JMP Securities|Barclays|Goldman Sachs|Morgan Stanley|BofA|Citigroup|UBS|Wells Fargo|Yorkville|Lincoln Park|Keystone Capital|White Lion|Tumim|Alumni Capital|Arena Business|Clearthink)"


def _usd(num, escala):
    v = float(num.replace(",", ""))
    return v * (1e6 if escala and escala.lower().startswith("m") else 1e9 if escala and escala.lower().startswith("b") else 1)


def analizar_shelf(p):
    """Lee un S-3/F-3/POS AM/424B5 y dice: de la empresa o REVENTA de terceros, importe base, ATM (importe y agente), frase literal."""
    t = limpiar(get(p["url"], sec=True) or "")
    if not t:
        return None
    cab = t[:15000]
    reventa = bool(re.search(r"selling (security ?holders?|shareholders?|stockholders?|holders?)", cab, re.I) and
                   (re.search(r"(will not|do not|shall not) receive any (of the )?proceeds", cab, re.I) or
                    re.search(r"relates to the (?:proposed )?(?:offer and )?(?:re)?sale[^.]{0,250}by the selling", cab, re.I)))
    o = dict(form=p["form"], fecha=p["fecha"], url=p["url"], tipo="reventa" if reventa else "empresa")
    if reventa:
        # 1-oct (FFR): una reventa de un inversor que compra con descuento a petición de la empresa = línea de capital (ELOC)
        el = re.search(r"VWAP Shares?|equity line|equity purchase agreement|standby equity|purchase agreement[^.]{0,200}(?:from time to time|at our (?:sole )?discretion)|committed equity facility", cab, re.I)
        if el:
            o["eloc"] = True; o["frase_eloc"] = cab[max(0, el.start() - 200):el.end() + 200]
        m = re.search(r"up to ([0-9][0-9,]{3,}) (?:of (?:the|our) )?(?:ordinary shares|common shares|shares of (?:our )?(?:class a )?common stock|shares|American Depositary Shares|ADSs)", cab, re.I)
        if m:
            o["acciones_reventa"] = int(m.group(1).replace(",", ""))
            o["frase"] = t[max(0, m.start() - 160):m.end() + 60]
        return o
    m = re.search(r"up to \$\s?([0-9][0-9,.]*)\s*(million|billion)?\s*(?:in the )?aggregate", t, re.I) or \
        re.search(r"PROSPECTUS \$\s?([0-9][0-9,.]*)\s*(million|billion)?", t, re.I)
    if m and p["form"] in ("S-3", "S-3/A", "F-3", "F-3/A", "S-3ASR", "POS AM"):
        o["base_usd"] = _usd(m.group(1), m.group(2)); o["frase_base"] = t[max(0, m.start() - 120):m.end() + 120]
    bs = re.search(r"General Instruction I\.B\.[56]", t)
    if bs:
        o["baby_shelf"] = True; o["frase_baby"] = t[max(0, bs.start() - 400):bs.end() + 250]
    a = re.search(r"aggregate offering price of up to \$\s?([0-9][0-9,.]*)\s*(million|billion)?", t, re.I)
    atm_ctx = re.search(r"at[- ]the[- ]market|sales agreement|equity distribution agreement|ATM [Aa]greement", t, re.I)
    if a and atm_ctx:
        o["atm_usd"] = _usd(a.group(1), a.group(2))
        ventana = t[max(0, a.start() - 600):a.end() + 900]
        ag = re.search(AGENTES, ventana)
        o["atm_agente"] = ag.group(1) if ag else None
        o["frase_atm"] = t[max(0, a.start() - 200):a.end() + 220]
        nv = re.search(r"(we have not (?:yet )?sold any[^.]{0,120}\.)", t, re.I)
        if nv:
            o["frase_sin_uso"] = nv.group(1)
    return o


def uso_atm(texto_informe):
    """Frases del último 10-Q/10-K/20-F sobre ventas bajo la ATM (importe vendido, restante)."""
    out = []
    for mm in re.finditer(r"[^.]{0,300}(?:Sales Agreement|ATM (?:Program|Agreement|offering)|at-the-market (?:offering|program))[^.]{0,400}\.", texto_informe, re.I):
        fr = mm.group(0).strip()
        if re.search(r"\bsold\b|net proceeds|remain(?:ing|ed)? available|no (?:shares|sales)", fr, re.I) and len(out) < 4:
            out.append(fr[:700])
    return out


def colocaciones(cik, ant, hoy):
    """Colocaciones privadas / registered direct de 12 meses con su precio por acción (1-oct, verificador: CNTB 6.13 M a $3.25 en mar-2026;
    quien compró caro y está en pérdidas es otro vendedor posible)."""
    out = []
    for p in [p for p in ant if p["form"] in ("8-K", "6-K") and (hoy - p["hora"].date()).days <= 365
              and ("3.02" in (p["items"] or "") or p["form"] == "6-K")][:6]:
        t = limpiar(get(p["url"], sec=True) or "")
        if p["form"] == "6-K" and not re.search(r"private placement|registered direct|securities purchase agreement", t, re.I):
            continue
        mm = re.search(r"(?:at|for) a (?:purchase |offering )?price of \$\s?([0-9]+(?:\.[0-9]+)?) per (?:share|Share|ordinary share|unit)", t)
        na = re.search(r"([0-9][0-9,]{4,}) (?:shares|ordinary shares|Shares|units)", t)
        if mm or na:
            out.append(dict(form=p["form"], fecha=p["fecha"], url=p["url"], precio=float(mm.group(1)) if mm else None,
                            acciones=int(na.group(1).replace(",", "")) if na else None,
                            frase=t[max(0, (mm or na).start() - 250):(mm or na).end() + 150]))
    return out


_SPLITS_M = {}


def splits_de(sym):
    """[(fecha, factor)] de los splits de los últimos 5 años (factor = nuevas/antiguas; 1:25 → 0.04).
    1-oct-2026: la lista de eventos de Yahoo OMITE contra-splits que sí aplica a sus precios (CRIS 1:20 del 29-sep-2023; SVRE
    cambio de ratio ADS 1:13.33 del 21-feb-2025) → se une con la de Massive (antes Polygon); duplicados (±5 días) se cuentan una vez."""
    out = []
    try:
        r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5y&interval=1mo&events=split", js=True)["chart"]["result"][0]
        out = [(dt.datetime.fromtimestamp(v["date"], NY).date(), v["numerator"] / v["denominator"])
               for v in (r.get("events", {}).get("splits") or {}).values()]
    except Exception:
        pass
    try:
        import requests
        hoy = dt.datetime.now(NY).date()
        if sym not in _SPLITS_M:
            for k in range(5):              # plan gratis: 5 consultas/min → espera y reintenta
                r = requests.get("https://api.polygon.io/v3/reference/splits", params=dict(ticker=sym, limit=100), timeout=(10, 30))
                if r.status_code == 429 or "exceeded" in r.text[:300]:
                    time.sleep(13); continue
                _SPLITS_M[sym] = r.json().get("results") or []
                break
        for x in _SPLITS_M.get(sym, []):
            d = dt.date.fromisoformat(x["execution_date"])
            if (hoy - d).days <= 5 * 365 and d <= hoy and not any(abs((d - e).days) <= 5 for e, _ in out):
                out.append((d, x["split_to"] / x["split_from"]))
    except Exception:
        pass
    return sorted(out)


def shelves(cik, pres, desde):
    ant = [p for p in pres if p["hora"] < desde and (desde.date() - p["hora"].date()).days <= 3 * 365]
    cand = [p for p in ant if p["form"] in ("S-3", "S-3/A", "F-3", "F-3/A", "S-3ASR", "POS AM", "S-1", "S-1/A", "F-1", "F-1/A")
            or (p["form"] == "424B5" and (desde.date() - p["hora"].date()).days <= 3 * 365)]
    out = []
    for p in cand[:10]:                     # los más recientes primero
        try:
            o = analizar_shelf(p)
        except Exception as e:
            o = dict(form=p["form"], fecha=p["fecha"], url=p["url"], error=str(e)[:80])
        if o and (o.get("tipo") == "reventa" or o.get("base_usd") or o.get("atm_usd") or p["form"].startswith(("S-3", "F-3"))):
            # las enmiendas (/A, POS AM) repiten la misma reventa: no se suman dos veces (GYGY: 3 × 16 M)
            if o.get("acciones_reventa") and any(x.get("acciones_reventa") == o["acciones_reventa"] for x in out):
                o["repetida"] = True
            out.append(o)
    return out



TOXICA = r"not determinable|variable conversion|% of the (average of the )?(three |five )?lowest|lowest (daily )?(vwap|trading price)"


def municion(cik, pres, desde, sym, precio):
    hoy = desde.date()
    ant = [p for p in pres if p["hora"] < desde]
    dias = lambda p: (hoy - p["hora"].date()).days
    m = dict(venta90=any(p["form"].startswith("424B") and dias(p) <= 90 for p in ant),
             s3=next((p["fecha"] for p in ant if p["form"] in ("S-3", "S-3/A", "F-3", "F-3/A", "S-3ASR") and dias(p) <= 3 * 365), None),
             s1=next((p["fecha"] for p in ant if p["form"] in ("S-1", "S-1/A", "F-1", "F-1/A") and dias(p) <= 365), None),
             ventas_12m=sum(1 for p in ant if p["form"] in ("424B4", "424B5") and dias(p) <= 365),
             p424_12m=sum(1 for p in ant if p["form"].startswith("424B") and dias(p) <= 365),   # 'serie' del histórico (11_seleccion.py)
             aviso_bolsa=any("3.01" in p["items"] for p in ant if dias(p) <= 365),
             contrasplits_2a=sum(1 for p in ant if "5.03" in p["items"] and dias(p) <= 730))
    m["ultimas_ventas"] = [dict(form=p["form"], fecha=p["fecha"], url=p["url"]) for p in ant if p["form"] in ("424B4", "424B5")][:4]
    # 1-oct (RZAI): un registro presentado DENTRO de la ventana (ayer 16:06, reventa de 19.8 M acciones) también es munición
    m["shelves"] = shelves(cik, pres, desde + dt.timedelta(hours=17, minutes=10))
    m["colocaciones"] = colocaciones(cik, ant, hoy)
    m["shelf_empresa"] = any(x.get("tipo") == "empresa" and x["form"] != "424B5" for x in m["shelves"])
    # acciones de cada reventa ajustadas por los splits POSTERIORES al registro (VBIO 30-sep: 51 M "registradas" con 0.89 M en
    # circulación: eran acciones de antes de un contra-split 1:25). Fuente: historial de splits de Yahoo
    spl = splits_de(sym)
    for x in m["shelves"]:
        if x.get("acciones_reventa"):
            fx = 1.0
            for fecha_s, fac in spl:
                if fecha_s > dt.date.fromisoformat(x["fecha"]):
                    fx *= fac
            x["acciones_reventa_hoy"] = int(x["acciones_reventa"] * fx)
            if fx != 1.0:
                x["ajuste_splits"] = round(fx, 6)
    # reventas de los últimos 12 meses (más atrás, los contra-splits cambian el número de acciones y la suma no tiene sentido)
    m["reventa_acciones"] = sum(x.get("acciones_reventa_hoy") or 0 for x in m["shelves"] if x.get("tipo") == "reventa" and not x.get("repetida")
                                and (hoy - dt.date.fromisoformat(x["fecha"])).days <= 365)
    m["atm_shelf"] = next((x for x in m["shelves"] if x.get("atm_usd")), None)
    # último 10-Q/10-K: ATM, convertible tóxica, going concern, warrants (texto)
    per = [p for p in ant if p["form"] in ("10-Q", "10-K", "10-Q/A", "10-K/A", "20-F")]
    if not per:   # 1-oct (RZAI, listada hace 3 días): sin informes periódicos → leer el último folleto (preferente tóxica, warrants a $8)
        per = [p for p in pres if p["form"] in ("424B4", "424B3", "F-1", "F-1/A", "S-1", "S-1/A") and p["hora"] <= desde + dt.timedelta(hours=17, minutes=10)]
    m.update(atm=False, toxica=False, going_concern=False, warrants=[])
    if per:
        t = limpiar(get(per[0]["url"], sec=True) or "")
        m["informe"] = dict(form=per[0]["form"], fecha=per[0]["fecha"], url=per[0]["url"])
        m["atm"] = bool(re.search(r"at-the-market|at the market offering|equity distribution agreement", t, re.I))
        m["eloc"] = bool(re.search(r"equity line|equity purchase agreement|standby equity|purchase agreement with (lincoln park|yorkville|ya ii)", t, re.I))
        m["toxica"] = bool(re.search(TOXICA, t, re.I))
        m["going_concern"] = bool(re.search(r"substantial doubt", t, re.I))
        m["uso_atm"] = uso_atm(t)
        # lo que la propia empresa dice de su caja (CNTB: "sufficient ... for at least one year" frente a ~2.9 meses con la quema medida)
        su = re.search(r"[^.]{0,250}(?:sufficient|enough) to (?:fund|meet|finance)[^.]{0,250}(?:one year|twelve months|12 months|into (?:the )?(?:first|second|third|fourth) (?:quarter|half) of 20\d\d|through 20\d\d)[^.]{0,150}\.", t, re.I)
        m["empresa_dice_caja"] = su.group(0).strip()[:600] if su else None
        ej = set()
        for mm in re.finditer(r"exercise price[^$.]{0,60}\$\s?([0-9]+(?:\.[0-9]+)?)", t, re.I):
            antes = t[max(0, mm.start() - 250):mm.start()].lower()     # 30-sep: CNTB $2.14 era el precio medio de OPCIONES
            if "warrant" in antes and antes.rfind("warrant") > antes.rfind("option") and 0.01 < float(mm.group(1)) < 10000:
                ej.add(round(float(mm.group(1)), 2))
        # 1-oct (VEEA, lección 9): precios de ejercicio del informe AJUSTADOS por contra-splits posteriores al informe (1:20 → ×20)
        fx = 1.0
        for fecha_s, fac in splits_de(sym):
            if fecha_s > dt.date.fromisoformat(per[0]["fecha"]) and fecha_s <= hoy:
                fx *= fac
        if fx != 1.0:
            m["warrants_sin_ajustar"] = sorted(ej)[:8]; m["ajuste_splits_warrants"] = round(1 / fx, 4)
            ej = {round(e / fx, 2) for e in ej}
        ej = sorted(ej)
        m["warrants"] = ej[:8]
        m["warrants_en_dinero"] = bool(precio and any(e < precio for e in ej))   # ojo: sin ajustar por contra-splits posteriores
    # 6-oct (OLOX, lo destapó el verificador): la nota convertible al "80% of the lowest closing price" solo estaba en el folleto de
    # REVENTA (424B3 7-ene-2026), no en el 10-Q → leer también los folletos de los últimos 12 meses (máx. 4)
    if not m.get("toxica"):
        fol = [p for p in ant if p["form"] in ("424B3", "424B4", "424B5", "S-1", "S-1/A", "F-1", "F-1/A")
               and (hoy - dt.date.fromisoformat(p["fecha"])).days <= 365][:4]
        for p in fol:
            tf = limpiar(get(p["url"], sec=True) or "")
            if re.search(TOXICA, tf, re.I):
                m["toxica"] = True
                m["toxica_fuente"] = dict(form=p["form"], fecha=p["fecha"], url=p["url"])
                break
    m["atm"] = bool(m.get("atm") or m.get("atm_shelf"))      # la ATM puede estar solo en la shelf (CNTB 30-sep)
    m["eloc"] = bool(m.get("eloc") or any(x.get("eloc") and (hoy - dt.date.fromisoformat(x["fecha"])).days <= 730 for x in m["shelves"]))
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
            if profundo:
                c["historial"] = historial_catalizadores(cik, pres, desde, c["sym"])
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


TIPOS_OK = set("CFRBKHSON")


def auditar(C, CL, replay):
    """Control de calidad antes de publicar. Errores = la lista NO se publica hasta corregirlos."""
    err, av = [], []
    cob = C.get("cobertura")
    if not replay:
        if not cob:
            err.append("Sin dato de cobertura del escáner: repetir 'escanear'")
        elif cob["universo"] < 5000 or (cob.get("ficheros_faltan") and (cob.get("fuentes_universo") or {}).get("sec", 0) < 6000):
            err.append(f"Universo incompleto ({cob['universo']} tickers; faltan {cob.get('ficheros_faltan')}): repetir 'escanear' "
                       "(29-sep: faltó el fichero de NYSE/NYSE American y se perdió SLND)")
        elif cob["pct"] < 0.97:
            err.append(f"Cobertura del escáner {cob['pct']:.1%} ({cob['cotizadas']}/{cob['universo']}): faltan cotizaciones, repetir 'escanear'")
    if not replay and cob and cob.get("ficheros_faltan") and (cob.get("fuentes_universo") or {}).get("sec", 0) >= 6000:
        av.append(f"nasdaqtrader no se descargó ({cob['ficheros_faltan']}): universo cubierto con la lista de la SEC "
                  f"({cob['fuentes_universo']['sec']} tickers Nasdaq/NYSE); los tickers MUY nuevos pueden faltar → TradingView los cubre")
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
        # 30-sep (caso LGHL): el catalizador tiene que ser de HOY (desde el cierre anterior). Una financiación de ayer es munición,
        # no el motivo del gap: si no hay ningún 8-K/6-K ni noticia en la ventana, el tipo correcto es N (lo viejo va en la nota)
        if t in TIPOS_OK - {"N"} and not fuentes and not cl.get("fuente_fuera_herramienta"):
            err.append(f"{s}: clasificado '{t}' pero no hay ningún 8-K/6-K ni noticia desde el cierre anterior: si el documento es "
                       "anterior, el tipo es N y lo viejo va en 'nota'; si la noticia existe pero la herramienta no la vio, anotar "
                       "'fuente_fuera_herramienta' con el enlace y la hora")
        neg = [n for k in c.get("catalizadores", []) for pa in k.get("partes", []) for n in (pa.get("negativos") or negativos(pa.get("texto", "")))]
        fallidos = [n for n in neg if n["tipo"] == "dato clínico fallido"]
        if fallidos and not cl.get("negativos_revisados"):
            err.append(f"{s}: el documento dice que algo NO fue significativo / no se cumplió ({len(fallidos)} frase(s), p. ej. "
                       f"«{fallidos[0]['frase'][180:300]}»): leerlo y anotar 'negativos_revisados' con lo que falló (caso CNTB 30-sep)")
        if t == "K" and any(n["tipo"] == "no vinculante / preliminar" for n in neg) and not cl.get("negativos_revisados"):
            err.append(f"{s}: clasificado 'contrato real' pero el documento habla de acuerdo no vinculante / LOI / MOU: revisar (¿humo?) "
                       "y anotar 'negativos_revisados'")
        if t in ("B", "K", "H") and c.get("historial") and not cl.get("historial_revisado") and not replay:
            peor = min((h["reaccion"]["cierre"] for h in c["historial"] if h.get("reaccion")), default=0)
            if peor <= -0.2:
                av.append(f"{s}: en los últimos 120 días hubo un catalizador con caída de {peor:+.0%} (ver historial en la ficha)")
        if t == "N" and not replay and not cl.get("fuentes_abiertas"):
            av.append(f"{s}: sin ninguna noticia; confirmar a mano en Finviz/Yahoo")
        if not replay and C.get("fecha", "") >= PASOS_DESDE:
            err += [f"{s}: {e}" for e in revisar_pasos(c, cl)]
            ec = comprobar_cita(c, cl)
            if ec and cl.get("cita_no_comprobable"):
                av.append(f"{s}: cita NO comprobada por programa ({cl['cita_no_comprobable']}); revisada a mano")
            else:
                err += [f"{s}: cita: {e}" for e in ec]
    return err, av


# 1-oct-2026 (pedido por el usuario): registro de pasos del trabajo de criterio, comprobado como el automático. Cada acción del
# escaneo lleva en _clasif.json "pasos" = qué se abrió y revisó; `finalizar` bloquea la lista si falta algo (desde el 2-oct).
PASOS_DESDE = "2026-10-02"
PASOS = {"fuentes": "lista de lo abierto y leído (cada 8-K/6-K con su hora y cada titular de noticias)",
         "anexos_leidos": "número de anexos/partes leídos (EX-99.1, EX-99.2…)",
         "negativos": "lo que NO dice el titular (objetivos fallidos, 'up to', no vinculante…) o 'ninguno, revisado'",
         "historial": "catalizadores de los 120 días y cómo reaccionó el precio, o 'sin historial'",
         "municion": "shelves/ATM/reventas/ELOC/424B/warrants revisados en la ficha (resumen)",
         "caja": "caja a hoy y going concern revisados (resumen)"}


def revisar_pasos(c, cl):
    p = cl.get("pasos") or {}
    e = [f"falta 'pasos.{k}' ({v})" for k, v in PASOS.items() if p.get(k) in (None, "", [])]
    if e:
        return e
    docs = len(c.get("catalizadores", [])); notis = len(c.get("noticias", []))
    partes = sum(len(k.get("partes", [])) for k in c.get("catalizadores", []))
    fu = p["fuentes"] if isinstance(p["fuentes"], list) else [p["fuentes"]]
    if len(fu) < docs + notis:
        e.append(f"'pasos.fuentes' tiene {len(fu)} y hay {docs} documento(s) + {notis} noticia(s): abrir y anotar TODOS")
    try:
        if int(p["anexos_leidos"]) < partes:
            e.append(f"'pasos.anexos_leidos' = {p['anexos_leidos']} y los documentos tienen {partes} partes/anexos: leerlos todos")
    except (TypeError, ValueError):
        e.append("'pasos.anexos_leidos' debe ser un número")
    if c.get("historial") and str(p["historial"]).strip().lower().startswith("sin historial"):
        e.append(f"'pasos.historial' dice 'sin historial' pero la ficha tiene {len(c['historial'])} catalizador(es) en 120 días")
    return e


# 1-oct-2026 (pedido por el usuario): comprobación automática de citas = el Ctrl+F hecho por un programa. La frase en inglés tiene que
# estar LITERAL en la fuente (documento de la SEC guardado o la página de 'frase_url' / de las noticias) y algún número de la cifra
# tiene que aparecer en la fuente. Si no, la lista no se publica (desde PASOS_DESDE).
def _norm(t):
    t = html.unescape(t or "").lower()
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u2013", "-"), ("\u2014", "-"), ("\xa0", " ")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def _num(t):
    return set(re.sub(r"[,\s]", "", m) for m in re.findall(r"\d{1,3}(?:[,\s]\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?", t or ""))


_CITAS = {}


def textos_fuente(c, cl):
    out = [p.get("texto", "") for k in c.get("catalizadores", []) for p in k.get("partes", [])]
    urls = ([cl["frase_url"]] if cl.get("frase_url") else []) + [n["url"] for n in c.get("noticias", []) if n.get("url")]
    for u in urls:
        if u not in _CITAS:
            _CITAS[u] = limpiar(get(u, sec="sec.gov" in u) or "")
        out.append(_CITAS[u])
    return out


def comprobar_cita(c, cl):
    fe = cl.get("frase_en") or ""
    if not fe.strip():
        return []
    fuente = _norm(" ".join(textos_fuente(c, cl)))
    if not fuente:
        return ["no hay texto de la fuente para comprobar la cita: anotar 'frase_url' con una copia legible (8-K/EX-99 de la SEC o Yahoo); "
                "si ninguna web se deja leer, 'cita_no_comprobable' con el motivo (sale como aviso en la línea de salud)"]
    e = []
    trozos = [t.strip(" .,;:\"'") for t in re.split(r"…|\.\.\.|\[…\]", _norm(fe))]
    falta = [t for t in trozos if len(t) >= 12 and t not in fuente]
    if falta:
        e.append(f"la frase en inglés NO aparece literal en la fuente («{falta[0][:90]}…»): copiarla exacta o anotar 'frase_url'")
    nums_fuente = _num(fuente)
    nc = set() if _norm(cl.get("cifra")).startswith(("sin cifra", "ninguna cifra")) else _num(cl.get("cifra"))
    if nc and not (nc & nums_fuente) and not cl.get("cifra_calculada"):
        e.append(f"ningún número de la cifra ({', '.join(sorted(nc)[:4])}) aparece en la fuente: revisar unidad/cifra o anotar "
                 "'cifra_calculada' explicando la cuenta")
    return e


# ------------------------------------------------------------------ puntuación de la tesis (ronda 12, validada 30-sep-2026)
PESOS_F = os.path.join(RAIZ, "smallcaps", "puntuacion_pesos.json")
FACTORES = [("gap_50_100", "Gap 50-100 %"), ("gap_100", "Gap ≥ 100 %"), ("cat_H", "Catalizador humo / cosmético"),
            ("cat_B", "Catalizador biotech real (FDA / datos)"), ("cat_K", "Contrato real con cifra"),
            ("venta90", "Vendió acciones (424B) en los últimos 90 días"), ("s3", "Shelf S-3 / F-3 registrado (3 años)"),
            ("serie", "Diluidor en serie (≥ 3 folletos 424B en 12 meses)"), ("solo_pr", "8-K solo nota de prensa (7.01/8.01, sin acuerdo 1.01)")]
# Resultado histórico del setup base (corto a la apertura, stop +30 % con 5 % de deslizamiento, coste 1 %, salida al cierre) por tramo
# de gap y tercio de puntuación. VAL 2022-26 con pesos congelados de DEV 2015-21 (smallcaps/INFORME_SELECCION.md, ronda 12).
ESTAD_TERCIO = {   # 1-oct-2026: ronda 12 con datos corregidos (precio real exacto/calibrado + festivos), `30_ronda12_corregida.py`;
    # coincide con la réplica a ciegas del verificador (VERIFICADOR_ESTUDIOS.md). Versión anterior: puntuacion_pesos_v1_30sep.json
    ("≥ 50 %", "Alta"): dict(n=157, R=0.25, WR=0.69, gan=0.80, perd=-0.98, PF=1.81, dev=0.15),
    ("≥ 50 %", "Media"): dict(n=80, R=0.08, WR=0.64, gan=0.77, perd=-1.14, PF=1.19, dev=0.14),
    ("≥ 50 %", "Baja"): dict(n=84, R=-0.15, WR=0.52, gan=0.63, perd=-1.00, PF=0.69, dev=-0.09),
    ("20-50 %", "Alta"): dict(n=97, R=-0.03, WR=0.56, gan=0.44, perd=-0.62, PF=0.88, dev=0.14),
    ("20-50 %", "Media"): dict(n=122, R=-0.06, WR=0.54, gan=0.53, perd=-0.75, PF=0.84, dev=0.05),
    ("20-50 %", "Baja"): dict(n=198, R=-0.02, WR=0.57, gan=0.47, perd=-0.66, PF=0.92, dev=-0.01),
}
DESCARTE = {"C": "Compra en efectivo: el precio queda anclado a la oferta (PF histórico 0.23). No se shortea nunca",
            "R": "Resultados o cifras de ventas (trimestrales, anuales o preliminares): históricamente malo para el corto (PF 0.61)",
            "F": "Financiación: históricamente malo para el corto (PF 0.72)",
            "S": "Aviso de bolsa / corporativo: históricamente malo para el corto (PF 0.64)"}
_PESOS = None


def puntuar(c, cl):
    global _PESOS
    if _PESOS is None:
        _PESOS = json.load(open(PESOS_F))
    w, ref = _PESOS.get("pesos_exactos") or _PESOS["pesos"], _PESOS["ref_dev"]   # exactos: sin redondeo, como en el histórico
    t, g, m = cl.get("tipo", "N"), c["gap"], c.get("municion") or {}
    k8 = [d for d in c.get("docs_hoy", []) if d["form"] in ("8-K", "8-K/A")]      # como en el histórico: solo 8-K (un 6-K cuenta como 'sin 8-K')
    its = [i.strip() for d in k8 for i in (d.get("items") or "").split(",")]
    serie = m.get("p424_12m", m.get("ventas_12m")) or 0
    f = dict(gap_50_100=0.5 <= g < 1, gap_100=g >= 1, cat_H=t == "H", cat_B=t == "B", cat_K=t == "K",
             venta90=bool(m.get("venta90")), s3=bool(m.get("s3")), serie=serie >= 3,
             solo_pr=bool(k8) and all(i in ("7.01", "8.01", "9.01", "") for i in its))
    pred = w["constante"] + sum(w[k] for k, v in f.items() if v)
    # pesos exactos (30-sep): con los redondeados a 4 decimales la puntuación salía hasta 4.8 puntos por debajo del histórico en 268 de
    # 1 222 casos, porque los empates (combinaciones iguales de factores) no contaban enteros. Comprobado contra res_27_puntuacion.csv
    pct = sum(1 for r in ref if r <= pred + 1e-9) / len(ref) * 100
    valor = round(pct)
    tercio = "Alta" if pct > 200 / 3 else "Media" if pct > 100 / 3 else "Baja"
    notas = []
    if t == "N":
        notas.append("Sin noticia: el histórico no tiene este grupo; puntúa como 'otros catalizadores'")
    if t == "O":
        notas.append("Catalizador 'otros': es la base del modelo (peso 0)")
    if "p424_12m" not in m:
        notas.append("Diluidor en serie contado solo con 424B4/424B5 (lista generada antes del 30-sep)")
    return dict(valor=valor, tercio=tercio, pred_R=round(pred, 3),
                factores=[dict(clave=k, nombre=n, activo=bool(f[k]), peso=round(w[k], 4)) for k, n in FACTORES],
                base=round(w["constante"], 4), notas=notas)


def riesgo_estructural(c, m):
    """Riesgo de squeeze / coste, APARTE de la tesis. NO validado como filtro (ronda 11): sirve para limitar el tamaño."""
    motivos, n = [], 0
    acc, vol = c.get("acciones"), c.get("vol_pre")
    rot = vol / acc if acc and vol else None
    if acc and acc < 1e6:
        n = 2; motivos.append(f"Solo {acc / 1e6:.2f} M de acciones en circulación")
    elif acc and acc < 5e6:
        n = max(n, 1); motivos.append(f"Pocas acciones en circulación ({acc / 1e6:.2f} M)")
    if rot is not None and rot > 3:
        n = 2; motivos.append(f"Rotación premarket {rot:.1f}× las acciones en circulación")
    elif rot is not None and rot > 1:
        n = max(n, 1); motivos.append(f"Rotación premarket {rot:.1f}× las acciones en circulación")
    if m and not (m.get("venta90") or m.get("s3") or m.get("atm") or m.get("eloc") or m.get("warrants_en_dinero")) and acc and acc < 5e6:
        n = max(n, 1); motivos.append("Pocas acciones y sin munición activa: perfil de squeeze (caso APUS)")
    return dict(nivel=["Normal", "Alto", "Extremo"][n], motivos=motivos, rotacion_pre=round(rot, 2) if rot is not None else None,
                validado=False)


def premarket_1m(s, sym, fecha):
    """Máximo, mínimo y volumen del premarket (4:00-9:30) con velas de 1 min de Yahoo (solo ~30 días hacia atrás)."""
    d = dt.date.fromisoformat(fecha)
    a = int(dt.datetime.combine(d, dt.time(4, 0), NY).timestamp()); b = int(dt.datetime.combine(d, dt.time(9, 30), NY).timestamp())
    try:
        r = s.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                  params=dict(period1=a, period2=b, interval="1m", includePrePost="true"), timeout=20).json()["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        v = [(t, h, l, vo) for t, h, l, vo in zip(r.get("timestamp") or [], q["high"], q["low"], q["volume"]) if h and a <= t < b]
        if not v:
            return {}
        i = max(range(len(v)), key=lambda k: v[k][1])
        return dict(pmh=round(max(x[1] for x in v), 4), pml=round(min(x[2] for x in v), 4),
                    pmh_hora=dt.datetime.fromtimestamp(v[i][0], NY).strftime("%H:%M"),
                    hasta=dt.datetime.fromtimestamp(v[-1][0], NY).strftime("%H:%M"))
    except Exception:
        return {}


def caja(cik, hoy=None):
    """Caja y quema de caja del último informe (XBRL de la SEC). Informativo: no entra en la puntuación (no hay histórico medido)."""
    d = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", sec=True, js=True, timeout=40) or {}
    F = d.get("facts", {})
    def ult(tags, duracion):
        mejor = None
        for ns in ("us-gaap", "ifrs-full"):
            for tg in tags:
                for u, vals in (F.get(ns, {}).get(tg, {}).get("units") or {}).items():
                    if u != "USD":
                        continue
                    for x in vals:
                        if x.get("form") not in ("10-Q", "10-K", "10-Q/A", "10-K/A", "20-F", "6-K") or ("start" in x) != duracion:
                            continue
                        clave = (x["end"], (dt.date.fromisoformat(x["end"]) - dt.date.fromisoformat(x["start"])).days if duracion else 0)
                        if mejor is None or clave > mejor[0]:
                            mejor = (clave, dict(x, etiqueta=tg))
        return mejor[1] if mejor else None
    ca = ult(["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents", "Cash"], False)
    fo = ult(["NetCashProvidedByUsedInOperatingActivities", "CashFlowsFromUsedInOperatingActivities"], True)
    if not ca:
        return None
    inv = ult(["ShortTermInvestments", "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"], False)
    inv = inv["val"] if inv and inv["end"] == ca["end"] else 0
    out = dict(caja=ca["val"], inversiones=inv, caja_fecha=ca["end"], caja_etiqueta=ca["etiqueta"], form=ca.get("form"),
               url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{ca['accn'].replace('-', '')}/")
    if fo:
        meses = max(round((dt.date.fromisoformat(fo["end"]) - dt.date.fromisoformat(fo["start"])).days / 30.44), 1)   # 3, 6, 9 o 12
        out.update(flujo_operativo=fo["val"], flujo_desde=fo["start"], flujo_hasta=fo["end"], meses=meses)
        if fo["val"] < 0:
            q = -fo["val"] / meses
            out.update(quema_mes=round(q), autonomia_meses=round((ca["val"] + inv) / q, 1))
            # 1-oct (caso CNTB): lo que queda A HOY, no a la fecha del informe (5.9 meses al 30-jun = ~2.9 meses al 30-sep),
            # suponiendo la misma quema y sin dinero nuevo desde el informe (las ventas posteriores se ven en la munición)
            if hoy:
                pasados = (hoy - dt.date.fromisoformat(ca["end"])).days / 30.44
                out.update(meses_desde_informe=round(pasados, 1), autonomia_hoy=round(out["autonomia_meses"] - pasados, 1),
                           caja_estimada_hoy=round(ca["val"] + inv - q * pasados))
    return out


def finalizar(fecha, replay, forzar=False, sin_actualizar=False):
    C = json.load(open(ruta(fecha, "_candidatos")))
    cl_f = ruta(fecha, "_clasif")
    CL = json.load(open(cl_f)) if os.path.exists(cl_f) else {}
    y = None
    try:
        y = Yahoo()
    except Exception as e:
        print("Yahoo no disponible:", e)
    if not replay and not sin_actualizar and C["candidatos"] and y:   # precio del premarket actualizado
        try:
            q = {x["symbol"]: x for x in y.cotizaciones([c["sym"] for c in C["candidatos"]])}
            for c in C["candidatos"]:
                x = q.get(c["sym"], {})
                # con el mercado abierto, el gap es el de la apertura (como en escanear), no el cambio del momento
                px = x.get("preMarketPrice") if x.get("marketState") in ("PRE", "PREPRE") else x.get("regularMarketOpen") or x.get("regularMarketPrice")
                if px:
                    c["precio"] = round(px, 4); c["gap"] = round(px / c["cierre_prev"] - 1, 4)
                if x.get("preMarketVolume"):
                    c["vol_pre"] = x["preMarketVolume"]
        except Exception as e:
            print("sin actualizar precios:", e)
    prev = {}
    if sin_actualizar and os.path.exists(ruta(fecha)):
        # 1-oct-2026: rehacer una lista publicada debe conservar SUS precios, gap y premarket (antes se tomaban los del escaneo y el
        # premarket se recalculaba a la hora del rehecho: VEEA pasó de gap 56 % a 44 % y perdió su tramo)
        L0 = json.load(open(ruta(fecha)))
        prev = {x["sym"]: x for x in L0.get("acciones", []) + L0.get("descartadas", [])}
        for c in C["candidatos"]:
            p0 = prev.get(c["sym"])
            if p0:
                c["precio"], c["gap"] = p0["precio"], p0["gap"]
                if p0.get("vol_pre") is not None:
                    c["vol_pre"] = p0["vol_pre"]
    err, av = auditar(C, CL, replay)
    for e in err:
        print("ERROR:", e)
    for a in av:
        print("aviso:", a)
    if err and not forzar:
        sys.exit("Auditoría con errores: lista NO generada. Corregir y repetir (o --forzar si es imposible corregir a tiempo).")
    acciones, descartadas = [], []
    for c in C["candidatos"]:
        cl = CL.get(c["sym"], {})
        t = cl.get("tipo", "N")
        m = c.get("municion") or {}
        base = dict(sym=c["sym"], nombre=c["nombre"], sector=c.get("sector", ""), precio=c["precio"], cierre_prev=c["cierre_prev"],
                    gap=c["gap"], cap=c.get("cap"), acciones=c.get("acciones"), vol_pre=c.get("vol_pre"), bolsa=c.get("bolsa"),
                    clasif=dict(cl, tipo_es=TIPOS.get(t, "")))
        # filtro de campo: lo que el histórico dice que NO se shortea queda fuera de la vista (se guarda con su motivo)
        motivo = DESCARTE.get(t) or ("424B presentado HOY: la empresa está vendiendo acciones en esta subida (financiación del día)"
                                     if c.get("venta_hoy") else None) \
            or ("Precio < $1: con un locate normal ($0.02 por acción) la ventaja histórica pasa a negativa (ronda 5)"
                if (c.get("precio") or 0) < PRECIO_OPERABLE else None) \
            or ("Split del día: el gap no es real" if c.get("split_hoy") else None)
        if motivo:
            descartadas.append(dict(base, motivo=motivo, docs_hoy=c.get("docs_hoy", []))); continue
        avisos = []
        if t == "H" and not c.get("catalizadores"):
            avisos.append("Humo solo en nota de prensa, sin 8-K/6-K (caso no medido por separado)")
        if t == "N":
            avisos.append("Sube sin ninguna noticia encontrada (caso no medido: días de prueba 2 de 5 ganadoras)")
        if m.get("toxica"):
            avisos.append("Convertible de precio variable (tóxica) en el último informe: munición continua")
        pm = prev[c["sym"]].get("premarket", {}) if c["sym"] in prev else (premarket_1m(y.s, c["sym"], fecha) if y else {})
        cat = []
        for k in c.get("catalizadores", []):
            partes = []
            for p in k.get("partes", []):
                txt = p.get("texto", "")
                if len(txt) <= 1600 and not replay:          # listas antiguas guardaban solo 1 600 caracteres: se relee completo
                    t2 = get(p["url"], sec=True)
                    txt = resumen_doc(limpiar(t2), 15000) if t2 else txt
                partes.append(dict(archivo=p["archivo"], url=p["url"], texto=txt, recortado=p.get("recortado", False),
                                   negativos=p.get("negativos") if "negativos" in p else negativos(txt)))
            cat.append(dict(form=k["form"], hora=k["hora"], items=k["items"],
                            items_es="; ".join(f"{i} {ITEMS.get(i, '')}" for i in (k["items"] or "").split(",") if i),
                            url=k["url"], partes=partes))
        tramo = "≥ 50 %" if c["gap"] >= GAP_LISTA else "20-50 %"
        pt = puntuar(c, cl)
        acciones.append(dict(base, tramo=tramo, puntuacion=pt, estad=ESTAD_TERCIO[(tramo, pt["tercio"])],
                             riesgo=riesgo_estructural(c, m), premarket=pm, caja=caja(c["cik"], dt.date.fromisoformat(fecha)) if c.get("cik") else None,
                             historial=c.get("historial", []),
                             catalizadores=cat, docs_hoy=c.get("docs_hoy", []), noticias=c.get("noticias", []), municion=m,
                             costes=dict(locate_1c_R=round(0.01 / (STOP * c["precio"]), 3) if c.get("precio") else None),
                             avisos=avisos))
    acciones.sort(key=lambda x: (-x["puntuacion"]["valor"], -x["gap"]))
    # 1-oct-2026: verificador independiente obligatorio (listas/VERIFICADOR.md) para gap ≥ 50 % o tesis alta
    vf = ruta(fecha, "_verificacion")
    V = json.load(open(vf)) if os.path.exists(vf) else {}
    for x in acciones:
        if (x["gap"] >= GAP_LISTA or x["puntuacion"]["tercio"] == "Alta"):
            v = V.get(x["sym"])
            x["verificacion"] = v or dict(estado="pendiente")
            if not replay and not v and not forzar:
                err.append(f"{x['sym']}: falta la verificación independiente (listas/VERIFICADOR.md → {os.path.basename(vf)})")
    if err and not forzar:
        for e in err:
            print("ERROR:", e)
        sys.exit("Auditoría con errores: lista NO generada (verificación pendiente). Corregir y repetir (o --forzar).")
    descartadas.sort(key=lambda x: -x["gap"])
    out = dict(fecha=fecha, generado=dt.datetime.now(NY).strftime("%Y-%m-%d %H:%M"), replay=replay, desde=C["desde"], corte=C["corte"],
               version=2, reglas=dict(gap_minimo=GAP_VIGILAR, stop=STOP, deslizamiento=DESL, coste=COSTE, riesgo_accion=RIESGO_ACCION),
               acciones=acciones, descartadas=descartadas, resultados=None,
               auditoria=dict(errores=err, avisos=av, cobertura=C.get("cobertura"), forzada=bool(err and forzar)))
    if not replay:
        out["salud"] = salud(fecha, C, CL, err, av, acciones, descartadas, bool(err and forzar))
        print(out["salud"]["linea"])
    if prev:      # rehecha: se conserva la hora de publicación original y se anota la del rehecho
        out["rehecho"], out["generado"] = out["generado"], L0.get("generado", out["generado"])
    json.dump(out, open(ruta(fecha), "w"), ensure_ascii=False, indent=1, default=str)
    print("→", ruta(fecha), "|", ", ".join(f"{x['sym']}:{x['puntuacion']['valor']}({x['riesgo']['nivel']})" for x in acciones),
          "| descartadas:", ", ".join(x["sym"] for x in descartadas))


def salud(fecha, C, CL, err, av, acciones, descartadas, forzada):
    """Línea de salud de la mañana (1-oct-2026, pedida por el usuario): ¿funcionó el robot como siempre?"""
    pr = {}
    try:
        pr = json.load(open(ruta("_pruebas")))
    except Exception:
        pass
    cob = C.get("cobertura") or {}
    fu = cob.get("fuentes_universo") or {}
    todas = acciones + descartadas
    citas = [x for x in todas if (x.get("clasif") or {}).get("frase_en")]
    nocomp = [x["sym"] for x in todas if (x.get("clasif") or {}).get("cita_no_comprobable")]
    verif_nec = [x["sym"] for x in acciones if x["gap"] >= GAP_LISTA or (x.get("puntuacion") or {}).get("tercio") == "Alta"]
    verif_ok = [s_ for s_ in verif_nec if any(y["sym"] == s_ and y.get("verificacion") for y in acciones)]
    d = dict(pruebas=(f"{pr['total'] - pr['fallos']}/{pr['total']}" if pr.get("fecha") == fecha else "NO EJECUTADAS HOY"),
             pruebas_ok=pr.get("fecha") == fecha and pr.get("fallos") == 0,
             universo=cob.get("universo"), cobertura=cob.get("pct"),
             nasdaqtrader="ok" if not cob.get("ficheros_faltan") else f"falta {', '.join(cob['ficheros_faltan'])} (cubierto con la SEC)",
             sec=fu.get("sec"), massive=bool(cob.get("massive")), tradingview=cob.get("tradingview") is not None,
             candidatos=len(C.get("candidatos", [])), verificadas=f"{len(verif_ok)}/{len(verif_nec)}",
             citas_comprobadas=(f"{len(citas) - len(nocomp)}/{len(citas)}" if fecha >= PASOS_DESDE else "comprobación no activa (antes del 2-oct)"),
             citas_no_comprobables=nocomp,
             errores=len(err), avisos=len(av), forzada=forzada)
    d["linea"] = (f"Salud: pruebas {d['pruebas']} · universo {d['universo']} ({(d['cobertura'] or 0):.1%} cotizadas) · "
                  f"nasdaqtrader {d['nasdaqtrader']} · Massive {'ok' if d['massive'] else 'NO'} · TradingView {'ok' if d['tradingview'] else 'NO'} · "
                  f"candidatos {d['candidatos']} · verificadas {d['verificadas']} · citas comprobadas {d['citas_comprobadas']}"
                  + (f" (no comprobables: {', '.join(nocomp)})" if nocomp else "") + f" · auditoría {d['errores']} errores, {d['avisos']} avisos"
                  + (" · PUBLICADA FORZADA" if forzada else ""))
    return d


def resultados(fecha):
    """Resultado real de cada acción de la lista (setup A) para validar la lista con el tiempo."""
    import yfinance as yf
    L = json.load(open(ruta(fecha)))
    d = dt.date.fromisoformat(fecha)
    res = {}
    todas = L.get("acciones", []) + L.get("descartadas", []) + L.get("lista", []) + L.get("vigilar", [])   # v2 y listas antiguas
    for x in [v for v in todas if v.get("precio")]:
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
            # 30-sep: el histórico se midió con el gap de la APERTURA (la lista usa el del premarket, p. ej. BKYI 29-sep: +71 % a las
            # 9:05 y +105 % a la apertura) → para comparar en vivo, puntuación y tramo también con la apertura
            if x.get("puntuacion") and x.get("cierre_prev"):
                g = o / x["cierre_prev"] - 1
                p = puntuar(dict(x, gap=g), x.get("clasif") or {})
                res[x["sym"]].update(gap_apertura=round(g, 4), tramo_apertura="≥ 50 %" if g >= GAP_LISTA else "20-50 %",
                                     puntuacion_apertura=p["valor"], tercio_apertura=p["tercio"])
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
    ap.add_argument("--sin_actualizar", action="store_true", help="rehacer una lista ya publicada con los precios que tenía")
    a = ap.parse_args()
    {"escanear": lambda: escanear(a.fecha, a.replay, a.corte), "finalizar": lambda: finalizar(a.fecha, a.replay, a.forzar, a.sin_actualizar),
     "resultados": lambda: resultados(a.fecha)}[a.paso]()
