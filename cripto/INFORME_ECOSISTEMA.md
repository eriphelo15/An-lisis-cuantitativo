# Cripto — ecosistema completo: catalizadores, memecoins y ciclos

Pre-registro: `HIPOTESIS_ECOSISTEMA.md` (commit 16c0275). Datos: 733 monedas spot + 860 perpetuos de Binance
(incluidas 190 ya retiradas), velas diarias y horarias 2017-2026; 2 706 anuncios oficiales de Binance con hora exacta;
precios de OKX para monedas que cotizaban fuera antes de llegar a Binance; funding real de cada perpetuo.
Costo 0.10 % por lado. Scripts `eco_01` … `eco_05`.

## Lo que SÍ funciona (catalizadores)

### 1. Corto tras anuncio de retiro (delisting) de Binance — el más limpio
Entrar en corto en el perpetuo al cierre de la vela horaria del anuncio (se pierde la caída de los primeros minutos, media −8 %) y salir a las 4 h.
| | n | neto por operación | t | % ganadoras |
|---|---|---|---|---|
| Todo (2022-2026) | 67 | +6.6 % | 4.9 | 75 % |
| 1ª mitad (hasta 2026-02) | 33 | +6.2 % | 2.5 | 67 % |
| 2ª mitad | 34 | +7.0 % | 6.2 | 82 % |
- Funding casi nulo en 4 h (−0.08 %). El perpetuo sigue abierto (ningún anuncio de cierre de futuros en ±3 días).
- Liquidez del perpetuo: mediana $1.2 M por hora (p25 $0.6 M) → posiciones de miles, no de cientos de miles.
- Peor operación −39 % (BSW). Pocos eventos antes de 2024 (2023: 3 eventos, negativo). Solo existe desde 2022 → no hay DEV antiguo; se validó por mitades.

### 2. Corto a nuevos listados spot ("vender la noticia")
Entrar en corto en el perpetuo al cierre del primer día de trading spot, salir a los 7 días.
- Pre-registrado (todas las monedas, precio spot): DEV +6.3 % (t 3.0), VAL +7.1 % (t 3.5), 68 % ganadoras. **Pasa la regla.**
- Ejecutado en perpetuo con funding (VAL, n=181): +8.0 % (t 2.6), 71 % ganadoras; ajustado a mercado (vs índice de alts) +7.2 % (t 2.4).
- Confirmado por otra vía: desde el anuncio de listado, a 7 días el precio cae −16 % (DEV, t −4.6) y −13.5 % (VAL, t −2.9).
- Riesgo de cola: memecoins como PNUT (+309 %) y NEIRO (+251 %) en la semana → pérdidas de −300 %.
  Sin memecoins: +12.3 % (t 5.5), 73 % ganadoras; con 5 % del capital por operación: 74 % de meses positivos, peor mes −5.7 %.
  **Ojo:** excluir memecoins se decidió DESPUÉS de ver esas pérdidas → necesita confirmación en vivo.
- Los stops (20-50 %) empeoran el resultado: es mejor tamaño pequeño que stop ajustado.

## Lo que NO funciona
| Idea | Resultado |
|---|---|
| Comprar al anuncio de listado | El salto (+22 % medio) ocurre en la misma hora del anuncio; después, 1-24 h ≈ 0 y luego cae. Solo gana quien llega en segundos (bots). |
| Comprar al anuncio de perpetuo | La moneda ya subió +27 % en las 24 h previas; después cae (−1.4 % en 1 h, t −3.3). |
| Corto tras pumps > 50 % | En precio spot parecía funcionar (+7.7 % a 3 días), pero en el perpetuo el funding que paga el corto (−2.7 % en 3 días) se lo come: +2.6 %, t 1.1. |
| Momentum cruzado (ganadoras vs perdedoras) | Nada: t entre −1.7 y +0.4. |
| Memecoins tras pumps | Muestra pequeña y sin consistencia. |

## La "lotería" (por qué parece que muchos se hacen millonarios)
Comprar cada moneda nueva de Binance al cierre de su primer día y mantener (658 monedas):
- 73 % pierde más de la mitad; 45 % pierde más del 90 %; mediana ×0.14.
- Solo 1.4 % termina ×10 o más (12.8 % llegó a ×10 en algún momento y lo devolvió).
- Solo 5 % le ganó a mantener BTC.
Memecoins en DEX (pump.fun): ~1.4 % de los tokens "gradúan", solo 3 % de usuarios ganó más de $1 000, y en 90 días
solo 6 % de 304 161 traders de memecoins en Solana tuvo ganancias. Los millonarios existen, pero son los que se ven entre cientos de miles que perdieron.

## Límites
- Sin datos de X/Telegram/rumores; el catalizador medible con hora exacta son los anuncios de Binance.
- Los catalizadores útiles son de 2023-2026 (pocos años). Necesitan seguimiento en vivo antes de poner dinero serio.
- Requieren cuenta en un exchange cripto con perpetuos (no Tradeify ni futuros CME).

## Los golpes de ×100 (10 000 %) — `eco_06_ganadoras.py`
Desde el cierre del primer día en Binance (658 monedas nuevas desde 2017-09):
| Llegó en algún momento a | % de monedas | Siguen ahí hoy | Días medianos hasta el pico | Caída mediana que hubo que aguantar antes del pico |
|---|---|---|---|---|
| ×10 | 16.3 % (107) | 9 | 514 | −86 % |
| ×100 | 2.3 % (15) | 2 | 592 | −84 % |
- Casi todos los ×10/×100 son monedas listadas en 2019-2020 que explotaron en la euforia de 2021. Listadas 2023-2026: 2 de 304 llegaron a ×10.
- De los que tocaron ×100, 13 de 15 devolvieron casi todo (hoy a −70 % / −100 % del pico). Para cobrarlo había que vender cerca del techo después de aguantar caídas de −80/−90 %.
- Algunos "picos del día 0" (APT, GAL, HFT, REEF…) son mechas del primer minuto de trading, no ganancias alcanzables.
- Hoy los ×100 ocurren ANTES de Binance, en DEX (pump.fun y similares), comprando a capitalizaciones de miles de dólares:
  - Solidus Labs: 98.6 % de los tokens de pump.fun muestran patrón de pump & dump o rug; de 7 M lanzados, solo 97 000 conservaron más de $1 000 de liquidez.
  - Dune: de ~44 000 tokens seguidos, 81 % nunca pasó de $500 k; 0.84 % llegó a $10-50 M; 2 superaron $1 000 M (PNUT, GOAT).
  - Los primeros compradores son bots "snipers" e insiders con monederos pre-fondeados (87 % de sus entradas ganadoras); solo 0.25 % de los traders de memecoins ganó más de $500 en 60 días.
- Conclusión: los ×100 son reales pero son lotería con ventaja para insiders y bots; no hay regla mecánica ni catalizador que los anticipe con los datos disponibles.
