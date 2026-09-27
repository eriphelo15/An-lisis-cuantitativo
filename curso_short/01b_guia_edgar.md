# Módulo 1 · Práctica — Cómo usar EDGAR paso a paso (con un ejemplo resuelto: AEMD)

## Qué es EDGAR
EDGAR es la base de datos pública y gratuita de la **SEC** (el regulador de la bolsa de EE. UU.). Toda empresa que cotiza
está obligada a subir ahí sus informes y cada vez que vende acciones. No hace falta cuenta ni pagar nada.
Está en inglés; aquí tienes lo necesario para moverte.

## Paso 1 — Entrar y buscar la empresa
1. Abre **https://www.sec.gov/edgar/search/**
2. Arriba verás un buscador que dice **"Company and person lookup"** (o "Company name, ticker, CIK number…").
   Escribe el **ticker** (ej. `AEMD`). Aparece el nombre de la empresa (Aethlon Medical, Inc.) → haz clic.
3. Llegas a la **página de la empresa**. Atajo directo: `https://www.sec.gov/edgar/browse/?CIK=AEMD` (cambia AEMD por el ticker).

## Paso 2 — Entender la lista de documentos ("Filings")
En la página de la empresa hay una tabla con todos los documentos, del más nuevo al más viejo. Columnas importantes:
- **Form type** (tipo de documento) · **Filing date** (fecha en que se subió) · un enlace para abrirlo.
- Puedes filtrar escribiendo el tipo en la caja de búsqueda de la tabla (ej. `10-Q`), o desplegar "View filings" / "Filing type".

Los tipos que un short seller mira SIEMPRE:
| Documento | Qué es | Por qué te importa |
|---|---|---|
| **10-Q** | Informe trimestral | Caja, pérdidas, going concern, ofertas recientes, warrants |
| **10-K** | Informe anual | Lo mismo, más completo |
| **8-K** | "Aviso de hecho relevante" | Ofertas, fusiones, contratos, avisos de Nasdaq, contra-splits. Se sube en 4 días hábiles |
| **S-3** | Registro "shelf" | La empresa queda lista para vender acciones rápido durante 3 años |
| **S-1** | Registro para ofertas (empresas que no pueden usar S-3) | Venta de acciones preparándose |
| **424B5 / 424B4 / 424B3** | Prospecto de una venta concreta | **La venta de acciones está ocurriendo**: cuántas, a qué precio, warrants |
| **EFFECT** | La SEC declaró efectivo un registro | Desde ese momento la empresa YA puede vender |
| **DEF 14A / PRE 14A** | Convocatoria de junta | Suelen pedir permiso para contra-splits o para emitir más acciones |
| **4 / 13G / 13D** | Compras/ventas de directivos y grandes accionistas | Quién tiene acciones y quién vende |

## Paso 3 — Abrir el 10-Q y sacar los números (Ejercicio 1)
1. En la tabla, busca el **10-Q** más reciente → clic en él (a veces primero aparece una página índice: haz clic en el documento `.htm` principal).
2. Se abre el informe en el navegador. Usa **Ctrl+F** (en Mac **Cmd+F**) para buscar dentro:
   - `Cash and cash equivalents` → en el **balance** (Balance Sheet). Toma la cifra de la primera columna (la más reciente).
   - `Net cash used in operating activities` → en el **flujo de caja** (Statements of Cash Flows). Es lo que la empresa quemó en el periodo.
   - `going concern` → la advertencia de que podría no sobrevivir 12 meses.
   - `at-the-market` → si vende acciones por ATM y cuánto vendió.
   - `subsequent event` → lo que pasó DESPUÉS del cierre del trimestre (ofertas, contra-splits). Muy importante.
   - `reverse stock split` → contra-splits.
   - `warrants outstanding` → warrants pendientes (acciones que pueden aparecer).
3. Calcula el runway: **caja ÷ (caja quemada por mes)**. Si el 10-Q es trimestral, caja quemada por mes = "net cash used" ÷ 3.

## Paso 4 — Buscar las ventas de acciones (Ejercicio 2)
En la tabla de documentos de los últimos 12 meses busca **S-3, S-1, EFFECT, 424B…** y los **8-K**. Abre los 8-K y mira el
**"Item"** que declaran (lo ves al leer el documento):
- **Item 1.01** (acuerdo importante): casi siempre una oferta ("Securities Purchase Agreement") o una fusión.
- **Item 3.01**: aviso de Nasdaq por incumplir reglas (precio < $1, patrimonio insuficiente…).
- **Item 3.02**: venta de acciones no registradas (colocación privada).
- **Item 5.03**: cambios de estatutos, a menudo el **contra-split**.
- **Item 8.01 / 7.01**: otros hechos / nota de prensa.

**Truco — búsqueda por texto completo:** en https://www.sec.gov/edgar/search/ usa el buscador grande (Full-Text Search):
escribe `"reverse stock split"` o `"going concern"`, pon el ticker en "Entity name" y te encuentra todos los documentos que lo mencionan.

## Paso 5 — Precio y contra-split (Ejercicio 3)
En TradingView, gráfico **diario** del ticker. Compara el precio de hoy con el del día del gap y busca saltos bruscos que no
son de mercado (el contra-split). Confírmalo en EDGAR con Ctrl+F `reverse stock split` en el 10-Q o en un 8-K (Item 5.03).

---

## EJEMPLO RESUELTO: AEMD (Aethlon Medical) — gap de +493 % el 17-sep-2026
Todo esto sale de documentos públicos en EDGAR (enlaces al final).

**Ejercicio 1 — La caja (10-Q del trimestre a 30-jun-2026, subido el 13-ago-2026)**
- Caja: **$4.93 M**. Caja quemada en el trimestre: **$1.90 M** → ~$0.63 M/mes → runway ≈ **8 meses**
  (la empresa dice que, con la oferta de julio, llega a 12 meses; el auditor ya no marca *going concern*, pero es gracias a vender acciones).
- Pérdida del trimestre: $1.55 M. Vive de vender acciones: en ese mismo trimestre vendió **$1.9 M por ATM** con H.C. Wainwright.

**Ejercicio 2 — La munición**
- **S-3 con ATM** (banco H.C. Wainwright). En junio ajustó cuánto puede vender por la **regla del baby shelf** (I.B.6):
  su public float era solo $7.2 M, así que solo puede vender 1/3 de eso por año por esa vía.
- **S-1 (junio) → EFFECT (6-jul) → 424B3 (7-jul) → 8-K (8-jul):** oferta pública de **$4.0 M a $0.71** por acción con Maxim Group,
  con **warrants para 5.63 M acciones a $0.71** (+ pre-funded warrants). Antes de la oferta tenía 2.37 M acciones; después, unas 8 M.
- **31-jul: contra-split 1 por 5.** Las acciones medias del trimestre pasaron de 41 529 (un año antes, ajustado) a 384 705 → **×9 en un año**.
  Los warrants de julio quedan en unos **1.13 M a ~$3.55** (0.71 × 5).
- **17-sep: 8-K + 425 → FUSIÓN** con North Immunology (Items 1.01 y 5.01, *cambio de control*). Ese es el catalizador del +493 %.

**Ejercicio 3 — La lectura de short seller**
- Abrió a $8.48 con ~1.6 M acciones en circulación. Los warrants a ~$3.55 están **muy "en el dinero"**: quien los tiene puede
  ejercerlos a $3.55 y vender a $8 → hasta **~1.13 M acciones nuevas**, cerca de un **70 %** más de oferta sobre las existentes.
  (Revisar en la convocatoria de junta —DEF 14A del 1-sep— si ya tienen permiso para ejercerse.)
- Además quedan el ATM vivo y la fusión (que suele traer más acciones).
- Resultado del día: abrió $8.48, máximo $9.50, **cerró $6.78**.

Así se piensa: **no "está muy subida"**, sino "hay 1.1 M de acciones a $3.55 esperando para venderse y un ATM activo".

Enlaces (EDGAR):
- Página de la empresa: https://www.sec.gov/edgar/browse/?CIK=882291
- 10-Q jun-2026: https://www.sec.gov/Archives/edgar/data/882291/000168316826006347/aethlon_i10q-063026.htm
- Prospecto oferta jul-2026: https://www.sec.gov/Archives/edgar/data/882291/000168316826005322/aethlon_424b3.htm
- ATM / baby shelf (424B5 jun-2026): https://www.sec.gov/Archives/edgar/data/882291/000168316826004539/aethlon_424b5.htm
- 8-K fusión 17-sep-2026: https://www.sec.gov/Archives/edgar/data/882291/000168316826007206/aethlon_8k.htm

Ahora te toca: **GIPR** (gap 18-sep) y **APUS** (gap 24-sep) con los mismos pasos.
