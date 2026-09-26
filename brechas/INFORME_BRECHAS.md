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
