"""Ronda 2b: resumen de cada catalizador (titular + primeras frases) para clasificarlo a mano y a ciegas.
El archivo de salida NO contiene el resultado de la acción."""
import glob, re
import pandas as pd

filas = []
for f in sorted(glob.glob("/home/user/data/sec/pr/*.txt")):
    sym, d = f.split("/")[-1][:-4].rsplit("_", 1)
    items, t = open(f).read().split("\n", 1)
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    if t.startswith("EX-99") or "SECURITIES AND EXCHANGE COMMISSION" not in t[:800].upper():
        s = re.sub(r"^EX-99\S*\s+\d+\s+\S+\s*", "", t)            # anexo: quitar cabecera "EX-99.1 2 archivo.htm"
        for _ in range(4):
            s = re.sub(r"^(EX-99\S*|Exhibit\s*99\S*|PRESS RELEASE|FOR IMMEDIATE RELEASE|News Release)\s*", "", s, flags=re.I)
    else:                                                               # documento principal: saltar la portada
        cab = t[:6000]
        ini = max(cab.rfind("☐"), cab.rfind("☒"), cab.rfind("□"), cab.rfind("þ"), cab.rfind("Form 40-F"), cab.rfind("240.13e-4(c))"), 0)
        s = t[ini:]
        m = re.search(r"Item\s*\d\.\d\d", s[:3000])
        s = s[m.start():] if m else s[1:].lstrip(" :.)")
        k = s[:2500].rfind("check mark")
        if k >= 0:                                                      # restos de la portada del 6-K
            s = re.sub(r"^[^:]*:?\s*(\[\s?\]|¨|☐|Yes|No|o\b)?\s*", "", s[k:])
    filas.append(dict(sym=sym, fecha=d, items=items.replace("ITEMS: ", ""), resumen=s[:380].strip()))
X = pd.DataFrame(filas)
X.insert(0, "id", range(len(X)))
X.to_csv("resumenes_catalizador.csv", index=False)
print(len(X))
