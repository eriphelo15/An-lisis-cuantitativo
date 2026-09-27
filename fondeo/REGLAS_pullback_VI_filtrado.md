# Pullback VI filtrado — reglas exactas (NQ / MNQ)

Estrategia validada en 15 años de NQ (2010-2026). Umbrales fijados con 2010-2018 y confirmados fuera de muestra en 2019-2026.
Ventaja media +0.10R por operación, 15 de 17 años positivos.

## Gráfico
- NQ o MNQ, velas de **1 minuto**, hora de Nueva York (ET).
- **EMA 20 y EMA 50** sobre el cierre, calculadas con la sesión completa (incluida la nocturna).
- **ATR del día** = media del rango RTH (máximo − mínimo de 09:30 a 16:00) de los **14 días anteriores**. Se calcula antes de abrir y no cambia en el día. Referencia actual: ~340–400 pts.

## Señal (compra; en venta todo al revés)
Se evalúa al **cierre de cada vela entre 09:31 y 11:29**:
1. **Tendencia:** EMA 20 > EMA 50 y la vela cierra por encima de ambas.
2. **Volume imbalance contra la tendencia:** el cuerpo de la vela actual queda completamente por debajo del cuerpo de la vela anterior (máx(apertura, cierre) actual < mín(apertura, cierre) anterior) y las mechas se tocan (máximo actual ≥ mínimo anterior).
3. **Filtro 1, día a favor:** cierre actual − apertura de 09:30 > **0.158 × ATR** (hoy ≈ 54 pts).
4. **Filtro 2, EMA 20 inclinada:** EMA 20 actual − EMA 20 de hace 10 velas > **0.074 × ATR** (hoy ≈ 25 pts).
5. **Filtro 3, stop válido:** stop = EMA 50 actual − 2 ticks. Distancia entrada–stop entre **0.069 × ATR y 0.25 × ATR** (hoy ≈ 24 a 86 pts). Fuera de ese rango no se opera.

## Ejecución
- **Entrada:** a mercado al cierre de la vela señal.
- **Stop:** fijo (EMA 50 − 2 ticks en el momento de entrar). No se mueve.
- **Objetivo:** **2 veces el riesgo**.
- **Salida por tiempo:** si no tocó stop ni objetivo, cierre a las **15:55**.
- **Máximo 1 operación al día:** la primera señal válida. Sin señal válida hasta las 11:29, no se opera.

## Tamaño (Tradeify 50K)
Contratos MNQ = riesgo en USD / (distancia del stop en pts × $2 + $2.82), redondeado hacia abajo. Nunca mezclar NQ y MNQ.
- **Examen Select 50K:** riesgo **$500** por operación (con stop de 57 pts ≈ 4 MNQ). Una ganancia (2R ≈ $1,000) respeta la consistencia del 40%.
- **Fondeada Select Flex:** riesgo **$250** por operación (con stop de 57 pts ≈ 2 MNQ). Retiro del 50% del beneficio cada 5 días de +$150.

## Qué esperar (15 años, precios de hoy)
| | |
|---|---|
| Días con operación | ~57% |
| Hora media de entrada | ~10:13 |
| Stop típico | 37–78 pts (mediana 57) |
| Winrate | 38% |
| Ganancia media / pérdida media | +1.89R / −1.01R |
| Resultado medio | +0.10R por operación |
| Peor racha de pérdidas seguidas | 14 |
| Fondeo (sim.): aprueba examen / fondeadas que cobran / neto por examen | 33–34% / 78–79% / $375–406 |

## Registro para el backtest manual (una fila por señal)
Fecha · hora de la vela señal · dirección · ATR del día · apertura 09:30 · cierre de la señal · EMA20 actual · EMA20 de hace 10 velas · EMA50 · stop (pts) · ¿pasa los 3 filtros? · resultado (R) · salida (stop / objetivo / 15:55) · deslizamiento observado (ticks).
