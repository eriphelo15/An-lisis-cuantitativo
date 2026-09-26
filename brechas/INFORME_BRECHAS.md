# Investigación amplia de brechas (NQ, ES, YM · 15 años · datos externos VIX/tipos/Fed)

Método: cada idea se evaluó en tres periodos separados: DEV 2010-18, VAL1 2019-21 y VAL2 2021-26.
Solo cuenta lo que funciona en los tres. Los costes se aplican a precios de hoy. Scripts: `brechas/01..14`.

## Qué se probó
| # | Línea | Resultado |
|---|---|---|
| 1 | Deriva por tramo horario (Asia, Europa, preapertura, tramos RTH, post-cierre) | La subida nocturna fue fuerte en 2010-21 y **casi desaparece en 2021-26**. El día RTH no tiene deriva útil. |
| 2 | Predicción de un tramo por otro (momentum/reversión: apertura→cierre, última media hora, día anterior) | Nada consistente. Lo máximo son efectos de 0.4-1 bp, menos que el coste. |
| 3 | Calendario: FOMC, fin/inicio de mes, OPEX, cuádruple hechicería, pre-festivo, día de la semana | Solo **la deriva pre-FOMC** (18:00→14:00 del día de la Fed) es positiva en los 3 índices y periodos. Son 8 veces al año. |
| 4 | Régimen de VIX (nivel, estructura 9D/3M, cambios), VVIX, tipos 2y/10y, dólar | La volatilidad sí se predice (corr. 0.45). **La dirección no**. |
| 5 | Relación NQ/ES/YM: adelanto-retraso a 1 min, divergencias | Correlaciones de ~0.01. Nada explotable. |
| 6 | Niveles: máx/mín de ayer, cierre de ayer, máx/mín nocturno, números redondos | Rebote/ruptura ≈ 50% (azar). Única excepción: romper el mínimo de ayer en NQ continúa el 55% de las veces (~+0.1R). |
| 7 | Gaps por tamaño (rellenar vs seguir) | Nada. |
| 8 | Breakout de rango inicial condicionado a volatilidad esperada | Nada estable. |
| 9 | Escaneo masivo (~50.000 reglas: hora × horizonte × contexto × VIX × día) | Ver abajo. |
| 10 | Rebalanceo de fin de mes | Inconsistente entre periodos. |

## La prueba clave: escaneo masivo con validación ciega
Se eligieron 521 reglas usando solo 2011-2018. Cada una tenía t ≥ 2.5 en NQ, ES e YM a la vez. Después se miró sin tocarlas:
- **Reglas de horario diurno:** después de 2018 rinden ~0 o negativo. Todas se desvanecen.
- **Reglas nocturnas:** conservan ~75% en 2019-21 y **caen a ~0.2-0.3 bp en 2021-26**, prácticamente nada.

Conclusión: lo que "descubre" una búsqueda masiva sobre precio público casi nunca sobrevive fuera de muestra.
Es la prueba de que el mercado es eficiente en lo fácil de medir.

## Lo que sí queda (validado)
| Bloque | Ventaja | Estado |
|---|---|---|
| A · Pullback VI filtrado (NQ, mañana) | +0.10 / +0.14 / +0.09 R por periodo | **Sólido**: umbrales fijados solo con DEV |
| C · Deriva pre-FOMC (largo 18:00→14:00 del día Fed) | positiva en los 3 índices y periodos; publicada (Lucca-Moench 2015) y sigue funcionando | Sólida pero rara (8/año); no mejora el fondeo |
| B · Comprar caída nocturna (00:30 y 05:30) | +0.06 a +0.16 R | **Débil**: las horas vecinas fallan en 2021-26; se eligió con todos los periodos |

## Palanca real: combinar bloques NO correlacionados
La correlación diaria entre bloques es de −0.01 a 0.08. Al sumarlos, el Sharpe anual pasa de 0.8 a 1.4.
En la simulación Tradeify (Select 50K → Flex):

| Cartera | Aprueba | Fondeadas que cobran | Neto por examen |
|---|---|---|---|
| Solo A | 32-34% | 78-81% | $373-393 |
| A + B | 27-37% | 80-91% | $507-678 |

B aún no está demostrado para el futuro. Hay que tratarlo como experimento, con tamaño pequeño o en simulación, hasta que acumule datos propios.

---
# Parte 2: Drive, literatura publicada y eventos macro

## Tu Drive
- **Reversal [EAO] (tu .pine):** programada fielmente en velas de 5 minutos con los mejores parámetros de tu grid (near 2, long 20, 09:30-10:00, SL 2 ATR, TP 2.5R).
  En NQ da −0.01R en 2010-17 (años que tu grid no vio) y +0.01R en 2018-26. En ES y YM es negativa. **No tiene ventaja**: el PF 1.32 de tu grid es el mejor de muchas combinaciones probadas, es decir, sobreajuste.
- **ares_grid_search.py (UASRS 1 min):** lee `NQ_continuous_15y.csv`, el archivo con el ajuste de contratos defectuoso que detectamos al principio.
  Los filtros en % (rango mínimo, pendiente de la EMA diaria) usan niveles de precio erróneos. Además elige el mejor de ~4.200 combinaciones sin prueba ciega.
- **Datos de oro (GC):** están en Drive, pero no se pueden descargar: no están compartidos por enlace y la conexión con Drive tiene un límite de 10 MB. Si se comparten por enlace, se pueden probar.

## Lo que dice la literatura y lo que muestran nuestros datos
| Estudio | Qué afirma | Nuestro resultado 2010-2026 |
|---|---|---|
| Gao, Han, Li, Zhou (JFE 2018): momentum intradía | La 1ª media hora predice la última | **Muerto.** En 2021-26 incluso se **invierte** (t≈−2 en los 3 índices) |
| Rebalanceo de ETFs apalancados (Barbon et al.) | El movimiento del día continúa en los últimos 30 min | Funcionó en 2010-18 (t 2.3-3.5). **Desaparece desde 2019** |
| Dim, Eraker, Vilkov (0DTE / gamma de dealers) | Con gamma positiva, reversión intradía | Coherente con la inversión que vemos en 2021-26. No se puede operar sin datos de gamma |
| Lucca-Moench (2015), deriva pre-FOMC; Kurov et al. dicen que "desapareció" en 2016-19 | Sube antes del anuncio de la Fed | **Vive**: positiva en los 3 índices y periodos. Operación concreta abajo |
| Knox-Londono-Samadi: prima en días CPI/NFP/FOMC | Más rentabilidad esos días | CPI y NFP: **nada consistente**. Solo FOMC |
| Estudio MNQ 2021-25 (arXiv 2605.04004) | 14 familias de señales OHLCV: ninguna pasa | Coincide con nuestro escaneo ciego |

Lección: casi toda anomalía publicada se desvanece después de publicarse. La que sobrevive (pre-FOMC) tiene explicación de prima de riesgo, no de "patrón".

## Nueva operación validada: F · noche previa a la Fed (NQ)
- **Qué hacer:** comprar NQ/MNQ a las 18:00 ET la víspera del anuncio FOMC y vender a las 08:30 ET del día del anuncio. Stop protector a 0.5 × ATR diario (hoy ≈ 180 pts).
- **Resultado:** +0.21R / +0.28R / +0.32R (DEV/VAL1/VAL2), acierto 73% / 88% / 75%, 16 de 17 años positivos, t = 4.2. Es más fuerte con el VIX alto.
- **Pega:** solo 8 veces al año. En la simulación de fondeo apenas cambia el neto por examen, porque es rara.
  Es un complemento con alto acierto, no un negocio por sí sola.
- **Fechas FOMC 2026:** 28 ene, 18 mar, 29 abr, 17 jun, 29 jul, 16 sep, 28 oct, 9 dic.
  Se entra el día anterior a las 18:00: 27 ene, 17 mar, 28 abr, 16 jun, 28 jul, 15 sep, 27 oct, 8 dic.

## Macro (datos oficiales: fechas de publicación de ALFRED/FRED, VIX de CBOE, tipos y dólar de FRED)
- NFP y CPI: ni la deriva previa, ni la reacción, ni la continuación son consistentes entre periodos.
- VIX (nivel, estructura 9D/3M, cambios), tipos 2 y 10 años, dólar: **predicen la volatilidad, no la dirección**. Sirven para ajustar el tamaño, no para elegir el lado.

---
# Parte 3: modelos ICT (script `19_ict.py`)
Reglas mecánicas en NQ, ES e YM durante 15 años, con 1 operación por modelo y día y costes a precios de hoy:
FVG con desplazamiento (entrada en el borde, o en el 50% = CE), Silver Bullet (10:00-11:00 tras barrer el rango de 09:30-10:00),
Judas Swing (barrido del máx/mín nocturno y cierre de vuelta dentro), Turtle Soup (barrido del máx/mín de ayer) y OTE (70.5% de un impulso ≥ 0.35 ATR).

| Modelo | NQ (DEV / VAL1 / VAL2, R por operación) | ES | YM |
|---|---|---|---|
| FVG (borde) | +0.06 / −0.04 / +0.04 | +0.03 / +0.03 / −0.06 | −0.04 / −0.09 / −0.02 |
| FVG 50% (CE) | −0.04 / −0.09 / −0.01 | −0.08 / −0.09 / −0.12 | −0.04 / −0.09 / −0.07 |
| Silver Bullet | +0.09 / +0.05 / −0.07 | +0.03 / −0.02 / +0.04 | +0.16 / −0.13 / −0.06 |
| Judas Swing | 0.00 / +0.08 / 0.00 | −0.12 / −0.23 / −0.13 | −0.11 / +0.04 / −0.10 |
| Turtle Soup | +0.02 / +0.06 / −0.06 | −0.05 / −0.16 / −0.07 | +0.04 / −0.03 / −0.04 |
| OTE | −0.04 / −0.08 / +0.08 | −0.16 / −0.15 / −0.18 | −0.13 / +0.18 / −0.12 |

Ningún modelo ICT es positivo de forma consistente en los tres periodos, ni siquiera en un solo índice. El acierto va del 25% al 44%.
Los barridos de liquidez (Judas, Turtle Soup) pierden en ES: el barrido tiende a continuar, como ya vimos con el mínimo de ayer en NQ.
