# Validación de criterios de selección — pre-registro (escrito ANTES de ver resultados)

**Muestra:** gappers (apertura ≥ +20 % sobre el cierre anterior, filtros de liquidez del estudio 02), 2015-2026, empresas que reportan a la SEC.
**Periodos:** DEV 2015-2021 (se miran y ajustan umbrales) · VAL 2022-2026 (solo confirmación).
**Solo información disponible ANTES de la apertura del día del gap:** documentos de EDGAR con hora de aceptación
(`acceptanceDateTime`) anterior a las 9:30 hora de Nueva York del día del gap; precios hasta el cierre anterior.

**Resultados medidos (lado corto):**
1. Corto apertura→cierre del día 1 (% y acierto).
2. Setup A: corto a la apertura, stop +30 %, 5 % de deslizamiento, coste 1 % → en R: esperanza, WR, ganancia media, pérdida media, PF.
3. Riesgo de squeeze: % de días en que la subida máxima desde la apertura supera +50 %, y percentil 90 de esa subida.
4. Día 2: cierre día 1 → cierre día 2.

**Hipótesis (dirección esperada = mejor para el corto):**
| # | Criterio | Mejor para el corto si… |
|---|---|---|
| H1 | Munición: S-3/F-3 presentado en los 3 años previos | tiene shelf |
| H2 | Munición: venta reciente (424B3/4/5) en los 90 días previos | tiene venta reciente |
| H3 | Diluidor en serie: ≥ 3 prospectos 424B en 12 meses | es diluidor en serie |
| H4 | Catalizador: hay 8-K aceptado entre el cierre anterior y la apertura | NO hay 8-K (solo nota de prensa o nada) |
| H5 | Tipo de 8-K: Item 1.01 (acuerdo firmado) vs solo 7.01/8.01 (nota de prensa) | solo 7.01/8.01 |
| H6 | Contra-split (8-K Item 5.03) o aviso de bolsa (Item 3.01) en los 12 meses previos | lo tiene |
| H7 | Día caliente: ≥ 2 gappers (≥ 50 %) del mismo sector SIC (2 dígitos) ese día | NO es día de tema |
| H8 | Tamaño: capitalización a la apertura < $30 M vs mayor | (sin dirección previa; exploratorio) |
| H9 | Empresa extranjera (reporta con 20-F/6-K) | (sin dirección previa; exploratorio) |
| H10 | Combinación "A" = H2 o H3 (munición) + H4 (sin 8-K) + H7 (no tema) | mejor que el resto |

**Regla de éxito:** mismo sentido en DEV y VAL; en VAL diferencia con t > 2 frente al resto (Holm sobre H1-H7 y H10).
Limitaciones conocidas: sin volumen premarket ni float exacto (datos gratuitos); solo empresas que siguen cotizando (sesgo de supervivencia que perjudica al corto).

---
## Ronda 2 — contenido del catalizador (pre-registro, escrito ANTES de ver resultados)
Muestra: gappers con 8-K o 6-K aceptado entre el cierre anterior y las 9:30 del día del gap (~3 000 de 8 604). Se lee el texto
(anexo EX-99 si existe; si no, el documento principal) y se clasifica con reglas fijas de palabras clave (en inglés):
- **Compra en efectivo:** "merger agreement"/"to be acquired"/"definitive agreement to be acquired" + "per share in cash"/"all-cash".
- **Resultados:** Item 2.02 o "reports … results"/"financial results".
- **FDA / clínico:** "FDA" + approv/clear/grant/designation, o "topline"/"primary endpoint".
- **Contrato/acuerdo con cifra:** agreement/contract/order/award + cifra en dólares ("$X million/billion").
- **Humo:** letter of intent/LOI/memorandum of understanding/MOU/non-binding/partnership/collaboration/explore/pilot, **sin cifra en dólares**.
- **Otros.**
Etiqueta aparte **"tema de moda"** si el texto o el nombre de la empresa contiene: artificial intelligence, AI, blockchain, bitcoin, crypto,
digital asset, token, quantum, drone, nuclear, uranium, rare earth, lithium, Greenland, defense, robot, space, satellite.

| # | Hipótesis | Mejor para el corto si… |
|---|---|---|
| H11 | Humo vs catalizador real (FDA, contrato con cifra, resultados) | es humo |
| H12 | El texto incluye una cifra en dólares | NO la incluye |
| H13 | Compra en efectivo | (descriptiva: se espera que NO se deba shortear) |
| H14 | Tema de moda (texto o nombre) — aplica a TODOS los gappers por el nombre | NO es tema de moda |
| H15 | Día de tema: ≥ 2 gappers (≥ 50 %) el mismo día que comparten palabra clave de tema | NO es día de tema |
Misma regla de éxito: mismo sentido en DEV y VAL; VAL t > 2 (Holm sobre H11, H12, H14, H15).

## Ronda 2b — clasificación MANUAL a ciegas (enmienda registrada ANTES de clasificar)
Motivo: la auditoría del clasificador por palabras clave mostró demasiados errores (p. ej. un MOU "por $200 M potenciales"
contado como contrato; un contrato de compraventa de acciones y un contra-split contados como humo). Cambio de método:
- Para cada gapper con 8-K/6-K previo a la apertura se extrae un **resumen** (titular + primeras frases del anexo EX-99 o, si no hay
  nota, del primer Item del 8-K). El archivo de resúmenes **no contiene el resultado** de la acción.
- Claude lee cada resumen y asigna **una** categoría con estas definiciones (orden de prioridad):
  - **C compra** — la empresa será comprada con pago en efectivo o precio fijo por acción (fusión definitiva, oferta pública).
  - **F financiación** — oferta de acciones, colocación privada, registered direct, warrants, convertibles, ELOC/SEPA, préstamo.
  - **R resultados** — resultados trimestrales/anuales o cifras preliminares de ventas.
  - **B biotech real** — aprobación/autorización de la FDA u otra agencia, o datos clínicos con resultado (topline, endpoint).
  - **K contrato real** — acuerdo firmado y definitivo con contraparte identificada **y** cifra en dólares (pedido, contrato,
    licencia, venta de activos, adquisición definitiva hecha por la empresa).
  - **H humo / cosmético** — LOI, MOU, acuerdo no vinculante, "partnership/collaboration" sin cifra, "explora/evalúa", pilotos,
    lanzamientos de producto sin ventas, cambios de nombre o giro de negocio (IA, cripto, tesorería de tokens), presentaciones
    en conferencias, patentes, cartas del CEO, recompras simbólicas, nombramientos, premios; y cifras "potenciales/hasta".
  - **S corporativo/bolsa** — contra-split, aviso o recuperación del cumplimiento de Nasdaq, junta de accionistas, cambios de auditor.
  - **O otros / no se puede saber** (sin texto útil).
- Hipótesis (mismo criterio de éxito: mismo sentido en DEV y VAL, VAL t > 2, Holm):
  - **H11b:** H (humo) vs reales (B + K + R) → mejor para el corto si es humo.
  - **H12b:** H vs todo lo demás.
  - **H13b (descriptiva):** C compra en efectivo → no se debe shortear (el precio queda anclado).
  - Descriptivas por categoría: R, WR, ganancia media, pérdida media, PF y % de squeeze (>+50 %) en DEV y VAL.

## Ronda 3 — ejecución DENTRO de la selección (pre-registro, escrito ANTES de ver resultados)
Muestra: gappers (≥ 20 %) con catalizador clasificado (ronda 2b) y velas de 1 h de Yahoo (oct-2023 → sep-2026; ~1 440 casos, 275 "humo").
DEV = oct-2023 → dic-2024 · VAL = ene-2025 → sep-2026. Con velas de 1 min / 5 min solo hay 8 / 24 casos humo: el indicador Reversal
NO se puede validar aún (se reporta solo como descriptivo). VWAP aproximado con velas de 1 h (precio típico × volumen acumulado).
Reglas (salida al cierre; coste 1 %; stop con 5 % de deslizamiento; R = beneficio / distancia al stop):
- **E0 apertura:** corto a la apertura, stop +30 % (setup A).
- **E1 1ª hora roja:** corto a las 10:30 solo si la 1ª vela cierra bajo la apertura; stop = máximo del día hasta ese momento × 1.05 (mín. 3 %).
- **E1c 1ª hora verde** (control de E1): igual pero si cierra sobre la apertura.
- **E2 bajo VWAP a las 11:30:** corto a las 11:30 si el cierre de la 2ª vela está bajo el VWAP; stop = máximo del día × 1.05 (mín. 3 %).
- **E2c sobre VWAP a las 11:30** (control de E2).
Hipótesis (en los gappers humo; se reporta también el resto para comparar):
| # | Hipótesis | Mejor si… |
|---|---|---|
| HE1 | 1ª hora roja vs verde (E1 vs E1c) | roja |
| HE2 | Bajo VWAP vs sobre VWAP a las 11:30 (E2 vs E2c) | bajo VWAP |
| HE3 | Esperar debilidad (E2) vs corto a la apertura (E0), mismas acciones | E2 |
Éxito: mismo sentido en DEV y VAL, VAL t > 2, Holm sobre HE1-HE3.

## Ronda 4 — "día de tema" mejorado (pre-registro, escrito ANTES de ver resultados)
La ronda 2 usó solo una lista fija de palabras (no detecta temas nuevos como "Greenland"). Nueva definición, sobre los 8 604 gappers:
- **Palabra de tema** de un gapper = (a) palabra poco común de su nombre (≥ 4 letras, aparece en ≤ 15 de los 8 604 nombres; así
  "greenland" cuenta y "holdings/therapeutics/energy" no) o (b) palabra de la lista fija de la ronda 2 (IA, cripto, cuántica, drones/defensa,
  nuclear/uranio, minerales, robótica/espacio) en el nombre o en el texto del catalizador.
- **Día de tema:** ese día hay ≥ 2 gappers (gap ≥ 20 %, empresas distintas) que comparten una palabra de tema.
- **Líder** del tema ese día = el de mayor gap; los demás = seguidores.
- Resultado: setup A (corto a la apertura, stop +30 % con 5 % de deslizamiento, coste 1 %). Muestra de prueba: gappers ≥ 50 %.
| # | Hipótesis | Mejor para el corto si… |
|---|---|---|
| HT1 | Día de tema vs día normal (gappers ≥ 50 %) | NO es día de tema |
| HT2 | Dentro de días de tema: seguidor vs líder | seguidor |
| HT3 | Gappers humo (ronda 2b): día de tema vs normal | NO es día de tema |
Éxito: mismo sentido en DEV (2015-21) y VAL (2022-26), VAL t > 2, Holm sobre HT1-HT3.
Limitación conocida: el nombre es el actual de la empresa (no el histórico).

## Ronda 5 — precio real < $1 y coste del locate (pre-registro, escrito ANTES de ver resultados, 28-sep-2026)
Motivo: los locates se cotizan en centavos por acción → en acciones baratas pesan mucho más en R.
**Corrección previa detectada al preparar la ronda:** los precios de Yahoo están ajustados por splits posteriores (WHLR 5-dic-2025 figura
a $36 677). Por eso (1) el "precio" histórico no es el precio real de ese día y (2) la capitalización de la ronda 1 (`mcap` = acciones de
la SEC de esa fecha × apertura AJUSTADA) queda inflada en las empresas que hicieron contra-splits después. Se reconstruye el precio real:
precio real = precio ajustado × producto de los ratios de los splits posteriores a la fecha (`splits.parquet`). Los splits vienen con
fecha de mes (día 1): si hay un split en el mismo mes del evento, el caso es ambiguo → se excluye del análisis principal (se reporta aparte).
Muestra: gappers humo (ronda 2b) con gap ≥ 50 % (la muestra del nivel B), y todos los humo como comparación. Setup A como siempre.
Coste del locate en R = L ÷ (0.30 × precio real de apertura), con L = $0.01, $0.02 y $0.05 por acción (escenarios; sin datos reales aún).
Comisión ida y vuelta con riesgo de $20 ≈ 0.05R (se resta igual a todos).
| # | Hipótesis | Criterio |
|---|---|---|
| HP1 | Humo gap ≥ 50 %: R bruto (coste 1 % como siempre) en precio real < $1 vs ≥ $1 | ¿difiere? (mismo sentido DEV y VAL, VAL t > 2) |
| HP2 | Humo gap ≥ 50 %: R neto con locate $0.02 y comisión 0.05R, < $1 vs ≥ $1 | ≥ $1 mejor (mismo sentido DEV y VAL, VAL t > 2) |
| HP3 | Repetir la prueba de capitalización de la ronda 1 (< $30 M peor) con la capitalización corregida | < $30 M peor (mismo criterio) |
Holm sobre HP1-HP3. Descriptivo: tramos < $1, $1-3, $3-10, ≥ $10; R, WR, ganancia media, pérdida media, PF.
