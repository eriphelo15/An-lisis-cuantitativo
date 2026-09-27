"""Acceso a las APIs públicas: GeckoTerminal y RugCheck."""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

GECKO = "https://api.geckoterminal.com/api/v2/networks/solana"
RUGCHECK = "https://api.rugcheck.xyz/v1/tokens"

CABECERAS = {"User-Agent": "Mozilla/5.0 (radar-memes)", "Accept": "application/json"}

# GeckoTerminal permite ~30 peticiones/min en su plan gratuito.
PAUSA_GECKO = 2.2
# RugCheck permite 15 peticiones/min.
PAUSA_RUGCHECK = 4.1

# Mints de SOL y stablecoins: nunca son el token que nos interesa.
MINTS_BASE = {
    "So11111111111111111111111111111111111111112",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
}


def _get(url, reintentos=3):
    for intento in range(reintentos):
        try:
            peticion = urllib.request.Request(url, headers=CABECERAS)
            with urllib.request.urlopen(peticion, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429:
                return None  # error del lado de la petición: reintentar no sirve
            time.sleep(10 * (intento + 1) if e.code == 429 else 2 * (intento + 1))
        except Exception:
            time.sleep(2 * (intento + 1))
    return None


def pools_recientes(paginas_nuevos=10, paginas_trending=2):
    """Pools nuevos y en tendencia de Solana (GeckoTerminal), sin duplicados."""
    urls = [f"{GECKO}/new_pools?page={p}&include=dex" for p in range(1, paginas_nuevos + 1)]
    urls += [f"{GECKO}/trending_pools?duration={d}&page={p}&include=dex"
             for d in ("5m", "1h") for p in range(1, paginas_trending + 1)]
    pools = {}
    for url in urls:
        datos = _get(url)
        for x in (datos or {}).get("data", []):
            pools[x["id"]] = x
        time.sleep(PAUSA_GECKO)
    return list(pools.values())


def rugcheck(mint):
    """Resumen de riesgos de RugCheck, o None si no respondió."""
    datos = _get(f"{RUGCHECK}/{mint}/report/summary")
    time.sleep(PAUSA_RUGCHECK)
    if not datos or "risks" not in datos:
        return None
    riesgos = datos.get("risks") or []
    return {
        "rc_score": datos.get("score_normalised"),
        "rc_peligros": sum(1 for r in riesgos if r.get("level") == "danger"),
        "rc_avisos": sum(1 for r in riesgos if r.get("level") == "warn"),
        "rc_riesgos": "|".join(r.get("name", "") for r in riesgos),
        "lp_bloqueado": datos.get("lpLockedPct"),
    }


def estado_tokens(mints):
    """Precio, market cap, liquidez y pool principal actuales, por lotes de 30.

    Usa GeckoTerminal, la misma fuente que la detección: DexScreener no indexa
    algunos pools (p. ej. ciertos de Meteora) y haría pasar por muertos a
    tokens vivos. Un mint ausente de la respuesta queda fuera del resultado.
    """
    estado = {}
    mints = list(mints)
    for i in range(0, len(mints), 30):
        lote = mints[i:i + 30]
        datos = _get(f"{GECKO}/tokens/multi/{','.join(lote)}?include=top_pools") or {}
        for x in datos.get("data", []):
            a = x.get("attributes", {})
            pools = ((x.get("relationships") or {}).get("top_pools") or {}).get("data") or []
            estado[a.get("address")] = {
                "precio": float(a.get("price_usd") or 0),
                "mc": float(a.get("market_cap_usd") or a.get("fdv_usd") or 0),
                "liq": float(a.get("total_reserve_in_usd") or 0),
                "pool": pools[0]["id"].split("_", 1)[1] if pools else None,
            }
        time.sleep(PAUSA_GECKO)
    return estado


def velas_5m(pool, hasta_ts, limite=300):
    """Velas de 5 min en USD hasta `hasta_ts`, en orden cronológico.

    Cada vela es (ts, apertura, máximo, mínimo, cierre, volumen).
    """
    url = (f"{GECKO}/pools/{pool}/ohlcv/minute?aggregate=5&limit={limite}"
           f"&currency=usd&before_timestamp={int(hasta_ts)}")
    datos = _get(url)
    time.sleep(PAUSA_GECKO)
    if not datos:
        return []
    lista = datos.get("data", {}).get("attributes", {}).get("ohlcv_list") or []
    return sorted(tuple(v) for v in lista)


def info_token(mint):
    """Holders y autoridades del token (GeckoTerminal), o None si no respondió.

    `top10_pct` es el % del suministro en manos de los 10 mayores holders
    según GeckoTerminal; `holders_antig_min` indica cuán reciente es el dato.
    """
    datos = _get(f"{GECKO}/tokens/{mint}/info")
    time.sleep(PAUSA_GECKO)
    a = (datos or {}).get("data", {}).get("attributes")
    if not a:
        return None
    h = a.get("holders") or {}
    dist = h.get("distribution_percentage") or {}
    antig = ""
    if h.get("last_updated"):
        t = datetime.fromisoformat(h["last_updated"].replace("Z", "+00:00"))
        antig = round((datetime.now(timezone.utc) - t).total_seconds() / 60)
    return {
        "holders": h.get("count") or "",
        "top10_pct": dist.get("top_10") or "",
        "top11_20_pct": dist.get("11_20") or "",
        "holders_antig_min": antig,
        "mint_autoridad": a.get("mint_authority") or "",
        "freeze_autoridad": a.get("freeze_authority") or "",
        "gt_score": round(a["gt_score"], 1) if a.get("gt_score") is not None else "",
    }
