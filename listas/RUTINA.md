# Rutina de la mañana — Radar de Cortos

Página: https://claude.ai/artifact/LXxGL8Y1LVHDLnuUo21zCo (base de datos: colección `listas`, un documento por día `AAAA-MM-DD`;
el diario del usuario vive en `diario` y NO se toca).
Objetivo: lista publicada **antes de las 9:10 (Nueva York)**. Si el tiempo se acaba, publicar lo que haya (mejor una lista con
catalizadores sin clasificar que ninguna) y seguir clasificando después.

## Pasos
1. Código: `git fetch origin claude/analisis-cuantitativo-45j7qe && git checkout -B claude/analisis-cuantitativo-45j7qe origin/claude/analisis-cuantitativo-45j7qe`.
   Si falta algún paquete: `pip install -q yfinance requests`.
1c. **Casos de oro (obligatorio desde el 1-oct):** `python3 tests/casos_oro.py`. Si falla alguno, NO seguir con datos dudosos: arreglar la
   causa (o, si es una caída de una fuente externa, comprobar que la de respaldo funciona) y avisar por push si retrasa la lista.
2. ¿Día hábil? `python3 -c "import sys;sys.path.insert(0,'herramientas');import lista_diaria as l,datetime as d;print(l.es_habil(d.datetime.now(l.NY).date()))"`.
   Si es `False`, terminar sin hacer nada más.
3. Resultados de días anteriores: para cada `listas/datos/AAAA-MM-DD.json` anterior a hoy con `"resultados": null`, ejecutar
   `python3 herramientas/lista_diaria.py resultados --fecha AAAA-MM-DD` y guardar ese archivo en la base de datos
   (`ArtifactData set`, colección `listas`, `doc_id` = fecha, `file_path` = el JSON).
(3b, estudio de la ruptura de las 9:30, y 1b, descarga de Massive: RETIRADOS el 1-oct por decisión del usuario — la regla no es rentable.)
4. Escanear: `python3 herramientas/lista_diaria.py escanear` → `listas/datos/HOY_candidatos.json`.
   El escáner usa DOS fuentes para el cierre de ayer: Yahoo (histórico diario) y **Massive** (antes Polygon; credencial en el entorno,
   1 consulta). Una acción entra como candidata si supera el 20 % contra cualquiera de las dos. Si los cierres difieren > 2 %,
   `finalizar` da ERROR (revisar a mano: suele ser un split). Si Massive no responde, aviso y se sigue con Yahoo.
   Segunda fuente de gappers: **TradingView** (escáner público, cambio premarket ≥ 20 %). Lo que ve TradingView y no el escáner
   se verifica con el cierre oficial y se añade; lo que no se pueda verificar aparece como aviso → revisarlo a mano antes de publicar.
   La auditoría bloquea la lista si el universo está incompleto (< 5 000 tickers o falta el fichero de NYSE/NYSE American).
5. Clasificar el catalizador de **cada candidato con gap ≥ 20 %** (desde el 29-sep también los de 20-50 %, que llevan ficha completa) (leer `catalizadores[].partes[].texto` y `noticias`; si solo hay
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
   **Registro de pasos (obligatorio desde el 2-oct, pedido por el usuario):** cada acción lleva además `"pasos"` con lo que se hizo:
   `{"fuentes": ["8-K 07:05 + EX-99.1", "Finviz 8:00 GlobeNewswire «titular»", …], "anexos_leidos": 2, "negativos": "…" o "ninguno, revisado",
   "historial": "…" o "sin historial", "municion": "resumen de shelves/ATM/reventas/ELOC/424B/warrants revisados", "caja": "caja a hoy / going concern"}`.
   `finalizar` comprueba que no falte ninguno, que haya al menos una fuente por documento y por noticia de la ventana, que los anexos
   leídos no sean menos que los de los documentos y que no diga "sin historial" si la ficha tiene historial. Si falta algo, la lista NO se publica.
5b. **Auditoría antes de publicar (obligatoria, nada se entrega sin ella):**
   - Cada titular y cada 8-K/6-K de las acciones con gap ≥ 20 % abierto y leído (no basta el titular). Mirar si la noticia es vieja reciclada.
   - `N` solo si se revisaron a mano Finviz, Yahoo y EDGAR sin encontrar nada → anotar `"fuentes_abiertas"` en el `_clasif.json`.
   - **El catalizador tiene que ser de HOY (desde el cierre anterior).** Un 6-K/8-K o nota de días anteriores (p. ej. una financiación de
     ayer) es munición o contexto, no el motivo del gap: tipo `N` y lo viejo en `nota` (LGHL 30-sep, MSGY 29-sep, DLXY 28-sep).
     `finalizar` da ERROR si el tipo no es N y no hay ningún 8-K/6-K ni noticia en la ventana; si la noticia de hoy existe pero la
     herramienta no la vio, anotar `"fuente_fuera_herramienta"` con el enlace y la hora.
   - Cada `frase_en` copiada literal del documento (verificable con Ctrl+F) y cada cifra con su unidad (dólares vs. acciones).
   - `finalizar` ejecuta un control automático (cobertura del escáner ≥ 97 %, todo clasificado, sin `N` con titulares sin abrir,
     frase + traducción + cifra presentes, munición analizada). Si da ERROR, corregir y repetir; `--forzar` solo si el tiempo se acaba,
     y decirlo en el mensaje final.
5c. **Verificador independiente (obligatorio desde el 1-oct, `listas/VERIFICADOR.md`):** para cada acción con gap ≥ 50 % o tesis alta,
   lanzar en paralelo un agente nuevo (Agent, general-purpose, en segundo plano) con el encargo de VERIFICADOR.md, sin acceso a nuestras
   conclusiones. Comparar su JSON con nuestra ficha, resolver cada diferencia leyendo la fuente, añadir a `tests/casos_oro.py` todo error
   nuestro que destape, y guardar `listas/datos/HOY_verificacion.json`. `finalizar` bloquea la lista si falta.
6. Finalizar: `python3 herramientas/lista_diaria.py finalizar` (actualiza precios del premarket; aplica el filtro de campo, calcula la
   puntuación de la tesis 0-100 de la ronda 12, el riesgo estructural, la caja, el PMH y guarda el texto de los 8-K; las descartadas
   quedan aparte con su motivo; **desde el 30-sep no hay letras A/B/Vigilar/NO/Nunca**, pedido del usuario) y guardar
   `listas/datos/HOY.json` en la base de datos (`ArtifactData set`, colección `listas`, `doc_id` = HOY).
7. `git add listas/datos && git commit -m "Lista diaria HOY" && git push -u origin claude/analisis-cuantitativo-45j7qe`
   (con las líneas de atribución de siempre).
8. Mensaje final en español: tabla del screener ordenada por tesis (ticker, tesis 0-100 y tercio, riesgo, gap, precio, catalizador),
   de cada una la frase original + traducción + cifra y la munición; las descartadas en una línea con su motivo; referencia de base
   del día anterior por tercio (es REFERENCIA, no validación: lo que valida es el diario del usuario; si hay operaciones nuevas en `diario`,
   sus resultados reales van primero) y enlace a la página.
   **Solo trabajo de campo (selección).** NO dar instrucciones de ejecución (entrada, stop, tamaño, salida): la ejecución es discrecional
   del usuario. El análisis de ejecución se trata aparte, en conversaciones de formación y estudios, nunca en la lista del día.
9. **Notificación push** (pedida por el usuario el 28-sep; probada y funciona): herramienta `PushNotification`, una línea < 200
   caracteres, sin formato, p. ej. `Radar 1-oct listo: CNTB 80 alta · FFR 61 · VBIO 26 (riesgo extremo) · fuera: LGHL, FRGT · Control OK`.
   Si la auditoría retrasa la lista o falla algo, avisar también por push (`Radar 29-sep RETRASADO: <motivo>`).

No cambiar reglas, pesos ni estadísticas: solo lo validado en `smallcaps/INFORME_SELECCION.md`. No crear otras rutinas.
