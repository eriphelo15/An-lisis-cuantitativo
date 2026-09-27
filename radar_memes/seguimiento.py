"""Controles posteriores: qué fue de cada token a los 30 min, 1 h, 6 h y 24 h."""

from datetime import datetime, timedelta, timezone

from . import fuentes

HORIZONTES = {"30m": 30, "1h": 60, "6h": 360, "24h": 1440}

# Un control tomado demasiado tarde ya no mide su horizonte: se marca como perdido.
# El de 24 h no se pierde nunca porque su precio sale de las velas, no del momento.
TOLERANCIA_MIN = {"30m": 15, "1h": 20, "6h": 60}

# Un token se da por muerto si su precio cae a un 10% o menos del de detección.
# (La liquidez no sirve: GeckoTerminal la da como 0 en algunos pools vivos.)
UMBRAL_MUERTO = 0.1

# Regla de salida del plan: vender 50% a 2x, 20% a 5x, 20% a 10x, dejar 10%;
# salir de todo lo que quede si cae a -50% desde la entrada.
ESCALONES = [(2.0, 0.5), (5.0, 0.2), (10.0, 0.2)]
STOP = 0.5

# Máximo de tokens con velas por ejecución, por el límite de GeckoTerminal.
MAX_VELAS_POR_RONDA = 20


def simular_regla(entrada, velas, vivo_al_final):
    """Multiplicador del capital a 24 h aplicando la regla de salida.

    Dentro de una misma vela no se sabe qué llegó antes, así que se asume
    lo peor: el stop se evalúa antes que los objetivos, y se ejecuta al peor
    precio entre el stop y el cierre de la vela (en un rug pull el precio se
    desploma en una sola vela y nadie vende a -50%).
    """
    restante, realizado = 1.0, 0.0
    alcanzados = set()
    for _, _, alto, bajo, cierre, _ in velas:
        if bajo <= entrada * STOP:
            return realizado + restante * min(STOP, cierre / entrada)
        for nivel, fraccion in ESCALONES:
            if nivel not in alcanzados and alto >= entrada * nivel:
                vendido = min(fraccion, restante)
                realizado += vendido * nivel
                restante -= vendido
                alcanzados.add(nivel)
    if not vivo_al_final or not velas:
        return realizado
    return realizado + restante * velas[-1][4] / entrada


def _analizar_velas(det, estado_actual):
    det_ts = datetime.fromisoformat(det["ts"]).timestamp()
    fin = det_ts + HORIZONTES["24h"] * 60
    pools = [det["pool"]]
    if estado_actual and estado_actual.get("pool") and estado_actual["pool"] != det["pool"]:
        pools.append(estado_actual["pool"])  # el token migró de pool (p. ej. pump.fun -> PumpSwap)

    por_ts = {}
    for pool in pools:
        for v in fuentes.velas_5m(pool, fin):
            if det_ts <= v[0] < fin and (v[0] not in por_ts or v[5] > por_ts[v[0]][5]):
                por_ts[v[0]] = v
    velas = [por_ts[t] for t in sorted(por_ts)]

    entrada = float(det["precio"])
    vivo = _vivo(det, estado_actual)
    if not velas or entrada <= 0:
        return {"max_x": "", "min_x": "", "min_hasta_max": "", "toco_2x": "",
                "regla_x": 0.0 if not vivo else "", "precio_24h": None}

    vela_max = max(velas, key=lambda v: v[2])
    max_x = vela_max[2] / entrada
    return {
        "max_x": round(max_x, 4),
        "min_x": round(min(v[3] for v in velas) / entrada, 4),
        "min_hasta_max": round((vela_max[0] - det_ts) / 60),
        "toco_2x": int(max_x >= 2),
        "regla_x": round(simular_regla(entrada, velas, vivo), 4),
        "precio_24h": velas[-1][4] if vivo else 0.0,
    }


def _vivo(det, e):
    return bool(e) and e["precio"] > UMBRAL_MUERTO * float(det["precio"])


def seguir(almacen, log=print):
    ahora = datetime.now(timezone.utc)
    hechos = {(s["mint"], s["horizonte"]) for s in almacen.seguimientos()}

    pendientes = []
    for d in almacen.detecciones():
        det_ts = datetime.fromisoformat(d["ts"])
        for h, minutos in HORIZONTES.items():
            objetivo = det_ts + timedelta(minutes=minutos)
            if (d["mint"], h) not in hechos and ahora >= objetivo:
                pendientes.append((d, h, (ahora - objetivo).total_seconds() / 60))
    if not pendientes:
        log("[seguimiento] nada pendiente")
        return []

    estado = fuentes.estado_tokens({d["mint"] for d, _, _ in pendientes})
    filas, velas_usadas, aplazados = [], 0, 0
    for d, h, retraso in pendientes:
        e = estado.get(d["mint"])
        vivo = _vivo(d, e)
        fila = {"mint": d["mint"], "horizonte": h, "ts": ahora.isoformat(timespec="seconds"),
                "retraso_min": round(retraso, 1), "vivo": int(vivo),
                "precio": e["precio"] if e else 0.0,
                "mc": e["mc"] if e else 0, "liq": e["liq"] if e else 0}

        if h == "24h":
            if velas_usadas >= MAX_VELAS_POR_RONDA:
                aplazados += 1
                continue
            velas_usadas += 1
            extra = _analizar_velas(d, e)
            precio_24h = extra.pop("precio_24h")
            if precio_24h is not None:
                fila["precio"] = precio_24h  # precio exacto a las 24 h, no el de ahora
            fila.update(extra)
        elif retraso > TOLERANCIA_MIN[h]:
            fila.update({"precio": "", "mc": "", "liq": "", "vivo": ""})  # perdido
        filas.append(fila)

    almacen.guardar_seguimientos(filas)
    log(f"[seguimiento] controles={len(filas)} aplazados_24h={aplazados}")
    return filas
