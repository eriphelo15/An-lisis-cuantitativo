# Seguimiento de un short seller de referencia (Capelo Trading, transmisiones en YouTube)
Fuente: resúmenes de Gemini pedidos por el usuario (citas con marca de tiempo). Datos de mercado: Yahoo diario. Solo hechos verificables.

## Sesiones
| Fecha | Acciones (qué hizo) | Tipo según nuestro Radar | Locates citados | Resultado del día | Resultado del mes (según él) |
|---|---|---|---|---|---|
| 2026-09-23 | IPDN (quería, no pudo), VTGN (vigiló), IMCC (descartó: cara), BENF (descartó: sin acciones), BFRG (vigiló), HCTI (operó, enganchado), GCDT (operó, susto), DCOY (vigiló: warrants $3.25), MSS (locate) | BENF = A · VTGN = Vigilar (<$1) · DCOY/MSS/BFRG/HCTI = 20-50 % · GCDT = disparada en sesión · IMCC = día 3 · IPDN = +77 % (fuera del universo del estudio) | MSS $0.016/acción (0.8 % del precio) | +$340 (máx. +$800) | — |
| 2026-09-22 **after-hours** (Gemini lo fechó mal como 28-sep) | DCOY (corto: 'me hizo perder al principio, luego le entré bien'), LHSW (operó: 'ha aguantado el trade'), QM → probablemente **QNME** (operó), WHLR (vigiló), JAX (vigiló, símbolo no encontrado) | **DCOY, LHSW y QNME = nivel A** en nuestro Radar reconstruido del 22-sep (humo + gap ≥ 100 % + ≥ $1). Base mecánica: LHSW +0.97R, QNME +1.15R, DCOY −1.25R (subió +48 % antes de caer −40 %: el stop mecánico salta, su reentrada gana) · WHLR: se disparó al día siguiente | ninguno | +$125 (llegó a −$600) | **−$2 500 en septiembre** (a 22-sep) |

## Reglas que repite (citas)
- No paga locates de más del ~5 % del precio (23-sep, 3:18:21).
- Busca empresas que emiten acciones constantemente (dilución) (23-sep, 11:47).
- Entradas: techos y rechazos rápidos, VWAP, pérdida de mínimos, velocidad de la cinta (23-sep).
- Reconoce errores de añadir en la apertura y de mantener largos (22-sep).

## Notas por sesión
- **22-sep after-hours (16:00-20:00):** sus operaciones fueron DESPUÉS del cierre, no a la apertura. After-hours según Yahoo (5 min):
  DCOY subió hasta +32 % sobre el cierre ($3.10 → $4.10 a las 17:10) tras la corrección de su warrant inducement (18:14; anuncio original 12:50),
  y al día siguiente abrió en $4.40 y cerró en $3.85 → "me hizo perder al principio, luego le entré bien". LHSW cayó hasta −20 % y QNME −13 %
  en after-hours. WHLR (vigilado) subió +122 % en after-hours (18:40) y al día siguiente abrió +178 %.
  Nuestro Radar solo cubre el premarket; el after-hours es otra sesión que no medimos.
