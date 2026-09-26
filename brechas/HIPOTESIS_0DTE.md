# Hipótesis de la época 0DTE, registradas ANTES de la prueba final

**Fecha de registro:** 2026-09-26. Queda fijada por el commit de git que añade este archivo.

## Mecanismo común
Desde 2021-22, el volumen de opciones que vencen el mismo día (0DTE) es enorme. La literatura (Dim, Eraker, Vilkov) dice:
- cuando los creadores de mercado tienen **gamma positiva**, cubren **contra** el movimiento, y eso produce **reversión intradía** y atracción hacia los strikes;
- con gamma negativa, cubren **a favor**, y eso produce **continuación**.

No tenemos datos de gamma. Por eso usamos aproximaciones:
- **VIX bajo** (por debajo de su mediana de 252 días): gamma positiva más probable;
- **VIX alto**: gamma negativa más probable.

## Reglas generales (iguales para todas)
- Instrumentos: NQ, ES e YM. **El veredicto se da sobre NQ.** ES e YM solo sirven de confirmación.
- Periodo de desarrollo (DEV0): 2021-03-15 a 2023-12-31.
- **Prueba final (FINAL): 2024-01-01 a 2026-03-13.**
- Operaciones por tiempo, sin stop, entrada y salida a mercado. Coste: comisión + 1 tick por lado.
  Resultado en puntos, reescalado al ATR de hoy. Una operación por hipótesis y día.
- Ningún umbral se optimiza. Los umbrales de tamaño ("movimiento grande") son el tercil superior de |movimiento| en DEV0, y se aplican tal cual en FINAL.
- **Criterio de éxito:** en NQ, resultado medio > 0 en DEV0 **y** en FINAL, con t ≥ 2.0 en FINAL (unilateral). Con 8 hipótesis, corrección de Holm: la mejor necesita p < 0.05/8 ≈ t 2.5.

## Hipótesis
| # | Nombre | Regla exacta | ¿Contaminada? |
|---|---|---|---|
| H1 | Reversión del cierre | Si el movimiento cierre de ayer (16:00) → 10:00 es grande, abrir en contra a las 15:30 y cerrar a las 15:59 | **Sí**: vi su agregado 2021-26 |
| H2 | Reversión de la tarde | Si el movimiento 10:00 → 14:00 es grande, abrir en contra a las 14:00 y cerrar a las 15:50 | No |
| H3 | Reversión tras latigazo de 30 min | Primera ventana de 30 min entre 10:00 y 15:00 (en saltos de 30 min) con movimiento > 0.25 ATR: abrir en contra 30 min | No |
| H4 | Imán de strikes al cierre | A las 15:00, si el precio está a menos de 0.1 ATR del número redondo más cercano (NQ 100, ES 25, YM 200 pts) y no está encima: abrir hacia él y cerrar a las 15:59 | No |
| H5 | Gamma por VIX (tarde) | Movimiento 09:30 → 13:00. Con VIX de ayer por debajo de su mediana de 252 días: abrir en contra a las 13:00 hasta 15:50. Con VIX por encima: abrir a favor | No |
| H6 | Gamma por VIX 9D/VIX | Igual que H5, pero con el ratio VIX9D/VIX: < 1 → contra, > 1 → a favor | No |
| H7 | ORB 15 min en NQ | Máx/mín de 09:30-09:45; entrada stop en la ruptura, stop en el otro extremo, salida 15:55 | **Sí**: vi resultados por año |
| H8 | ORB solo con VIX bajo/alto | H7 solo en días con VIX de ayer por encima de su mediana de 252 días | Parcial |
