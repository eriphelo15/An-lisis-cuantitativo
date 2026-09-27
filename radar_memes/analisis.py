"""Informe: qué señales en la detección anticipan los tokens que se duplican o mueren."""

import os
from datetime import datetime, timedelta, timezone

import pandas as pd

APUESTA = 50        # dólares por token en el plan
COSTE_LADO = 0.03   # comisiones + slippage estimados por operación (entrada y salida)
N_MINIMO = 30       # por debajo, la muestra no permite sacar conclusiones


def cargar(almacen):
    det = pd.DataFrame(almacen.detecciones())
    seg = pd.DataFrame(almacen.seguimientos())
    if det.empty:
        return det
    num = ["edad_min", "precio", "mc", "liq", "compradores_h1", "vendedores_h1",
           "vol_h1", "var_m5", "var_h1", "rc_peligros", "clones", "pasa_filtro", "puntuacion",
           "holders", "top10_pct", "gt_score", "calor_narrativa", "puesto_narrativa"]
    for c in num:
        det[c] = pd.to_numeric(det[c], errors="coerce") if c in det else float("nan")
    for c in ["narrativa", "catalizador", "motivo_descarte", "dex"]:
        det[c] = det[c].fillna("") if c in det else ""
    det["ts"] = pd.to_datetime(det["ts"], utc=True)

    if seg.empty:
        return det
    for c in ["precio", "vivo", "max_x", "min_x", "min_hasta_max", "toco_2x", "regla_x"]:
        seg[c] = pd.to_numeric(seg[c], errors="coerce")
    for h in ["30m", "1h", "6h", "24h"]:
        s = seg[seg["horizonte"] == h].set_index("mint")
        det[f"vivo_{h}"] = det["mint"].map(s["vivo"])
        det[f"x_{h}"] = det["mint"].map(s["precio"]) / det["precio"]
    s24 = seg[seg["horizonte"] == "24h"].set_index("mint")
    for c in ["max_x", "min_x", "min_hasta_max", "toco_2x", "regla_x"]:
        det[c] = det["mint"].map(s24[c])
    return det


def _resumen(g):
    g = g[g["x_24h"].notna()]
    n = len(g)
    if n == 0:
        return pd.Series({"n": 0})
    muertos = ((g["vivo_24h"] == 0) | (g["x_24h"] <= 0.1)).mean()
    regla = g["regla_x"].dropna()
    neto = regla * (1 - COSTE_LADO) ** 2
    return pd.Series({
        "n": n,
        "muertos_24h": f"{muertos:.0%}",
        "tocaron_2x": f"{g['toco_2x'].mean():.0%}" if g["toco_2x"].notna().any() else "-",
        "mediana_24h": f"{g['x_24h'].median() - 1:+.0%}",
        "regla_$_por_50": f"{(neto.mean() - 1) * APUESTA:+.2f}" if len(regla) else "-",
        "aviso": "muestra pequeña" if n < N_MINIMO else "",
    })


def _tabla(df, columna, titulo):
    t = df.groupby(columna, observed=True).apply(_resumen, include_groups=False)
    return f"### {titulo}\n\n{t.to_markdown()}\n"


def generar(almacen):
    df = cargar(almacen)
    ahora = datetime.now(timezone.utc)
    lineas = [f"# Informe del radar de memecoins\n",
              f"Generado: {ahora:%Y-%m-%d %H:%M} UTC\n"]
    if df.empty:
        return "\n".join(lineas + ["Todavía no hay detecciones."])

    con24 = df[df.get("x_24h", pd.Series(dtype=float)).notna()] if "x_24h" in df else df.iloc[0:0]
    lineas.append(f"- Tokens registrados: **{len(df)}** (desde {df['ts'].min():%Y-%m-%d %H:%M})")
    lineas.append(f"- Con resultado a 24 h: **{len(con24)}**"
                  + ("" if len(con24) else " (el primero llega 24 h después de la primera detección)"))
    lineas.append(f"- Pasan el filtro v1: **{int(df['pasa_filtro'].sum())}**")
    lineas.append(f"- Resultado de la regla en dólares: por cada apuesta de ${APUESTA}, "
                  f"con {COSTE_LADO:.0%} de costes en la entrada y en la salida.\n")

    if len(con24):
        df = df.copy()
        df["filtro_v1"] = df["pasa_filtro"].map({1: "pasa", 0: "no pasa"})
        df["edad"] = pd.cut(df["edad_min"], [0, 15, 30, 60, 180, 1440],
                            labels=["<15 min", "15-30 min", "30-60 min", "1-3 h", "3-24 h"])
        df["cap"] = pd.cut(df["mc"], [0, 50e3, 150e3, 500e3, 1.5e6, 1e12],
                           labels=["<50K", "50-150K", "150-500K", "500K-1.5M", ">1.5M"])
        ratio = df["compradores_h1"] / df["vendedores_h1"].clip(lower=1)
        df["compradores_vs_vendedores"] = pd.cut(ratio, [0, 1.2, 3, 8, 1e9],
                                                 labels=["<1.2", "1.2-3", "3-8", ">8"])
        df["volumen_vs_cap"] = pd.cut(df["vol_h1"] / df["mc"], [0, 0.5, 1, 3, 1e9],
                                      labels=["<0.5", "0.5-1", "1-3", ">3"])
        df["peligros_rugcheck"] = df["rc_peligros"].map(
            lambda v: "sin datos" if pd.isna(v) else ("2+" if v >= 2 else str(int(v))))
        df["narrativa_"] = df["narrativa"].replace("", "sin narrativa")
        df["papel_en_narrativa"] = df.apply(
            lambda r: "sin narrativa" if not r["narrativa"]
            else ("líder" if r["puesto_narrativa"] == 1 else "seguidor/clon"), axis=1)
        df["calor"] = pd.cut(df["calor_narrativa"], [0, 1, 3, 8, 1e9],
                             labels=["1 token", "2-3", "4-8", "9+"])
        df["con_catalizador"] = df["catalizador"].map(lambda c: "sí" if c else "no")
        df["top10_holders"] = pd.cut(df["top10_pct"], [-1, 15, 25, 35, 50, 101],
                                     labels=["<15%", "15-25%", "25-35%", "35-50%", ">50%"])
        df["num_holders"] = pd.cut(df["holders"], [0, 100, 300, 1000, 3000, 1e9],
                                   labels=["<100", "100-300", "300-1K", "1K-3K", "3K+"])
        df["gt_score_"] = pd.cut(df["gt_score"], [-1, 30, 45, 60, 101],
                                 labels=["<30", "30-45", "45-60", "60+"])
        df["puntuacion_q"] = pd.qcut(df["puntuacion"].rank(method="first"), 5,
                                     labels=["Q1 (baja)", "Q2", "Q3", "Q4", "Q5 (alta)"])

        lineas.append("## ¿Funciona el filtro?\n")
        lineas.append(_tabla(df.assign(todos="todos"), "todos", "Todos los tokens"))
        lineas.append(_tabla(df, "filtro_v1", "Filtro v1"))
        motivos = df.assign(motivo=df["motivo_descarte"].fillna("").str.split("|")).explode("motivo")
        motivos = motivos[motivos["motivo"] != ""]
        if len(motivos):
            lineas.append(_tabla(motivos, "motivo", "Por motivo de descarte (un token puede tener varios)"))

        lineas.append("## Narrativas\n")
        for col, titulo in [("narrativa_", "Por narrativa"),
                            ("papel_en_narrativa", "Líder de su narrativa frente a seguidores y clones"),
                            ("calor", "Calor de la narrativa (tokens con el mismo tema en el escaneo)"),
                            ("con_catalizador", "Con catalizador próximo")]:
            lineas.append(_tabla(df, col, titulo))

        lineas.append("## Holders\n")
        for col, titulo in [("top10_holders", "% del suministro en los 10 mayores holders"),
                            ("num_holders", "Número de holders"), ("gt_score_", "GT Score")]:
            lineas.append(_tabla(df, col, titulo))

        lineas.append("## Señales por separado\n")
        for col, titulo in [("edad", "Edad al detectarlo"), ("cap", "Capitalización al detectarlo"),
                            ("compradores_vs_vendedores", "Compradores / vendedores (1 h)"),
                            ("volumen_vs_cap", "Volumen de 1 h / capitalización"),
                            ("peligros_rugcheck", "Peligros de RugCheck"),
                            ("puntuacion_q", "Puntuación (quintiles)"), ("dex", "DEX")]:
            lineas.append(_tabla(df, col, titulo))

        lineas.append("## Supervivencia por horizonte\n")
        for h in ["30m", "1h", "6h", "24h"]:
            v = df[f"vivo_{h}"].dropna()
            if len(v):
                lineas.append(f"- {h}: {v.mean():.0%} vivos (n={len(v)})")
        lineas.append("")

    lineas.append("## Narrativas activas (últimas 2 h)\n")
    ult = df[(df["ts"] >= ahora - timedelta(hours=2)) & (df["narrativa"] != "")]
    if len(ult):
        filas = []
        for narrativa, g in ult.groupby("narrativa"):
            lider = g.sort_values("liq", ascending=False).iloc[0]
            cat = g["catalizador"].iloc[0]
            filas.append({"narrativa": narrativa, "tokens_nuevos": len(g),
                          "lider": lider["simbolo"], "mc_lider": f"{lider['mc'] / 1e3:.0f}K",
                          "catalizador": f"{cat} (en {int(g['dias_catalizador'].iloc[0])} días)" if cat else "",
                          "mint_lider": lider["mint"]})
        t = pd.DataFrame(filas).sort_values("tokens_nuevos", ascending=False)
        lineas.append(t.to_markdown(index=False) + "\n")
    else:
        lineas.append("Ninguna.\n")

    recientes = df[(df["pasa_filtro"] == 1) & (df["ts"] >= ahora - timedelta(hours=1))]
    lineas.append("## Pasan el filtro en la última hora\n")
    lineas.append("Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. "
                  "Comprueba el contrato en rugcheck.xyz antes de hacer nada.\n")
    if len(recientes):
        cols = ["ts", "simbolo", "narrativa", "mc", "liq", "edad_min", "compradores_h1",
                "vendedores_h1", "top10_pct", "mint"]
        t = recientes[cols].copy()
        t["ts"] = t["ts"].dt.strftime("%H:%M")
        t["mc"] = (t["mc"] / 1e3).round().astype(int).astype(str) + "K"
        t["liq"] = (t["liq"] / 1e3).round().astype(int).astype(str) + "K"
        lineas.append(t.to_markdown(index=False))
    else:
        lineas.append("Ninguno.")
    return "\n".join(lineas) + "\n"


def escribir(almacen, log=print):
    texto = generar(almacen)
    ruta = os.path.join(almacen.carpeta, "INFORME.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    log(f"[informe] {ruta}")
    return texto
