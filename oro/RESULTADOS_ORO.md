# Oro (GC) — ¿se comporta igual que NQ?

Datos: GC continuo 1 minuto, 2021-03 a 2026-03 (reconstruido; el ajuste de rolls del CSV venía defectuoso igual que en NQ).
Costos: $5.76 + 1 tick por lado. DEV 2021-03..2023-06, VAL 2023-07..2026-03.

## Tramos y calendario (01_tramos_calendario.py)
- Ningún tramo horario predecible de forma estable.
- La única deriva es la tendencia alcista del oro en VAL (+9.9 pb/día), no un patrón intradía.
- FOMC / CPI / NFP: sin efecto consistente entre periodos (CPI alcista con muestra pequeña).

## Estrategias (02_estrategias.py), R por operación
| Estrategia | DEV | VAL |
|---|---|---|
| Pullback VI filtrado, ventana COMEX | -0.04 | -0.08 |
| Pullback VI filtrado, ventana NY | -0.01 | +0.045 |
| Pullback VI sin filtros, NY | +0.007 | +0.057 |
| Variantes con salida parcial | ~0 | ~0 |
| VI original | -0.06 (t -5) | -0.05 |
| VI original + parcial | ~0 | ~0 |
| ORB 15 min COMEX 08:20 (salida 13:30) | +0.10 (t 1.4) | +0.03 (t 0.4) |
| ORB 15 min 09:30 | +0.115 | -0.02 |

## Conclusión
El oro es tan eficiente intradía como NQ/ES. Los VI no tienen ventaja; el único candidato (ORB COMEX) no es significativo.
Limitación: solo 5 años de datos.
