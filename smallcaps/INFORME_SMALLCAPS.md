# Small caps: estudio con datos (2015-2026)

## Datos y método
- Universo: ~5.700 acciones comunes de EE. UU. listadas hoy en NASDAQ, NYSE y AMEX. Precios diarios de Yahoo, 2015 a sep-2026.
  Velas de 5 min de Yahoo para los últimos ~60 días.
- **Evento "gapper":** abre ≥ +20% sobre el cierre de ayer, con estas condiciones:
  - acción pequeña/ilíquida: < $20M de volumen medio diario en los 20 días previos;
  - operable: ≥ $1M negociados ese día;
  - en juego: volumen ≥ 3× su media.
  - Resultado: **8.604 eventos en 2.119 acciones**, cada vez más frecuentes (133 en 2015, 1.685 en 2025).
- **Costes:** 1% de ida y vuelta (spread + deslizamiento). **No** incluye el coste de préstamo de las acciones para ponerse corto.
- **Stops conservadores:** si el máximo o mínimo del día toca el stop, cuenta como pérdida.
- **Épocas:** 2015-19, 2020-22 y 2023-26.
- **Sesgo importante:** faltan las empresas que dejaron de cotizar. Esto **favorece a los largos** y **perjudica a los cortos** en este estudio.

## Resultados (datos diarios)
| Estrategia | 2015-19 | 2020-22 | 2023-26 | Comentario |
|---|---|---|---|---|
| **Comprar a la apertura** (gap and go), cierre al final del día | −2.1% | −3.0% | −2.8% | Pierde siempre. Mediana −7.5%. Solo 28-33% cierran por encima de la apertura |
| Comprar con stop 10/20/30% | −0.4 a −1.9% | −2.9 a −4.1% | −1.9 a −2.4% | Pierde en todas las variantes |
| Corto a la apertura, stop 30% (todos los gappers) | +1.4% | +1.3% | +0.1% | Se está apagando |
| **Corto, solo gaps de +50% a +100%**, stop 30% | +5.4% | +1.9% | +1.6% | Positivo |
| **Corto, solo gaps > +100%**, stop 30% | +6.3% | +7.5% | +4.6% | El más fuerte |
| Día 2: comprar si cerró fuerte | −5.5% | −2.9% | −2.6% | Pierde |

Cuanto mayor es el gap, mayor es el desvanecimiento posterior. El patrón es monótono y tiene lógica: agotamiento y dilución.

## La trampa: los stops en subidas explosivas
Si el stop del 30% no se ejecuta en +30% sino en +45% (paradas de cotización, huecos al alza), la ventaja **desaparece**:
- gaps > 100%: de +5.3% a −0.2%;
- gaps 50-100%: de +2.1% a −2.5%.

Con un stop más holgado del 50%, sigue siendo positivo (+6.4% y +2.3%), pero eso es **+0.13R por operación** con un riesgo enorme por posición.
Hay que sumar también el préstamo de acciones difíciles de conseguir (a menudo no hay acciones disponibles o cuesta un 0.5-2% diario) y el riesgo de short squeeze.

## Intradía (velas de 5 min reales, últimos 60 días, 344 gappers)
| Entrada | Todos: R medio (acierto) | Solo gaps ≥ 50% |
|---|---|---|
| Corto a la apertura, stop +30% | 0.00R (56%) | +0.05R |
| Corto al romper el mínimo de la 1ª vela | −0.12R (46%) | +0.03R |
| Corto al perder el VWAP (10:00-12:00) | −0.03R (53%) | **+0.10R** (61%) |
| **Largo ORB de 5 min (gap and go)** | **−0.50R (20%)** | −0.55R |
| Largo ORB de 5 min con objetivo 2R | −0.26R (32%) | −0.23R |

## Conclusiones
1. **El "gap and go" en largo, que es lo que más se enseña, pierde de forma sistemática** en 11 años de datos diarios y también en el intradía reciente, incluso con un sesgo de datos que lo favorece.
2. **La ventaja real en small caps está en el lado corto** de los gappers más extremos (+50%, sobre todo +100%). Es de las ventajas más grandes que hemos visto en %, pero en R es parecida (~+0.1R). Depende de:
   - conseguir acciones para ponerse corto;
   - su coste de préstamo;
   - sobrevivir a los squeezes y las paradas de cotización.
   Es un negocio de ejecución y de gestión de riesgo extremo, no de patrón.
3. Las empresas de fondeo de futuros no permiten esto. Haría falta un bróker de acciones con buena disponibilidad de préstamo (con $25k en EE. UU., o un bróker offshore) o una empresa de fondeo de acciones.
