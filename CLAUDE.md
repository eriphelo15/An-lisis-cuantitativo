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
  Niveles: A (humo + gap ≥50 % + 424B 90 d + cap ≥$30 M), B (humo + gap ≥50 %), Vigilar, NO (resultados/financiación/bolsa/424B hoy), Nunca (compra en efectivo).
  Pendiente ofrecido: medir el caso "sube sin ninguna noticia" (días de prueba, revisados a mano: BTTC −1.25R, VEEE −1.25R, WHLR −1.25R, WETO +0.73R, SKYE +1.35R; GRML NO era "sin noticia": noticia de tema Groenlandia).
  Auditoría obligatoria antes de publicar (RUTINA.md paso 5b + control automático en `finalizar`, que bloquea la lista si hay errores).
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
- **Validación de selección (8 604 gappers, EDGAR a la hora exacta, DEV 2015-21/VAL 2022-26; `smallcaps/INFORME_SELECCION.md`):** VALIDADOS: venta 424B en 90 días (dif. +0.136R VAL, t 5.7; DEV +0.06), shelf S-3 (+0.072R, t 3.2), 8-K solo nota de prensa vs acuerdo 1.01 (+0.151R, t 2.7). NO validados: sin 8-K, contra-split/aviso, diluidor en serie, día de tema por SIC, combinación A. Capitalización < $30 M = PEOR para el corto (más squeezes). Mejor combinación (exploratoria): gap ≥50 % + venta 424B 90 d + cap ≥ $30 M → VAL +0.095R (50-100 %, PF 1.24) y +0.119R (≥100 %, PF 1.25) con setup A mecánico. Aún < +0.20R. Pendiente: definir 'día de tema' por palabras clave; volumen premarket/float (datos de pago).
- **Contenido del catalizador (ronda 2b, 3 000 notas clasificadas a mano y a ciegas; `smallcaps/INFORME_SELECCION.md`):** VALIDADO: gap por **humo/cosmético** (LOI, MOU, no vinculante, alianza sin cifra, cifras 'hasta', patentes, preclínico, giros IA/cripto, recompras simbólicas) → VAL +0.145R, WR 66 %, PF 1.46 (DEV +0.10R); resto −0.08R; t 4.5. Humo + gap ≥50 % → VAL +0.22R, PF 1.63 (DEV +0.15R); humo + gap ≥100 % → +0.40R, PF 2.3 (exploratorio, n 73). Resultados (PF 0.61), financiación (0.72) y avisos de bolsa (0.64) = malos para el corto; compra en efectivo = no shortear nunca. Contrato real/FDA: buenos en 2015-21, ≈0R en 2022-26.
- **Ejecución dentro de la selección (ronda 3, velas 1 h, oct-2023→sep-2026, 222 humo):** en humo el corto a la apertura (stop +30 %) da VAL +0.22R, PF 1.76 (DEV +0.14R). Esperar debilidad (a las 11:30 bajo VWAP) es PEOR: −0.38R por operación (t −5.5, igual en DEV) → la caída ocurre pronto. 1ª hora roja y bajo VWAP como filtros: no validados. Exploratorio: salir a las 11:30 si sigue sobre VWAP → +0.25R, PF 1.99. Reversal/1-5 min: sin muestra suficiente (8/24 casos).
- **Día de tema (ronda 4, palabras raras del nombre + lista de temas en nombre/catalizador):** hipótesis 'no shortear en día de tema' NO validada; en VAL 2022-26 fue al revés: día de tema +0.30R, WR 72 %, PF 2.06 (119 casos, 87 días) vs día normal +0.01R (t −3.2); DEV sin muestra (5). IA +0.45R, cripto +0.17R, espacio +0.29R, drones −0.34R (7). Líder vs seguidor: sin diferencia. GRML (líder, −1.25R) fue la excepción, no la regla. El tema NO es filtro.
- Conclusión: la ventaja debe venir de selección (catalizador + munición activa) + ejecución fina en 1-5 min + gestión del riesgo; se medirá con el diario de operaciones del usuario y, si hace falta, datos de 1 min de pago con deslistadas.

## Mapa del repositorio
- `curso_short/` curso y glosario · `herramientas/` herramientas · `fichas/` fichas por acción
- `smallcaps/` estudios de gappers, intradía y dilución (datos en `/home/user/data/smallcaps`, se regeneran con los scripts)
- `brechas/`, `estudio_nq/`, `fondeo/`, `pine/` trabajo de futuros NQ · `cripto/` estudio cripto · `oro/` estudio GC
