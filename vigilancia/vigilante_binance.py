"""Vigilante de anuncios de Binance (retiros y listados) para seguimiento EN PAPEL de las reglas validadas
en cripto/INFORME_ECOSISTEMA.md. Uso: python3 vigilante_binance.py [minutos_hacia_atras]
Imprime una línea por alerta nueva y la añade a vigilancia/registro_papel.csv."""
import csv, json, os, re, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(AQUI, "registro_papel.csv")
UA = {"User-Agent": "curl/8.0"}
MEMES = {"DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "BOME", "MEME", "TURBO", "NEIRO", "PNUT", "ACT", "MOODENG",
         "PEOPLE", "1000SATS", "DOGS", "HMSTR", "CAT", "POPCAT", "MEW", "BRETT", "GOAT", "CHILLGUY", "PENGU", "TRUMP",
         "FARTCOIN", "BABYDOGE", "BAN", "MUBARAK", "BROCCOLI", "TST", "SPX", "GIGA", "PUMP", "CHEEMS", "WLFI"}


def get(u):
    for k in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))
        except Exception:
            time.sleep(2 * (k + 1))
    return None


def anuncios(cat):
    d = get(f"https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId={cat}&pageNo=1&pageSize=20")
    return d["data"]["catalogs"][0]["articles"] if d and d.get("data") else []


def precio_perp(tk):
    """Precio del perpetuo USDT en Binance (vía OKX si Binance bloquea); None si no hay."""
    for s in [tk, "1000" + tk]:
        d = get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}USDT")
        if d and "price" in d:
            return s + "USDT", float(d["price"])
    d = get(f"https://www.okx.com/api/v5/market/ticker?instId={tk}-USDT-SWAP")
    if d and d.get("data"):
        return tk + "-USDT-SWAP (OKX)", float(d["data"][0]["last"])
    return None, None


def main(minutos):
    desde = datetime.now(timezone.utc) - timedelta(minutes=minutos)
    vistos = set()
    if os.path.exists(REG):
        vistos = {(r["id"], r["tk"]) for r in csv.DictReader(open(REG))}
    alertas = []
    for x in anuncios(161):
        t = datetime.fromtimestamp(x["releaseDate"] / 1000, timezone.utc)
        if t < desde or not re.search(r"Will Delist", x["title"]) or re.search(r"Futures|Margin|Options|Alpha|Pairs", x["title"]):
            continue
        for tk in re.findall(r"\b([A-Z0-9]{2,15})\b", x["title"].split("Delist")[1].split(" on ")[0]):
            alertas.append(dict(id=x["id"], tk=tk, tipo="RETIRO", t=t, titulo=x["title"],
                                regla="CORTO en perpetuo al cierre de la hora del anuncio, salir a las 4 h (validado: +6.6%/op, 75% ganadoras)"))
    for x in anuncios(48):
        t = datetime.fromtimestamp(x["releaseDate"] / 1000, timezone.utc)
        if t < desde or not re.match(r"^(Binance Will List|Introducing .+ on Binance (HODLer|Launchpool|Megadrop))", x["title"]):
            continue
        for tk in re.findall(r"\(([A-Z0-9]{2,15})\)", x["title"]):
            meme = tk in MEMES
            alertas.append(dict(id=x["id"], tk=tk, tipo="LISTADO", t=t, titulo=x["title"],
                                regla=("MEMECOIN: NO operar (riesgo de squeeze)" if meme else
                                       "CORTO en perpetuo al cierre del 1er día de trading spot, salir a los 7 días (validado: +8%/op, 71% ganadoras)")))
    nuevas = [a for a in alertas if (str(a["id"]), a["tk"]) not in vistos]
    nuevo = not os.path.exists(REG)
    with open(REG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "tk", "tipo", "anuncio_utc", "detectado_utc", "perp", "precio", "regla", "titulo"])
        if nuevo:
            w.writeheader()
        for a in nuevas:
            perp, p = precio_perp(a["tk"])
            w.writerow(dict(id=a["id"], tk=a["tk"], tipo=a["tipo"], anuncio_utc=a["t"].isoformat(timespec="minutes"),
                            detectado_utc=datetime.now(timezone.utc).isoformat(timespec="minutes"), perp=perp or "sin perpetuo",
                            precio=p or "", regla=a["regla"], titulo=a["titulo"]))
            print(f"ALERTA {a['tipo']} {a['tk']} | anuncio {a['t']:%Y-%m-%d %H:%M} UTC | perpetuo {perp or 'NO HAY (no operable)'} {p or ''} | {a['regla']}")
    if not nuevas:
        print("SIN_ALERTAS")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 75)
