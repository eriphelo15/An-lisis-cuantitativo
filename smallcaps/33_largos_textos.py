"""Ronda 15: descarga el texto completo (8-K/6-K + TODOS sus EX-99) de los eventos que pasan el embudo A.
Usa el mismo lector que el Radar (`texto_catalizador` de lista_diaria.py: anexos por tipo en el índice de la SEC).
Salida: /home/user/data/largos/textos/<cik>_<entrada>.json. No contiene precios."""
import json, os, sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "herramientas"))
import lista_diaria as L

D = "/home/user/data/largos"
OUT = f"{D}/textos"
os.makedirs(OUT, exist_ok=True)
U = pd.read_parquet(f"{D}/universo_U1.parquet")
U = U[U.pasa_A]
print("eventos a leer:", len(U), flush=True)
for i, r in enumerate(U.itertuples(index=False)):
    f = f"{OUT}/{r.cik}_{r.entrada}.json"
    if os.path.exists(f):
        continue
    docs = []
    for acc, doc in zip(r.accns.split(","), r.docs.split(",")):
        partes = L.texto_catalizador(r.cik, dict(acc=acc.replace("-", ""), doc=doc))
        docs.append(dict(acc=acc, partes=partes))
    json.dump(dict(cik=int(r.cik), entrada=r.entrada, docs=docs), open(f, "w"))
    if i % 100 == 0:
        print(i, flush=True)
print("FIN", flush=True)
