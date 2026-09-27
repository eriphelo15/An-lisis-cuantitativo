# Módulo 3 — Leer la SEC como un short seller: ¿cuánto puede vender la empresa HOY?

> En el Módulo 1 aprendiste a ver SI una empresa necesita dinero. Ahora vas a calcular CUÁNTAS acciones puede
> soltar al mercado, POR QUÉ vía y CUÁNDO. Esa es la diferencia entre "está muy subida" y "hay 1.1 millones de
> acciones esperando para venderse a $3.55".

## 1. El mapa: las 7 vías por las que aparecen acciones nuevas
| # | Vía | Velocidad | Dónde se ve |
|---|---|---|---|
| 1 | **ATM** (venta directa al mercado por un banco) | Inmediata y silenciosa, durante la sesión | 424B5 "up to $X" + S-3 efectivo; lo vendido aparece en el siguiente 10-Q |
| 2 | **Oferta con S-3** (registered direct / oferta pública rápida) | De un día para otro (se anuncia por la tarde/noche, abre abajo) | 8-K + 424B5 |
| 3 | **Oferta con S-1** (empresas que no pueden usar S-3) | Lenta: la SEC revisa. Señal de inminencia: S-1/A con precio + **EFFECT** | S-1, S-1/A, EFFECT, 424B4 |
| 4 | **Warrants en el dinero** | Inmediata si están registrados; el tenedor ejerce y vende | 10-Q (tabla de warrants), 424B, 8-K de *inducement* |
| 5 | **Convertibles / preferentes** | Inmediata si son de precio variable (tóxicas) | 10-Q, 8-K Item 1.01/3.02 |
| 6 | **Reventa (resale)** de inversores privados (PIPE) | Cuando se declara efectivo su S-1/S-3 de reventa | S-1/S-3 con "selling stockholders" + EFFECT |
| 7 | **Línea de capital (ELOC / equity line)** | Continua: la empresa "pone" acciones al inversor (p. ej. Yorkville, Lincoln Park), que las vende | 8-K 1.01 + S-1 de reventa |

## 2. La regla del baby shelf (Instrucción I.B.6 del formulario S-3) — la más importante
Si el **public float** de la empresa es **menor de $75 M**, por su S-3 solo puede vender, en 12 meses, como máximo
**1/3 de su public float**.
- **Public float** = acciones en manos de NO afiliados (sin directivos ni grandes accionistas) × **el precio de cierre MÁS ALTO de los últimos 60 días**.
- Al límite se le restan las ventas hechas por esta vía en los 12 meses anteriores.
- **No cuentan** para este límite: ofertas por S-1, warrants, convertibles, reventas.
- Si el public float supera $75 M (con cualquier cierre de los últimos 60 días), **el límite desaparece**.

**Por qué esto es clave para ti:** un pump **aumenta el precio más alto de 60 días** → aumenta el public float →
**aumenta cuánto puede vender la empresa**. El pump literalmente le recarga la munición. Y si la empresa estaba topada,
el pump puede ser justo lo que necesitaba para volver a vender.

### Ejemplo real: AEMD (424B5 del 4-jun-2026, lo dice la propia empresa)
- Acciones de no afiliados: 2 337 629 · precio más alto de 60 días: $3.07 → **public float $7 176 521**.
- Límite de 12 meses: 1/3 → **$2 392 174**.
- Ya vendido por esta vía en 12 meses: **$1 849 457**.
- Capacidad restante: **$542 716** (es exactamente el "Up to $542,716" de la portada del 424B5).
- Tras el contra-split 1:5 y el pump de septiembre: ~711 000 acciones × cierre máximo de 60 días (~$6.8) ≈ **$4.8 M** de public float → límite ≈ $1.6 M,
  menos lo vendido en los últimos 12 meses → **capacidad por ATM casi agotada** (cálculo aproximado).
- **Lectura:** en AEMD la amenaza real NO es el ATM sino los **~1.13 M de warrants a $3.55** de la oferta de julio (que fue por S-1, fuera del límite).

## 3. Warrants: las 4 preguntas
1. **¿Precio de ejercicio vs precio actual?** Solo importan los que están EN el dinero (ajusta siempre por contra-splits).
2. **¿Están registrados?** Si las acciones del warrant están registradas (o hay reventa efectiva), se venden al instante. Si no, el tenedor espera a la registración o usa *cashless exercise* (regla 144, 6 meses).
3. **¿Tienen "blocker"?** Suelen limitar al tenedor a 4.99 %/9.99 % de la empresa: ejerce por tandas, vende y vuelve a ejercer. No frena la venta, la reparte en el tiempo.
4. **¿Tienen reset / ajustes?** Cláusulas que bajan el precio de ejercicio si hay contra-split u ofertas más baratas (GIPR: precio con "floor" de $0.0562). Los *inducements* (GIPR 18-sep) bajan el precio a cambio de ejercer YA.

## 4. Convertibles y preferentes
- **Precio fijo:** solo convierten si la acción está por encima del precio de conversión.
- **Precio variable (tóxicas):** convierten a un **descuento** sobre los precios más bajos recientes (ej. GIPR: 80 % del promedio de los 3 precios más bajos de 10 días).
  Cuanto más cae la acción, más acciones reciben → venden → cae más. Frase delatora: *"number of shares … not determinable"*.
- **Tope del 19.99 % (regla 5635(d) de Nasdaq):** emitir más del 20 % de las acciones con descuento requiere aprobación de la junta.
  Si ves una **junta (DEF 14A/PRE 14A) que pide aprobar la emisión** para warrants o convertibles → dilución grande en camino.

## 5. Señales de que una oferta es INMINENTE
- **S-1/A** que ya incluye precio o número de acciones, o un **FWP** (free writing prospectus).
- **EFFECT** recién publicado (la SEC declaró efectivo el registro): muchas ofertas se fijan esa misma tarde/noche.
- **Junta que aprueba aumentar las acciones autorizadas** o la emisión del 20 %.
- Pump + empresa con **runway corto** + S-3 efectivo con capacidad → oferta muy probable en 0-2 días.
- Bancos colocadores habituales en small caps: H.C. Wainwright, Maxim, Aegis, ThinkEquity, A.G.P., Dawson James, Spartan, Univest…
  Ver su nombre en un 8-K o 424B es señal de que la empresa está en "modo financiación".

## 6. Señales de que NO puede vender (todavía) → más riesgo de squeeze
- Sin S-3 efectivo, sin ATM, sin warrants en el dinero registrados.
- **Lock-up de la empresa:** tras una oferta, la empresa suele comprometerse a NO emitir más durante 30-90 días (lo dice el 424B/8-K: *"lock-up"*, *"will not issue … for a period of"*).
- **Baby shelf agotado** (como AEMD por ATM).
- Conversiones que requieren aprobación de junta aún pendiente (APUS: preferentes a la espera de la conversión).

## 7. Nasdaq: el reloj que obliga a diluir
- **Precio < $1 durante 30 días hábiles** → aviso (8-K Item 3.01) → 180 días para recuperar ($1 durante 10 días seguidos); a veces 180 más.
- **Patrimonio < $2.5 M** (Capital Market) → aviso; se cumple vendiendo acciones (GIPR tiene patrimonio negativo).
- **Reglas endurecidas en 2025:** si la empresa ya hizo un contra-split en el último año y vuelve a caer de $1, **no tiene periodo de gracia**;
  y si acumula contra-splits de 250:1 o más en 2 años, tampoco. Resultado: más contra-splits agresivos y más urgencia de subir el precio o el patrimonio.

## 8. La "cuenta de munición" (lo que harás con cada gapper)
| Vía | Acciones o $ disponibles HOY | ¿Registrado/efectivo? | Precio vs actual |
|---|---|---|---|
| ATM / baby shelf | $ restantes | S-3 EFFECT sí/no | — |
| Warrants | nº | sí/no | ejercicio $X vs precio $Y |
| Convertibles | nº o "variable" | — | conversión $X o % descuento |
| Reventa PIPE | nº | EFFECT sí/no | — |
| **Total en acciones vs acciones en circulación** | **× veces** | | |

Regla práctica: **munición inmediata > 30-50 % de las acciones en circulación + pump fuerte = la oferta de acciones nuevas llegará**.
Munición ≈ 0 y float diminuto = no pelees el primer tramo: espera debilidad confirmada.

## 9. Ejercicios
1. Abre el 424B5 de AEMD del 4-jun-2026 (enlace en la ficha) y encuentra tú mismo las tres cifras del baby shelf: public float, ya vendido, capacidad restante.
2. Rellena la "cuenta de munición" de **GIPR** con lo que ya sabes (warrants del inducement, nota de Silverback, 424B de junio).
3. Busca en EDGAR un **FWP** o un **S-1/A** reciente de cualquier small cap (Full-Text Search, tipo de formulario) y dime: ¿qué empresa, cuántas acciones y a qué precio pensaba vender?
