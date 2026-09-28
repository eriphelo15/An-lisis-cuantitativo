"""Ronda 2b: une las etiquetas manuales (escritas a ciegas por lotes) en clasificacion_catalizador.csv."""
import re, sys
import pandas as pd

d = {}
for f in sys.argv[1:]:
    for k, v in re.findall(r"(\d+):([A-Z])", open(f).read()):
        k = int(k)
        if k in d and d[k] != v:
            print("conflicto", k, d[k], v)
        d.setdefault(k, v)
X = pd.read_csv("resumenes_catalizador.csv")
# regla fija aplicada antes de leer (ids >= 395): Item 2.02 = resultados; Item 3.01/5.07 = bolsa; solo 5.02 = otros
for i, a, s in zip(X.id, X["items"].fillna("").astype(str), X.resumen.fillna("").astype(str)):
    if i >= 395 and i not in d:
        if "2.02" in a:
            d[i] = "R"
        elif re.match(r"Item 3\.01|Item 5\.07", s):
            d[i] = "S"
        elif a.strip() in ("5.02", "5.02,9.01"):
            d[i] = "O"
falt = sorted(set(X.id) - set(d))
print("faltan", len(falt), falt[:40])
X["cat"] = X.id.map(d)
X[["id", "sym", "fecha", "cat"]].to_csv("clasificacion_catalizador.csv", index=False)
print(X.cat.value_counts(dropna=False).to_dict())
