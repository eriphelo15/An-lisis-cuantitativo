# Validación de criterios de selección — resultados

Pre-registro: `HIPOTESIS_SELECCION.md` (commit aa7afa9). Script: `11_seleccion.py`. 8 604 gappers 2015-2026 con historial EDGAR
reconstruido a la hora exacta (solo documentos aceptados antes de las 9:30 del día del gap).
Resultado medido: setup A (corto a la apertura, stop +30 %, 5 % de deslizamiento, coste 1 %), en R.
DEV 2015-2021 (2 712 gappers) · VAL 2022-2026 (5 892).

## Hipótesis pre-registradas (VAL, cumple vs resto)
| Hipótesis | DEV dif. R | VAL: cumple (R / PF) | VAL: resto (R / PF) | VAL dif. R (t) | Veredicto |
|---|---|---|---|---|---|
| **H2 venta 424B en los 90 días previos** | +0.060 | **+0.040 / 1.11** | −0.096 / 0.75 | **+0.136 (5.7)** | ✅ VALIDADA (Holm) |
| **H1 shelf S-3 en 3 años** | +0.048 | −0.021 / 0.94 | −0.094 / 0.76 | +0.072 (3.2) | ✅ VALIDADA (Holm) |
| **H5 8-K solo nota de prensa (vs acuerdo 1.01)** | +0.066 | **+0.074 / 1.24** | −0.077 / 0.80 | +0.151 (2.7) | ✅ VALIDADA (Holm; muestras pequeñas: 448 vs 443) |
| H3 diluidor en serie (≥3 424B/año) | −0.007 | +0.017 / 1.05 | −0.076 / 0.80 | +0.093 (3.7) | ❌ signo distinto en DEV |
| H4 sin 8-K antes de abrir | −0.015 | | | +0.035 (1.5) | ❌ |
| H6 contra-split o aviso de bolsa (12 m) | −0.051 | | | +0.002 (0.1) | ❌ sin efecto |
| H7 NO es día de tema (proxy: sector SIC) | +0.024 | | | −0.030 (−1.1) | ❌ (el proxy por sector no captura "temas" como Groenlandia) |
| H10 combinación A | −0.002 | +0.007 | −0.069 | +0.077 (2.9) | ❌ signo distinto en DEV |
| H8 (exploratoria) capitalización < $30 M | −0.033 | −0.131 / 0.70 | −0.034 / 0.91 | −0.097 (−3.0) | ⚠️ PEOR para el corto (más squeezes: 18 % vs 14 %) |

## Lo que más pesa: tamaño del gap × venta reciente (exploratorio, decidido tras ver H1-H10)
| Gap | Todos (VAL) R / PF | Con venta 424B 90 d y cap ≥ $30 M (VAL) R / WR / PF | Sin venta reciente (VAL) R / PF |
|---|---|---|---|
| 20-50 % | −0.089 / 0.74 | +0.027 / 62 % / 1.09 | −0.134 / 0.62 |
| 50-100 % | −0.008 / 0.98 | **+0.095 / 64 % / 1.24** (DEV +0.024) | −0.068 / 0.84 |
| ≥ 100 % | +0.078 / 1.16 | **+0.119 / 58 % / 1.25** (DEV +0.124) | +0.049 / 1.10 |

## Conclusiones
1. **El criterio más sólido es "la empresa vendió acciones (424B) en los últimos 90 días"**: confirmado en los dos periodos y el más significativo.
   Convierte gappers mediocres en positivos y mejora los gaps grandes.
2. **Shelf S-3** también ayuda, menos. **Catalizador con 8-K de solo nota de prensa** es mejor para el corto que un acuerdo firmado (1.01).
3. **Las empresas muy pequeñas (< $30 M) son PEORES para el corto**: más squeezes. Evitarlas o tamaño mínimo.
4. **No se confirmaron:** "sin 8-K", contra-splits/avisos de bolsa, diluidor en serie y "día de tema" medido por sector.
   El "día de tema" tipo GRML/GLND necesita una definición mejor (por palabras clave del nombre o noticia) antes de descartarlo.
5. **Selección validada hoy:** gap ≥ 50 % + venta 424B en 90 días + capitalización ≥ $30 M → ≈ +0.10-0.12R, PF ≈ 1.25 con el setup mecánico A.
   Aún por debajo de +0.20R (el umbral acordado para subir el riesgo al 5 %). La ejecución fina (Módulo 5-6) y más criterios deben sumar el resto.

## Ronda 2b — contenido del catalizador (clasificación manual a ciegas, `14`→`14b`→`15_catalizador_manual.py`)
3 000 gappers con 8-K/6-K entre el cierre anterior y las 9:30. Cada nota se leyó (titular + primeras frases) **sin ver el resultado** y se
clasificó con las definiciones registradas antes (commit e1c2798). Etiquetas en `etiquetas_catalizador/`; ~770 de resultados/avisos se
etiquetaron con una regla fija (Item 2.02 = resultados, 3.01/5.07 = bolsa). El clasificador por palabras clave (ronda 2, `13_`) se descartó por impreciso.

**Setup A (corto a la apertura, stop +30 % con 5 % de deslizamiento, coste 1 %):**
| Catalizador | DEV 2015-21 R / WR / PF (n) | VAL 2022-26 R / WR / gan. media / pérd. media / PF (n) | Squeeze >+50 % (VAL) |
|---|---|---|---|
| **Humo / cosmético** | **+0.100 / 66 % / 1.33 (199)** | **+0.145 / 66 % / +0.70 / −0.91 / 1.46 (386)** | 14 % |
| Contrato real con cifra | +0.104 / 72 % / 1.66 (67) | +0.012 / 61 % / 1.05 (83) | 6 % |
| Biotech real (FDA / datos) | +0.097 / 71 % / 1.42 (149) | −0.008 / 59 % / 0.98 (201) | 12 % |
| Resultados | −0.025 / 58 % / 0.90 (251) | −0.114 / 46 % / 0.61 (696) | 6 % |
| Financiación (oferta, PIPE, ELOC) | −0.056 / 54 % / 0.84 (56) | −0.119 / 54 % / 0.72 (271) | 18 % |
| Corporativo / bolsa | −0.119 / 60 % / 0.74 (25) | −0.172 / 50 % / 0.64 (113) | 20 % |
| Compra en efectivo | (2) | −0.038 / 8 % / 0.23 (13) — el precio queda anclado | 0 % |
| Otros | −0.082 / 57 % / 0.78 (170) | −0.037 / 56 % / 0.90 (318) | 15 % |

**Hipótesis pre-registradas:**
| # | DEV dif. R (t) | VAL dif. R (t) | Veredicto |
|---|---|---|---|
| H11b humo vs catalizador real (B+K+R) | +0.068 (1.0) | **+0.227 (4.5)** | ✅ VALIDADA (mismo sentido, Holm) |
| H12b humo vs todo lo demás | +0.107 (1.7) | **+0.230 (4.7)** | ✅ VALIDADA (mismo sentido, Holm) |
| H13b compra en efectivo | — | WR 8 % | ✅ descriptiva: no shortear |

**Exploratorio (decidido tras ver los resultados):**
| Filtro | DEV R / WR / PF (n) | VAL R / WR / gan. / pérd. / PF (n) |
|---|---|---|
| Humo + gap ≥ 50 % | +0.150 / 66 % / 1.39 (79) | **+0.222 / 68 % / +0.85 / −1.10 / 1.63 (168)** |
| Humo + gap ≥ 100 % | +0.353 / 70 % / 2.12 (20) | **+0.399 / 73 % / +0.96 / −1.09 / 2.33 (73)** |
| Humo + gap ≥ 50 % + venta 424B 90 d | +0.063 / 65 % / 1.16 (31) | +0.301 / 69 % / 1.87 (68) |
| Humo + gap ≥ 50 % + cap ≥ $30 M | +0.052 / 60 % / 1.12 (58) | +0.229 / 65 % / 1.59 (85) |
Humo por año (R): 2019 +0.56, 2020 +0.02, 2021 +0.21, 2022 −0.04, 2023 +0.07, 2024 +0.09, 2025 +0.22, 2026 +0.21 → positivo en la mayoría de años recientes, no en todos.

**Conclusiones ronda 2b:**
1. **El contenido del catalizador es el criterio más fuerte medido hasta ahora.** Un gap por humo/cosmético se desinfla: VAL +0.145R (PF 1.46)
   frente a −0.08R del resto. Con gap ≥ 50 % sube a +0.22R (PF 1.63): **primera vez que se supera el umbral de +0.20R en VAL**.
2. **Resultados, financiación y avisos de bolsa son MALOS para el corto** (PF 0.6-0.7 en VAL): el gap por resultados suele sostenerse.
3. **Compra en efectivo: nunca shortear** (el precio queda clavado al precio de compra).
4. Contratos reales y FDA fueron buenos en 2015-21 pero ≈ 0R en 2022-26: el mercado ya no los vende tan rápido.
5. **Cautelas:** (a) la clasificación la hizo una sola persona (Claude) y aunque fue a ciegas, conocer algunos casos famosos puede sesgar;
   (b) los filtros exploratorios (gap ≥ 100 %, combinaciones) tienen muestras de 20-70 y deben confirmarse con operaciones nuevas;
   (c) la pérdida media (~−1.1R) incluye el deslizamiento del stop: los squeezes siguen ocurriendo (14-17 %).

## Ronda 3 — ejecución dentro de la selección (`16_ejecucion_humo.py`, velas de 1 h, oct-2023 → sep-2026)
1 239 gappers con catalizador clasificado y velas de 1 h (222 humo). DEV = oct-2023 → dic-2024, VAL = 2025-26.
| Regla (gappers humo) | DEV R / WR / PF (n) | VAL R / WR / gan. / pérd. / PF (n) |
|---|---|---|
| **E0 corto a la apertura, stop +30 %** | **+0.139 / 67 % / 1.46 (60)** | **+0.224 / 69 % / +0.75 / −0.95 / 1.76 (162)** |
| E1 a las 10:30 si la 1ª hora es roja | +0.095 / 61 % / 1.57 (41) | +0.010 / 57 % / 1.04 (126) |
| E1c a las 10:30 si la 1ª hora es verde | −0.346 / 42 % / 0.49 (19) | −0.075 / 56 % / 0.86 (36) |
| E2 a las 11:30 bajo el VWAP | −0.052 / 46 % / 0.70 (48) | +0.033 / 56 % / 1.24 (124) |
| E2c a las 11:30 sobre el VWAP | −0.033 / 58 % / 0.94 (12) | −0.295 / 53 % / 0.55 (38) |
| (Gappers NO humo) E0 apertura | −0.151 / 46 % / 0.60 (254) | −0.081 / 50 % / 0.75 (763) |

| Hipótesis | DEV dif. R (t) | VAL dif. R (t) | Veredicto |
|---|---|---|---|
| HE1 1ª hora roja vs verde | +0.44 (1.4) | +0.08 (0.3) | ❌ no significativa |
| HE2 bajo vs sobre VWAP (11:30) | −0.02 (−0.1) | +0.33 (1.7) | ❌ no validada (signo distinto en DEV) |
| HE3 esperar debilidad (E2) vs apertura (E0) | −0.43 (−4.7) | **−0.38 (−5.5)** | ❌ **al revés: esperar es PEOR** (validado en sentido contrario) |

Exploratorio: corto a la apertura + **salir a las 11:30 si el precio sigue sobre el VWAP** → VAL +0.249R, PF 1.99 (vs +0.224R, PF 1.76);
pérdida media −0.83R en vez de −0.95R; DEV +0.146R vs +0.139R. Mejora pequeña, a confirmar.
Velas de 1 / 5 min: solo 8 / 24 casos humo → el indicador Reversal y la entrada fina NO se pueden validar aún con datos gratuitos.

**Conclusiones ronda 3:**
1. En gappers humo **la caída ocurre pronto**: entrar a la apertura (o en el primer empuje) captura la mayor parte; esperar a 10:30-11:30 deja
   sin la mejor parte del movimiento (−0.4R por operación, muy significativo en los dos periodos).
2. Los filtros de "confirmación" (1ª hora roja, bajo VWAP) no añaden ventaja medible con velas de 1 h.
3. Estar **sobre el VWAP a las 11:30** es mala señal (VAL −0.30R): sirve como regla de salida/no añadir, no como filtro de entrada (exploratorio).
4. **La selección manda:** con la misma regla E0, humo = +0.22R y el resto = −0.08R.

## Ronda 4 — "día de tema" mejorado (`17_dia_de_tema.py`)
Día de tema = ≥ 2 gappers (≥ 20 %) el mismo día que comparten palabra poco común del nombre o tema de la lista (en nombre o catalizador).
Gappers ≥ 50 %, setup A:
| Grupo | DEV 2015-21 R / WR / PF (n) | VAL 2022-26 R / WR / gan. / pérd. / PF (n) | Squeeze (VAL) |
|---|---|---|---|
| Día normal | +0.076 / 63 % / 1.19 (777) | +0.007 / 59 % / +0.77 / −1.07 / 1.02 (2 024) | 21 % |
| **Día de tema** | −0.011 (5) — sin muestra | **+0.303 / 72 % / +0.81 / −1.03 / 2.06 (119; 87 días)** | 13 % |
| Tema: líder | (5) | +0.287 / 71 % / 1.90 (92) | 15 % |
| Tema: seguidor | (0) | +0.359 / 78 % / 3.02 (27) | 7 % |
| Humo en día normal | +0.166 / 66 % / 1.44 (77) | +0.184 / 67 % / 1.50 (144) | 18 % |
| Humo en día de tema | (2) | +0.447 / 75 % / 2.64 (24) | 13 % |

| Hipótesis | VAL dif. R (t) | Veredicto |
|---|---|---|
| HT1 "no shortear en día de tema" | −0.30 (−3.2; por días: t −2.4, 87 días) | ❌ **al revés**: en 2022-26 los días de tema fueron MEJORES para el corto; DEV sin muestra (5 casos) → no validado en ningún sentido |
| HT2 seguidor mejor que líder | +0.07 (0.4) | ❌ no significativa |
| HT3 humo fuera de día de tema | −0.26 (−1.1) | ❌ no significativa (signo al revés) |

Por tema (VAL): IA +0.45R (77), robótica/espacio +0.29R (25), cripto +0.17R (20), drones/defensa −0.34R (7).
Las palabras raras del nombre casi nunca forman tema (Greenland, Argentina…): casi todos los días de tema vienen de la lista (IA, cripto, espacio).
GRML/GLND (21-sep-2026) sí salen como día de tema: GRML (líder) perdió −1.25R (stop), GLND ganó +0.12R.

**Conclusiones ronda 4:**
1. **La idea "día de tema = no shortear" NO se sostiene con datos**: en 2022-26 los gappers de tema (sobre todo IA) se desinflaron MÁS.
   GRML fue un caso real de squeeze, pero no la regla. En 2015-21 casi no hay días de tema detectables, así que no hay confirmación.
2. Tampoco hay diferencia clara entre líder y seguidores.
3. Lo que protege del squeeze sigue siendo la selección validada (humo + munición + cap ≥ $30 M) y el tamaño; el tema no es un filtro.

## Ronda 5 — precio real < $1, coste del locate y capitalización corregida (28-sep-2026)
Script `18_precio_real.py` (pre-registro en `HIPOTESIS_SELECCION.md`). **Error de datos detectado y corregido:** Yahoo ajusta los precios por
splits posteriores (el 55 % de los gappers hizo split después; precio mediano de apertura "ajustado" $16.07 vs real **$2.72**). El R del setup
no cambia (usa proporciones), pero sí cualquier criterio en dólares: precio y **capitalización** (mediana de la ronda 1 $468 M vs real **$41 M**).
Se reconstruye el precio real con `splits.parquet`; 547 casos con split en el mismo mes quedan apartados (ambiguos).

**Humo con gap ≥ 50 % por precio real** (R bruto con coste 1 %; neto = − locate ÷ (0.30 × precio) − 0.05R de comisión):
| Tramo | VAL n | VAL R bruto | WR | PF | Neto locate $0.01 | $0.02 | $0.05 | DEV R bruto (n) |
|---|---|---|---|---|---|---|---|---|
| < $1 | 40 | +0.26 | 70 % | 1.68 | +0.03 | **−0.14** | −0.66 | +0.14 (8) |
| $1-3 | 58 | +0.21 | 66 % | 1.61 | +0.14 | +0.13 | +0.07 | −0.08 (19) |
| $3-10 | 46 | +0.20 | 70 % | 1.62 | +0.14 | +0.14 | +0.12 | +0.20 (34) |
| ≥ $10 | 12 | +0.21 | 67 % | 1.59 | +0.15 | +0.15 | +0.14 | +0.23 (12) |
- **HP1 (bruto < $1 vs ≥ $1): sin diferencia** (VAL +0.26 vs +0.21, t 0.25). La ventaja antes de costes es la misma.
- **HP2 (neto con locate $0.02): ≥ $1 mejor** en DEV y VAL (VAL +0.13R vs −0.14R) pero **t 1.0 → no validado** (solo 40 casos < $1).
  Es aritmética más que estadística: el locate en centavos pesa ~3-6 veces más en R en una acción de $0.40 que en una de $2.
- **HP3 (capitalización corregida < $30 M peor): NO se confirma** (VAL −0.055 vs −0.048, t −0.3; por tramos no hay patrón). El hallazgo
  "cap < $30 M = peor" de la ronda 1 era un **artefacto** del precio ajustado. Se retira el aviso del Radar.
- Nivel A: sus estadísticas (+0.30R, n 68) son de humo + gap ≥ 50 % + 424B 90 d **sin** filtro de capitalización; en DEV el 424B dentro del
  humo va al revés (+0.06 con 424B vs +0.21 sin) → la ventaja de A sobre B **no está validada**.
- Rotación > 10× (07_filtros) revisada con volumen corregido: se mantiene (VAL −0.13R; DEV −0.25R).
**Decisión práctica:** en acciones < $1 operar solo con locate ≤ ~$0.01 por acción (≈ 2.5 % del precio deja la mitad de la ventaja); en ≥ $1 el
locate típico ($0.02) deja ~+0.13R netos. Medir los locates reales en el diario.

## Ronda 6 — ¿más oportunidades con base medida? (28-sep-2026)
Script `19_mas_oportunidades.py` (pre-registro en `HIPOTESIS_SELECCION.md`). Precio real ≥ $1, setup base.
| Grupo | Periodo | n | R | WR | Gan. media | Pérd. media | PF |
|---|---|---|---|---|---|---|---|
| Humo gap 20-50 % | DEV | 99 | +0.02 | 67 % | +0.43 | −0.80 | 1.09 |
| Humo gap 20-50 % | VAL | 138 | +0.09 | 65 % | +0.57 | −0.76 | 1.35 |
| Resto gap 20-50 % | VAL | 950 | −0.12 | 46 % | +0.36 | −0.54 | 0.57 |
| Sin 8-K, gap ≥ 50 % | DEV | 511 | +0.12 | 64 % | +0.79 | −1.07 | 1.31 |
| Sin 8-K, gap ≥ 50 % | VAL | 1 065 | +0.00 | 58 % | +0.78 | −1.06 | 1.00 |
| Día 2 del humo gap ≥ 50 % | DEV | 65 | +0.03 | 63 % | +0.33 | −0.48 | 1.17 |
| Día 2 del humo gap ≥ 50 % | VAL | 116 | −0.05 | 48 % | +0.36 | −0.43 | 0.79 |
- HM1: el humo 20-50 % es **mejor que el resto** de su tramo (VAL t 3.1, Holm OK; mismo sentido en DEV, muy pequeño), pero su base propia es
  pequeña (+0.02 / +0.09R, t 1.4) → tras costes ≈ 0: parecida al nivel B. ~0.4 casos/día con precio ≥ $1.
- HM2 (sin 8-K ≈ sin noticia): base ≈ 0 en VAL (+0.00R) → no utilizable.
- HM3 (día 2 del humo): ≈ 0 / negativo → no utilizable.
**Conclusión:** ninguna de las tres añade una base positiva validada; la única base fuerte sigue siendo el nivel A (humo + gap ≥ 100 % + ≥ $1).

## Ronda 7 — subgrupos del humo 20-50 % (28-sep-2026)
Script `20_humo_20_50.py`, 237 casos (≥ $1). Ningún subgrupo pasa el criterio pre-registrado (Holm: ninguno).
| Subgrupo | DEV R (n) | VAL R (n) | VAL WR | VAL PF | resto VAL R |
|---|---|---|---|---|---|
| con 424B 90 d | +0.01 (34) | +0.06 (43) | 67 % | 1.16 | +0.11 |
| con shelf S-3 | +0.05 (72) | **+0.15 (87)** | 67 % | 1.60 | −0.01 |
| solo nota de prensa (vs 1.01) | +0.07 (46) | +0.15 (63) | 64 % | 1.61 | −0.08 (12) |
Lo más prometedor: humo 20-50 % + shelf S-3 (mismo sentido en ambos periodos, VAL t 1.75) — no validado; se sigue en vivo.

## Ronda 8 — "primer día rojo" de Edu Trades / Hamlin, corto el mismo día (28-sep-2026)
Script `21_primer_dia_rojo.py` (pre-registro en `HIPOTESIS_SELECCION.md`). Diario 2015-2026, precio real ≥ $1, sin mirar el futuro
(un corredor de varios días genera un candidato cada día). Patrón completo: ≥ 2 días verdes seguidos, subida acumulada ≥ +100 %,
volumen creciente en la racha, el día D abre todavía verde. A = corto a la apertura; B = corto cuando se pone rojo (toca el cierre de D-1).
| Grupo | Setup | Periodo | n | R | WR | Gan. media | Pérd. media | PF |
|---|---|---|---|---|---|---|---|---|
| Patrón completo | A | DEV | 165 | +0.03 | 60 % | +0.66 | −0.93 | 1.07 |
| Patrón completo | A | VAL | 220 | −0.02 | 56 % | +0.57 | −0.78 | 0.95 |
| Patrón completo | B | DEV | 98 | +0.07 | 68 % | +0.29 | −0.43 | 1.47 |
| Patrón completo | B | VAL | 127 | −0.01 | 54 % | +0.29 | −0.35 | 0.94 |
| Volumen NO creciente | B | DEV | 259 | +0.04 | 57 % | +0.28 | −0.27 | 1.37 |
| Volumen NO creciente | B | VAL | 610 | +0.01 | 57 % | +0.33 | −0.41 | 1.08 |
- HR1 (A) VAL t 0.06, HR2 (B) VAL t −0.23, HR3 (volumen creciente mejor) VAL t −1.39 (al revés): **ninguna validada (Holm: ninguna)**.
- Con costes reales (locate 1 % del precio + comisión 0.05R): A −0.06R DEV / −0.10R VAL; B −0.01R DEV / −0.08R VAL.
- Descriptivo (no validación): racha de 2 días B VAL +0.07R (n 60); racha "sin ponerse roja en el día" (Hamlin) B VAL +0.08R (n 28) —
  muestras pequeñas; ≥ 3 días B VAL −0.08R. Solo el 39 % de los candidatos acaba cerrando rojo.
- Frecuencia (último año): ~0.18 candidatos/día; ~0.13/día con entrada B.
- Limitaciones: velas diarias (en B no se sabe si el máximo fue antes o después de ponerse rojo → se cuenta como stop, conservador);
  universo listado hoy (faltan deslistadas); casos con split en el mismo mes excluidos (p. ej. DFNS jul-2026); la definición de "volumen
  creciente" exige subir en TODOS los días de la racha, y un día verde pequeño al inicio (DAIC 21-ago) la rompe.
**Conclusión:** el primer día rojo **mecánico** (con o sin la condición de volumen) ≈ 0R, igual que el "día siguiente al rojo" de la ronda
de setups. La ventaja que Edu obtiene en ese patrón (TGL, BMNR, DAIC) no está en el patrón diario en sí: vendría de la ejecución
intradía (dónde entra, cuánto aguanta, qué descarta) y de la selección discrecional — no medible con estos datos.

## Ronda 9 — ideas de las listas de Edu (29-sep-2026, `22_ronda9_edu.py`; pre-registro en HIPOTESIS_SELECCION.md)
**E1 — Overextended gap down** (≥ 2 días verdes, subida ≥ +100 %, el día D abre bajo el cierre de D-1; precio real ≥ $1):
| Setup | Periodo | n (corredores) | R por operación | R por corredor | WR | Gan. media | Pérd. media | PF |
|---|---|---|---|---|---|---|---|---|
| A: corto apertura, stop +30 % | DEV 2015-21 | 671 (596) | +0.07 | — (t 5.7) | 66 % | +0.37 | −0.49 | 1.43 |
| A | VAL 2022-26 | 1 521 (1 247) | **−0.06** | +0.01 (t 0.8) | 51 % | +0.42 | −0.56 | 0.79 |
| B (Edu): stop sobre el cierre de D-1 | DEV | 671 | +0.12 | (t 4.0) | 57 % | +1.11 | −1.19 | 1.24 |
| B | VAL | 1 521 | **−0.23** | (t −1.3) | 41 % | +1.31 | −1.27 | 0.70 |
| Comparación: abre SOBRE el cierre, A | DEV / VAL | 520 / 1 051 | +0.07 / −0.02 | | 63 % / 55 % | | | 1.28 / 0.94 |
- Funcionó en 2015-21 y **dejó de funcionar en 2022-26** (igual que otros setups diarios). Neto de locate 1 % + comisión: A −0.14R, B −0.41R (VAL).
- Abrir bajo el cierre NO es mejor que abrir sobre el cierre (HG3, t −1.6).
- Comprobado a mano un caso (LUCY 13-abr-2023: racha de 4 días verdes, +221 %, abre −10 %; A +0.07R, B −1.24R): cuadra.
**E2 — Historial de spikes** (gappers ≥ 50 %, precio ≥ $1; spikes del año anterior sin los 10 días previos):
| Grupo | Periodo | n | R | WR | Gan. media | Pérd. media | PF |
|---|---|---|---|---|---|---|---|
| Mayoría de spikes previos rojos | DEV / VAL | 36 / 48 | +0.14 / **−0.09** | 64 % / 52 % | +0.87 / +0.80 | −1.14 / −1.05 | 1.35 / 0.83 |
| Mayoría verdes | DEV / VAL | 593 / 1 296 | +0.13 / +0.01 | 65 % / 59 % | +0.77 / +0.75 | −1.07 / −1.05 | 1.35 / 1.01 |
| Sin spikes previos | DEV / VAL | 46 / 70 | −0.22 / +0.02 | | | | |
- El historial "cerró rojo" es raro (4 % de los casos) y **no mejora** el corto (HE2, t −0.6). Con "devolvió la mitad de la subida" tampoco (VAL −0.03 vs +0.01).
**Holm (VAL): ninguna validada** (HG3 t −1.60, HG2 −1.29, HG1 +0.79, HE2 −0.60).
Conclusión: los dos criterios de Edu medibles con datos diarios no dan ventaja por sí solos. Refuerza lo aprendido: la base viene del
tipo de catalizador (humo) y la munición; lo de Edu es lectura discrecional del precio y del volumen en el momento.

## Exploratorio (idea del usuario, 29-sep-2026, `23_ruptura_930.py`): ruptura temprana de la vela de las 9:30, solo cortos
Reglas: vela de 1 min de las 9:30 (O, máx., L); corto cuando una vela CIERRA bajo L (hasta 11:00); cubre cuando una vela cierra sobre O;
re-entra si vuelve a cerrar bajo L; tamaño constante; coste 0.5 % por intento. Sin el filtro discrecional del usuario (volumen, lectura).
Muestra: 1 min = 19 días (31-ago → 25-sep-2026), 27 días con ruptura en gaps ≥ 50 % y ≥ $1; 5 min (primera vela de 5 min) = 60 días, 75 casos.
1R = distancia de la entrada a O (mín. 2 %) — definición cambiada tras ver resultados (la inicial, L→O, infravaloraba el riesgo real:
en TURB la entrada fue 1.40 con L 1.48 y O 1.50).
| Datos | Tramo | Salida | n | R | Mediana | WR | Gan. media | Pérd. media | PF | Sin los 3 mejores días |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | gap ≥ 50 % | fin 10:30 | 26 | +0.77 | +0.68 | 58 % | +2.05 | −0.98 | 2.85 | |
| 1 min | gap ≥ 50 % | fin 16:00 | 27 | +1.12 | −0.26 | 44 % | +4.66 | −1.71 | 2.18 | **−0.22** |
| 5 min | gap ≥ 50 % | fin 10:30 | 69 | +0.11 | +0.09 | 58 % | +0.89 | −0.98 | 1.26 | |
| 5 min | gap ≥ 50 % | fin 16:00 | 75 | +0.21 | +0.06 | 52 % | +2.00 | −1.73 | 1.25 | **−0.14** |
| 1 min | gap 20-50 % | fin 16:00 | 50 | −0.64 | −1.13 | 36 % | +2.44 | −2.38 | 0.58 | |
| 5 min | gap 20-50 % | fin 16:00 | 113 | −0.18 | −0.65 | 39 % | +1.72 | −1.39 | 0.79 | |
Referencia mismos días (1 min, ≥ 50 %): corto a la apertura, stop +30 % = +0.04R (WR 65 %).
Lectura: en gaps ≥ 50 % sale positivo, pero **depende de 3 días** (SGRX, SSM, RDHL con +12 a +18R); sin ellos es negativo. Ningún t > 2.
En gaps 20-50 % pierde claramente. Colas: TURB (−10R, 17-sep) y GRML (−9R, 21-sep) por salir al cierre de vela muy por encima de O.
No validado; muestra pequeña y no separable en DEV/VAL. Para medirlo de verdad hacen falta más meses de datos de 1 min.
