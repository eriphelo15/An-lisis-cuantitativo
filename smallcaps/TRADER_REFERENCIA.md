# Seguimiento de un short seller de referencia (Capelo Trading, transmisiones en YouTube)
Fuente: resúmenes de Gemini pedidos por el usuario (citas con marca de tiempo). Datos de mercado: Yahoo diario. Solo hechos verificables.

## Sesiones
| Fecha | Acciones (qué hizo) | Tipo según nuestro Radar | Locates citados | Resultado del día | Resultado del mes (según él) |
|---|---|---|---|---|---|
| 2026-09-23 | IPDN (quería, no pudo), VTGN (vigiló), IMCC (descartó: cara), BENF (descartó: sin acciones), BFRG (vigiló), HCTI (operó, enganchado), GCDT (operó, susto), DCOY (vigiló: warrants $3.25), MSS (locate) | BENF = A · VTGN = Vigilar (<$1) · DCOY/MSS/BFRG/HCTI = 20-50 % · GCDT = disparada en sesión · IMCC = día 3 · IPDN = +77 % (fuera del universo del estudio) | MSS $0.016/acción (0.8 % del precio) | +$340 (máx. +$800) | — |
| 2026-09-22 **after-hours** (Gemini lo fechó mal como 28-sep) | DCOY (corto: 'me hizo perder al principio, luego le entré bien'), LHSW (operó: 'ha aguantado el trade'), QM → probablemente **QNME** (operó), WHLR (vigiló), JAX (vigiló, símbolo no encontrado) | **DCOY, LHSW y QNME = nivel A** en nuestro Radar reconstruido del 22-sep (humo + gap ≥ 100 % + ≥ $1). Base mecánica: LHSW +0.97R, QNME +1.15R, DCOY −1.25R (subió +48 % antes de caer −40 %: el stop mecánico salta, su reentrada gana) · WHLR: se disparó al día siguiente | ninguno | +$125 (llegó a −$600) | **−$2 500 en septiembre** (a 22-sep) |
| 2026-07-15 (sesión sin especificar) | TGHL (vigiló: 'no he podido, era muy cara'), CUST → probablemente **KUST** (vigiló: 'muy cara'), BJDX (operó: 'se está reanimando'), RNA → probablemente **ERNA** (vigiló: 'flotante bajo pero mucha dilución') | Radar 15-jul reconstruido: B = ELVA (Amazon, sin cifra); Vigilar = VIVS ($5 M de Eli Lilly = contrato real); 20-50 %: KUST (sin noticia, +48 %), ERNA (preclínico = humo, +40 %), TGHL (sin noticia, < $1) · BJDX: sin gap (+2 %) | '12 de locate' en el día (~$12 en total); Gemini leyó '$5 por acción en CUST a $18' → no cuadra con ninguna acción (KUST ~$1.5): dato dudoso | ~$200 a mitad de sesión; '330 más lo que saquen' al final | — |

## Reglas que repite (citas)
- 'La pérdida máxima va a ser la prima, nunca más' (15-jul, 12:56).
- Reconoce que pierde cuando las acciones rompen el máximo del premarket con fuerza (15-jul, 4:52:20).
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
