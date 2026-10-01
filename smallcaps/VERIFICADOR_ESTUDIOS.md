# Verificador independiente de los estudios

Creado el 1-oct-2026 a petición del usuario (tercera mejora del sistema anti-errores). **Por qué:** el verificador de `listas/VERIFICADOR.md`
cubre el trabajo de campo de cada acción, pero NO las cifras de los estudios que usa el Radar (puntuación de la tesis, estadísticas de base).
Un error en los datos de un estudio (p. ej. la lista de splits de Yahoo incompleta, encontrada el 1-oct) pasa a todas las listas sin que
nadie lo vea. Aquí un agente nuevo, sin acceso a nuestros scripts ni resultados, rehace el estudio desde los datos originales y la
definición escrita; después se comparan las cifras caso a caso.

## Cuándo
- Antes de que una cifra de un estudio entre en el Radar (factor nuevo, pesos nuevos, estadística nueva).
- Cuando se corrija un dato de entrada de un estudio que ya usa el Radar.
- Una vez para lo que ya está en uso: ronda 12 (puntuación de la tesis) — hecho el 1-oct (ver registro).

## Reglas del encargo
- El agente NO puede leer: `smallcaps/*.py`, `smallcaps/res_*.csv`, `smallcaps/puntuacion_pesos.json`, `INFORME_*.md`, `CLAUDE.md`,
  `listas/`, ni nada que contenga nuestros resultados. Solo los datos originales y la definición escrita del estudio.
- Debe obtener el precio real por su cuenta y con dos fuentes (regla de `smallcaps/PROTOCOLO_ESTUDIOS.md`).
- Devuelve: sus cifras + la lista de casos usados (sym, fecha, R, factores) en un CSV en el scratchpad, para comparar caso a caso.

## Comparación (la hace Claude)
1. Casos: los que están en una lista y no en la otra → explicar cada grupo (filtro de precio, emparejamiento de etiquetas…).
2. Para los casos comunes: R y factores idénticos. Cada diferencia se resuelve leyendo la fuente.
3. Cifras finales: si la conclusión cambia, el Radar no usa la cifra hasta resolverlo. Error nuestro → caso de oro nuevo.

## Registro
- **1-oct, ronda 12 (puntuación de la tesis), réplica a ciegas en 6 min:** el agente usó 1 277 casos; los nuestros (1 222) están TODOS en su
  lista, con R y etiqueta idénticos, y venta90 / s3 / serie idénticos en todos. Diferencias encontradas, todas resueltas leyendo la fuente:
  (a) **error nuestro:** la ventana del catalizador usaba `pd.offsets.BDay` sin festivos → GNPX 21-ene-2020 y UUU 2-sep-2025 tenían
  'solo nota de prensa' cuando el viernes por la tarde hubo un 8-K con Item 1.01 / 5.03 (366 eventos tras festivo; 7 cambian de factor;
  5 etiquetados con documentos no leídos: ninguno cambia de etiqueta); (b) **error nuestro:** Yahoo lista splits recientes que aún no
  aplica a sus precios → CPOP 10-sep-2025 ($2.10, no $0.14) y YAAS 27-abr-2026 ($1.445, no $0.29), confirmado con Massive; (c) decisión
  distinta, no error: 50 casos con split en el mismo mes que nosotros excluimos y él resolvió con fechas exactas.
  Resultado: VAL tesis alta + gap ≥ 50 %: nuestro original +0.26R PF 1.86 (160) · corregido +0.25R PF 1.81 (157) · verificador +0.24R
  PF 1.74 (203); alto − bajo t 2.97 / 2.77 / 2.98. **La conclusión se mantiene.** El Radar pasa a los pesos corregidos
  (`30_ronda12_corregida.py`; anteriores en `puntuacion_pesos_v1_30sep.json`). Casos de oro 27 y 28.
