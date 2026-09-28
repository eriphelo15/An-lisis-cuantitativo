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
- **Principio del usuario: toda idea o criterio se valida con datos antes de usarlo.** Aunque tenga lógica, no se da por buena sin medirla.
- El usuario tiene mucha experiencia ejecutando (futuros): su trabajo es ejecutar el mejor setup según la acción del precio; el trabajo fino de selección es de Claude.
- Commits y push en la rama `claude/analisis-cuantitativo-45j7qe`. Sin PR salvo que lo pida.

## Estado actual
- **Curso de short seller** en `curso_short/` (programa en `00_PROGRAMA.md`). Hechos: módulos 1 (economía de la dilución),
  1b (guía EDGAR + lecciones), 2 (mecánica del corto), 3 (leer la SEC: munición y baby shelf), 4 (anatomía del pump).
  Módulo 5 (setups medidos) y Módulo 6 (ejecución condensada: diferencias vs futuros) hechos.
  **Orden acordado:** Módulo 7 (riesgo) → Módulo 8 (infraestructura: bróker, locates, fondeo de acciones) → **validar con datos los criterios de selección** (munición activa el día del gap, catalizador, float/rotación premarket, etc.) → sistema de lista diaria (solo cuando lo pida).
  Práctica pendiente del usuario: ejecución en DCOY, LHSW, INLF, GRML, GLND (fichas en `fichas/`). Ejercicios del módulo 4: WHLR (usuario) y BENF (Claude como ejemplo) hechos.
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
- Conclusión: la ventaja debe venir de selección (catalizador + munición activa) + ejecución fina en 1-5 min + gestión del riesgo; se medirá con el diario de operaciones del usuario y, si hace falta, datos de 1 min de pago con deslistadas.

## Mapa del repositorio
- `curso_short/` curso y glosario · `herramientas/` herramientas · `fichas/` fichas por acción
- `smallcaps/` estudios de gappers, intradía y dilución (datos en `/home/user/data/smallcaps`, se regeneran con los scripts)
- `brechas/`, `estudio_nq/`, `fondeo/`, `pine/` trabajo de futuros NQ · `cripto/` estudio cripto · `oro/` estudio GC
