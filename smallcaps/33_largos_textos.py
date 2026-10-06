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
os.makedirs(f"{D}/textos_v1", exist_ok=True)
U = pd.read_parquet(f"{D}/universo_U1.parquet")
U = U[U.pasa_A]
print("eventos a leer:", len(U), flush=True)
W, K = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 0)   # trabajadores en paralelo (límite SEC 10/s)
for i, r in enumerate(U.itertuples(index=False)):
    f = f"{OUT}/{r.cik}_{r.entrada}.json"
    if i % W != K:
        continue
    if os.path.exists(f) and json.load(open(f)).get("v") == 2:     # v2 (6-oct): anexos EX-1 en 6-K y hasta 8 anexos
        continue
    if os.path.exists(f):
        os.replace(f, f.replace("/textos/", "/textos_v1/"))     # se guarda la versión anterior para saber qué cambió
    docs = []
    for acc, doc in zip(r.accns.split(","), r.docs.split(",")):
        a = acc.replace("-", "")
        partes = L.texto_catalizador(r.cik, dict(acc=a, doc=doc))
        if doc not in [p["archivo"] for p in partes]:   # el cuerpo del 8-K/6-K SIEMPRE (ahí está el item 1.01 / la financiación)
            t = L.get(f"https://www.sec.gov/Archives/edgar/data/{r.cik}/{a}/{doc}", sec=True)
            if t:
                c = L.resumen_doc(L.limpiar(t), 10 ** 7)
                partes.insert(0, dict(archivo=doc, url=f"https://www.sec.gov/Archives/edgar/data/{r.cik}/{a}/{doc}",
                                      texto=c[:30000], recortado=len(c) > 30000, negativos=L.negativos(c)))
        docs.append(dict(acc=acc, partes=partes, principal=True))
    json.dump(dict(cik=int(r.cik), entrada=r.entrada, docs=docs, v=2), open(f, "w"))
    if i % 100 == 0:
        print(i, flush=True)
print("FIN", flush=True)
