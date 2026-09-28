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
