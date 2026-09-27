"""Ficha de dilución para short sellers de small caps.

Uso:  python3 herramientas/ficha_dilucion.py TICKER [TICKER ...]
Genera una ficha en Markdown (pantalla + fichas/TICKER_AAAA-MM-DD.md) con datos de SEC EDGAR y precios de Yahoo:
caja usable, quema mensual, runway, going concern, instrumentos que pueden convertirse en acciones, warrants con precio
de ejercicio vs. precio actual, ventas de acciones recientes (S-1/S-3/EFFECT/424B), 8-K recientes con sus Items,
contra-splits, avisos de Nasdaq y una lectura final "¿puede vender HOY?".

Todo es AUTOMÁTICO: los números clave deben confirmarse en el documento enlazado antes de arriesgar dinero.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "research eriphelo15 contact@example.com"}
AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(os.path.dirname(AQUI), "fichas")
HOY = dt.date.today()


# ------------------------------------------------------------------ utilidades
def _get(url, texto=False):
    for k in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
            time.sleep(0.12)                      # la SEC permite ~10 peticiones/s
            return r.decode("utf-8", "ignore") if texto else json.loads(r)
        except Exception:
            time.sleep(1.5 * (k + 1))
    return None


def limpiar(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = html.unescape(re.sub(r"<[^>]+>", " ", h))
    return re.sub(r"\s+", " ", h)


def fragmento(t, patron, antes=150, despues=450, n=1):
    out = []
    for m in re.finditer(patron, t, re.I):
        out.append(t[max(0, m.start() - antes): m.end() + despues].strip())
        if len(out) >= n:
            break
    return out


def usd(x):
    if x is None:
        return "n/d"
    s = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1e9:
        return f"{s}${x/1e9:.2f} B"
    if x >= 1e6:
        return f"{s}${x/1e6:.2f} M"
    if x >= 1e3:
        return f"{s}${x/1e3:.0f} k"
    return f"{s}${x:.2f}"


def num(x):
    return "n/d" if x is None else f"{x:,.0f}".replace(",", ".")


def fecha(s):
    return dt.date.fromisoformat(s[:10])


# ------------------------------------------------------------------ SEC
_TICKERS = None


def cik_de(ticker):
    global _TICKERS
    if _TICKERS is None:
        _TICKERS = _get("https://www.sec.gov/files/company_tickers.json") or {}
    for v in _TICKERS.values():
        if v["ticker"].upper() == ticker.upper():
            return v["cik_str"], v["title"]
    return None, None


def hechos(cik):
    return _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json") or {}


def ultimo(facts, tags, taxo="us-gaap", unidad="USD", duracion=False):
    """Último valor reportado entre varios tags. duracion=True -> devuelve (valor, meses, fin)."""
    mejor = None
    for tag in tags:
        u = facts.get("facts", {}).get(taxo, {}).get(tag, {}).get("units", {}).get(unidad, [])
        for f in u:
            if duracion and "start" not in f:
                continue
            if not duracion and "start" in f:
                continue
            clave = (f["end"], f.get("filed", ""))
            if mejor is None or clave > mejor[0]:
                mejor = (clave, f, tag)
    if mejor is None:
        return (None, None, None) if duracion else (None, None)
    f = mejor[1]
    if duracion:
        meses = max(1, round((fecha(f["end"]) - fecha(f["start"])).days / 30.4))
        return f["val"], meses, f["end"]
    return f["val"], f["end"]


def documentos(cik):
    d = _get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json") or {}
    r = d.get("filings", {}).get("recent", {})
    out = []
    for i in range(len(r.get("form", []))):
        acc = r["accessionNumber"][i]
        out.append(dict(form=r["form"][i], fecha=r["filingDate"][i], doc=r["primaryDocument"][i],
                        desc=r.get("primaryDocDescription", [""] * 9999)[i], items=r.get("items", [""] * 9999)[i],
                        url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{r['primaryDocument'][i]}"))
    return out, d.get("exchanges", []), d.get("name", "")


# ------------------------------------------------------------------ precios
def precios(ticker):
    try:
        import yfinance as yf
        h = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=False)
        if h is None or h.empty:
            return None
        if hasattr(h.columns, "levels"):
            h.columns = h.columns.get_level_values(0)
        return h.dropna(subset=["Close"])
    except Exception:
        return None


def spl(ticker):
    """Splits de Yahoo: lista de (fecha, ratio). Contra-split 1:10 -> 0.1."""
    try:
        import yfinance as yf
        s = yf.Ticker(ticker).splits
        return [(i.date(), float(v)) for i, v in s.items() if v > 0]
    except Exception:
        return []


# ------------------------------------------------------------------ ficha
ITEMS = {"1.01": "Acuerdo importante (oferta, fusión, préstamo)", "1.02": "Fin de un acuerdo", "2.03": "Nueva deuda",
         "3.01": "AVISO DE NASDAQ/BOLSA (incumplimiento)", "3.02": "Venta de acciones no registradas (colocación privada)",
         "3.03": "Cambio en derechos de accionistas", "5.01": "Cambio de control", "5.02": "Cambios de directivos",
         "5.03": "Cambio de estatutos (contra-split frecuente)", "5.07": "Resultado de votación de junta",
         "7.01": "Nota de prensa (Reg FD)", "8.01": "Otros hechos", "9.01": "Anexos"}
PALABRAS = [("securities purchase agreement", "acuerdo de compra de acciones"), ("registered direct", "registered direct"),
            ("inducement", "warrant inducement"), ("at-the-market|at the market offering|sales agreement", "ATM"),
            ("private placement", "colocación privada"), ("pre-funded warrant", "pre-funded warrants"),
            ("reverse stock split", "contra-split"), ("deficiency|minimum bid|delist", "aviso Nasdaq / deslistado"),
            ("convertible note|convertible debenture", "nota convertible"), ("equity line|equity purchase agreement|standby equity", "línea de capital (ELOC)"),
            ("merger|business combination", "fusión")]


def ficha(ticker):
    ticker = ticker.upper()
    L = []
    p = L.append
    cik, titulo = cik_de(ticker)
    if cik is None:
        return f"# {ticker}\nNo encontré el ticker en la SEC (¿empresa extranjera que reporta con 20-F/6-K o ticker nuevo?).\n"
    facts = hechos(cik)
    docs, bolsas, nombre = documentos(cik)
    px = precios(ticker)

    # --- precio y acciones
    acciones, acc_fecha = ultimo(facts, ["EntityCommonStockSharesOutstanding"], taxo="dei", unidad="shares")
    precio = ult_vol = max60 = None
    if px is not None and len(px):
        precio = float(px["Close"].iloc[-1])
        ult_vol = float(px["Volume"].iloc[-1])
        max60 = float(px["Close"].tail(60).max())
    mcap = acciones * precio if acciones and precio else None

    p(f"# Ficha de dilución — {ticker} · {nombre or titulo}")
    p(f"_Generada {HOY} · bolsa: {', '.join(bolsas) or 'n/d'} · CIK {cik} · [EDGAR](https://www.sec.gov/edgar/browse/?CIK={cik})_\n")
    p("## 1. Tamaño y precio")
    p(f"- Precio último cierre: **{usd(precio)}** · máximo de cierre 60 días: {usd(max60)}")
    p(f"- Acciones en circulación (portada del último informe, {acc_fecha or 'n/d'}): **{num(acciones)}**")
    p(f"- Capitalización aproximada: **{usd(mcap)}**")
    if ult_vol and acciones:
        p(f"- Volumen del último día: {num(ult_vol)} acciones → **{ult_vol/acciones:.1f} veces** las acciones en circulación")
    if px is not None and len(px) >= 5:
        p("- Últimos 5 días: " + " | ".join(f"{i.date()}: O {r.Open:.2f} H {r.High:.2f} C {r.Close:.2f}" for i, r in px.tail(5).iterrows()))

    # --- caja y quema
    caja, caja_f = ultimo(facts, ["CashAndCashEquivalentsAtCarryingValue", "Cash"])
    restr, _ = ultimo(facts, ["RestrictedCashCurrent", "RestrictedCash", "RestrictedCashAndCashEquivalentsAtCarryingValue"])
    ocf, meses, ocf_f = ultimo(facts, ["NetCashProvidedByUsedInOperatingActivities"], duracion=True)
    patrimonio, _ = ultimo(facts, ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"])
    deuda_conv, _ = ultimo(facts, ["ConvertibleNotesPayableCurrent", "ConvertibleNotesPayable", "ConvertibleDebtCurrent", "ConvertibleDebt"])
    antidil, _, antidil_f = ultimo(facts, ["AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount"], unidad="shares", duracion=True)
    quema = -ocf / meses if ocf is not None and ocf < 0 else None
    runway = caja / quema if caja is not None and quema else None
    p("\n## 2. Caja y quema (datos XBRL del último 10-Q/10-K)")
    p(f"- Caja usable (Cash and cash equivalents, {caja_f or 'n/d'}): **{usd(caja)}**" + (f" · caja RESTRINGIDA aparte: {usd(restr)} (no cuenta)" if restr else ""))
    if ocf is not None:
        p(f"- Flujo de caja operativo: {usd(ocf)} en **{meses} meses** (hasta {ocf_f}) → quema mensual **{usd(quema) if quema else 'no quema (genera caja)'}**")
    p(f"- **Runway: {runway:.1f} meses**" if runway is not None else "- Runway: n/d")
    if patrimonio is not None:
        p(f"- Patrimonio de los accionistas: {usd(patrimonio)}" + (" ⚠️ NEGATIVO" if patrimonio < 0 else ""))
    if deuda_conv:
        p(f"- Deuda convertible en balance: {usd(deuda_conv)}")
    if antidil:
        rel = f" → **{antidil/acciones:.1f}×** las acciones en circulación" if acciones else ""
        p(f"- Acciones potenciales excluidas del BPA (warrants, opciones, convertibles…): **{num(antidil)}**{rel}")

    # --- último informe periódico: texto
    per = [d for d in docs if d["form"] in ("10-Q", "10-K", "10-Q/A", "10-K/A")]
    t = limpiar(_get(per[0]["url"], texto=True) or "") if per else ""
    p(f"\n## 3. Lo que dice el último informe ({per[0]['form']} del {per[0]['fecha']}) — [abrir]({per[0]['url']})" if per else "\n## 3. Último informe: no encontrado")
    if t:
        gc = bool(re.search(r"substantial doubt", t, re.I))
        p(f"- Going concern: **{'SÍ ⚠️' if gc else 'no aparece'}**")
        for etiqueta, patron, a, dsp in [
                ("Caja restringida", r"restricted cash (of|consists|represents|is held)", 50, 350),
                ("ATM", r"at-the-market|at the market (offering|sales)", 120, 450),
                ("Contra-split", r"(effected|effect of|approved) (a|the)? ?\d?-?(for|to)?-?\d* ?reverse (stock )?split|\d+-for-\d+ reverse|reverse (stock )?split (was|became) effective", 120, 350),
                ("Convertible de precio variable", r"not determinable|variable conversion|lower of .{0,80}(conversion|price)|% of the (lowest|average)", 250, 300),
                ("Warrants", r"warrants? (were )?outstanding|outstanding warrants", 250, 450),
                ("Hechos posteriores al cierre", r"subsequent events?", 0, 900)]:
            fr = fragmento(t, patron, a, dsp)
            if fr:
                p(f"- **{etiqueta}:** “…{fr[0][:900]}…”")

    # --- warrants: precios de ejercicio encontrados, ajustados por splits posteriores al documento
    splits = spl(ticker)
    fuentes = [(per[0]["fecha"], per[0]["form"], t)] if t else []
    recientes = [d for d in docs if fecha(d["fecha"]) >= HOY - dt.timedelta(days=150)]
    for d in [d for d in recientes if d["form"].startswith("424B") or d["form"] == "8-K"][:8]:
        d["_txt"] = limpiar(_get(d["url"], texto=True) or "")
        fuentes.append((d["fecha"], d["form"], d["_txt"]))
    ejer = {}
    prefunded = False
    for f_doc, form, tx in fuentes:
        # factor de los splits ocurridos DESPUÉS del documento (0.1 para un contra-split 1:10)
        factor = 1.0
        for f_sp, r in splits:
            if f_sp > fecha(f_doc):
                factor *= r
        for m in re.finditer(r"exercise price[^$.]{0,60}\$\s?([0-9]+(?:\.[0-9]+)?)", tx, re.I):
            v = float(m.group(1))
            if v <= 0.01:
                prefunded = True               # pre-funded: ya pagados, equivalen a acciones
                continue
            if v < 10000:
                va = round(v / factor, 4)
                clave = round(va, 2)
                ejer.setdefault(clave, (va, v, factor, f_doc, form))
    if ejer or prefunded:
        p("\n## 4. Warrants: precios de ejercicio encontrados (último informe + 424B/8-K de 150 días), AJUSTADOS por contra-splits")
        for clave in sorted(ejer):
            va, v, factor, f_doc, form = ejer[clave]
            estado = "—"
            if precio:
                estado = "**EN EL DINERO ⚠️ (se pueden ejercer y vender)**" if va < precio else "fuera del dinero"
            ajuste = f" (original ${v:g} en {form} del {f_doc}, ajustado ×{1/factor:g} por contra-split)" if factor != 1 else f" ({form} del {f_doc})"
            p(f"- **${va:g}**{ajuste} → {estado}")
        if prefunded:
            p("- Hay **pre-funded warrants** (precio ~$0.001): ya están pagados y equivalen a acciones que pueden aparecer en cualquier momento.")
        p("_Los precios salen de búsquedas de texto: pueden mezclar warrants, opciones o precios ya ejercidos. Confirma en el documento._")

    # --- ventas de acciones y registros
    p("\n## 5. Munición: registros y ventas de acciones (últimos 12 meses)")
    reg = [d for d in docs if fecha(d["fecha"]) >= HOY - dt.timedelta(days=365)
           and re.match(r"^(S-1|S-3|F-1|F-3|S-11|EFFECT|424B\d|RW|POS AM)", d["form"])]
    if not reg:
        p("- Ninguno. (La dilución, si existe, vendría por conversiones, ATM ya registrado antes o colocaciones privadas.)")
    for d in reg[:15]:
        extra = ""
        if d["form"].startswith("424B"):
            tx = d.get("_txt") or limpiar(_get(d["url"], texto=True) or "")
            m = re.search(r"(Up to \$[0-9,\.]+|[0-9][0-9,]{3,} Shares of Common Stock[^.]{0,200}?)", tx)
            pr = re.search(r"(public offering price|offering price|purchase price) of \$\s?([0-9\.]+)", tx, re.I)
            sup = bool(re.search(r"prospectus supplement no\.", tx[:600], re.I))
            if sup:                                   # anexo: el precio está en el 424B original, no aquí
                extra = " · SUPLEMENTO (anexo de una venta anterior; suele traer pegado un 8-K reciente)"
            else:
                extra = " · " + " · ".join(x for x in [m.group(1)[:140] if m else "", f"precio ${pr.group(2)}" if pr else ""] if x)
        p(f"- {d['fecha']} **{d['form']}** [{d['desc'] or 'doc'}]({d['url']}){extra}")

    # --- 8-K recientes
    p("\n## 6. 8-K de los últimos 60 días")
    ochok = [d for d in docs if d["form"] in ("8-K", "8-K/A") and fecha(d["fecha"]) >= HOY - dt.timedelta(days=60)]
    if not ochok:
        p("- Ninguno.")
    for d in ochok[:12]:
        its = [i.strip() for i in (d["items"] or "").split(",") if i.strip()]
        desc = "; ".join(f"{i} {ITEMS.get(i, '')}".strip() for i in its)
        tx = d.get("_txt") or limpiar(_get(d["url"], texto=True) or "")
        claves = [nom for pat, nom in PALABRAS if re.search(pat, tx, re.I)]
        p(f"- {d['fecha']} [8-K]({d['url']}) · Items: {desc or 'n/d'}" + (f" · palabras clave: **{', '.join(claves)}**" if claves else ""))

    # --- contra-splits y avisos
    avisos = [d for d in docs if fecha(d["fecha"]) >= HOY - dt.timedelta(days=730) and d["form"] == "8-K" and ("3.01" in (d["items"] or "") or "5.03" in (d["items"] or ""))]
    if avisos:
        p("\n## 7. Avisos de bolsa (3.01) y cambios de estatutos (5.03, suele ser contra-split) — 2 años")
        for d in avisos[:10]:
            p(f"- {d['fecha']} [8-K]({d['url']}) Items {d['items']}")

    # --- lectura final
    p("\n## 8. Lectura rápida (automática)")
    banderas = []
    if runway is not None and runway < 6:
        banderas.append(f"runway corto ({runway:.1f} meses): necesita dinero pronto")
    if t and re.search(r"substantial doubt", t, re.I):
        banderas.append("going concern")
    if patrimonio is not None and patrimonio < 0:
        banderas.append("patrimonio negativo")
    s3 = [d for d in docs if d["form"] in ("S-3", "S-3/A", "F-3") and fecha(d["fecha"]) >= HOY - dt.timedelta(days=365 * 3)]
    venta90 = any(d["form"].startswith("424B") and fecha(d["fecha"]) >= HOY - dt.timedelta(days=90) for d in docs)
    atm = bool(t and re.search(r"at-the-market", t, re.I))
    itm = bool(precio and any(ejer[k][0] < precio for k in ejer))
    toxica = bool(t and re.search(r"not determinable|variable conversion|% of the (average of the )?(three )?lowest|lowest (daily )?(VWAP|trading price)", t, re.I))
    if s3:
        banderas.append(f"shelf S-3 presentado ({s3[0]['fecha']}) → puede vender rápido si está efectivo")
    if venta90:
        banderas.append("venta de acciones (424B) en los últimos 90 días")
    if atm:
        banderas.append("programa ATM mencionado en el último informe")
    if itm:
        banderas.append("warrants EN EL DINERO")
    if prefunded:
        banderas.append("pre-funded warrants pendientes (equivalen a acciones)")
    if antidil and acciones and antidil / acciones > 1:
        banderas.append(f"acciones potenciales = {antidil/acciones:.1f}× las actuales")
    if toxica:
        banderas.append("convertible de precio variable (tóxica): el tenedor convierte con descuento y vende")
    if any("3.01" in (d["items"] or "") for d in docs if fecha(d["fecha"]) >= HOY - dt.timedelta(days=365)):
        banderas.append("aviso de Nasdaq/bolsa en el último año")
    if s3 and max60 and acciones and max60 * acciones < 75e6:
        banderas.append(f"baby shelf: public float < $75 M → por S-3 solo puede vender ~1/3 del float/año (≈ {usd(max60*acciones/3)} como máximo, aproximado)")
    for b in banderas:
        p(f"- ⚠️ {b}")
    empresa = s3 or venta90 or atm
    if empresa or itm:
        veredicto = "**Probablemente SÍ**: hay munición activa (" + ", ".join(x for x, c in [("shelf/ATM", s3 or atm), ("venta reciente 424B", venta90), ("warrants en el dinero", itm)] if c) + "). Revisa secciones 4 y 5."
    else:
        veredicto = "**No se ve munición activa de la empresa** en EDGAR (sin S-3/ATM/424B recientes ni warrants en el dinero): la oferta nueva de acciones puede tardar → **más riesgo de squeeze**."
    if toxica:
        veredicto += " ⚠️ Pero hay una **convertible tóxica**: su tenedor sí puede convertir y vender en la subida."
    p(f"\n**¿Puede vender acciones HOY?** {veredicto}")
    p("\n_Ficha automática. Confirma los números clave en los enlaces antes de operar. Las ventas por ATM se conocen con retraso "
      "(siguiente 10-Q) y los 8-K pueden tardar hasta 4 días hábiles; las notas de prensa no siempre están en EDGAR._")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    os.makedirs(SALIDA, exist_ok=True)
    for tk in sys.argv[1:]:
        f = ficha(tk)
        print(f)
        open(os.path.join(SALIDA, f"{tk.upper()}_{HOY}.md"), "w").write(f)
