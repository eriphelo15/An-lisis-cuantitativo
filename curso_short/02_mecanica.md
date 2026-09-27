# Módulo 2 — La mecánica del corto

> Antes de apretar "vender" tienes que saber exactamente qué pasa por detrás: de dónde salen las acciones,
> cuánto cuestan, qué reglas te pueden bloquear y qué puede salir mal sin que sea culpa del gráfico.

## 1. Qué es exactamente vender en corto
1. Pides **prestadas** acciones que no tienes (tu bróker las consigue).
2. Las **vendes** al precio de hoy (ej. $6).
3. Más tarde las **recompras** (ej. a $4) y las **devuelves**.
4. Tu ganancia es la diferencia ($2 por acción) **menos el coste del préstamo**.

La asimetría que nunca debes olvidar: en largo lo máximo que pierdes es el 100 %. **En corto la pérdida no tiene techo**:
una acción de $6 puede irse a $30. Por eso el corto se gestiona distinto (Módulo 7).

## 2. Conseguir las acciones: locates, ETB y HTB
- **Locate:** antes de vender en corto, la ley (Reg SHO, regla 203) exige que tu bróker haya **localizado** acciones para prestarte.
- **ETB (Easy To Borrow):** hay de sobra; se shortea sin pedir nada, casi gratis. Raro en los gappers que nos interesan.
- **HTB (Hard To Borrow):** escasas; hay que **pedir el locate** y **pagar**. Es lo normal en small caps que suben fuerte.
- **Sin inventario ("no locates"):** no hay acciones → no puedes shortear, aunque el setup sea perfecto. Pasa mucho en los mejores candidatos.

### Cómo se cobra (depende del bróker)
| Tipo | Cómo funciona | Típico en |
|---|---|---|
| **Locate por acción (intradía)** | Pagas por adelantado, p. ej. $0.02-$0.20 por acción, lo uses o no; vale solo ese día | Brókers para day traders de small caps (con plataforma tipo DAS) |
| **Tasa anual (overnight)** | Porcentaje anual sobre el valor prestado, cobrado por cada día que mantienes la posición de un día para otro | Brókers generalistas (p. ej. Interactive Brokers) |

**Traducir una tasa anual a coste diario:** tasa ÷ 360. Una tasa de 300 % anual ≈ **0.83 % por día**. En un gapper las tasas de 100-1 000 % no son raras.

### Ejemplo de coste real
Quieres shortear 1 000 acciones de APUS a $6 y el locate cuesta $0.10 por acción:
- Pagas **$100** antes de entrar (el 1.7 % del valor de la posición).
- Para empatar, la acción tiene que caer al menos **$0.10** (+ comisiones y spread).
- Si el setup falla y no entras, **los $100 ya están pagados**. Por eso pides locates solo de lo que de verdad vas a operar.

## 3. La regla SSR (Short Sale Restriction, Regla 201)
- Se activa cuando una acción **cae 10 % o más respecto al cierre de ayer** durante la sesión.
- Dura **el resto de ese día y todo el día siguiente**.
- Con SSR activo **solo puedes vender en corto por encima del mejor bid** (no puedes "pegarle" al bid). En la práctica: entras con órdenes límite al ask o por encima, esperando a que alguien te compre.
- Consecuencia práctica: con SSR es más difícil entrar en el momento exacto de la ruptura hacia abajo; muchos short sellers **planean entradas en subidas (rebotes)** en lugar de en caídas.
- Un gapper que abre +200 % casi nunca activa SSR el día 1: tendría que caer por debajo del cierre de AYER −10 %, y está muy por encima.
  Ojo: la referencia es el cierre anterior, **no** el máximo del día. Caer 40 % desde el máximo no activa SSR si sigue por encima de ese nivel.
- El día 2 sí es frecuente: si el día 2 abre y cae 10 % bajo el cierre del día 1, se activa. Y si se activó el día 1, sigue activo todo el día 2. Revísalo siempre en tu plataforma antes de planear la entrada.

## 4. Halts (paradas de cotización)
### a) Halts por volatilidad (LULD — Limit Up/Limit Down)
- La bolsa fija una **banda** alrededor del precio medio de los últimos 5 minutos. Si el precio se sale de la banda y no vuelve en 15 segundos, **la acción se para ~5 minutos** (puede alargarse).
- Las bandas son más anchas en acciones baratas (p. ej. 20 % entre $0.75 y $3, y más amplias por debajo) y se **amplían al principio y al final de la sesión**.
- En la reapertura el precio puede **saltar**: tu stop no se ejecuta en el nivel que pusiste sino en el precio de reapertura.
- **Halt al alza estando corto = el peor escenario.** Si estás corto y la acción se para al alza, no puedes salir durante 5 minutos y puede reabrir mucho más arriba. El estudio del Módulo 1 lo mostró: si el stop del 30 % se ejecuta en +45 % por un halt, la ventaja desaparece.

### b) Halts por noticias o regulatorios
- **T1 (News Pending):** la empresa va a publicar una noticia. Puede durar de minutos a horas.
- **T12 (Additional Information Requested):** la bolsa pide información a la empresa. Puede durar **días o semanas**; si estás corto, estás atrapado todo ese tiempo.
- **Suspensión de la SEC:** hasta 10 días. Raro, pero existe en promociones fraudulentas.

**Regla práctica:** nunca entres grande en corto en una acción que acaba de tener halts al alza seguidos y no ha mostrado debilidad.

## 5. Recalls y buy-ins
- Las acciones prestadas **pueden ser reclamadas** por su dueño (*recall*). Si tu bróker no encuentra otras, te obliga a **recomprar** (*buy-in*), normalmente al precio del momento, aunque no quieras.
- Pasa más en posiciones **overnight** de acciones HTB muy demandadas, justo cuando la acción sube (todo el mundo quiere las acciones a la vez).
- Si una acción entra en la **Threshold List** (demasiados fallos de entrega), las reglas de cierre obligatorio se endurecen (Reg SHO, regla 204).

## 6. Margen y dinero necesario
Son **dos reglas distintas** y el bróker aplica la que exija más dinero tuyo:
- **Regla 1 — para abrir (Reg T, 150 %):** el dinero de la venta en corto queda retenido (100 %) y además pones un **50 % tuyo**.
- **Regla 2 — para mantener (FINRA 4210), acciones por debajo de $5:** tu dinero debe ser el **mayor** entre
  **$2.50 × número de acciones** y el **100 % del valor en dólares de la posición** (acciones × precio).

Ejemplo: 2 000 acciones a $3.50 → valor de la posición = 2 000 × $3.50 = **$7 000**.
| Regla | Dinero tuyo que exige |
|---|---|
| 1 (abrir, 50 %) | $3 500 |
| 2 (mantener): mayor entre 2 000 × $2.50 = $5 000 y 100 % × $7 000 = $7 000 | **$7 000** ← manda esta |
En la cuenta quedan retenidos $14 000: los $7 000 de la venta + $7 000 tuyos.
**En acciones de menos de $5, para shortear $X necesitas al menos $X de tu dinero** (y más en acciones de centavos por la regla de $2.50).
Muchos brókers exigen **todavía más** en acciones HTB.
- Si la acción sube, el requisito sube → te pueden pedir más dinero (*margin call*) o cerrar tu posición.
- **Regla PDT:** eliminada. La SEC aprobó en abril de 2026 quitar el mínimo de $25 000; en vigor desde el 4 de junio de 2026, con plazo para los brókers hasta octubre de 2027. Confirma cómo lo aplica el tuyo.
- **Liquidación T+1:** las operaciones se liquidan al día hábil siguiente.

## 7. Resumen: la lista de chequeo antes de cada corto
1. ¿Hay **locates**? ¿Cuánto cuestan por acción? ¿Compensa frente al recorrido esperado?
2. ¿Tiene **SSR** hoy? → ¿cómo voy a entrar (límite en rebotes)?
3. ¿Ha tenido **halts al alza** hoy? ¿Cuánto podría saltar en una reapertura contra mí?
4. ¿Cuánto **margen** inmoviliza esta posición a este precio?
5. ¿La mantengo **overnight**? → coste de préstamo por día + riesgo de recall + riesgo de noticia/gap al alza.
6. ¿Mi **pérdida máxima realista** (stop + salto por halt) cabe en mi riesgo por operación?

## 8. Ejercicios
1. Averigua en tu bróker (o en el que piensas usar): ¿cobra locates por acción o tasa anual? ¿Cuánto costaba ayer localizar una acción de la lista de gappers?
2. Calcula: shortear 2 000 acciones a $3.50 con locate de $0.06 → ¿cuánto pagas por el locate? ¿Qué % de la posición es? ¿Cuánto margen inmoviliza con la regla de $2.50/100 %?
3. Busca en tu plataforma o en la web (Nasdaq Trader → *Trading Halts*) los halts de ayer: ¿cuántos fueron LULD? ¿Alguno T1 o T12?
4. Mira un gapper que tuvo halts al alza: ¿a qué distancia reabrió respecto al precio de la parada?

En el Módulo 3 volvemos a EDGAR a un nivel profesional: calcular **exactamente** cuánto puede vender la empresa hoy (baby shelf, ATM restante, warrants, convertibles).
