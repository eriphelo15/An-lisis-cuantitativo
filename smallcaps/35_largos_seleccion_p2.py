"""Ronda 15: elige qué eventos pasan al paso 2 (lectura completa por un segundo lector ciego), según la enmienda del pre-registro:
todo tipo que pasa, toda confianza baja, resultados sin crecimiento calculable, + 15 % aleatorio (semilla fija) del resto."""
import glob, hashlib, json
D = "/home/user/data/largos"
PASA = {"CONTRATO_FIRME", "FDA_APROBACION", "DATOS_POSITIVOS", "RESULTADOS_FUERTES", "INVERSION_ESTRATEGICA"}
L = [json.loads(l) for f in sorted(glob.glob(f"{D}/lecturas/p1/*.jsonl")) for l in open(f) if l.strip()]
hechos = set()
for f in glob.glob(f"{D}/lotes/p2/*.txt"):
    hechos |= {l.split("=== EVENTO ")[1].split(" ===")[0] for l in open(f) if l.startswith("=== EVENTO ")}
obligado, resto = [], []
for x in L:
    res_sin = "esultado" in (x.get("nota") or "") and x.get("crecimiento_ventas_pct") is None and x["tipo"] == "RUTINARIO"
    (obligado if (x["tipo"] in PASA or x.get("confianza") == "baja" or res_sin) else resto).append(x["id"])
# sorteo por evento con un hash fijo del id: el mismo evento sale siempre igual aunque se añadan eventos nuevos
muestra = sorted(i for i in resto if int(hashlib.md5(f"r15-{i}".encode()).hexdigest(), 16) % 100 < 15)
sel = [i for i in sorted(set(obligado) | set(muestra)) if i not in hechos]
json.dump(dict(obligado=sorted(obligado), muestra=muestra), open(f"{D}/seleccion_p2.json", "w"))
open(f"{D}/ids_p2.txt", "w").write("\n".join(sel))
print("leídos p1:", len(L), "| obligados:", len(obligado), "| muestra 15 %:", len(muestra), "| nuevos para p2:", len(sel))
