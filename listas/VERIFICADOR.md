# Verificador independiente del trabajo de campo

Creado el 1-oct-2026 a petición del usuario ("hay que buscarle una solución definitiva a los errores").
**Por qué existe:** quien construye el análisis comparte sus puntos ciegos con quien lo revisa si es la misma cabeza. El verificador es
un agente nuevo, sin el contexto de la conversación y **sin ver nuestras conclusiones**, que rehace el trabajo de campo de cada acción
importante desde las fuentes originales. Después se comparan los dos resultados; cada diferencia se resuelve leyendo la fuente antes de
publicar. Caso que lo motivó: CNTB 30-sep (secundario fallido en la presentación, ATM de $150 M en la shelf, reventa de 6.13 M acciones,
caja a hoy ≈ 2.9 meses) — un trader externo lo vio y nosotros no.

## Cuándo (RUTINA.md, paso 5c)
Para cada acción de la lista con **gap ≥ 50 %** o **tesis alta**, y para cualquiera que el usuario pida. Un agente por acción, en paralelo
y en segundo plano (Agent, subagent_type `general-purpose`). Tiempo objetivo: ≤ 10 minutos. Si no da tiempo, publicar la lista
marcando esas acciones como "verificación pendiente" y terminarla después.

## Encargo que se le da al agente (copiar tal cual, cambiando TICKER, FECHA y VENTANA)
> Eres un analista de short selling de small caps. Trabaja SOLO con fuentes primarias (EDGAR de la SEC: https://data.sec.gov/submissions/CIK##########.json,
> los índices de cada presentación y sus anexos; precios diarios de Yahoo `https://query1.finance.yahoo.com/v8/finance/chart/TICKER?range=1y&interval=1d`).
> Cabecera obligatoria para la SEC: `User-Agent: research eriphelo15 contact@example.com`. No uses ningún archivo de `listas/` ni `fichas/`
> (no debes ver conclusiones previas). Acción: **TICKER**. Día: **FECHA**. Ventana del catalizador: desde **VENTANA** (cierre anterior, 16:00 NY) hasta las 9:10.
> Devuelve SOLO un JSON con estas claves, cada dato con la **frase original en inglés**, su **URL** y la **cifra con unidad** (dólares o acciones):
> Horas de la SEC: usa SIEMPRE la hora 'Accepted' de la página índice de cada presentación (`…-index.html`), que es hora de Nueva York;
> el `acceptanceDateTime` del JSON de submissions trae a veces la hora de NY con una 'Z' falsa (presentaciones del mismo día) y otras veces UTC.
> 1. `catalizador`: documentos 8-K/6-K/notas de prensa DENTRO de la ventana; qué anuncian; si es acuerdo firmado (Item 1.01) o solo nota (7.01/8.01).
> 2. `negativos`: lo que NO dice el titular — leer TODOS los anexos (EX-99.1, EX-99.2 presentación…): objetivos no significativos o no cumplidos,
>    condiciones, "non-binding", cifras "up to", cliente sin nombre, financiación incluida.
> 3. `historial`: catalizadores de los 120 días anteriores y cómo reaccionó el precio ese día (cierre vs cierre anterior).
> 4. `shelves`: cada S-3/F-3/S-1/POS AM de 3 años: ¿de la empresa o REVENTA de terceros (selling securityholders)? importe base, ATM (importe y agente),
>    si se ha usado (buscar en el último 10-Q/10-K), y si es baby shelf (General Instruction I.B.6).
> 5. `reventas_eloc`: acciones registradas para reventa y líneas de capital (ELOC, VWAP shares, Yorkville, Lincoln Park…), ajustadas por contra-splits posteriores.
> 6. `ventas_recientes`: 424B de 90 días (precio y acciones) y colocaciones privadas (precio).
> 7. `warrants_convertibles`: precios de ejercicio de WARRANTS (no opciones de empleados), convertibles y si son de precio variable (tóxicas).
> 8. `caja`: caja + inversiones a corto plazo del último informe, flujo de caja operativo (dividido por los meses correctos), quema mensual y
>    **meses que quedan HOY** (restando los meses ya pasados desde el informe); going concern.
> 9. `acciones`: acciones en circulación (portada del último informe) y contra-splits de 2 años.
> 10. `dudas`: lo que no pudiste verificar.

## Comparación (la hace Claude, no el agente)
1. Poner lado a lado el JSON del verificador y la ficha de la lista (`listas/datos/FECHA_candidatos.json` + `_clasif.json`).
2. Para cada diferencia: abrir la fuente y decidir quién tiene razón. Si el error es nuestro → corregir el dato **y añadir un caso a
   `tests/casos_oro.py`** antes de darlo por resuelto. Si el error es del verificador → anotarlo.
3. Guardar `listas/datos/FECHA_verificacion.json`: `{"TICKER": {"estado": "ok" | "corregido" | "pendiente", "diferencias": [...], "hora": "HH:MM"}}`.
   `finalizar` da ERROR si falta la verificación de alguna acción con gap ≥ 50 % o tesis alta (salvo `--forzar`, que queda anotado).

## Otras defensas (todas obligatorias)
- `tests/casos_oro.py` (paso 1c de la rutina): cada error real del pasado es una prueba con el caso real. Si falla una, la rutina no sigue.
- Auditoría de `finalizar`: catalizador fuera de la ventana, negativos sin revisar, contrato real "no vinculante", cobertura del universo, etc.
- Contraste externo: cada vez que el usuario traiga el análisis de otro trader (Edu, Veprek, DilutionTracker…), comparar punto por punto;
  cada cosa que ellos vieron y nosotros no → caso de oro nuevo.
- Lenguaje: nunca decir "todo revisado". Decir exactamente qué se comprobó, contra qué y qué NO se comprobó.

## Registro de pruebas del verificador
- 30-sep CNTB (prueba del 1-oct, a ciegas): encontró los 4 puntos de Veprek (secundario no significativo en EX-99.2, asma 15-sep −32 %,
  ATM $150 M Cantor sin usar, caja ≈ 2.9 meses) y además: colocación privada de 6.13 M acciones a **$3.25** (mar-2026), baby shelf
  (I.B.5), la empresa dice tener caja para "at least one year", el 81 % del titular es 77 % (p 0.037) a 28 días exactos, la población es
  48-55 % Serbia. Destapó un error nuestro grave: horas de la SEC del mismo día 4 h antes (la "Z" falsa). Error suyo: tomó la hora del
  JSON como hora de NY en una presentación antigua (15-sep "11:06"; oficial 07:06). → Regla de horas añadida arriba.
