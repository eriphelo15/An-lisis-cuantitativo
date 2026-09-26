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

---
## Resultados (script `23_hipotesis_0dte.py`, ejecutado después del registro)
$ por operación con 1 NQ a la escala de volatilidad de hoy, con costes. DEV0 = 2021-03 a 2023-12, FINAL = 2024-01 a 2026-03.

| Hipótesis | DEV0 | FINAL | t FINAL | Veredicto |
|---|---|---|---|---|
| H1 reversión del cierre *(contaminada)* | +$233 (t 2.9) | +$62 | 0.67 | no pasa: se desvanece (en ES e YM igual) |
| H2 reversión de la tarde | −$395 | +$179 | 1.25 | no pasa |
| H3 reversión tras latigazo 30 min | −$132 | −$75 | −0.81 | no pasa |
| H4 imán de strikes | +$22 | −$77 | −0.85 | no pasa |
| H5 gamma por VIX | −$32 | −$92 | −0.79 | no pasa |
| H6 gamma por VIX9D/VIX | −$33 | +$220 | 1.90 | no pasa |
| H7 ORB 15 min *(contaminada)* | +$276 (t 2.2) | +$291 | 1.98 | justo en el límite |
| H8 ORB con VIX alto *(parcial)* | +$284 | +$488 | 2.28 | pasa t ≥ 2.0, **no** pasa la corrección de Holm (2.5) |

**Conclusión:** ninguna hipótesis nueva sobre gamma, strikes o reversión funciona.
La única señal persistente de la época es el **ORB de 15 min en NQ**, sobre todo con el VIX por encima de su mediana anual. Es positivo en 2021-23 y en 2024-26 (acierto 41-44%).
En ES e YM no funciona. Como ya había visto sus resultados por año, la evidencia es buena pero no ciega: **candidato para operar en pequeño, no una ventaja confirmada.**
