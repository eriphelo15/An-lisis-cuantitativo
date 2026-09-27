# Cripto (BTC y ETH) — resultados de las hipótesis pre-registradas

Datos: perpetuos Binance, 1 minuto, 2020-01 → 2026-08 (3.5 M velas por activo, sin huecos relevantes) + funding.
Costo 0.05 % por lado. DEV 2020-2022, VAL 2023-2026. Pre-registro: `HIPOTESIS_CRIPTO.md` (commit f1f7f46).
Scripts: `01_hipotesis.py` (H1-H7, H9), `02_orb_vi.py` (H8). Resultados completos en `res_01_hipotesis.csv`, `res_02_orb.csv`.

## Veredicto: ninguna hipótesis pasa la regla fijada de antemano

| # | Idea | Resultado (neto) |
|---|---|---|
| H1 | Hora del día | Las 24 horas pierden en VAL (−6 a −15 pb). Las horas "buenas" de DEV se invierten o desaparecen. El movimiento medio por hora (2-5 pb) es menor que el costo (10 pb). |
| H2 | Alrededor del cobro de funding | Negativo en todo. |
| H3 | Funding negativo → comprar 24 h | BTC DEV +73 pb (t 3.0), VAL +25 pb (t 1.5); ETH DEV +10, VAL +49. Único candidato, pero no llega a t > 2 en BTC VAL y las ventanas de 24 h se solapan (t real menor). Tampoco es intradía. |
| H4 | Momentum intradía (Wen 2022) | Negativo (−9 a −12 pb). No se replica. |
| H5 | Tendencia diaria 14/28 días | +9 a +11 pb/día en BTC, similar a comprar y mantener. Es seguimiento de tendencia de swing, no intradía; no apto para fondeo intradía. |
| H6 | Rebote tras cascadas de liquidación | Negativo: el precio sigue, no rebota lo suficiente para pagar costos. |
| H7 | Día de la semana | Miércoles/lunes positivos, jueves negativo en ambos periodos, pero t < 2 en todo. |
| H8 | ORB 15/30 min (00:00 UTC y apertura NY) | Negativo en VAL en BTC y ETH (−0.06 a −0.59 R). Los costos se comen 0.2-0.5 R por operación. |
| H8 | Tu VI | El VI en cripto no existe como tal: los "huecos" entre cuerpos son de 1 tick (mediana 0.02 pb); ninguna de tus reglas tiene sentido aquí. |
| H9 | "El gap de CME siempre se llena" | Falso: con stop simétrico se llena antes del stop el 41 % (BTC) y 44 % (ETH), peor que el azar (50 %). |

## Conclusión
Cripto no es más fácil que NQ intradía: los movimientos de minutos/horas son pequeños frente al costo y los patrones
populares (gap de CME, rebote de liquidaciones, horas mágicas) no se sostienen. Lo único con algo de señal es de
plazo de días (funding muy negativo, tendencia de 2-4 semanas), que es inversión de swing, no trading de fondeo intradía.
