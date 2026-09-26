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
