"""Une los registros mensuales del canal de Telegram de Tom Hougaard (ene-2023 .. abr-2024) en una tabla de operaciones.
Cada fila: producto, fecha, hora (UK), dirección, entrada, stop, tamaño, puntos logrados (Point = 100% de la posición),
puntos convertidos (ponderados por salidas parciales). R = Converted / |entrada - stop|."""
import glob, os, sys
import numpy as np, pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."
# una versión por mes (la final/completa)
MESES = {"2023-01": "2023-01", "2023-02": "2023-02", "2023-03": "2023-03", "2023-04": "2023-04", "2023-05": "2023-05",
         "2023-06": "2023-06", "2023-07": "2023-07", "2023-08": "2023-08", "2023-09": "2023-09", "2023-10": "2023-10",
         "2024-01": "2024-01a", "2024-02": "2024-02b", "2024-03": "2024-03", "2024-04": "2024-04"}


def parse(f, mes):
    x = pd.ExcelFile(f); filas = []
    for s in x.sheet_names:
        d = x.parse(s, header=None)
        h = d.iloc[7].astype(str).str.strip().tolist()
        def col(name, k=0):
            idx = [i for i, v in enumerate(h) if v == name]
            return idx[k] if len(idx) > k else None
        c = dict(canal=col("Day or Swing"), producto=col("Product"), fecha=col("Date"), hora=col("Time"), dir=col("↑↓"),
                 ent=col("Entry"), stop=col("Stop Loss"), tam=col("25%/50%/100%"), pts=col("Point"), conv=col("Converted*"))
        ex1 = col("1st Exit") if col("1st Exit") is not None else col("Exit")
        c["salida"] = ex1; c["hora_sal"] = col("Time", 1)
        c["salida2"] = col("2nd Exit")
        for _, r in d.iloc[9:].iterrows():
            if pd.isna(r[c["producto"]]) or pd.isna(r[c["ent"]]) or str(r[c["dir"]]).strip() not in ("Long", "Short"):
                continue
            g = {k: (r[v] if v is not None else np.nan) for k, v in c.items()}
            g["hoja"] = s; g["mes"] = mes
            filas.append(g)
    return filas


todo = []
for mes, base in MESES.items():
    todo += parse(os.path.join(DIR, base + ".xlsx"), mes)
T = pd.DataFrame(todo)
for k in ["ent", "stop", "pts", "conv", "tam", "salida", "salida2"]:
    T[k] = pd.to_numeric(T[k], errors="coerce")
T["producto"] = T["producto"].astype(str).str.strip().str.upper()
T["canal"] = T["canal"].astype(str).str.strip()
T["riesgo"] = (T.ent - T.stop).abs()
T["R"] = T.conv / T.riesgo
T["R_full"] = T.pts / T.riesgo
T["fecha"] = pd.to_datetime(T.fecha, errors="coerce")
T.to_csv(os.path.join(os.path.dirname(__file__), "tom_telegram_trades.csv"), index=False)
print(T.groupby(["canal"]).size()); print(T.producto.value_counts().head(20))
print(T[["riesgo", "pts", "conv", "R"]].describe())
print("sin puntos:", T.conv.isna().sum())
