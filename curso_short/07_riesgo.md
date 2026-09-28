# Módulo 7 — El riesgo del short seller (con datos)

> Elegir bien sube la probabilidad. Pero hasta una acción perfectamente elegida puede hacer +100 % en tu contra.
> El riesgo no se gestiona para ser conservador: se gestiona para **seguir vivo el día que llega la cola** y poder
> apretar el acelerador cuando la ventaja está demostrada.

## 1. Las colas: cuánto puede subir EN CONTRA (8 604 gappers, 2015-2026)
Subida máxima desde la apertura (lo que sufre un corto abierto a las 9:30):

| Gap | Mediana | 1 de cada 4 | 1 de cada 10 | 1 de cada 100 | Supera +50 % | Supera +100 % | Días 1-2: supera +100 % |
|---|---|---|---|---|---|---|---|
| 20-50 % | +12 % | +26 % | +56 % | +228 % | 11 % | 4.5 % | 6.3 % |
| 50-100 % | +16 % | +37 % | +76 % | +260 % | 18 % | 6.4 % | 8.7 % |
| **≥ 100 %** | **+19 %** | **+46 %** | **+98 %** | **+319 %** | **23 %** | **9.7 %** | **12.5 %** |

**Lectura:** en los gaps que más nos interesan (≥ 100 %), **1 de cada 10 duplica su precio de apertura** en el día, y 1 de cada 100 lo multiplica ×4.
Si operas 5 gappers por semana, verás varios de estos al año. No son "cisnes negros": son parte normal del juego.

## 2. Tamaño: lo que aguanta una cuenta (Monte Carlo con operaciones reales)
Setup A del Módulo 5 (corto temprano en gaps ≥ 100 %, stop +30 %, con 5 % de deslizamiento por halts): 397 operaciones reales,
ventaja pequeña (+0.05R). 200 operaciones por trayectoria, 20 000 simulaciones:

| Riesgo por operación | Resultado mediano | Peor 5 % | Caída máxima típica | Prob. caída > 30 % | Prob. caída > 50 % |
|---|---|---|---|---|---|
| 0.5 % | +5 % | −8 % | 7 % | 0 % | 0 % |
| **1 %** | **+9 %** | **−16 %** | **13 %** | **1 %** | **0 %** |
| 2 % | +16 % | −31 % | 25 % | 32 % | 2 % |
| 5 % | +21 % | −67 % | 54 % | 98 % | 61 % |
| 10 % | **−24 %** | −94 % | 84 % | 100 % | 99 % |

- Racha de pérdidas seguidas esperable en 200 operaciones: **6 típica, 8 en 1 de cada 10 casos**.
- Con una ventaja pequeña, **arriesgar 10 % por operación lleva a perder dinero aunque la estrategia gane**: las caídas te sacan antes de cobrar.
- Con **mejor selección** (ventaja mayor, a validar) la tabla mejora y se puede arriesgar más. **Primero se demuestra la ventaja, luego se sube el riesgo.**

## 3. Las reglas (medibles, no "ser conservador")
1. **Riesgo por idea: 1 % de la cuenta** como base. Hasta 2 % solo en acciones clasificadas **A** y cuando el diario demuestre ventaja con ≥ 50 operaciones.
2. **El riesgo se calcula con el stop EJECUTADO, no con el stop puesto:** stop + 10-20 % de deslizamiento (halts). Tamaño = riesgo en $ ÷ (distancia al stop × 1.2).
3. **Límite por liquidez:** nunca más del 5-10 % del volumen de 1 minuto (Módulo 6), aunque el cálculo de riesgo permita más.
4. **Pérdida máxima diaria: 3R.** Al llegar, se apaga la plataforma. Los peores días de un short seller vienen de "recuperar" en un squeeze.
5. **Sin stop definido no hay operación.** Y no se mueve hacia arriba nunca. El reciclaje (cubrir abajo, volver a vender arriba) es válido **solo si el total de la posición respeta el riesgo de la idea**.
6. **Añadir solo cuando la operación funciona** (reciclar en rebotes que fallan), **nunca promediar** una posición que va en contra en una acción que sube.
7. **Riesgo correlacionado:** en un día de tema (varias acciones del mismo sector subiendo juntas) todas las posiciones son **una sola apuesta**: riesgo total ≤ el de una idea.
8. **Overnight:** solo con plan específico, tamaño reducido a la mitad y sabiendo el coste de préstamo; un gap al alza de la mañana siguiente no tiene stop.
9. **Reducción automática:** si la cuenta cae 10 % desde su máximo, el riesgo por idea baja a la mitad hasta recuperar la mitad de la caída.

## 4. Cuándo apretar el acelerador (y cuándo no)
**Sí:** acción **A** (munición activa + catalizador débil + sin perfil de squeeze), precio bajo el VWAP o rechazándolo, locates baratos,
el diario ya demuestra ventaja en ese setup → 1.5-2 % de riesgo y reciclaje agresivo a favor.
**No:** acción B/C, día de tema, halts al alza seguidos, float diminuto sin munición, precio sobre un VWAP que sube (GRML) → tamaño mínimo o nada.

## 5. Ejercicios
1. Con tu cuenta actual (o la que piensas usar), calcula el tamaño en acciones para: entrada $6.00, stop $6.60, riesgo 1 %, deslizamiento 20 %.
2. ¿Cuántas acciones podrías operar si el volumen de 1 minuto es de 40 000? ¿Cuál de los dos límites manda?
3. Revisa tus 5 prácticas (DCOY, LHSW, INLF, GRML, GLND): ¿en cuál habrías llegado a la pérdida máxima diaria de 3R?
