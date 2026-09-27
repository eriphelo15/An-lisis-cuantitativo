# Módulo 1 — Por qué caen: la economía de las small caps

> Un short seller profesional no apuesta contra el precio: apuesta contra el **modelo de negocio** de la empresa.
> Si entiendes cómo se financian estas empresas, entiendes por qué la mayoría de los pumps terminan donde terminan.

## 1. La idea central en una frase
La mayoría de las small caps que se disparan **no ganan dinero, queman caja y necesitan vender acciones para sobrevivir**.
Cada subida fuerte es, para la empresa, **la mejor oportunidad del año para vender acciones caras**. Tú, como corto,
te pones del mismo lado que la empresa y sus banqueros: el lado que vende.

## 2. El ciclo de vida típico (el "ciclo de la dilución")
1. **La empresa quema caja.** Pierde, por ejemplo, $5 M por trimestre y tiene $8 M en el banco → le quedan ~5 meses (*runway*).
   Lo ves en el 10-Q: efectivo, flujo de caja operativo y, muchas veces, la frase *"substantial doubt about our ability to continue as a going concern"*.
2. **Prepara la munición.** Registra un *shelf* (formulario S-3) que le permite vender acciones rápido cuando quiera,
   o firma un programa **ATM** (*at-the-market*): un banco va vendiendo acciones directamente al mercado, poco a poco, sin anunciarlo el día a día.
3. **Llega el catalizador** (real o de humo): una nota de prensa, un contrato, un dato de un ensayo, un "pivot" a IA o cripto.
   Poco float + mucho volumen minorista = la acción sube 50 %, 100 %, 300 %.
4. **La empresa vende en la subida.** Por el ATM (en silencio, mientras sube) o con una oferta anunciada
   (*registered direct*, *public offering*), normalmente con **warrants** de regalo para los compradores.
5. **La acción vuelve a caer** (más acciones, mismo negocio). A menudo por debajo de donde empezó.
6. **Se repite** hasta que el precio baja de $1. La bolsa (Nasdaq) exige cotizar ≥ $1:
   30 días seguidos por debajo → aviso → 180 días para arreglarlo → **contra-split** (reverse split: 10, 20 o 50 acciones viejas = 1 nueva).
   El precio "sube" de golpe por aritmética y el ciclo vuelve a empezar desde el paso 1.

## 3. Lo que dicen NUESTROS datos (no opiniones)

### 3a. Toda la SEC, incluidas las empresas que ya murieron (sin sesgo de supervivencia)
12 646 empresas, 2014-2024. Crecimiento del número de acciones en 12 meses según su tamaño (*public float*):

| Tamaño | Diluyen > 20 % en un año | Duplican acciones (×2+) | Caída > 50 % del nº de acciones (contra-split) | Dejan de reportar en 2 años |
|---|---|---|---|---|
| < $50 M | **32 %** | **14 %** | **12 %** | **18 %** |
| $50-300 M | 22 % | 4 % | 5 % | 13 % |
| $300 M-2 B | 12 % | 2 % | 1 % | 9 % |
| > $2 B | 7 % | 2 % | 1 % | 6 % |

Cuanto más pequeña la empresa, más diluye, más contra-splits hace y más desaparece. La relación es escalonada y limpia.

### 3b. Los gappers (lo que tú vas a operar): qué pasa con sus acciones en los 12 meses siguientes
4 262 gappers (≥ +20 % de apertura, 2015-2026) con datos de la SEC antes y después, corrigiendo splits:

| Gap del día | Número de acciones 12 meses después (mediana) | Al menos duplican | Al menos ×5 | Hacen contra-split ese año |
|---|---|---|---|---|
| Todos (≥ 20 %) | **×1.72** | 45 % | 27 % | 33 % |
| 50-100 % | **×2.43** | 55 % | 34 % | 39 % |
| > 100 % | **×2.69** | 58 % | 36 % | 40 % |

- Por época: 2015-19 ×1.44, 2020-22 ×1.40, **2023-26 ×2.71** → el juego de la dilución se ha **intensificado**.
- Los 2 119 tickers que tuvieron algún gap hicieron **2 022 contra-splits** entre 2014 y 2026 (casi uno por empresa).
- Ojo: esto solo cuenta empresas que **siguen cotizando hoy**. Las que murieron diluyeron aún más. La realidad es peor para los largos.

### 3c. Lo que eso le hace al precio (del estudio 02, datos diarios 2015-2026)
- **Comprar la apertura del gapper (gap and go)** pierde en las tres épocas (−2 a −3 % por operación); solo el 28-33 % cierra por encima de la apertura.
- **Corto a los gaps > 100 %** (stop 30 %): +6.3 % / +7.5 % / +4.6 % por operación en las tres épocas.
- Cuanto más grande el gap, más grande el desvanecimiento posterior. **Encaja con 3b**: los gaps más grandes son los que más diluyen después.

## 4. Por qué NO es dinero fácil (y por qué eso es bueno para el que lo domina)
La ventaja existe porque el trade da **miedo** y es **difícil de ejecutar**:
- **Squeezes:** una acción que "debería" caer puede subir otro 200 % antes. El que entra demasiado pronto o demasiado grande muere.
- **Halts al alza:** tu stop no se ejecuta donde lo pusiste; reabre más arriba.
- **Locates:** las mejores acciones para shortear son las más difíciles de pedir prestadas, y caras.
- **Timing de la dilución:** la empresa puede NO vender todavía (le falta el S-3 efectivo, el baby shelf la limita, o espera más arriba).

Nuestro estudio lo mostró: si el stop del 30 % se ejecuta en +45 % por un halt, la ventaja del corto a gaps >100 % pasa de +5.3 % a −0.2 %.
**El dinero no está en saber que "caen"; está en saber CUÁNDO la empresa puede y quiere vender, y en sobrevivir al tramo en que todavía sube.**
Eso es lo que separa al short seller mediocre del mejor, y es exactamente lo que vamos a construir en los módulos 3 a 7.

## 5. Glosario del módulo
- **Float / public float:** acciones que se pueden negociar libremente (sin contar las de directivos y bloqueadas). En dólares, *public float* = float × precio.
- **Runway:** meses de caja que le quedan a la empresa al ritmo actual de pérdidas.
- **Going concern:** advertencia del auditor de que la empresa podría no sobrevivir 12 meses.
- **Shelf (S-3):** registro previo que permite vender acciones rápidamente durante 3 años.
- **ATM (at-the-market):** venta continua de acciones nuevas al mercado a través de un banco.
- **Registered direct / oferta pública:** venta de un bloque de acciones a inversores, casi siempre con descuento y con warrants.
- **Warrant:** derecho a comprar acciones nuevas a un precio fijo; si la acción sube por encima, se ejercen y aparecen más acciones.
- **Contra-split (reverse split):** juntar acciones viejas en menos acciones nuevas para subir el precio por encima de $1.

## 6. Ejercicios
1. Elige 3 gappers recientes de +100 % (del escáner o de la lista `smallcaps/res_02_gappers.csv`). En EDGAR (sec.gov), busca su último 10-Q y anota: efectivo, pérdida trimestral, runway en meses y si aparece *going concern*.
2. En la lista de documentos de cada una, busca si tiene un **S-3** o un **424B5** en los últimos 12 meses (señal de que puede vender acciones).
3. Mira el gráfico diario de un año de esas 3 acciones. ¿Dónde está hoy el precio respecto al día del gap? ¿Hubo contra-split?

En el Módulo 2 vemos la mecánica del corto: cómo se pide prestada la acción, qué cuesta, y todas las reglas (SSR, halts, recalls, margen y el fin del PDT).

---
Fuentes de datos: SEC EDGAR XBRL (`dei:EntityCommonStockSharesOutstanding`, `dei:EntityPublicFloat`), Yahoo Finance (precios y splits).
Scripts: `smallcaps/02_gappers.py`, `smallcaps/05_dilucion.py`.
