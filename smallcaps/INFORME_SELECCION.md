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
