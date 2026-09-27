"""Detección: registra los tokens nuevos que superan un mínimo de actividad."""

from collections import Counter
from datetime import datetime, timedelta, timezone

from . import fuentes

# Mínimo para registrar un token (no es el filtro de compra: se registran
# también los que no lo pasan, para poder comparar).
MINIMO = {
    "mc_min": 10_000, "mc_max": 5_000_000,
    "liq_min": 5_000, "edad_max_min": 24 * 60, "compradores_h1_min": 25,
}

# Máximo de consultas a RugCheck por escaneo (~3 min con su límite de 15/min).
MAX_RUGCHECK_POR_ESCANEO = 40

# Filtro de compra v1: hipótesis a validar con los datos, no una verdad.
FILTRO = {
    "mc_min": 50_000, "mc_max": 1_500_000,
    "liq_mc_min": 0.08, "liq_mc_max": 0.6,
    "vol_mc_max": 3.0,
    "compradores_h1_min": 100,
    "ratio_cv_min": 1.2, "ratio_cv_max": 8.0,
}


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _simbolo(nombre):
    return nombre.split(" / ")[0].strip()


def _clave(simbolo):
    return "".join(c for c in simbolo.lower() if c.isalnum())


def _fila(pool, ahora):
    a = pool["attributes"]
    rel = pool["relationships"]
    mint = rel["base_token"]["data"]["id"].split("_", 1)[1]
    if mint in fuentes.MINTS_BASE:
        return None
    t, v, pc = a["transactions"], a["volume_usd"], a["price_change_percentage"]
    creado = datetime.fromisoformat(a["pool_created_at"].replace("Z", "+00:00"))
    return {
        "ts": ahora.isoformat(timespec="seconds"),
        "mint": mint,
        "simbolo": _simbolo(a["name"]),
        "nombre": a["name"],
        "pool": a["address"],
        "dex": ((rel.get("dex") or {}).get("data") or {}).get("id", ""),
        "edad_min": round((ahora - creado).total_seconds() / 60, 1),
        "precio": _f(a.get("base_token_price_usd")),
        "mc": _f(a.get("market_cap_usd")) or _f(a.get("fdv_usd")),
        "liq": _f(a.get("reserve_in_usd")),
        "compradores_m5": t["m5"].get("buyers") or 0,
        "vendedores_m5": t["m5"].get("sellers") or 0,
        "compradores_h1": t["h1"].get("buyers") or 0,
        "vendedores_h1": t["h1"].get("sellers") or 0,
        "compras_h1": t["h1"].get("buys") or 0,
        "ventas_h1": t["h1"].get("sells") or 0,
        "vol_m5": _f(v.get("m5")),
        "vol_h1": _f(v.get("h1")),
        "var_m5": _f(pc.get("m5")),
        "var_h1": _f(pc.get("h1")),
        "var_h6": _f(pc.get("h6")),
    }


def _supera_minimo(r):
    m = MINIMO
    return (m["mc_min"] <= r["mc"] <= m["mc_max"] and r["liq"] >= m["liq_min"]
            and r["edad_min"] <= m["edad_max_min"]
            and r["compradores_h1"] >= m["compradores_h1_min"] and r["precio"] > 0)


def evaluar_filtro(r):
    """Devuelve la lista de motivos por los que el token no pasa (vacía = pasa)."""
    f = FILTRO
    motivos = []
    # Sin respuesta de RugCheck (falla a menudo) no se descarta: el informe
    # separa esos tokens como "sin datos" para ver si importa.
    if r.get("rc_peligros") not in (None, "") and int(r["rc_peligros"]) > 0:
        motivos.append("peligro_rugcheck")
    if int(r.get("clones") or 0) > 0:
        motivos.append("nombre_clonado")
    if not f["mc_min"] <= r["mc"] <= f["mc_max"]:
        motivos.append("mc_fuera_rango")
    liq_mc = r["liq"] / r["mc"] if r["mc"] else 0
    if not f["liq_mc_min"] <= liq_mc <= f["liq_mc_max"]:
        motivos.append("liquidez_anomala")
    if r["mc"] and r["vol_h1"] / r["mc"] > f["vol_mc_max"]:
        motivos.append("volumen_inflado")
    if r["compradores_h1"] < f["compradores_h1_min"]:
        motivos.append("pocos_compradores")
    ratio = r["compradores_h1"] / max(1, r["vendedores_h1"])
    if ratio > f["ratio_cv_max"]:
        motivos.append("compras_desbalanceadas")
    elif ratio < f["ratio_cv_min"]:
        motivos.append("presion_venta")
    return motivos


def puntuar(r):
    """Puntuación orientativa (la del primer escaneo manual), para evaluarla."""
    ratio = r["compradores_h1"] / max(1, r["vendedores_h1"])
    rotacion = r["vol_h1"] / max(1, r["mc"])
    liq_mc = r["liq"] / max(1, r["mc"])
    s = min(ratio, 3) * 20 + min(rotacion, 2) * 15 + min(r["compradores_h1"], 600) / 20
    s += 10 if r["var_m5"] > 0 else -5
    s += 10 if 0.08 <= liq_mc <= 0.5 else -10
    s -= 40 * int(r.get("rc_peligros") or 0)
    return round(s, 1)


def escanear(almacen, con_rugcheck=True, log=print):
    ahora = datetime.now(timezone.utc)
    pools = fuentes.pools_recientes()
    filas = {}
    for p in pools:
        try:
            r = _fila(p, ahora)
        except (KeyError, TypeError, ValueError):
            continue
        if r and (r["mint"] not in filas or r["liq"] > filas[r["mint"]]["liq"]):
            filas[r["mint"]] = r

    previas = almacen.detecciones()
    vistos = {d["mint"] for d in previas}

    # Clones: mismo símbolo con distinto mint, en este escaneo o en las
    # detecciones de las últimas 48 h.
    limite = ahora - timedelta(hours=48)
    mints_por_simbolo = {}
    for d in previas:
        if datetime.fromisoformat(d["ts"]) >= limite:
            mints_por_simbolo.setdefault(_clave(d["simbolo"]), set()).add(d["mint"])
    for r in filas.values():
        mints_por_simbolo.setdefault(_clave(r["simbolo"]), set()).add(r["mint"])

    nuevas = [r for r in filas.values() if r["mint"] not in vistos and _supera_minimo(r)]
    # Si hay más tokens nuevos que consultas disponibles, primero los de más compradores.
    nuevas.sort(key=lambda r: -r["compradores_h1"])
    for i, r in enumerate(nuevas):
        r["clones"] = len(mints_por_simbolo.get(_clave(r["simbolo"]), set())) - 1
        rc = fuentes.rugcheck(r["mint"]) if con_rugcheck and i < MAX_RUGCHECK_POR_ESCANEO else None
        r.update(rc or {"rc_score": "", "rc_peligros": "", "rc_avisos": "",
                        "rc_riesgos": "", "lp_bloqueado": ""})
        motivos = evaluar_filtro(r)
        r["pasa_filtro"] = int(not motivos)
        r["motivo_descarte"] = "|".join(motivos)
        r["puntuacion"] = puntuar(r)

    almacen.guardar_detecciones(nuevas)
    log(f"[escaneo] pools={len(pools)} tokens={len(filas)} nuevos_registrados={len(nuevas)} "
        f"pasan_filtro={sum(r['pasa_filtro'] for r in nuevas)}")
    return nuevas
