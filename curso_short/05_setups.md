# Módulo 5 — Setups de corto medidos con datos (y la verdad incómoda)

> Aquí se mide cada setup "de libro" con datos reales y en **R** (1R = lo que arriesgas hasta el stop).
> La conclusión es importante y hay que decirla sin adornos: **los setups aplicados de forma mecánica casi no ganan.**
> La ventaja está en la selección (qué acción) y en la ejecución (cómo y cuándo), no en el nombre del patrón.

## 1. Cómo se midió
- **Intradía:** velas de 1 hora, ~2 años (oct-2024 → sep-2026), **3 518 gappers** (apertura ≥ +20 %) de 1 316 acciones.
- **Diario:** 2015-2026 para día 2 y *first red day*.
- Costes 1 % ida y vuelta. Si una vela toca el stop, se pierde (conservador).
- **Prueba de estrés:** el stop se ejecuta un 5 % más arriba (lo que pasa con halts y huecos al alza).
- Limitación: velas de 1 hora son gruesas. Los setups reales se ejecutan en 1-5 minutos; esto mide **la idea**, no tu ejecución.

## 2. Los setups y sus resultados (gaps ≥ 50 %)
| Setup | Regla medida | n | % ganadoras | R medio | Con halts (+5 %) |
|---|---|---|---|---|---|
| **A. Corto a la apertura** | Entrar a las 9:30, stop +30 %, salir al cierre | 1 030 | 58 % | **+0.08R** | +0.01R |
| … solo gaps ≥ 100 % | igual | 397 | 57 % | **+0.13R** | +0.05R |
| **B. Primera hora roja** | Si 9:30-10:30 cierra en rojo → corto 10:30, stop máximo +2 % | 694 | 53 % | −0.02R | −0.09R |
| … gaps ≥ 100 % | | 260 | 62 % | +0.05R | −0.01R |
| **C. Máximo fallido** | Si la 2ª hora no supera el máximo de la 1ª → corto 11:30 | 850 | 53 % | −0.01R | −0.06R |
| … gaps ≥ 100 % | | 327 | 59 % | +0.05R | +0.01R |
| **E. Fade de la tarde** | 13:30 bajo la apertura y bajo el VWAP → corto, stop máximo | 690 | 50 % | −0.01R | −0.02R |
| **F. Día 2** (diario 2015-26) | Corto a la apertura del día 2, stop = máximo del día 1 | 3 006 | 43-54 % | ≈ 0R en todas las épocas | — |
| **G. First red day** (diario) | 2 días subiendo ≥ 20 % y primer día rojo → corto al día siguiente | 1 650 | 52-55 % | ≈ 0R | — |

### Qué significa
1. **Ningún setup mecánico da una ventaja grande y estable.** Ganan más de la mitad de las veces, pero lo que ganan se compensa con lo que pierden.
2. **La única ventaja clara está en los extremos:** gaps de +100 % o más, corto temprano con stop amplio. Pero **los halts se comen casi toda la ventaja**.
3. **Esperar confirmación** (primera hora roja, máximo fallido) sube un poco el % de aciertos en gaps grandes, pero no mejora el resultado: el stop queda lejos (en el máximo) y la parte fácil de la caída ya pasó.
4. **Días de frenesí** (el float rota más de 10 veces en el día): el corto a la apertura pierde (−0.02R) → son los squeezes. Ojo: la rotación total del día no se conoce a las 9:30; en vivo se estima con el volumen del premarket y de los primeros minutos.

## 3. Entonces, ¿de dónde sale la ventaja de un short seller profesional?
De tres capas que se suman. Los setups son solo la tercera:
1. **Selección (lo hago yo con las fichas):** gap extremo + catalizador débil + **munición activa** (puede vender HOY) + sin perfil de squeeze.
   Descarta la mitad de los gappers que en la tabla de arriba "empatan".
2. **Contexto del día:** ¿día caliente de sector? ¿SSR? ¿halts al alza? ¿locates disponibles y a qué precio?
3. **Ejecución fina (tu trabajo, en 1-5 minutos):**
   - No entrar en la primera subida vertical: esperar el **primer máximo más bajo** (lower high) en 1-5 min.
   - Entrar en **rebotes que fallan** bajo un nivel (VWAP, máximo del premarket, número redondo), no persiguiendo caídas.
   - **Stop encima de la estructura** que invalida la idea (el último máximo), no un % fijo → R más pequeño y mejor relación.
   - **Salidas parciales** en soportes (mínimo del premarket, VWAP desde abajo, mitad del rango) y dejar correr el resto.
   - **Tamaño según el riesgo real** incluyendo el salto de un halt (Módulo 7).

Esta capa 3 **no se puede medir con velas de 1 hora**. Se mide con datos de 1 minuto (con empresas deslistadas incluidas)
o, mejor aún, con **tu propio diario de operaciones**. Por eso el diario es obligatorio desde el primer día en simulador.

## 4. Los setups de ejecución que vas a practicar (definiciones)
| Setup | Cuándo | Entrada | Stop | Objetivos |
|---|---|---|---|---|
| **1. Lower high en la apertura** | Gap extremo, primera subida se frena | Rotura del mínimo de la vela que hizo el máximo más bajo (1-2 min) | Encima del máximo más bajo | Mínimo del premarket / VWAP / mitad del rango |
| **2. Rechazo del VWAP** | La acción ya perdió el VWAP y rebota hacia él | Vela de rechazo en el VWAP (mecha arriba, cierre abajo) | Encima del VWAP + margen | Mínimo del día |
| **3. Fallo en el máximo del premarket** | Intenta superar el máximo del premarket y no puede | Rechazo en ese nivel con volumen | Encima del nivel | VWAP / apertura |
| **4. Rotura del soporte de media mañana** | Consolidación lateral bajo el VWAP | Rotura del mínimo del rango con volumen | Encima del rango | Proyección del rango / mínimo del día |
| **5. Día 2 con munición** | Día 1 cerró débil + la empresa puede vender (ficha) | Rebote fallido en el premarket o apertura | Encima del máximo del rebote | Cierre del día 1 − x % / VWAP |

Con SSR activo, los setups 2 y 3 (entradas en rebotes) son los naturales: vendes cuando sube, no cuando cae.

## 5. El diario de operaciones (tu fuente de datos)
Por cada operación, en simulador o real, anota:
- Ticker, fecha, gap %, catalizador (clase), veredicto de la ficha (¿puede vender hoy?), SSR sí/no, halts previos.
- Setup (1-5), hora de entrada, precio de entrada, stop, tamaño, coste del locate.
- Salidas (parciales), resultado en $ y en **R**, y una captura del gráfico.
- ¿Seguiste el plan? (sí/no) y una línea de lo aprendido.

Con 50-100 operaciones sabremos **qué setup te funciona a ti**, con tus reglas y tu ejecución. Esa estadística vale más que cualquier backtest.

## 6. Ejercicios
1. Abre en el simulador (TradingView "Replay" sirve) 5 gappers de +100 % de este mes, en velas de 1 minuto. Para cada uno marca dónde estaría el setup 1 (lower high) y el setup 2 (rechazo del VWAP). Anota entrada, stop y dónde habrías cubierto.
2. Calcula el R de cada una: (entrada − salida) ÷ (stop − entrada).
3. Compara: ¿en cuántas el máximo del día llegó antes de tu entrada? ¿Cuántas te habrían sacado por el stop antes de caer?

En el Módulo 6 entramos en la ejecución: Level 2, cinta, órdenes, qué hacer en un halt y cómo cubrir con liquidez.

---
Scripts: `smallcaps/06_setups.py` (setups), `smallcaps/07_filtros.py` (filtros por capitalización y rotación). Resultados en `smallcaps/res_06_*.csv`.
