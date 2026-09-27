# Estudio cuantitativo NQ (1 minuto, 2021-03 → 2026-03)

Datos: `NQ_continuous.csv` (Drive, carpeta `continuous_contracts`). No se versiona; ruta vía `NQ_DATA_DIR` (default `/home/user/data`).

## Hallazgo crítico en los datos
El ajuste de contrato continuo del CSV está **mal hecho** (offset aplicado dos veces): la serie "cae" de 51k a 24k
cuando el NQ real subió de 13k a 25k, y hay saltos de −2,880…0 pts en cada roll. `01_limpieza.py` reconstruye el precio
real de cada contrato (validado contra mínimos históricos conocidos, error < 0.5%) y una serie back-adjusted correcta.
Probablemente los demás archivos (ES, YM, GC, 15y) tienen el mismo problema.

## Disciplina
- DEV = 2021-03 … 2024-12 (exploración). HOLDOUT = 2025-01 … 2026-03 (evaluado **una sola vez** con reglas congeladas).
- Costos: $5.76 RT (Tradeify, comisión + exchange) + 1 tick de slippage por lado = 0.788 pts/trade.
- Supuestos conservadores: entrada a la barra siguiente, stop antes que target si ambos en la misma barra.
- ~750 configuraciones registradas en `resultados/` para control de múltiples pruebas.

## Scripts (en orden)
| Script | Qué hace |
|---|---|
| 00_auditoria.py | Auditoría del CSV crudo |
| 01_limpieza.py | Reconstrucción de precios reales → parquet |
| 02_caracterizacion.py | Volatilidad, autocorrelación, variance ratio, día de semana |
| 03_eventos.py | Probabilidades de toque (gap fill, ONH/ONL, PDH/PDL), momentum intradía |
| 04_barreras.py | Fades/rupturas vs nulo martingala S/(S+T) |
| 05_estacionalidad.py | Slots de 30 min y calendario |
| 06_diario_reversion.py | IBS, RSI2, rachas bajistas |
| 07_dip_trend.py | "Comprar la caída en tendencia" sin solapamiento + grid |
| 08_intradia.py | ORB, VWAP, momentum/reversión 15 min |
| 09_ml.py | LightGBM walk-forward |
| 10_validacion_dev.py | Permutación, bootstrap, estrés de costos, vecindad |
| 11_holdout.py | Evaluación única del holdout (7 hipótesis congeladas, Holm) |
| 12_resumen.py | Serie completa de candidatos + JSON para el informe |

## Extensión a 15 años (`NQ_continuous_15y.csv`, 2010-10 → 2026-03)
Mismo error de ajuste continuo (2010 aparece en 165,181). Reconstrucción: `python 01_limpieza.py NQ_15y.csv nq15_1m.parquet`
(coincide con el archivo de 5 años en el tramo común). Los scripts usan `NQ_PARQUET=nq15_1m.parquet`; `BRUTO=1` mide en % del ATR por periodo.

| Script | Qué hace |
|---|---|
| 11_holdout.py (con EVAL_START/EVAL_END/TAG) | Prueba ciega de las 7 hipótesis congeladas en 2010-10 → 2021-03 |
| 14_por_año_15y.py | H1/H3/H5 por año en unidades relativas, contra su nulo |
| 04/08 con BRUTO=1 TAG=15y | Familias de niveles e intradía por periodo DEV/VAL1/VAL2 |
| 15_diario_calendario_15y.py | Reversión diaria, franjas de 30 min, calendario |
| 16_overnight_15y.py | Estrategia overnight vs RTH vs buy & hold |
| 17_secundarias_15y.py | Viernes de OPEX y momentum 15m por año |

Periodos: DEV 2010-10 → 2018-12, VAL1 2019-01 → 2021-03 (nunca vista), VAL2 2021-03 → 2026-03 (usada en el estudio de 5 años).
Resultado: las 3 candidatas de 5 años no replican; la deriva overnight es la única que pasa la regla pre-fijada.
