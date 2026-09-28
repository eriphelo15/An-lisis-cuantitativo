"""Inserta la lista más reciente como respaldo dentro de la página (se ve aunque la base de datos no cargue)."""
import glob, json, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
fs = sorted(f for f in glob.glob(os.path.join(AQUI, "datos", "????-??-??.json")))
datos = json.load(open(sys.argv[1] if len(sys.argv) > 1 else fs[-1])) if fs else {}
h = open(os.path.join(AQUI, "radar.html")).read()
js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
h = re.sub(r'(<script id="respaldo" type="application/json">).*?(</script>)', lambda m: m.group(1) + js + m.group(2), h, flags=re.S)
open(os.path.join(AQUI, "radar_publicar.html"), "w").write(h)
print("respaldo:", datos.get("fecha"), "→ radar_publicar.html")
