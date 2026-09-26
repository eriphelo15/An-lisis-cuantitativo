"""Fase 0b — Reconstrucción de precios reales y dataset limpio.

El CSV original viene con un ajuste de contrato continuo defectuoso: cada segmento
(contrato) lleva un offset constante que crece hacia el pasado de forma cuadrática
(ajuste aplicado dos veces). Síntomas: en cada roll hay un salto de -2,880 … 0 pts y
la serie 'cae' de 51k a 24k entre 2021 y 2026 cuando el NQ real subió de 13k a 25k.

Modelo verificado: gap_r = -sum_{j>r} spread_j  =>  spread_r = gap_r - gap_{r-1}.
Con eso se recupera el offset de cada segmento y el precio real del contrato (raw).
Validación contra niveles históricos conocidos (ver auditoría) con error < 0.5%.

Salidas (parquet en DATA_DIR):
  nq_1m.parquet : ts (ET, naive), open/high/low/close reales, volume, symbol,
                  adj_* = serie back-adjusted correcta (sin salto en rolls, anclada al último contrato)
"""
import os, sys
import numpy as np, pandas as pd

DATA_DIR = os.environ.get("NQ_DATA_DIR", "/home/user/data")
RAW = os.path.join(DATA_DIR, sys.argv[1] if len(sys.argv) > 1 else "NQ_continuous.csv")
OUT = sys.argv[2] if len(sys.argv) > 2 else "nq_1m.parquet"

df = pd.read_csv(RAW, usecols=["timestamp", "open", "high", "low", "close", "volume", "symbol"])
df["ts"] = pd.to_datetime(df["timestamp"]); df = df.drop(columns="timestamp")
seg = ((df.symbol != df.symbol.shift()).cumsum() - 1).to_numpy()
roll_idx = np.flatnonzero(np.diff(seg)) + 1
gap = df.open.to_numpy()[roll_idx] - df.close.to_numpy()[roll_idx - 1]

spread = np.empty(len(gap)); spread[1:] = gap[1:] - gap[:-1]; spread[0] = 0.0
off = np.zeros(len(gap) + 1)
for r in range(len(gap) - 1, -1, -1):
    off[r] = off[r + 1] + spread[r] - gap[r]
o = off[seg]
for c in ["open", "high", "low", "close"]:
    df[c] = df[c].to_numpy() - o

# back-adjust correcto: al cruzar el roll r, el contrato nuevo está 'spread_r' por encima
# del viejo -> sumar a cada segmento viejo la suma de spreads posteriores (en puntos).
cum = np.zeros(len(gap) + 1)
for r in range(len(gap) - 1, -1, -1):
    cum[r] = cum[r + 1] + spread[r]
for c in ["open", "high", "low", "close"]:
    df["adj_" + c] = df[c].to_numpy() + cum[seg]
df["seg"] = seg.astype(np.int16)

rolls = pd.DataFrame({"ts": df.ts.to_numpy()[roll_idx], "de": df.symbol.to_numpy()[roll_idx - 1],
                      "a": df.symbol.to_numpy()[roll_idx], "gap_csv": gap, "spread_implicito": spread,
                      "offset_segmento_viejo": off[:-1]})
print(rolls.to_string(index=False))
df.to_parquet(os.path.join(DATA_DIR, OUT), index=False)
rolls.to_csv(os.path.join(os.path.dirname(__file__), "resultados", OUT.replace(".parquet", "") + "_rolls.csv"), index=False)
print("filas", len(df), "precio real primero/último:", df.close.iloc[0], df.close.iloc[-1])
