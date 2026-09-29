"""Hipótesis del usuario (29-sep-2026), EXPLORATORIA (muestra pequeña, sin DEV/VAL): ruptura temprana de la vela de las 9:30, solo cortos.
Reglas fijadas antes de ver resultados:
- Días: gappers de eventos_recientes con gap ≥ 50 % y apertura ≥ $1 (descriptivo: gap 20-50 %).
- Niveles: apertura (O), máximo y mínimo (L) de la vela de las 9:30 (1 min; con 5 min = primera vela de 5 min como aproximación).
- Entrada: primera vela que CIERRA por debajo de L → corto a ese cierre (sin órdenes stop). Entradas solo hasta las 11:00.
- Salida: una vela cierra por encima de O (recupera la apertura de las 9:30) → cubre a ese cierre.
- Reciclaje: tras salir, si otra vela vuelve a cerrar bajo L (antes de las 11:00) → corto otra vez. Tamaño constante (sin añadir).
- Fin: si sigue corto, cubre al cierre de la última vela antes de las 16:00 (variantes descriptivas: 10:30 y 11:30).
- 1R = distancia de L a O (mínimo 2 % del precio). Coste por intento: 0.5 % del precio (y 1 % como sensibilidad).
- Referencias en los mismos días: corto a la apertura de las 9:31 con la misma salida; corto a la apertura con stop +30 % al cierre."""
import os
import numpy as np
import pandas as pd

D = "/home/user/data/smallcaps"
E = pd.read_parquet(f"{D}/eventos_recientes.parquet")
E["date"] = pd.to_datetime(E.date)


def dia(sym, fecha, sub):
    f = f"{D}/{sub}/{sym}.parquet"
    if not os.path.exists(f):
        return None
    x = pd.read_parquet(f)
    x.columns = [c.lower() for c in x.columns]
    x = x[x.index.date == fecha.date()]
    x = x.between_time("09:30", "15:59")
    if len(x) < 10 or x.index[0].strftime("%H:%M") != "09:30":
        return None
    return x


def simular(x, fin="15:59", coste=0.005, entrar_ya=False):
    o, l = x.open.iloc[0], x.low.iloc[0]
    riesgo = max((o - l) / l, 0.02)
    t = x.index.strftime("%H:%M")
    c = x.close.to_numpy()
    pos, entrada, pnl, intentos, last, r2 = False, 0.0, 0.0, 0, 0, 0.0
    for i in range(1, len(x)):
        if t[i] > fin:
            break
        if not pos and t[i] <= "11:00" and (c[i] < l or (entrar_ya and intentos == 0)):
            pos, entrada, intentos = True, (x.open.iloc[i] if entrar_ya and intentos == 0 else c[i]), intentos + 1
            last = i
            continue
        if pos and c[i] > o:
            pnl += (entrada - c[i]) / entrada - coste
            r2 += ((entrada - c[i]) / entrada - coste) / max((o - entrada) / entrada, 0.02)
            pos = False
        last = i
    if pos:
        k = min(last, len(x) - 1)
        pnl += (entrada - c[k]) / entrada - coste
        r2 += ((entrada - c[k]) / entrada - coste) / max((o - entrada) / entrada, 0.02)
    return dict(intentos=intentos, pnl=pnl, R=pnl / riesgo if intentos else np.nan, riesgo=riesgo, R2=r2 if intentos else np.nan)


def stop30(x, coste=0.01):
    o = x.open.iloc[0]
    if x.high.max() >= o * 1.3:
        return -((o * 1.3 * 1.05 - o) / o + coste) / 0.3
    return ((o - x.close.iloc[-1]) / o - coste) / 0.3


filas = []
for sub, desde in [("m1", "2026-08-31"), ("m5", "2026-07-01")]:
    for _, e in E[(E.date >= desde) & (E.open >= 1) & (E.gap >= 0.2)].iterrows():
        x = dia(e.sym, e.date, sub)
        if x is None:
            continue
        base = dict(datos=sub, sym=e.sym, fecha=e.date.date(), gap=e.gap, tramo="≥ 50 %" if e.gap >= 0.5 else "20-50 %")
        r = simular(x)
        filas.append({**base, "regla": "ruptura 9:30, fin 16:00", **r})
        filas.append({**base, "regla": "ruptura 9:30, fin 16:00, coste 1 %", **simular(x, coste=0.01)})
        filas.append({**base, "regla": "ruptura 9:30, fin 10:30", **simular(x, fin="10:30")})
        filas.append({**base, "regla": "ruptura 9:30, fin 11:30", **simular(x, fin="11:30")})
        filas.append({**base, "regla": "ref: corto 9:31 misma salida", **simular(x, entrar_ya=True)})
        filas.append({**base, "regla": "ref: corto apertura stop +30 %", "intentos": 1, "R": stop30(x)})
X = pd.DataFrame(filas)
X.to_csv("res_23_ruptura_930.csv", index=False)


def met(v):
    v = v.dropna(); g, p = v[v > 0], v[v <= 0]
    return pd.Series(dict(n=len(v), R=v.mean(), mediana=v.median(), WR=(v > 0).mean(), gan=g.mean(), perd=p.mean(),
                          PF=g.sum() / -p.sum() if p.sum() < 0 else np.nan, t=v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan))


pd.set_option("display.width", 250)
T = X.groupby(["datos", "tramo", "regla"]).R.apply(met).unstack()
print(T.round(2).to_string())
T2 = X[X.regla.str.startswith("ruptura")].groupby(["datos", "tramo", "regla"]).R2.apply(met).unstack()
print("\nR2 = 1R por intento desde la entrada hasta la apertura de las 9:30 (añadido tras ver resultados)")
print(T2.round(2).to_string())
print("\ndías sin ruptura (1 min, ≥ 50 %):", X[(X.datos == "m1") & (X.tramo == "≥ 50 %") & (X.regla == "ruptura 9:30, fin 16:00")].intentos.eq(0).sum())
print("intentos medios por día con ruptura:", X[(X.regla == "ruptura 9:30, fin 16:00") & (X.intentos > 0)].groupby(["datos", "tramo"]).intentos.mean().round(2).to_dict())
print("riesgo mediano (O-L)/L:", X[X.regla == "ruptura 9:30, fin 16:00"].groupby("datos").riesgo.median().round(3).to_dict())

# dependencia de pocos días y detalle
for sub in ["m1", "m5"]:
    W = X[(X.datos == sub) & (X.tramo == "≥ 50 %") & (X.regla == "ruptura 9:30, fin 16:00")].dropna(subset=["R"]).sort_values("R")
    print(f"{sub} ≥50 % [R2]: media {W.R2.mean():+.2f}R; sin los 3 mejores {W.sort_values('R2').R2.iloc[:-3].mean():+.2f}R")
    print(f"{sub} ≥50 %: media {W.R.mean():+.2f}R; sin los 3 mejores {W.R.iloc[:-3].mean():+.2f}R; mejores:",
          W.tail(3)[["sym", "fecha", "R"]].round(2).values.tolist(), "peores:", W.head(3)[["sym", "fecha", "R"]].round(2).values.tolist())
