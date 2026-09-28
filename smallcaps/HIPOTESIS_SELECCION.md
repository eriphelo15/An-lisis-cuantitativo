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
