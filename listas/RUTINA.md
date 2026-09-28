# Rutina de la mañana — Radar de Cortos

Página: https://claude.ai/artifact/LXxGL8Y1LVHDLnuUo21zCo (base de datos: colección `listas`, un documento por día `AAAA-MM-DD`;
el diario del usuario vive en `diario` y NO se toca).
Objetivo: lista publicada **antes de las 9:10 (Nueva York)**. Si el tiempo se acaba, publicar lo que haya (mejor una lista con
catalizadores sin clasificar que ninguna) y seguir clasificando después.

## Pasos
1. Código: `git fetch origin claude/analisis-cuantitativo-45j7qe && git checkout -B claude/analisis-cuantitativo-45j7qe origin/claude/analisis-cuantitativo-45j7qe`.
   Si falta algún paquete: `pip install -q yfinance requests`.
2. ¿Día hábil? `python3 -c "import sys;sys.path.insert(0,'herramientas');import lista_diaria as l,datetime as d;print(l.es_habil(d.datetime.now(l.NY).date()))"`.
   Si es `False`, terminar sin hacer nada más.
3. Resultados de días anteriores: para cada `listas/datos/AAAA-MM-DD.json` anterior a hoy con `"resultados": null`, ejecutar
   `python3 herramientas/lista_diaria.py resultados --fecha AAAA-MM-DD` y guardar ese archivo en la base de datos
   (`ArtifactData set`, colección `listas`, `doc_id` = fecha, `file_path` = el JSON).
4. Escanear: `python3 herramientas/lista_diaria.py escanear` → `listas/datos/HOY_candidatos.json`.
5. Clasificar el catalizador de cada candidato con gap ≥ 50 % (leer `catalizadores[].partes[].texto` y `noticias`; si solo hay
   noticia de agencia, abrirla con WebFetch). **Nunca poner N si hay algún titular sin abrir** (GYGY 28-sep: el artículo
   de Benzinga explicaba la subida; también mirar si es una noticia vieja reciclada). Escribir `listas/datos/HOY_clasif.json`:
   `{"TICKER": {"tipo": "...", "frase_en": "frase ORIGINAL en inglés", "frase_es": "traducción", "cifra": "cifra con su unidad", "nota": "..."}}`
   Definiciones (registradas en `smallcaps/HIPOTESIS_SELECCION.md`, ronda 2b), en orden de prioridad:
   - **C** compra en efectivo: la empresa será comprada con pago en efectivo o precio fijo por acción (fusión definitiva, oferta pública).
   - **F** financiación: oferta de acciones, colocación privada, registered direct, warrants, convertibles, ELOC/SEPA, préstamo.
   - **R** resultados: trimestrales/anuales o cifras preliminares de ventas.
   - **B** biotech real: aprobación/autorización de la FDA u otra agencia, o datos clínicos con resultado (topline, endpoint).
   - **K** contrato real: acuerdo firmado y definitivo con contraparte IDENTIFICADA **y** cifra en dólares.
   - **H** humo / cosmético: LOI, MOU, no vinculante, "partnership/collaboration" sin cifra, "explora/evalúa", pilotos, lanzamientos
     sin ventas, cambios de nombre o giro de negocio (IA, cripto, tesorería de tokens), conferencias, patentes, preclínico, cartas
     del CEO, recompras simbólicas, nombramientos, premios; cifras "potenciales/hasta"; cliente sin nombre.
   - **S** corporativo/bolsa: contra-split, aviso o recuperación de cumplimiento de Nasdaq, juntas, auditor.
   - **O** otros. · **N** no se encontró ninguna noticia ni documento.
   Método acordado con el usuario: frase original en inglés + traducción + cifra con su unidad. Ser honesto si hay dudas (anotarlo en `nota`).
6. Finalizar: `python3 herramientas/lista_diaria.py finalizar` (actualiza precios del premarket y asigna nivel/plan) y guardar
   `listas/datos/HOY.json` en la base de datos (`ArtifactData set`, colección `listas`, `doc_id` = HOY).
7. `git add listas/datos && git commit -m "Lista diaria HOY" && git push -u origin claude/analisis-cuantitativo-45j7qe`
   (con las líneas de atribución de siempre).
8. Mensaje final corto en español: niveles de la lista (A/B/Vigilar/NO/Nunca con tickers) y enlace a la página.

No cambiar reglas, niveles ni estadísticas: solo lo validado en `smallcaps/INFORME_SELECCION.md`. No crear otras rutinas.
