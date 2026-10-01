# Memoria del proyecto (leer al inicio de cada sesión)

## Quién es el usuario y cómo trabajar con él
- Trader hispanohablante. Opera futuros (NQ, a veces ES/GC) en cuentas de fondeo (Tradeify) y se está especializando
  como **short seller de small caps de EE. UU.** Quiere ser de los mejores; alta tolerancia al riesgo, pero valora
  entender bien los riesgos. No quiere que lo limiten ni le pidan conformarse con poco.
- **Responder siempre en español simple, sin jerga**; explicar paso a paso y con ejemplos reales. Es nuevo en SEC/EDGAR.
- Los documentos de la SEC están en inglés y le cuesta traducirlos sin cruzar datos (dólares vs. acciones).
  **Método acordado:** Claude lee EDGAR y entrega cada dato con **la frase original en inglés + traducción + la cifra
  resaltada y su unidad**; el usuario entiende, verifica con Ctrl+F y decide.
- **Reparto de trabajo acordado para operar:** Claude hace el trabajo de campo (escáner, catalizadores, dilución,
  historial, niveles, clasificación); el usuario hace la ejecución sobre el gráfico y confirma locates en su bróker.
- **No crear rutinas, alertas, automatizaciones ni herramientas que no haya pedido explícitamente.** Si pregunta
  "¿se puede…?", responder y ofrecer; no ejecutar. (Ya pasó una vez con unas rutinas y pidió borrarlas.)
- Ser honesto con los datos: si algo no funciona, decirlo; distinguir lo validado de lo decidido a posteriori.
- **Precisión quirúrgica (exigencia del usuario, 28-sep-2026):** nada se entrega sin validarlo de principio a fin. Abrir y leer cada fuente
  (no solo titulares), comprobar cada cifra y su unidad, contrastar con una segunda fuente cuando exista, y revisar el resultado final antes
  de mostrarlo. Si algo no se pudo verificar, decirlo explícitamente. Aplica a todas las áreas (listas, estudios, SEC, código).
- **Principio del usuario: toda idea o criterio se valida con datos antes de usarlo.** Aunque tenga lógica, no se da por buena sin medirla.
- El usuario tiene mucha experiencia ejecutando (futuros): su trabajo es ejecutar el mejor setup según la acción del precio; el trabajo fino de selección es de Claude.
- **Operará acciones en bróker normal, sin fondeo.** Cuenta prevista: ~$2 000. **Reside en República Dominicana.** Bróker previsto: TradeZero International (mín. $500, locates integrados) para cortos; IBKR secundario (mín. margen $2 000); Cobra/CenterPoint cuando la cuenta ≥ $30 000. Política de riesgo del usuario: 1 % base; hasta 5 % cuando la ventaja estadística esté validada. Referencia medida (Kelly sobre R reales del setup A, ajustados): ventaja +0.05R → Kelly 4 %; +0.10R → 8 %; +0.20R → 16.5 % (5 % ≈ 1/3 Kelly, aún 78 % prob. de caída >30 %); +0.30R → 25 %. Regla acordada: 5 % solo con ventaja validada ≥ ~+0.20R y ≥ 50-100 operaciones; la cola real (halts) puede ser peor que la de la muestra.
- **Principio del usuario (30-sep): la base mecánica NO valida nada.** Es una regla fija sin ejecución; en vivo solo da más o menos peso a una
  tesis. Lo que ya tiene valor en el trabajo de campo está definido (filtro + puntuación validados en el histórico). Lo ÚNICO que certifica es
  el diario: selección de Claude + ejecución del usuario + cierre real de cada operación → esperanza/WR/PF reales. Presentar la base como
  "referencia", nunca como validación; cuando haya operaciones en el diario, esas son las cifras principales.
- **Formato de resultados:** el usuario piensa en WR, ganancia media, pérdida media y PF. Dar SIEMPRE los resultados en ambos formatos: esperanza en R + WR + ganancia media (R) + pérdida media (R) + PF (y en $ para su cuenta cuando aplique). Equivalencia: +0.20R ≈ PF 1.4-1.5.
- Commits y push en la rama `claude/analisis-cuantitativo-45j7qe`. Sin PR salvo que lo pida.

## Estado actual
- **Curso de short seller** en `curso_short/` (programa en `00_PROGRAMA.md`). Hechos: módulos 1 (economía de la dilución),
  1b (guía EDGAR + lecciones), 2 (mecánica del corto), 3 (leer la SEC: munición y baby shelf), 4 (anatomía del pump).
  Módulo 5 (setups medidos) y Módulo 6 (ejecución condensada: diferencias vs futuros) hechos.
  Módulo 7 (riesgo, con colas y Monte Carlo) hecho.
  Módulo 8 (infraestructura) hecho.
  Validación de criterios de selección: rondas 1 y 2b (contenido del catalizador) hechas (ver lecciones). Ronda 3 (ejecución dentro de la selección) hecha. Ronda 4 (día de tema) hecha: no es filtro.
  **Sistema de lista diaria HECHO (pedido por el usuario, 28-sep-2026): "Radar de Cortos".** Página https://claude.ai/artifact/LXxGL8Y1LVHDLnuUo21zCo
  (base de datos: `listas/AAAA-MM-DD` = lista del día; `diario/FECHA_TICKER` = diario del usuario, no tocar). Generador `herramientas/lista_diaria.py`
  (escanear → Claude clasifica en `_clasif.json` → finalizar → resultados al día siguiente; `--replay` para días pasados). Rutina programada
  (pedida por el usuario) `trig_01LxzygdMnVhjKcap2MrESi5`: L-V 8:17 Nueva York, se ejecuta en ESTA sesión (session_01Y3DyUXFtmwsaxpZC7KkFLE) siguiendo `listas/RUTINA.md`. Al terminar envía notificación push con el resumen (pedida y probada el 28-sep). Una sesión nueva por disparo NO sirve: arranca sin repositorio ni base de datos de la página (probado el 28-sep).
  **Desde el 30-sep (pedido por el usuario: "algo verdaderamente profesional"): SCREENER SIN LETRAS.** Letras A/B solo para estrategias de
  ejecución con backtest completo (ninguna aún). La página es una tabla ordenada por la **tesis 0-100** (ronda 12, `smallcaps/puntuacion_pesos.json`;
  tercios Alta/Media/Baja; la ventaja medida está en tesis alta + gap ≥ 50 %: VAL +0.26R PF 1.86; en 20-50 % no separa) + **riesgo estructural**
  aparte (Normal/Alto/Extremo: acciones < 1 M / < 5 M, rotación premarket > 3× / > 1×, pocas acciones sin munición; NO validado, sirve para el tamaño)
  + PMH (Yahoo 1 min), caja/quema/autonomía (XBRL, informativo, verificado a mano en CNTB) y el texto del 8-K legible en la ficha (clic en la fila).
  Descartadas ocultas con su motivo (C, R, F, S, 424B hoy, precio < $1, split). Listas 21-30 sep rehechas al formato nuevo (`version: 2`) con sus precios.
  Desde el 29-sep (pedido por el usuario): trabajo de campo completo (catalizador + munición + noticias) también para los gappers de 20-50 %,
  (desde el 30-sep van en la misma tabla del screener). `escanear --corte HH:MM` rehace un día ya abierto; `finalizar --sin_actualizar` rehace una lista publicada conservando sus precios, gap y premarket (corregido 1-oct: antes los cambiaba; caso de oro 22).
  **Reparto acordado:** el Radar entrega SOLO selección (SEC, catalizador, munición, estadística de base). Sin plan de ejecución, stop ni tamaño:
  la ejecución es discrecional del usuario. El análisis de ejecución/estrategias sigue, pero en conversaciones de formación, no en la lista diaria.
  Medido en la ronda 6 (sin 8-K ≈ 0R); casos de prueba del caso "sube sin ninguna noticia" (días de prueba, revisados a mano: BTTC −1.25R, VEEE −1.25R, WHLR −1.25R, WETO +0.73R, SKYE +1.35R; GRML NO era "sin noticia": noticia de tema Groenlandia).
  Auditoría obligatoria antes de publicar (RUTINA.md paso 5b + control automático en `finalizar`, que bloquea la lista si hay errores).
  Lector de noticias corregido (28-sep): cortaba la tabla de Finviz a 200 000 caracteres y devolvía solo las 8 noticias más recientes
  → en días pasados se perdían noticias; ahora filtra por el corte (`noticias(sym, desde, hasta)`). Revisados los 'sin noticia' de los días de prueba: se mantienen.
  Errores corregidos el 28-sep al comparar con TradingView/Cowork: gap medido con el precio del momento (no la apertura), ADS extranjeras excluidas (NAMI), GYGY 'sin noticia' con un artículo sin abrir, y en los días de prueba HHS (compra a $5.00 = Nunca) y SURG (resultados = NO) sin clasificar.
  Práctica de ejecución en DCOY, LHSW, INLF, GRML, GLND hecha por el usuario. Conclusión del usuario (compartida): el indicador captura bien las caídas cuando la acción 'valida la teoría' y falla cuando no; **lo decisivo es la selección fuera del gráfico**. Ejercicios del módulo 4: WHLR (usuario) y BENF (Claude como ejemplo) hechos.
- **Herramientas externas evaluadas (28-sep-2026):** DilutionTracker (el usuario la tiene) = auditor independiente de la munición + float
  verificado; comparar las A/B del Radar con ella (sin API, CAPTCHA). Momo Screener (gratis) = solo pantalla del usuario (halts, aceleración);
  precios pueden ir retrasados. Yahoo = ya es fuente del Radar (float poco fiable). Webull: no disponible en R. Dominicana. Flash Research:
  sin catalizador, sin dilución, sin exportar; Premium $89.95/mes → ahora no. SageTrader: corto de difíciles de prestar solo en Pro
  ($145/mes + $3 000 mínimo) → ahora no; buen router de locates para cuenta ≥ ~$10 000. FINRA: PDT baja a $2 000 desde el 4-jun-2026.
  Con riesgo 1 % los requisitos de garantía en corto ($5 o $2.50 por acción) no limitan.
- **TradeZero International (verificado en tradezero.com/pricing-and-fees, 28-sep-2026):** mín. $500; no acepta EE. UU./Canadá/Bahamas (R. Dominicana
  no excluida). Gratis solo órdenes límite no ejecutables en acciones ≥ $1; si no, $0.005/acción, mín. $0.49 y máx. $7.95 por orden; acciones < $1 siempre de pago.
  ZeroPro $59/mes (TZ1, ZeroFree y móvil gratis). Locator en todas las plataformas (cuenta 'advanced' aprobada); locates Single Use más baratos y se
  pueden devolver si no se usan. Máx. apalancamiento 2:1 al cierre. Con riesgo 1 % ($20) la comisión ida y vuelta ≈ 0.05-0.07R y el locate
  que anula la ventaja (+0.22R) ≈ 7 % del precio por acción → registrar el coste real del locate de cada operación (diario de la página).
  Tabla oficial (PDF 1-ago-2026) confirma comisiones; 'profesional' solo cambia datos ($250/mes), no comisiones. Gratis: límite no ejecutable,
  > $1 y ≥ 100 acciones. Locates se cotizan en CENTAVOS por acción (ejemplos: $0.02 reseña jun-2026; $0.08 ejemplo de TradeZero) → pesan mucho
  más en acciones < $1 (coste en R = locate ÷ (0.375 × precio): $0.02 en $0.38 = 0.14R; en $2.44 = 0.02R). Pendiente confirmar si el locate
  mínimo es de 100 acciones.
- **Massive (antes Polygon), añadido como herramienta el 29-sep (pedido del usuario):** credencial en el entorno (api.polygon.io / api.massive.com).
  Plan gratis: cierres diarios de TODO el mercado (1 consulta), velas de 1 min sin ajustar desde 29-sep-2024 hasta ayer, 5 consultas/min.
  NO da datos del día en curso ni snapshot/gainers (Starter $29/mes: 15 min de retraso). En el Radar: segunda fuente del cierre de ayer
  (`massive_cierres` en lista_diaria.py) + red extra de candidatos + control Yahoo vs Massive (> 2 % = error).
- Herramienta de dilución hecha: `herramientas/ficha_dilucion.py TICKER` (SEC EDGAR + Yahoo; ~7 s). Fichas en `fichas/`.
- Futuro (cuando termine la formación): construir un sistema propio tipo "Flash Research" con estadísticas propias.
  No construirlo antes de que el usuario lo pida.
- El plan de fondeo en NQ está cerrado y entendido (pullback VI con salida parcial + drift pre-FOMC). Cripto: cerrado
  (ventajas solo en catalizadores de Binance; no encaja con su perfil de mercados profesionales).

## Lecciones aprendidas (añadir cada vez que aprendamos algo)
### Lectura de la SEC
1. En un 10-Q del 2º/3º trimestre el flujo de caja es de 6/9 meses: dividir por los meses correctos.
2. Todos los números del flujo de caja de la misma tabla (no mezclar con la tabla de patrimonio, que es trimestral).
3. `Restricted cash` no cuenta como caja usable (APUS: $8 M restringidos, $278 k usables → ~6 días de runway).
4. Pérdida neta ≠ quema de caja: usar *Net cash used in operating activities*.
5. 424B3 "Prospectus Supplement" = anexo; el precio está en el 424B4/424B5 original; el anexo suele traer un 8-K pegado.
6. Warrant inducement = precio de ejercicio rebajado + warrants nuevos para ejercer YA (GIPR, 18-sep-2026, día del gap).
7. Buscar la tabla de valores anti-dilutivos (preferentes convertibles, warrants, opciones, acciones comprometidas).
8. Convertible con acciones "not determinable" o "X% of the lowest…" = precio variable = tóxica.
9. Warrants: comparar precio de ejercicio (ajustado por contra-splits) con el precio actual.
10. Catalizador con nota de prensa pero sin 8-K = probablemente inmaterial ("PR de humo").
11. Baby shelf (S-3 I.B.6): todo en **dólares**: acciones de no afiliados × cierre máximo de 60 días = public float; límite = 1/3 al año − lo ya vendido. Un pump sube el límite.
12. La dilución no siempre viene de quemar caja: WHLR (REIT que genera caja) diluye por **intercambios de preferentes por comunes** y hace **contra-splits encadenados** (1:5, 1:4, 1:9 en 2 meses = 1:180).
13. Form 4 = informe de operaciones de insiders (directores / >10 %), no el acuerdo en sí.
14. Verificar siempre lo que diga Gemini u otras IA: en WHLR exageró la rotación del float ("cientos de veces" vs. ~77-154).
15. Catalizador en 8-K Item 7.01 (nota de prensa "furnished") con verbos "seeks / pursuing / proposed" = plan, no acuerdo firmado; un acuerdo firmado va en Item 1.01 (BENF 23-sep-2026).
16. ELOC / SEPA (p. ej. Yorkville): la empresa puede vender acciones al inversor en cualquier momento, que las revende al mercado → munición continua; suele venir con notas convertibles del mismo inversor (BENF: SEPA de hasta $100 M + notas convertibles de $4 M).
17. Los datos gratuitos de Yahoo pueden no coincidir entre velas de 5 min y cierre diario en small caps muy volátiles: usar el cierre oficial para conclusiones.
18. El catalizador del gap es lo publicado desde el cierre anterior. Una financiación o noticia de ayer es munición/contexto, no el motivo:
    clasificar N (LGHL 30-sep: 6-K de la convertible del 29-sep 5:15; detectado al comparar con las posiciones de Edu; MSGY y DLXY igual).
    Control automático en `auditar` (ERROR si tipo ≠ N sin ningún documento ni noticia en la ventana).
19. **Revisión completa del 30-sep (pedida por el usuario), errores encontrados y corregidos:** (a) puntuación en vivo hasta 4.8 puntos distinta
    del histórico (pesos redondeados + empates) → pesos exactos en `puntuacion_pesos.json`, comprobado caso a caso: 1 222/1 222 iguales;
    (b) 'diluidor en serie' contaba solo 424B4/5 y el histórico todas las 424B → corregido (GYGY 28-sep pasa de Alta a Media);
    (c) el anexo EX-99 no se leía si el archivo tenía un nombre raro (CNTB 'a991.htm') → se busca por su tipo en el índice de la SEC;
    (d) 'warrants' incluía precios de OPCIONES de empleados (CNTB $2.14, MSS, CLRO $35.33) → solo frases con 'warrant';
    (e) antes de abrir, sin volumen premarket se usaba el volumen de AYER (rotación falsa) → solo preMarketVolume;
    (f) tickers nuevos sin CIK (FFR = antes AIXC) → búsqueda de texto de EDGAR ("Nasdaq: FFR");
    (g) el rendimiento en vivo se agrupaba con el gap de las 9:05 y el histórico usa el de la APERTURA (BKYI +71 % → +105 %) → resultados
    guardan gap/tesis de la apertura; (h) el texto de la rutina automática aún pedía letras → actualizado; (i) la descarga de Massive
    muere con cada reinicio del contenedor → paso 1b de RUTINA.md. Verificado: resultados guardados = Massive en 30/30 casos.

20. **Contraste con David Veprek (@veptrader) en CNTB 30-sep: él vio 4 cosas que nosotros no** (verificado en la SEC): (a) el secundario clave
    (función pulmonar día 7) NO significativo, escondido en la presentación EX-99.2; (b) el 15-sep (asma) cayó −32 % y esa medida era el
    "proposed primary endpoint for Phase 3"; (c) shelf F-3 de $300 M con **ATM de $150 M con Cantor sin usar** (el Radar decía "sin ATM":
    solo miraba el 10-Q); (d) caja a HOY ≈ 2.9 meses (mostrábamos 5.9 a la fecha del informe). Nosotros vimos que el F-3 de may-2026 es
    REVENTA de 6.13 M acciones (que antes contábamos como shelf de la empresa). Corregido el 1-oct: shelves empresa/reventa con importes,
    ATM y agente; ELOC dentro de reventas (FFR: 55 M "VWAP Shares"); reventas ajustadas por contra-splits (VBIO); todos los EX-99 + frases
    negativas automáticas; historial de catalizadores 120 días con reacción; caja a hoy; universo con 2.ª fuente SEC (nasdaqtrader nos
    bloqueó el 30-sep por la noche).
21. **Sistema anti-errores (1-oct, pedido por el usuario):** (1) `tests/casos_oro.py` = cada error real es una prueba permanente; la rutina
    no sigue si falla (paso 1c). (2) Verificador independiente (`listas/VERIFICADOR.md`, paso 5c): agente nuevo y ciego rehace el trabajo
    de campo de cada acción con gap ≥ 50 % o tesis alta; las diferencias se resuelven antes de publicar; `finalizar` bloquea sin él.
    (3) Contraste externo con otros traders → casos de oro nuevos. (4) Nunca decir "todo revisado": decir qué se comprobó y qué no.
    Causa raíz de los fallos: la revisión del 30-sep comprobó el código contra su propia intención y contra el histórico, NO la cobertura
    del análisis frente a un experto; y quien revisa era quien construyó (mismos puntos ciegos).

22. **Primera prueba del verificador independiente (CNTB 30-sep, a ciegas, 4 min):** encontró los 4 puntos de Veprek y más (colocación
    privada a $3.25, baby shelf I.B.5, la empresa dice caja para "at least one year", 81 % del titular = 77 % a 28 días exactos) y destapó
    un error grave nuestro: **el JSON de submissions de la SEC da la hora de NY con una "Z" falsa en las presentaciones del mismo día**
    (CNTB 8-K: JSON 07:05Z, oficial 07:05 NY; muestra 5/5 mismo día mal, 49/49 antiguas bien). El Radar ponía esas horas 4 h antes.
    Corregido: para los últimos 3 días se usa la hora oficial de la cabecera (`hora_oficial`). Los estudios históricos NO están afectados
    (datos bajados semanas después, ya corregidos por la SEC). En las listas 28-30 sep: COLA contó un 8-K de las 9:21 (ya descartada);
    ningún catalizador perdido. El verificador también se equivocó en una hora (al revés) → regla de horas en VERIFICADOR.md.

### Mercado y datos propios
- Gappers >100 %: el día 1 cierra bajo su apertura el 76 %; el día 2 supera el máximo del día 1 solo el 11 %; corto apertura día 1 → cierre día 2 gana el 80 % (mediana +29 %), pero en el peor 10 % hay subidas de +117 % en contra.
- Día típico (gap ≥50 %, velas 5 min): máximo del día antes de las 10:00 el 60 %, antes de las 11:00 el 78 %; subida mediana apertura→máximo +18 % (p90 +107 %); caída mediana desde el máximo −41 %; 72 % del volumen en la primera hora.
- Dilución (SEC): gappers multiplican sus acciones ×1.7 en 12 meses (×2.7 en gaps >100 %; ×2.7 en 2023-26); 40 % hacen contra-split ese año.
- Corto en gappers >100 % (datos diarios 2015-26): +4.6 % a +7.5 % por operación con stop 30 %, pero los halts que ejecutan el stop más arriba pueden anular la ventaja.
- Perfil de squeeze: float diminuto + sin munición activa (APUS) → la subida puede seguir días.
- Setups mecánicos (velas 1 h, 3 518 gappers oct-2024→sep-2026; diario 2015-26): casi todos ≈ 0R. Solo el corto temprano en gaps ≥100 % con stop amplio da +0.13R, y con 5 % de deslizamiento por halts baja a +0.05R. Primera hora roja, máximo fallido, fade de tarde, día 2 y first red day ≈ 0R. Días con rotación >10× → el corto a la apertura pierde.
- Indicador **Reversal** del usuario (near 2, long 20) usado en corto con reciclaje (corto en señal de venta, cubrir en la de compra, stop sobre el máximo barrido +0.5 %, coste 1 %): gappers de sep-2026 en 1 min (130 días) y 60 días en 5 min → elige mejores puntos que el azar (35 % vs 26 % ganadoras; gap ≥50 % en 1 min: −0.07R vs −0.25R) pero **no tiene ventaja propia tras costes** (≈ 0R o negativo). Filtros VWAP: muestras pequeñas, nada concluyente. Útil solo como gatillo de timing dentro de acciones bien seleccionadas; pendiente validar con más datos. `smallcaps/08_reversal_smallcaps.py`.
- GRML (21-sep-2026): 5 señales de venta del Reversal, 2 ganadoras y 3 stops; subió +76 % desde las 9:55 pese a tener munición (shelf/ATM/warrants). Precio siempre sobre un VWAP ascendente + mínimos crecientes + **día de tema** (GLND 'Greenland' +152 % el mismo día). Hipótesis medidas después: (a) bajo VWAP como filtro de entrada → no validado (ronda 3); (b) 'día de tema' = no shortear → no validado, al revés (ronda 4); (c) munición activa no basta por sí sola → el catalizador humo pesa más (ronda 2b).
- Colas (8 604 gappers): en gaps ≥100 % la subida máxima desde la apertura supera +100 % el 9.7 % de las veces en el día (12.5 % en 2 días); p99 +319 %. Monte Carlo con setup A (+0.05R): riesgo 1 %/op → caída típica 13 %; 5 %/op → 61 % de prob. de caer >50 %; 10 %/op → pierde aunque la estrategia gane. `smallcaps/09_riesgo.py`.
- **Validación de selección (8 604 gappers, EDGAR a la hora exacta, DEV 2015-21/VAL 2022-26; `smallcaps/INFORME_SELECCION.md`):** VALIDADOS: venta 424B en 90 días (dif. +0.136R VAL, t 5.7; DEV +0.06), shelf S-3 (+0.072R, t 3.2), 8-K solo nota de prensa vs acuerdo 1.01 (+0.151R, t 2.7). NO validados: sin 8-K, contra-split/aviso, diluidor en serie, día de tema por SIC, combinación A. Capitalización < $30 M = PEOR para el corto (más squeezes) → **ARTEFACTO, retirado en la ronda 5**. Mejor combinación (exploratoria): gap ≥50 % + venta 424B 90 d + cap ≥ $30 M → VAL +0.095R (50-100 %, PF 1.24) y +0.119R (≥100 %, PF 1.25) con setup A mecánico. Aún < +0.20R. Pendiente: definir 'día de tema' por palabras clave; volumen premarket/float (datos de pago).
- **Contenido del catalizador (ronda 2b, 3 000 notas clasificadas a mano y a ciegas; `smallcaps/INFORME_SELECCION.md`):** VALIDADO: gap por **humo/cosmético** (LOI, MOU, no vinculante, alianza sin cifra, cifras 'hasta', patentes, preclínico, giros IA/cripto, recompras simbólicas) → VAL +0.145R, WR 66 %, PF 1.46 (DEV +0.10R); resto −0.08R; t 4.5. Humo + gap ≥50 % → VAL +0.22R, PF 1.63 (DEV +0.15R); humo + gap ≥100 % → +0.40R, PF 2.3 (exploratorio, n 73). Resultados (PF 0.61), financiación (0.72) y avisos de bolsa (0.64) = malos para el corto; compra en efectivo = no shortear nunca. Contrato real/FDA: buenos en 2015-21, ≈0R en 2022-26.
- **Ejecución dentro de la selección (ronda 3, velas 1 h, oct-2023→sep-2026, 222 humo):** en humo el corto a la apertura (stop +30 %) da VAL +0.22R, PF 1.76 (DEV +0.14R). Esperar debilidad (a las 11:30 bajo VWAP) es PEOR: −0.38R por operación (t −5.5, igual en DEV) → la caída ocurre pronto. 1ª hora roja y bajo VWAP como filtros: no validados. Exploratorio: salir a las 11:30 si sigue sobre VWAP → +0.25R, PF 1.99. Reversal/1-5 min: sin muestra suficiente (8/24 casos).
- **Día de tema (ronda 4, palabras raras del nombre + lista de temas en nombre/catalizador):** hipótesis 'no shortear en día de tema' NO validada; en VAL 2022-26 fue al revés: día de tema +0.30R, WR 72 %, PF 2.06 (119 casos, 87 días) vs día normal +0.01R (t −3.2); DEV sin muestra (5). IA +0.45R, cripto +0.17R, espacio +0.29R, drones −0.34R (7). Líder vs seguidor: sin diferencia. GRML (líder, −1.25R) fue la excepción, no la regla. El tema NO es filtro.
- **Ronda 5 (28-sep-2026, `smallcaps/18_precio_real.py`): los precios de Yahoo están ajustados por splits posteriores** (precio mediano
  "ajustado" $16 vs real $2.72). R no cambia, pero sí todo criterio en dólares. **La 'cap < $30 M = peor' era un artefacto → NO se confirma**
  con la capitalización corregida (aviso retirado del Radar). Humo gap ≥ 50 %: ventaja bruta igual en < $1 (+0.26R VAL) y ≥ $1 (+0.21R); con
  locate $0.02 + comisión: < $1 −0.14R, ≥ $1 +0.13R (no validado, n 40, pero aritmético). Nivel A vs B no validado (424B dentro del humo
  va al revés en DEV). Rotación > 10× se mantiene con datos corregidos. Decidido por el usuario: niveles A/B nuevos y < $1 a Vigilar.
- **Ronda 6 (`smallcaps/19_mas_oportunidades.py`):** humo gap 20-50 % (≥ $1) mejor que el resto de su tramo (VAL t 3.1) pero base propia
  pequeña (+0.02R DEV / +0.09R VAL, PF 1.35) ≈ nivel B; gap ≥ 50 % sin 8-K ≈ 0R VAL; día 2 del humo ≈ 0 / −0.05R. Ninguna añade base validada. El usuario decidió dejarlas como están (humo 20-50 % sigue en 'Vigilar 20-50 %').
  Frecuencia (último año, ≥ $1): A ~0.2/día (≈1/semana), B ~0.3/día, humo 20-50 % ~0.4/día.
- **Ronda 7 (`smallcaps/20_humo_20_50.py`):** subgrupos del humo 20-50 % (424B, S-3, solo nota de prensa): ninguno validado. El más
  prometedor, humo 20-50 % + shelf S-3: +0.05R DEV / +0.15R VAL (PF 1.60, t 1.75) → seguir en vivo, no operable por ahora.
- **Ronda 8 (`smallcaps/21_primer_dia_rojo.py`): "primer día rojo" de Edu/Hamlin corto el MISMO día** (≥ 2 días verdes, +100 %, volumen
  creciente, D abre verde): A (apertura) DEV +0.03R / VAL −0.02R; B (green to red) DEV +0.07R / VAL −0.01R; volumen creciente NO mejora.
  No validado; con locate 1 % + comisión, negativo. Su ventaja en ese patrón sería ejecución/selección discrecional, no el patrón diario.
- **Edu Trades (33 directos, `smallcaps/referencias/EDUTRADES.md`):** WR 73-75 % con R/B < 1; grandes pérdidas por halts (STAK −$100 000).
  Regla de locates: < 1 % del precio casi siempre compra, > 5 % nunca; coste anual 10-20 % de sus ganancias. Varios brókers con distintas
  cámaras de compensación = más locates. Critica a TradeZero (sin motivo técnico claro; tiene afiliación con Sage).
- **Edu, listas de YouTube (Patrones/Aprendizaje/Trades, 51 vídeos 2018-23; `EDUTRADES.md`):** confirma ciclo pump-dump, 1.ª hora, rotación = peligro (su umbral ≈ 1×, el nuestro medido > 10×), dilución como munición. Sus setups diarios ya dan ≈ 0R (ronda 8). Hipótesis propuestas: E1-E5. **Ronda 9 (`smallcaps/22_ronda9_edu.py`, aprobada y medida 29-sep):** E1 overextended gap down: A DEV +0.07R / VAL −0.06R (PF 0.79), B (stop sobre el cierre anterior) DEV +0.12R / VAL −0.23R; no mejor que abrir sobre el cierre. E2 historial de spikes rojos: raro (4 %) y sin mejora (VAL −0.09R vs +0.01R). Ninguna validada. Quedan sin medir E3 (escalones de rotación), E4 (precio sobre colocación), E5 (instituciones).
- **Ruptura de la vela de 1 min de las 9:30, solo cortos (idea del usuario, 29-sep, `smallcaps/23_ruptura_930.py`, EXPLORATORIO):** gap ≥ 50 %: 1 min (27 días) +1.12R, WR 44 %, PF 2.18 pero −0.22R sin los 3 mejores días; 5 min (75) +0.21R, −0.14R sin los 3 mejores; gap 20-50 % pierde (−0.64R / −0.18R). Colas de −9/−10R (TURB, GRML). No validado: faltan meses de datos de 1 min.
  Reglas reales del usuario (1 solo intento por acción, entrada hasta 11:00, todo fuera a las 11:30; `23b_ruptura_930_usuario.py`): gap ≥ 50 % 1 min (27) +0.31R, WR 44 %, PF 1.38 (−0.57R sin los 3 mejores); 5 min (75) +0.14R, WR 55 %, PF 1.26 (−0.07R); gap 20-50 % negativo en ambos (−0.26R / −0.21R). Día 28-sep (Radar): B +3.15R, todo +8.37R. Salir por cierre de vela puede costar > 1R (MEDS −2R).
  **Seguimiento en vivo (aprobado 29-sep; RETIRADO el 1-oct):** `herramientas/ruptura_930.py` guarda cada día las velas de 1 min de las acciones del
  Radar en `listas/m1/` (paso 3b de RUTINA.md, dentro de la rutina existente) y mide la regla → `listas/ruptura_930.csv`. Estudio aparte, no va a la página.
  Inicio (21, 22, 23 y 28-sep; los 3 primeros son listas reconstruidas): A/B 5 op. +0.72R WR 40 % PF 2.15; Vigilar ≥ 50 % ≥ $1 5 op. +0.46R;
  20-50 % 17 op. −0.66R WR 12 % PF 0.39. Objetivo: ~100 operaciones en gap ≥ 50 % antes de decidir.
  **Ronda 10 (backtest con Massive, 29-sep, `smallcaps/25_ruptura_massive.py`):** 2 años, 1 121 operaciones en gap ≥ 50 % (≥ $1, con deslistadas):
  DEV +0.06R / VAL −0.06R (WR 40/35 %, PF 1.07/0.93, stops medios −1.61R) → NO validada. ≥ 100 %: +0.11/+0.14R (t < 1). Corto a la apertura
  (stop 30 %, fuera 11:30) en todos los días: +0.055/−0.017R. Días que no rompen el mínimo de las 9:30 (~13 %): el corto a la apertura pierde ~−1R.
  HB2 parcial (1-oct, 61 % de los 20-50 %): la regla en gap 20-50 % pierde: DEV −0.27R (1 090 op., WR 33 %, PF 0.71) / VAL parcial −0.41R
  (265, PF 0.58); diferencia con ≥ 50 % VAL t 2.04. **Estudio CERRADO el 1-oct por decisión del usuario** (no rentable tal cual): descarga de
  Massive detenida, pasos 1b/3b retirados de RUTINA.md y de la rutina; no dedicar más tiempo a la ruptura de las 9:30.
  Error propio corregido: comparar con la referencia solo en los días con entrada sesga a favor de la referencia.
  **Credencial de Massive** guardada en el entorno (API credentials, api.polygon.io y api.massive.com; funciona en esta sesión). Plan gratis:
  1 min sin ajustar desde 29-sep-2024, 5 consultas/min. Datos en /home/user/data/massive (se regeneran con `24_massive_descarga.py`).
  **Error corregido 29-sep en el Radar:** antes de la apertura Yahoo pone el cierre de ayer en regularMarketPrice; el escáner usaba el de anteayer.
  Segunda corrección (29-sep, al comparar con la lista de Edu): SLND +58 % real quedó fuera → el escáner ahora hace red amplia con los dos campos
  y verifica cada candidato contra el cierre oficial de la última sesión (histórico diario de Yahoo, `cierre_ultima_sesion`) y el último precio de 1 min.
  **Causa real de SLND (encontrada después):** el 29-sep no se descargó el fichero otherlisted (NYSE/NYSE American): universo 3 436 en vez de 5 910.
  Corregido: 6 reintentos + ERROR de auditoría si falta un fichero o universo < 5 000. Añadidos: TradingView como 2.ª fuente de gappers
  (`tradingview_premarket`) y detección de splits del día (cotización Yahoo ajustada vs cierre sin ajustar ×2 o más → `split_hoy`).
- **Ronda 11 (29-sep, caso BKYI; `smallcaps/26_avisos_acciones_municion.py`):** < 5 M acciones y 'sin munición' (sin 424B 90 d ni S-3) NO validados como filtro
  (signos opuestos DEV/VAL; las dos juntas DEV +0.48R / VAL −0.40R, n 36/50). Añadidos al Radar como avisos informativos sin tocar el nivel
  (acciones = sharesOutstanding de Yahoo; 'sin munición' no se muestra si el catalizador es F o C).
- **Ronda 12 (30-sep, `smallcaps/27_puntuacion_tesis.py`): PUNTUACIÓN GLOBAL DE LA TESIS VALIDADA.** Pesos de DEV (gap ≥100 %, humo, biotech,
  contrato, 424B 90 d, solo nota; S-3 y serie ≈ 0) → VAL: tercio alto +0.15R PF 1.53, bajo −0.07R PF 0.81 (t 2.97, Spearman p 0.003);
  en gap ≥ 50 % tercio alto +0.26R PF 1.86. Pesos en `smallcaps/puntuacion_pesos.json`.
- **Ronda 13 (1-oct, `smallcaps/28_precio_colocacion.py`): E4 de Edu (precio del gap ÷ precio de la última colocación 424B) NO validada**
  y al revés de la idea: ratio ≥ 2 frente a < 1 → DEV −0.19R / VAL −0.42R (t −1.68); 281 casos con precio fiable. Exploratorio: muy por encima
  de la colocación = peor para el corto (VAL t −2.83 con la puntuación como control, n 45). No se usa sin pre-registro nuevo.
  **Error de datos encontrado:** Yahoo omite contra-splits en su lista de eventos (CRIS 1:20 29-sep-2023, SVRE ADS 1:13.33); el "precio real"
  de la ronda 5 acierta en el 94 % de casos recientes (R no cambia). Radar: `splits_de` une Yahoo + Massive (caso de oro 23).
  **Comprobación (decidida por Claude, el usuario delegó el criterio):** rondas 5/11/12 con precio corregido (`29_sensibilidad_precio.py`):
  mejor estimación (precio exacto de Massive si existe; si no, Yahoo, que acierta más cuando discrepan) = mismos resultados (tesis alta + gap
  ≥ 50 % VAL +0.26R PF 1.86; pesos sin cambios). Margen por precios dudosos (1 288 de 8 604): +0.15R a +0.26R (PF 1.43-1.86). Ronda 11 igual.
- **Decisiones del usuario (30-sep):** fuera las letras A/B/Vigilar/NO/Nunca. El Radar pasa a ser un SCREENER profesional: solo las acciones que
  pasan el filtro de campo (descartadas guardadas pero ocultas: compra en efectivo, resultados, financiación del día, avisos de bolsa, < $1),
  ordenadas por puntuación 0-100 (gap = un factor más) + riesgo estructural aparte (acciones, locate, < $1, rotación) que limita el tamaño;
  ficha al hacer clic con todo el detalle y documentos legibles. Sesgo por defecto bajista; la ejecución es del usuario.
- Conclusión: la ventaja debe venir de selección (catalizador + munición activa) + ejecución fina en 1-5 min + gestión del riesgo; se medirá con el diario de operaciones del usuario y, si hace falta, datos de 1 min de pago con deslistadas.

## Mapa del repositorio
- `curso_short/` curso y glosario · `herramientas/` herramientas · `fichas/` fichas por acción
- `smallcaps/` estudios de gappers, intradía y dilución (datos en `/home/user/data/smallcaps`, se regeneran con los scripts)
- `brechas/`, `estudio_nq/`, `fondeo/`, `pine/` trabajo de futuros NQ · `cripto/` estudio cripto · `oro/` estudio GC
