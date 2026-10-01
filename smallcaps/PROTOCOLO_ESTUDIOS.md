# Protocolo obligatorio de los estudios (1-oct-2026)

Pedido por el usuario tras encontrar errores antiguos en los datos de los estudios (splits de Yahoo, ventana sin festivos).
Todo estudio cuyas cifras puedan llegar al Radar cumple estos pasos; el informe dice cuáles se hicieron y con qué resultado.

1. **Pre-registro** en `HIPOTESIS_SELECCION.md` antes de ver resultados (como siempre). Cambios después = enmienda fechada y explicada,
   hecha antes de mirar el resultado.
2. **Segunda fuente para todo dato externo.** Precios en dólares: precio exacto de Massive (velas de 1 min / diario sin ajustar) donde
   exista, y el informe da el % de coincidencia con el método usado. Splits: Yahoo y Massive. Horas de la SEC: hora oficial para lo reciente.
   Días hábiles: `comun.dia_habil_anterior` (con festivos), nunca `pd.offsets.BDay`.
3. **Control de calidad de lo extraído a mano o por texto** (precios de folletos, etiquetas): muestra al azar leída a mano con umbral escrito.
4. **Verificador independiente** (`VERIFICADOR_ESTUDIOS.md`) antes de que una cifra entre en el Radar: réplica a ciegas, comparación caso a caso.
5. **Caso de oro** en `tests/casos_oro.py` por cada error encontrado.
