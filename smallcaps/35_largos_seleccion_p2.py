"""Ronda 15: elige qué eventos pasan al paso 2 (lectura completa por un segundo lector ciego), según la enmienda del pre-registro:
todo tipo que pasa, toda confianza baja, resultados sin crecimiento calculable, + 15 % aleatorio (semilla fija) del resto."""
import glob, hashlib, json
D = "/home/user/data/largos"
PASA = {"CONTRATO_FIRME", "FDA_APROBACION", "DATOS_POSITIVOS", "RESULTADOS_FUERTES", "INVERSION_ESTRATEGICA"}
L = [json.loads(l) for f in sorted(glob.glob(f"{D}/lecturas/p1/*.jsonl")) for l in open(f) if l.strip()]
hechos = set()
for f in glob.glob(f"{D}/lotes/p2/*.txt"):
    hechos |= {l.split("=== EVENTO ")[1].split(" ===")[0] for l in open(f) if l.startswith("=== EVENTO ")}
# 6-oct (enmienda 2, antes de ver precios): "resultados sin crecimiento calculable" se comprueba con el XBRL de ventas del
# trimestre/año que se anuncia (mismo número que la nota de prensa, presentado después en el 10-Q/10-K): crecimiento ≥ 30 % → paso 2.
import pandas as pd, os
U = pd.read_parquet(f"{D}/universo_U1.parquet").assign(id=lambda x: x.cik.astype(str) + "_" + x.entrada)
info = U.set_index("id")[["cik", "t_ny", "items"]].to_dict("index")
_V = {}


def crecimiento_xbrl(i):
    r = info.get(i)
    if not r or "2.02" not in (r["items"] or ""):
        return None
    c = r["cik"]
    if c not in _V:
        f = f"{D}/ventas/{c}.parquet"
        _V[c] = pd.read_parquet(f) if os.path.exists(f) else None
    v = _V[c]
    if v is None or not len(v):
        return None
    v = v[(v["var"] == "ventas")].copy()
    v["dias"] = (pd.to_datetime(v.end) - pd.to_datetime(v.start)).dt.days
    dia = r["t_ny"].strftime("%Y-%m-%d")
    lim = (r["t_ny"] - pd.Timedelta(days=120)).strftime("%Y-%m-%d")
    act = v[(v.end < dia) & (v.end >= lim) & (v.dias.between(80, 100) | v.dias.between(350, 380))].sort_values("end")
    if not len(act):
        return None
    a = act.iloc[-1]
    e0 = pd.Timestamp(a.end) - pd.Timedelta(days=365)
    prev = v[(abs(pd.to_datetime(v.end) - e0) <= pd.Timedelta(days=10)) & (abs(v.dias - a.dias) <= 10)]
    if not len(prev) or prev.val.iloc[0] <= 0:
        return None
    return a.val / prev.val.iloc[0] - 1


obligado, resto, xb = [], [], {}
for x in L:
    g = crecimiento_xbrl(x["id"])
    xb[x["id"]] = g
    fuerte_xbrl = g is not None and g >= 0.30 and x["tipo"] not in PASA
    (obligado if (x["tipo"] in PASA or x.get("confianza") == "baja" or fuerte_xbrl) else resto).append(x["id"])
json.dump(xb, open(f"{D}/crecimiento_xbrl.json", "w"))
# sorteo por evento con un hash fijo del id: el mismo evento sale siempre igual aunque se añadan eventos nuevos
muestra = sorted(i for i in resto if int(hashlib.md5(f"r15-{i}".encode()).hexdigest(), 16) % 100 < 15)
sel = [i for i in sorted(set(obligado) | set(muestra)) if i not in hechos]
json.dump(dict(obligado=sorted(obligado), muestra=muestra), open(f"{D}/seleccion_p2.json", "w"))
open(f"{D}/ids_p2.txt", "w").write("\n".join(sel))
print("leídos p1:", len(L), "| obligados:", len(obligado), "| muestra 15 %:", len(muestra), "| nuevos para p2:", len(sel))
