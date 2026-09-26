# Cripto — hipótesis pre-registradas (antes de mirar resultados)

Datos: Binance USDT-M perpetuos BTCUSDT y ETHUSDT, 1 minuto, 2020-01 → 2026-08; funding cada 8 h.
Costo: 0.05% por lado (0.10% ida y vuelta) — equivale aprox. a taker Binance o micro BTC/ETH de CME con deslizamiento.
Periodos: DEV 2020-2022 (se eligen parámetros/direcciones), VAL 2023-2026-08 (solo confirmación).

**Regla de éxito (fijada ahora):** mismo signo en DEV y VAL, neto de costos, VAL con t > 2 en BTC,
y mismo signo en ETH (réplica). Corrección de Holm sobre las familias H1-H9 en VAL.

| # | Hipótesis | Base / origen | Prueba |
|---|---|---|---|
| H1 | Estacionalidad horaria | literatura de estacionalidad intradía en BTC | signo de cada hora UTC en DEV → operar esa hora en VAL (escaneo ciego, 24 horas) |
| H2 | Deriva alrededor del funding (00/08/16 UTC) | presión de cierre de posiciones antes del cobro | retorno 60 min antes / después, condicionado al signo del funding |
| H3 | Funding extremo contrario | exceso de apalancamiento de un lado | funding en decil superior (inferior) según DEV → corto (largo) 8 h y 24 h |
| H4 | Momentum intradía (1ª media hora → última) | Wen et al. 2022 | retorno 00:00-00:30 y 00:00-23:30 UTC → operar 23:30-24:00 |
| H5 | Momentum diario (TSMOM) | Liu & Tsyvinski 2021 | signo del retorno de 1/7/14/28 días → posición siguiente día |
| H6 | Reversión tras cascadas de liquidación | caídas/subidas bruscas por liquidaciones | movimiento 5 min > k × volatilidad (k de DEV) → contra 30/60 min |
| H7 | Efecto fin de semana | menor liquidez en fin de semana | retorno sábado-domingo y lunes vs resto |
| H8 | Tus estrategias y ORB | lo probado en NQ/GC | ORB 15 min en 00:00 UTC y 13:30 UTC (apertura NY); pullback VI filtrado y VI original en ventana NY |
| H9 | "El gap de CME siempre se llena" | folclore cripto | desde reapertura CME (domingo 22:00/23:00 UTC) hacia el cierre del viernes; probabilidad de llenado vs nivel aleatorio a la misma distancia |

Métricas de comodidad reportadas también: % ganadoras, meses positivos, peor racha, R² de la curva.
