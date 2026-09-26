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
