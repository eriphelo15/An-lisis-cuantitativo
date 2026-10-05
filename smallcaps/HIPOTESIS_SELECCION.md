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

## Ronda 6 — ¿más oportunidades con base medida? (pre-registro, escrito ANTES de ver resultados, 28-sep-2026)
Precio real (ronda 5), solo precio ≥ $1, casos ambiguos por split fuera. Setup base como siempre (corto a la apertura, stop +30 % con 5 %
de deslizamiento, coste 1 %, salida al cierre). DEV 2015-21 / VAL 2022-26. Se reporta R, WR, ganancia media, pérdida media, PF, squeeze.
| # | Grupo | Hipótesis (mejor para el corto si…) |
|---|---|---|
| HM1 | Humo con gap 20-50 % (clasificados en la ronda 2b) vs resto de catalizadores con gap 20-50 % | humo > resto |
| HM2 | Gappers ≥ 50 % **sin 8-K** antes de abrir (aproximación a "sin noticia": la historia no tiene noticias de agencias, solo EDGAR) | descriptivo (¿base > 0?) |
| HM3 | **Día 2** de los humo con gap ≥ 50 %: corto a la apertura del día siguiente, stop +30 %, salida al cierre | descriptivo (¿base > 0?) |
Criterio para considerar una base "utilizable": R > 0 en DEV y en VAL, VAL t > 2. Holm sobre HM1-HM3 (en HM2 y HM3 el test es R ≠ 0).
Limitación de HM2: "sin 8-K" incluye acciones con nota de prensa sin 8-K (humo o no); no es exactamente "sin ninguna noticia".

## Ronda 7 — subgrupos del humo con gap 20-50 % (pre-registro, escrito ANTES de ver resultados, 28-sep-2026)
Muestra: humo (ronda 2b) con gap 20-50 %, precio real ≥ $1, ambiguos fuera; setup base. Criterios elegidos porque YA están validados en
general (ronda 1) — se comprueba si también separan dentro de este grupo:
| # | Subgrupo | Hipótesis |
|---|---|---|
| HS1 | venta 424B en los 90 días previos | con 424B > sin 424B |
| HS2 | shelf S-3 presentado | con S-3 > sin S-3 |
| HS3 | 8-K solo nota de prensa (items 7.01/8.01, sin 1.01) | solo nota > con acuerdo 1.01 |
Base "operable" para un subgrupo: R > 0 en DEV y en VAL, y VAL t (R ≠ 0) > 2. Holm sobre HS1-HS3 (diferencias en VAL).
No se probarán más combinaciones después de ver estos resultados.

## Ronda 8 — "primer día rojo" de Edu Trades / Hamlin (pre-registro, escrito ANTES de ver resultados, 28-sep-2026)
Origen: 33 directos de Edu (`referencias/EDUTRADES.md`). Su patrón ideal: varios días verdes seguidos con **volumen creciente**, y corto el
día que se vuelve rojo ("anticipándome como gap extension con poco size y luego fuerte en la confirmación del green to red").
Diferencia con lo medido antes (06_setups, "G first red day"): allí el corto era el DÍA SIGUIENTE al día rojo; aquí es el MISMO día.
Datos: diario 2015-2026 (Yahoo, universo listado hoy → sesgo de supervivencia), precio real por splits (ronda 5), ambiguos fuera.
**Sin mirar el futuro:** en la apertura del día D solo se sabe lo ocurrido hasta D-1; un corredor de 5 días genera un candidato cada día.
Definiciones:
- Día verde: cierre > cierre anterior. Racha: k ≥ 2 días verdes seguidos que terminan en D-1.
- Subida acumulada: cierre D-1 ÷ cierre del día previo a la racha − 1 ≥ **+100 %**.
- Volumen creciente: cada día de la racha con más volumen que el anterior de la racha.
- Filtros: precio real de apertura D ≥ $1; volumen en dólares de D-1 ≥ $1 M; D abre por encima del cierre D-1 (todavía verde).
Setups (costes como siempre: 1 % ida y vuelta, 5 % de deslizamiento en el stop):
- **A (anticipación):** corto a la apertura de D, stop apertura × 1.30, salida al cierre.
- **B (green to red):** entra solo si el mínimo de D toca el cierre D-1 (se pone rojo); entrada = cierre D-1; stop = apertura × 1.30;
  si el máximo de D alcanza el stop cuenta como stop (conservador: con velas diarias no se sabe el orden); salida al cierre.
| # | Hipótesis | Criterio |
|---|---|---|
| HR1 | Setup A en el patrón completo | R > 0 en DEV 2015-21 y VAL 2022-26, VAL t > 2 |
| HR2 | Setup B en el patrón completo | R > 0 en DEV y VAL, VAL t > 2 |
| HR3 | Volumen creciente vs no creciente (resto igual), setup B | creciente mejor, mismo signo DEV y VAL, VAL t > 2 |
t calculado con la media por episodio (racha) para no contar varias veces el mismo corredor. Holm sobre HR1-HR3 (VAL).
Descriptivo (no cuenta como validación): subida ≥ +50 %; k = 2 vs k ≥ 3; racha "sin ponerse roja en el día" (mínimo ≥ cierre anterior,
criterio de Hamlin); coste de locate 1 % del precio (+0.033R) y comisión 0.05R; primer candidato de cada racha.
No se probarán más variantes después de ver estos resultados.

## Ronda 9 — ideas de las listas de Edu: E1 overextended gap down y E2 historial de la acción (pre-registro, ANTES de ver resultados, 29-sep-2026)
Origen: `referencias/EDUTRADES.md` (listas Patrones/Aprendizaje/Trades). Aprobado por el usuario ("Procede").
Datos: diario 2015-2026 (Yahoo, universo listado hoy → sesgo de supervivencia), precio real por splits (ronda 5), ambiguos fuera,
precio real ≥ $1. Costes como siempre: 1 % ida y vuelta, deslizamiento en el stop. DEV 2015-21 / VAL 2022-26.

**E1 — Overextended gap down (Edu):** tras una sobre extensión, el día D abre POR DEBAJO del cierre de D-1; riesgo = cierre de D-1.
Candidatos con la misma construcción que la ronda 8 (sin mirar el futuro): racha de k ≥ 2 días verdes que termina en D-1, subida
acumulada ≥ +100 %, volumen en dólares de D-1 ≥ $1 M, y **apertura de D < cierre de D-1** (la ronda 8 exigía lo contrario).
- **Setup A:** corto a la apertura de D, stop apertura × 1.30 (+5 % de deslizamiento), salida al cierre.
- **Setup B (el de Edu):** corto a la apertura de D, stop = máx(cierre D-1 × 1.02, apertura × 1.03), relleno del stop con +2 %;
  si el máximo de D toca el stop cuenta como stop (conservador: con velas diarias no se sabe el orden); salida al cierre.
**E2 — Historial de spikes (Edu en ISEE: "las dos veces que hizo más de 20 % cerró rojo"):** en los gappers ≥ 50 % (8 604 eventos,
setup base: corto a la apertura, stop +30 %), mirar los 365 días naturales anteriores excluyendo los 10 días hábiles previos al evento.
Spike previo = día con máximo ≥ cierre anterior × 1.20. "Rojo" = cierre < apertura de ese día. Grupos: sin spikes previos; **mayoría roja**
(≥ 1 spike y ≥ 2/3 rojos); **mayoría verde** (≥ 1 spike y < 2/3 rojos).
| # | Hipótesis | Criterio |
|---|---|---|
| HG1 | E1 setup A: R > 0 | R > 0 en DEV y VAL, VAL t > 2 (t con media por episodio) |
| HG2 | E1 setup B: R > 0 | igual |
| HG3 | E1 (abre bajo el cierre) mejor que la ronda 8 (abre sobre el cierre), setup A | mismo signo DEV y VAL, VAL t > 2 |
| HE2 | E2: mayoría roja mejor que mayoría verde (gap ≥ 50 %) | mismo signo DEV y VAL, VAL t > 2 |
Holm sobre HG1, HG2, HG3, HE2 (VAL).
Descriptivo (no valida nada): E1 con subida ≥ +50 %; E2 dentro del humo gap ≥ 50 %; E2 con "rojo" = devolvió ≥ la mitad de la subida
del día; neto de locate 1 % + comisión 0.05R; frecuencia en el último año.
No se probarán más variantes después de ver estos resultados.

## Ronda 10 — backtest de la ruptura de la vela de las 9:30 con Massive/Polygon (pre-registro, ANTES de descargar datos, 29-sep-2026)
Idea del usuario (`23b_ruptura_930_usuario.py`). Datos: Massive (antes Polygon), plan gratis: velas de 1 min SIN ajustar desde el
29-sep-2024 y barras diarias de todas las acciones de cada día (incluidas las que después dejaron de cotizar → sin sesgo de supervivencia).
**Universo:** días hábiles 1-oct-2024 → 25-sep-2026. Gap = apertura ÷ cierre anterior − 1 con barras diarias ajustadas por splits.
Tickers de 1-5 letras, tipo acción común o ADR (referencia de Massive), fuera warrants/derechos/unidades. Gap 20 %-500 %, volumen en
dólares del día ≥ $1 M (mismo filtro que `02_gappers.py`), precio real de apertura (vela 9:30 sin ajustar) ≥ $1, vela de las 9:30 presente.
**Regla (la del usuario):** O y L = apertura y mínimo de la vela de 1 min de las 9:30; corto al CIERRE de la primera vela que cierra bajo L
(solo hasta las 11:00); un solo intento; sale al cierre de la primera vela que cierra sobre O o a las 11:30. 1R = entrada → O (mín. 2 %).
Coste 0.5 % del precio (sensibilidad: 1 %). Referencia en los mismos días: corto a la apertura de las 9:30, stop +30 % (relleno +5 %), salida 11:30.
**Periodos:** DEV = oct-2024 → sep-2025 · VAL = oct-2025 → sep-2026.
| # | Hipótesis | Criterio |
|---|---|---|
| HB1 | Regla en gap ≥ 50 %: R > 0 | R > 0 en DEV y VAL, VAL t > 2 |
| HB2 | Gap ≥ 50 % mejor que gap 20-50 % | mismo signo DEV y VAL, VAL t > 2 |
| HB3 | Regla mejor que la referencia (corto a la apertura) en gap ≥ 50 %, diferencia por día emparejada | mismo signo DEV y VAL, VAL t > 2 |
Holm sobre HB1-HB3 (VAL). Descriptivo (no valida): gap ≥ 100 %, tipo de catalizador donde haya etiqueta de la ronda 2b, días sin ruptura,
dependencia de los 3-5 mejores días, colas (peor día), coste 1 %, frecuencia por día.
No se probarán más variantes de la regla después de ver estos resultados (cualquier cambio posterior se marcará como exploratorio).

## Ronda 11 — avisos del Radar: pocas acciones y sin munición (pre-registro, ANTES de ver resultados, 29-sep-2026)
Origen: BKYI 29-sep (nivel B; 1.44 M de acciones, sin munición activa; rotación ~59× tras la apertura). Aprobado por el usuario.
Datos: base de la ronda 1/5 (`res_18_precio_real.csv`, 8 604 gappers 2015-26, acciones de la SEC a esa fecha, precio real). Gap ≥ 50 %,
precio real ≥ $1, ambiguos fuera. Setup base: corto a la apertura, stop +30 % (+5 % deslizamiento), coste 1 %, salida al cierre.
Acciones en circulación = capitalización real ÷ precio real (acciones de la SEC en esa fecha).
| # | Hipótesis | Criterio |
|---|---|---|
| HX1 | Menos de 5 M de acciones → corto PEOR que con ≥ 5 M | mismo signo DEV y VAL, VAL t < −2 |
| HX2 | Sin munición activa (sin venta 424B en 90 días y sin shelf S-3) → corto PEOR que con munición | mismo signo DEV y VAL, VAL t < −2 |
Holm sobre HX1-HX2 (VAL). Descriptivo: dentro del humo; las dos condiciones juntas; escalones de acciones (< 2 M, 2-5 M, 5-20 M, > 20 M).
Los avisos se añaden a la ficha como información aunque no se validen; solo cambiarían el NIVEL si se validan.

## Ronda 12 — puntuación global de la tesis de corto (pre-registro, ANTES de ver resultados, 30-sep-2026)
Pedido por el usuario: sustituir las letras por una puntuación global (gap como un factor más) + riesgo estructural aparte.
**Universo:** 3 000 catalizadores clasificados a mano (ronda 2b), gap ≥ 20 %, precio real ≥ $1, ambiguos fuera, y SIN los grupos que el
Radar descarta (C compra en efectivo, R resultados, F financiación, S bolsa) → 1 222 casos (DEV 501 / VAL 721).
**Resultado medido:** setup base (corto a la apertura, stop +30 % con 5 % de deslizamiento, coste 1 %, salida al cierre), en R.
**Factores (todos conocidos antes de la apertura):** gap 50-100 % y gap ≥ 100 % (base 20-50 %); catalizador H humo, B biotech, K contrato
(base O otros); venta 424B en 90 días; shelf S-3; diluidor en serie (≥ 3 ventas 424B en 365 días); 8-K solo nota de prensa.
**Pesos:** regresión lineal de R sobre esos factores SOLO con DEV 2015-21. Puntuación = valor predicho, pasado a 0-100 por percentiles de DEV.
| # | Hipótesis (en VAL 2022-26, pesos congelados de DEV) | Criterio |
|---|---|---|
| HS1 | La puntuación ordena: correlación de rangos puntuación-R > 0 | p < 0.05 (Spearman) |
| HS2 | Tercio alto mejor que tercio bajo | diferencia > 0, t > 2 |
Descriptivo: R, WR, ganancia/pérdida media y PF por tercios en DEV y VAL; dentro de gap ≥ 50 %; pesos obtenidos.
Factores que el Radar ve hoy pero NO existen en el histórico (ATM, ELOC, warrants en dinero, convertible tóxica, going concern, caja):
se mostrarán en la ficha, pero con peso 0 hasta que se puedan medir. El riesgo estructural (acciones < 5 M, precio, rotación) NO entra
en la puntuación: va aparte y limita el tamaño.
Si HS1 y HS2 no se cumplen, la puntuación se usa solo para ordenar la lista, marcada "no validada".

## Ronda 13 — E4 de Edu: precio del gap frente al precio de la última colocación (pre-registro, ANTES de ver resultados, 1-oct-2026)
Aprobado por el usuario el 1-oct. Origen: CNTB 30-sep (compradores a $3.25, acción a $1.10 = en pérdida) y RZAI 1-oct (preferentes a $8,
acción a $37 = muy en ganancia). Idea: si quien compró en la última colocación está muy en ganancia, tiene incentivo a vender en el pump
(más oferta → mejor para el corto); si está en pérdida, no.
**Universo:** base de la ronda 5/11 (`res_18_precio_real.csv`): gap ≥ 50 %, precio real ≥ $1, ambiguos fuera (2 089 casos). Resultado = R del
setup base (corto a la apertura, stop +30 % con 5 % de deslizamiento, coste 1 %, salida al cierre). DEV 2015-21 / VAL 2022-26.
**Última colocación:** el último folleto con precio (424B1, 424B4 o 424B5) aceptado en los 365 días anteriores, ANTES del cierre previo
(16:00 del día hábil anterior; lo del mismo día es "financiación de hoy", que el Radar descarta). Precio = primera frase de la portada del
tipo "public offering price of $X per share" / "offering price … $X per share" (incluye "combined … per share and accompanying warrant").
Folletos sin precio fijo (ATM "at-the-market") o sin frase legible = sin precio (se cuentan aparte, no entran en HE).
Precio ajustado por los splits entre la colocación y el gap (`splits.parquet`); si hay un split en el mismo mes de la colocación o del gap,
el caso es ambiguo y queda fuera. **Ratio = precio de apertura real ÷ precio de la colocación ajustado.**
Control de calidad ANTES de medir: leer a mano 20 folletos al azar y comprobar el precio extraído; si hay > 2 errores, corregir el lector.
| # | Hipótesis | Criterio |
|---|---|---|
| HE4a | Ratio ≥ 2 (compradores muy en ganancia) → corto MEJOR que ratio < 1 (compradores en pérdida) | mismo signo DEV y VAL, VAL t > 2 |
| HE4b | El ratio ordena: correlación de rangos ratio-R > 0 (casos con precio) | VAL p < 0.05 (Spearman), mismo signo en DEV |
Holm sobre HE4a-HE4b (VAL). Descriptivo (no valida): tramos < 1, 1-1.5, 1.5-2, 2-4, ≥ 4; sin colocación en 365 días; colocación sin precio
(ATM); dentro de los casos que el Radar no descarta (etiqueta 2b ≠ C/R/F/S, donde exista); efecto añadido a la puntuación de la ronda 12
(regresión con la puntuación como control). Colocaciones privadas (8-K Item 3.02) NO entran (no hay lector histórico fiable): limitación.
Si se valida, se propondrá al usuario como factor nuevo de la puntuación (pesos de DEV); no se cambia nada sin su aprobación.
**Enmienda (1-oct, ANTES de ver ningún resultado de R; la salida de una medición de prueba se borró sin leer):** el ajuste por
`splits.parquet` no es fiable: Yahoo omite contra-splits en su lista de eventos aunque los aplica a sus precios (CRIS 1:20 del 29-sep-2023,
SVRE cambio de ratio ADS 1:13.33 del 21-feb-2025; comprobado con Massive). Contra velas sin ajustar de Massive (2 313 casos oct-24→sep-26),
el "precio real" de la ronda 5 acierta (±3 %) el 94 % y un ajuste con la lista de splits de Massive el 93 %, con errores distintos.
**Método nuevo, sin listas de splits:** todo en la serie ajustada de Yahoo. El propio folleto dice el último precio de mercado ("last
reported sale price … on [fecha] was $X"); factor k = cierre ajustado de Yahoo de esa fecha ÷ X; colocación ajustada = precio de la
colocación × k; **ratio = apertura ajustada del gap ÷ colocación ajustada**. Folletos sin esa frase (sobre todo salidas a bolsa, sin mercado
previo) = sin precio comparable, se cuentan aparte. Hipótesis, tramos y criterios NO cambian.
Control de calidad añadido: comparar la fecha y el precio de mercado extraídos en 20 folletos al azar (≤ 2 errores).
Filtro de calidad (decidido ANTES de ver R, mirando solo precios): se usa la colocación solo si precio de colocación ÷ precio de mercado del
folleto está entre 0.3 y 1.3 (rango normal de una colocación registrada; mediana medida 0.885). Fuera de ese rango casi siempre es una lectura
mezclada (precio por ADS frente a acción ordinaria, valor nominal $0.0001 leído como precio, colocaciones antiguas citadas): 31 de 280.

## Ronda 14 — LADO LARGO, fase 1 (pre-registro, ANTES de ver resultados, 5-oct-2026)
Pedido por el usuario: un radar de largos con criterios propios del lado largo, foco en small caps y más pequeñas, trabajo de campo más
profundo que en cortos porque el sesgo natural de los gappers es bajista. Las hipótesis son de CAMPO (SEC + catalizador); el gap solo define
el universo. Datos: base corregida de la ronda 12 (`res_18_precio_real.csv` + precios de `res_29_precios.csv`/`30_ronda12_corregida.py`),
8 604 gappers ≥ 20 %, precio real ≥ $1, etiquetas manuales del catalizador (3 000). DEV 2015-21 / VAL 2022-26.
**Resultado (setup base largo, mecánico, solo referencia):** compra a la apertura; stop −20 % (si el mínimo del día toca open × 0.80, salida a
open × 0.80 × 0.98 por deslizamiento); si no, salida al cierre. Coste 0.5 % (sin locate). R = ((salida − apertura)/apertura − 0.005)/0.20.
Variante día 2: si no salta el stop el día 1, se mantiene hasta el cierre del día 2 (stop igual; si el día 2 abre por debajo del stop, salida a la
apertura del día 2). Descriptivo: % de casos con máximo ≥ +50 % y ≥ +100 % sobre la apertura (la cola que da la asimetría).
**Munición activa** = venta 424B en 90 días o shelf S-3/F-3 de 3 años (definiciones validadas en cortos). **Catalizador real** = etiqueta K o B.
| # | Hipótesis | Criterio |
|---|---|---|
| HL1 | Catalizador real (K/B) + SIN munición → largo R > 0 (día 1) | R > 0 en DEV y VAL, VAL t > 2 |
| HL2 | Catalizador real (K/B): SIN munición mejor que CON munición (la munición es veto) | mismo signo DEV y VAL, VAL t > 2 |
| HL3 | HL1 + pocas acciones (< 5 M) mejor que HL1 con ≥ 5 M | mismo signo DEV y VAL, VAL t > 2 |
| HL4 | Tesis bajista BAJA (tercio bajo de la puntuación corta) → largo R > 0 | R > 0 en DEV y VAL, VAL t > 2 |
Holm sobre HL1-HL4 (VAL). Descriptivo (no valida): variante día 2; por tramo de gap; humo (H) como control negativo (se espera largo < 0);
sin noticia (N); cola ≥ +50 / +100 %. Pendiente de fases 1b/1c con datos nuevos (no se miden aquí): compras de directivos (Form 4 código P),
13D/13G nuevos, caja a la fecha, float verificado, curva de tiempo desde la hora del documento (velas de 1 min de Massive).
Si nada se valida, el radar de largos NO se construye sobre estas reglas.

## Ronda 15 — LADO LARGO con TRABAJO DE CAMPO PRIMERO (pre-registro, 5-oct-2026, ANTES de mirar ningún precio posterior al evento)
Pedido por el usuario tras la ronda 14: "el trabajo de campo es lo que filtra; el backtest se hace SOBRE las acciones filtradas". La ronda 14
partía de los gappers (selección por precio) y usaba etiquetas pensadas para el corto → muestra contaminada. Aquí el orden es:
**documento de la SEC → trabajo de campo de largo (sin ver precios posteriores) → backtest solo de los que pasan.**

**Datos (sin sesgo de supervivencia):** Massive (incluye empresas deslistadas; diario sin ajustar y ajustado; 1 min con pre y post mercado).
El plan gratis solo cubre ~2 años → ventana de eventos 7-oct-2024 → 25-sep-2026. DEV = 7-oct-2024 → 30-sep-2025; VAL = 1-oct-2025 → 25-sep-2026.
NO se usan 2015-2024: los diarios de Yahoo solo tienen las empresas que siguen vivas, y para el largo eso infla el resultado (las que quebraron
y se deslistaron, que serían pérdidas, no están). Documentos: índice completo de EDGAR (8-K y 6-K originales) + submissions (hora de aceptación
e items) + XBRL companyfacts (acciones, caja, flujo operativo, solo lo presentado ANTES del evento).

**Universo U1 (automático, nada posterior al evento):** 8-K con item 1.01, 2.01, 2.02, 7.01 u 8.01, o 6-K; empresa con acción común (CS/ADR)
en Massive que cotizó la sesión anterior; cierre anterior sin ajustar ≥ $1; capitalización previa (acciones del último XBRL presentado antes del
evento, corregidas por splits posteriores a esa fecha, × cierre anterior) < $300 M; volumen medio en $ de las 20 sesiones previas ≥ $50 000.
Varios documentos de la misma empresa en la misma ventana de sesión = un solo evento (hora del primero; se leen todos).

**Embudo de campo (lista de comprobación de largo):**
- **A (automático) — ¿puede la empresa vender acciones encima de la subida?** A1: ninguna 424B en los 90 días previos; A2: ni 424B, S-1,
  S-3, F-1, F-3 ni item 3.02 entre el día anterior y el evento; A3: caja + inversiones a corto ≥ 12 meses de quema (flujo operativo del último
  periodo presentado, dividido por sus meses reales) o flujo operativo ≥ 0.
- **B (lectura a ciegas del 8-K/6-K y TODOS sus EX-99, sin precios) — ¿la noticia cambia la empresa?** Tipo de largo:
  CONTRATO_FIRME (acuerdo/pedido/adjudicación firmado, contraparte con nombre, importe en $ concreto; no "hasta", no marco, no LOI/MOU);
  FDA_APROBACION (aprobación/autorización de comercialización, FDA u otra agencia principal); DATOS_POSITIVOS (ensayo fase 2/3 que cumple el
  objetivo principal con significación estadística); RESULTADOS_FUERTES (ventas ≥ +30 % interanual y beneficio operativo positivo o mejora clara,
  o subida de previsiones); INVERSION_ESTRATEGICA (empresa operativa compra acciones a precio ≥ mercado); ADQUISICION_DE_LA_EMPRESA (excluida:
  el precio queda topado); HUMO; FINANCIACION; RUTINARIO; NEGATIVO. Cada clasificación lleva frase literal en inglés + importe.
  **Pasa B:** CONTRATO_FIRME con importe ≥ 10 % de la capitalización previa, FDA_APROBACION, DATOS_POSITIVOS, RESULTADOS_FUERTES, INVERSION_ESTRATEGICA.
- **C (lectura profunda del último 10-Q/10-K/20-F previo, solo para quien pasa A y B):** sin convertible de precio variable (tóxica), sin ATM
  ni ELOC/SEPA activo, sin duda de "going concern". Warrants con precio de ejercicio ≤ 1.2 × cierre previo = factor secundario (no excluye).
- **Verificación (precisión):** cada evento que pasa B se relee por un segundo agente ciego; además una muestra aleatoria del 15 % de los que NO
  pasan. Discrepancias: Claude lee la fuente y decide antes de ver precios. Tasa de acuerdo publicada.

**Backtest (referencia mecánica, la ejecución real es del usuario):** largo, stop −20 % (si el mínimo toca entrada × 0.80 → salida a 0.80 × 0.98;
si una sesión abre por debajo del stop → salida a esa apertura), coste 0.5 %, R = rentabilidad / 0.20.
Entrada principal E1 = primera apertura regular posterior a la aceptación (antes de 9:30 → apertura del mismo día; 9:30-16:00 o después →
apertura del día siguiente). Secundaria E2 = primera vela de 1 min con volumen que empiece ≥ 1 min después de la aceptación (4:00-20:00;
madrugada → primera vela de pre-mercado), + 1 % de deslizamiento. Salidas: S1 cierre de la sesión de entrada, S3 cierre de la 3.ª, S5 de la 5.ª.
| # | Hipótesis | Criterio |
|---|---|---|
| HL5 | Filtrados (A+B+C) → largo E1 R > 0 | R > 0 en DEV y en VAL por separado, t conjunto > 2, en S1, S3 o S5 (Holm sobre las 3) |
| HL6 | Filtrados mejores que el resto de U1 | diferencia > 0 en DEV y VAL, t conjunto > 2 (misma salida ganadora de HL5) |
Si VAL tiene < 30 filtrados → "no medible", no validado. Descriptivo (no valida): por tipo de largo, nano (< $50 M) vs micro, < 10 M acciones,
compras de directivos (Form 4 'P' en 90 días), 13D nuevo, warrants en el dinero, cuánto subió ya a la apertura, entrada E2, cola ≥ +50/+100 %.
Si nada se valida, NO se construye el radar de largos con estas reglas; el resultado se dice tal cual.
