# Lectura a ciegas del catalizador — lado LARGO (ronda 15, etapa B)

Definiciones fijadas en el pre-registro de la ronda 15 (`HIPOTESIS_SELECCION.md`, commit 59a072a). Quien lee NO ve precios, ni gráficos, ni
lo que hizo la acción después. Solo lee el texto de la SEC del evento (8-K/6-K + todos sus anexos EX-99) que se le entrega en un archivo local.
**Prohibido** abrir internet, Massive, Yahoo, Finviz o cualquier dato de precios, y prohibido leer `smallcaps/res_*`, `INFORME_*`, `CLAUDE.md`.

## Pregunta única: ¿esta noticia cambia la empresa a mejor de forma concreta y verificable?
Elegir UN `tipo` (si hay varias noticias en el evento, la más importante; si una de ellas es financiación de la empresa, ver FINANCIACION):

| tipo | Cuándo |
|---|---|
| CONTRATO_FIRME | Acuerdo, pedido, licencia o adjudicación YA FIRMADO, contraparte con nombre, importe en dólares concreto (o calculable del texto). No: "hasta", marco sin pedido mínimo, LOI, MOU, "no vinculante", "potencial". |
| FDA_APROBACION | Aprobación / autorización de comercialización (FDA, EMA, NMPA, PMDA, Health Canada) o 510(k)/De Novo concedido. No: aceptación de solicitud, designación (Fast Track, Orphan, BTD), fecha PDUFA, reunión. |
| DATOS_POSITIVOS | Ensayo clínico fase 2 o 3 que CUMPLE su objetivo principal con significación estadística (p < 0.05 o equivalente dicho en el texto). No: fase 1, preclínico, "tendencia", datos parciales sin objetivo principal, objetivo principal fallido. |
| RESULTADOS_FUERTES | Resultados (trimestrales/anuales/preliminares) con ventas ≥ +30 % frente al mismo periodo del año anterior Y (beneficio operativo positivo o pérdida operativa claramente menor), O subida explícita de previsiones (guidance raise). |
| INVERSION_ESTRATEGICA | Una empresa operativa (no un fondo/inversor financiero) compra acciones de la empresa a precio igual o superior al de mercado. |
| ADQUISICION_DE_LA_EMPRESA | La empresa va a ser comprada / fusionada con prima (el precio queda topado). |
| FINANCIACION | Oferta de acciones, colocación privada (PIPE), registered direct, convertible, warrants, ELOC/SEPA/equity line, ATM, inducement de warrants, préstamo/deuda relevante. **Si el evento incluye una financiación de la empresa junto con otra noticia, el tipo es FINANCIACION.** |
| HUMO | LOI, MOU, acuerdo no vinculante, alianza/colaboración sin importe, cifras "hasta"/"potencial", patentes, preclínico, giro a IA/cripto/tesorería de criptomonedas, recompra simbólica, "explorar alternativas", premios, ferias. |
| NEGATIVO | Ensayo fallido, pérdida de contrato/cliente, going concern, aviso de deslistado, impago, rechazo regulatorio (CRL), dimisión de auditor. |
| RUTINARIO | Junta/votaciones, nombramientos, presentaciones a inversores, fecha de resultados, cumplimiento de bolsa recuperado, resultados que NO cumplen RESULTADOS_FUERTES, contra-split, cambio de nombre, todo lo demás. |

## Campos de salida (una fila por evento, JSON Lines)
- `id`: el nombre del archivo sin `.json` (p. ej. `1234567_2025-03-04`).
- `tipo`: uno de la tabla.
- `importe_usd`: importe en dólares del contrato / inversión / ventas del periodo (número, sin texto); `null` si no hay. Convertir "million" ×1e6.
  Si el importe está en otra moneda, convertir solo si el propio texto da el equivalente; si no, `null` y anotarlo en `nota`.
- `contraparte`: nombre de la otra parte (o `null`).
- `frase_en`: frase LITERAL copiada del texto (sin cambiar una letra) que justifica el tipo; para CONTRATO_FIRME debe contener el importe.
- `negativos`: lista de frases literales que restan (financiación en el mismo documento, "up to", "non-binding", objetivo no cumplido…); `[]` si no hay.
- `crecimiento_ventas_pct` (solo RESULTADOS_FUERTES/RUTINARIO de resultados): número si el texto permite calcularlo.
- `confianza`: alta / media / baja.
- `nota`: una frase en español explicando la decisión.

Reglas: ante la duda entre un tipo que pasa (CONTRATO_FIRME, FDA_APROBACION, DATOS_POSITIVOS, RESULTADOS_FUERTES, INVERSION_ESTRATEGICA) y uno
que no pasa, elegir el que NO pasa y poner `confianza: baja`. No inventar cifras: si no está en el texto, `null`.
