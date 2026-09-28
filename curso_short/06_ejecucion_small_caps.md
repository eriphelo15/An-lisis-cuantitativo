# Módulo 6 — Ejecución: lo que cambia en small caps (para un trader que ya sabe ejecutar)

> No es un curso de ejecución desde cero. Es la lista de diferencias entre operar NQ y shortear un gapper de $3
> que puede hacer +100 % en una hora. Cada punto es una forma concreta de perder dinero si no se adapta.

## 1. Órdenes
| Situación | Qué usar | Por qué |
|---|---|---|
| Entrada normal | **Límite** (o límite "marketable": un poco por debajo del bid al vender) | El spread puede ser 1-3 %; una orden a mercado en un pico puede ejecutarse varios % peor |
| Premarket / after-hours | **Solo límite** | Casi todos los brókers no aceptan órdenes a mercado ni stops fuera de horario |
| Con SSR activo | Límite **por encima del bid** (en el ask o más arriba) | La regla no te deja vender golpeando el bid: vendes en los rebotes |
| Cubrir en una caída fuerte | Límite contra el bid, en tramos | Hay liquidez en las caídas; cubres vendedores asustados |
| Cubrir con prisa (squeeze) | Límite agresivo por encima del ask | A mercado en un squeeze te ejecutan en el peor tick |

## 2. Stops: el gran cambio respecto a los futuros
- En NQ un stop se ejecuta casi donde lo pones. **Aquí no:** halts, huecos y libros vacíos hacen que salga más arriba.
- Muchos brókers **no activan stops en el premarket** y un stop grande visible en una acción fina puede ser buscado.
- Práctica habitual de short sellers: **stop mental con disciplina absoluta** + alerta de precio + un stop "de catástrofe" más arriba en el bróker.
- **Dimensiona suponiendo que el stop puede ejecutarse 10-20 % peor.** Ejemplo: stop a $5.50 con entrada en $5.00 → planifica la pérdida como si saliera a $5.60-$5.75.

## 3. Tamaño según la liquidez, no solo según el stop
- Regla práctica: tu orden no debería superar el **5-10 % del volumen de 1 minuto** de ese momento. Si mueve 30 000 acciones por minuto, entra con 1 500-3 000, no con 20 000.
- **Entra y sal por tramos** (2-4 partes). Así no mueves el precio contra ti y puedes añadir si la idea se confirma.
- Liquidez para salir: las caídas tienen compradores (cubres ahí); los squeezes no tienen vendedores (por eso el tamaño debe ser pequeño cuando el riesgo de squeeze es alto).

## 4. Leer el Level 2 y la cinta en un gapper
| Lo que ves | Qué suele significar |
|---|---|
| Un vendedor grande en el ask que **se repone** una y otra vez en el mismo precio | Vendedor oculto/iceberg: posible **ATM, tenedor de warrants o convertible** vendiendo. Señal de techo |
| Muchas operaciones en el ask **sin que el ask suba** | Alguien absorbe las compras: oferta de acciones → a favor del corto |
| Operaciones en el bid **sin que el bid baje** | Comprador oculto: cuidado, puede haber rebote fuerte |
| El ask "desaparece" (se retiran las órdenes) y el precio salta | Libro vacío arriba: riesgo de squeeze y halt al alza |
| Números redondos ($1, $2, $5, $10) y **precios de ejercicio de warrants** | Zonas donde aparecen vendedores (la ficha te da esos precios) |
| Volumen de la cinta que se seca en cada nuevo máximo | Agotamiento de compradores |

## 5. Halts: plan decidido ANTES de entrar
1. **Nunca añadas** a un corto justo antes o durante un halt al alza.
2. Si te atrapa un **halt al alza**: durante los 5 minutos mira el precio indicativo de reapertura (muchas plataformas lo muestran).
   Decide con la regla que ya tenías: si reabre por encima de tu stop, **cubres al menos una parte en la reapertura**; no "esperas a que vuelva".
3. Las reaperturas son violentas en ambos sentidos: si reabre muy arriba y a los segundos cae, no persigas; espera la estructura.
4. **Halt a la baja** estando corto: a favor. Suele reabrir más abajo; cubre parte en la reapertura si llegó a tu objetivo.
5. Si ves **2-3 halts al alza seguidos** y la acción no muestra debilidad: no es tu día en esa acción (perfil de squeeze del Módulo 4).

## 6. Horarios
- **Premarket (4:00-9:30):** poco volumen, spreads grandes. Útil para ver niveles y munición (ofertas anunciadas), peligroso para entrar grande.
- **9:30-10:30:** 70 % del volumen y la mayoría de los máximos del día (Módulo 4). Es donde está el dinero y el mayor riesgo.
- **10:30-12:00:** zona de rebotes fallidos y pérdidas de VWAP.
- **Tarde:** movimientos más lentos; los squeezes tardíos existen, sobre todo en acciones de float diminuto.
- **Overnight:** evitar salvo plan específico (coste de préstamo, recall, noticia o gap al alza).

## 7. Locates en la práctica
- Pídelos **en el premarket**, en cuanto la acción entra en tu lista: en los mejores candidatos desaparecen en minutos.
- Pide solo lo que vas a usar (se pagan igual aunque no operes).
- Si el locate cuesta más del ~2 % del precio de la acción, la ventaja de la operación tiene que ser muy grande para compensarlo.

## 8. Checklist de ejecución (antes de cada entrada)
1. ¿Locates confirmados y coste aceptable?
2. ¿SSR? → tipo de orden.
3. ¿Halts al alza hoy? ¿Cuántos?
4. Stop estructural y **pérdida si se ejecuta 10-20 % peor**: ¿cabe en mi riesgo?
5. Tamaño ≤ 5-10 % del volumen de 1 minuto; entrada en tramos.
6. Objetivos (niveles de la ficha y del gráfico) y dónde cubro cada tramo.
7. ¿Qué hago si hay halt al alza? (decidido antes).
