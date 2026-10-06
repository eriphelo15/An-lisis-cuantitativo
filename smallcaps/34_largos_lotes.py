"""Ronda 15: prepara lotes de lectura a ciegas (sin precios) para los agentes lectores.
  python 34_largos_lotes.py p1            → paso 1: cuerpo + cada EX-99 recortados a 1 800 caracteres, 60 eventos por lote
  python 34_largos_lotes.py p2 ids.txt    → paso 2: texto completo (hasta 30 000 caracteres por parte), 10 eventos por lote
Los lotes van a /home/user/data/largos/lotes/<paso>/ y las lecturas a /home/user/data/largos/lecturas/<paso>/."""
import glob, json, os, re, sys
import pandas as pd

D = "/home/user/data/largos"
paso = sys.argv[1]
CORTE, TAM = (1800, 60) if paso == "p1" else (30000, 10)
os.makedirs(f"{D}/lotes/{paso}", exist_ok=True)
os.makedirs(f"{D}/lecturas/{paso}", exist_ok=True)
U = pd.read_parquet(f"{D}/universo_U1.parquet")
U = U[U.pasa_A].assign(id=lambda x: x.cik.astype(str) + "_" + x.entrada)
nombres = dict(zip(U.id, U.name))
items = dict(zip(U.id, U["items"]))
forms = dict(zip(U.id, U.forms))

hechos = set()
for f in glob.glob(f"{D}/lotes/{paso}/*.txt"):
    hechos |= set(l.split("=== EVENTO ")[1].split(" ===")[0] for l in open(f) if l.startswith("=== EVENTO "))
if paso == "p1":
    ids = sorted(i for i in U.id if os.path.exists(f"{D}/textos/{i}.json"))
else:
    ids = [l.strip() for l in open(sys.argv[2]) if l.strip()]
ids = [i for i in ids if i not in hechos]
listos = []
for i in ids:
    j = json.load(open(f"{D}/textos/{i}.json"))
    if not j["docs"] or not all(d.get("principal") for d in j["docs"]):
        continue
    bloque = [f"=== EVENTO {i} ===", f"Empresa: {nombres[i]} | Documentos: {forms[i]} | Items: {items[i]}"]
    for d in j["docs"]:
        for p in d["partes"]:
            bloque.append(f"--- {p['archivo']} ---")
            t = p["texto"]
            m = re.search(r"Item\s*\d\.\d\d", t)
            # 6-oct: en algunos 8-K con XBRL en línea el texto empieza con la cabecera técnica (RILY) → saltar hasta el primer Item
            if m and m.start() > 0 and re.search(r"\b0001\d{6}\b|Member\b|SECURITIES AND EXCHANGE COMMISSION", t[:m.start()]):
                t = t[m.start():]
            bloque.append(t[:CORTE])
    listos.append("\n".join(bloque))
n0 = len(glob.glob(f"{D}/lotes/{paso}/*.txt"))
for k in range(0, len(listos), TAM):
    with open(f"{D}/lotes/{paso}/lote_{n0 + k // TAM:04d}.txt", "w") as f:
        f.write("\n\n".join(listos[k:k + TAM]))
print("eventos nuevos:", len(listos), "| lotes nuevos:", (len(listos) + TAM - 1) // TAM)
