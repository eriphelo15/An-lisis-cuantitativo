# Radar de memecoins (Solana)

Registra los tokens nuevos de Solana y vuelve a mirarlos a los **30 min, 1 h, 6 h y 24 h**
para medir con datos reales qué señales separan a los que se duplican de los que mueren.
**No compra ni vende nada.**

## Cómo funciona

1. **Escaneo:** lee los pools nuevos y en tendencia de GeckoTerminal. Registra cada token con
   una actividad mínima (capitalización de $10K a $5M, liquidez de al menos $5K, menos de
   24 h de vida y al menos 25 compradores en la última hora). A cada uno le pasa RugCheck y
   consulta en GeckoTerminal sus holders: cuántos hay, qué % tienen los 10 mayores y si las
   autoridades de mint y freeze están revocadas.
   - **Narrativa:** clasifica cada token por su nombre (videojuegos, IA, política, Elon,
     celebridades, animales, cripto) en `radar_memes/narrativas.py`. Mide el **calor** (cuántos
     tokens del mismo tema hay en el escaneo) y si el token es el **líder** de su narrativa
     (el de más liquidez) o un seguidor/clon.
   - **Catalizadores:** fechas de eventos por narrativa en `radar_memes/catalizadores.json`
     (lanzamiento de GTA 6, elecciones de EE. UU., festividades). Se pueden añadir más editando
     ese archivo.
   - **Palabras calientes:** cuántos tokens del escaneo comparten palabra con el token. Así se
     detectan temas nuevos que no están en la lista (p. ej. "Newscum" apareció en 17 tokens a la
     vez antes de añadirlo a política).
   - **Carteras compradoras:** guarda las carteras que compraron cada token (compras de $100 o
     más) en `carteras.csv`, para encontrar las que entran temprano una y otra vez en los que
     luego suben.
2. **Filtro v1:** marca qué tokens habría elegido el filtro. **Es una hipótesis, no una
   recomendación**; se registran también los descartados para poder compararlos.
   Criterios (en `radar_memes/escaner.py`, `FILTRO`):
   - Sin peligros en RugCheck y sin otro token con el mismo símbolo (clones). Si RugCheck no
     responde (pasa a menudo), el token no se descarta: queda como "sin datos" en el informe.
   - Capitalización de $50K a $1.5M.
   - Liquidez entre el 8% y el 60% de la capitalización.
   - Volumen de 1 h de como mucho 3 veces la capitalización (más que eso suele ser volumen falso).
   - Al menos 100 compradores en 1 h, y entre 1.2 y 8 compradores por cada vendedor.
   - Los 10 mayores holders con un 35% del suministro como mucho, y autoridades de mint y
     freeze revocadas. Sin datos de holders, no se descarta.
3. **Seguimiento:** precio, liquidez y si el token sigue vivo a los 30 min, 1 h, 6 h, 24 h,
   3 días y 7 días (muerto = precio al 10% o menos del de detección). A las 24 h descarga las
   velas de 5 min y calcula el máximo alcanzado y el resultado de la regla de salida:
   - Vender 50% a 2x, 20% a 5x y 20% a 10x, y dejar el 10% restante.
   - Salir de todo si cae a −50%. Se ejecuta al peor precio entre el stop y el cierre de la
     vela: en un rug pull nadie vende a −50%.

   A los 7 días descarga velas de 1 h y mide el máximo alcanzado (¿llegó a 10x, 50x, 100x?) y
   la **regla de tendencia**, pensada para no cortar las subidas grandes:
   - Vender 1/3 a 3x (recuperas lo invertido).
   - El resto, con stop móvil: salir si cae un 50% desde el máximo alcanzado.
4. **Informe:** `INFORME.md` compara resultados por filtro, narrativa (líder frente a
   clones, calor, catalizador), carteras inteligentes, concentración de holders, edad,
   capitalización, compradores/vendedores, volumen, RugCheck y DEX, con un 3% de costes por
   operación. También incluye:
   - **Carteras inteligentes:** las que tienen 3+ tokens con resultado y al menos la mitad
     llegó a 2x. Para cada token cuenta solo el historial conocido en el momento de detectarlo,
     sin mirar al futuro.
   - **Palabras calientes** de las últimas 3 h frente a las 24 h anteriores.
   - **Narrativas activas** de las últimas 2 h y su token líder.

## Dónde verlo

GitHub Actions lo ejecuta cada 5 minutos (`.github/workflows/radar.yml`) y guarda los datos
en la rama **`radar-datos`**:

- `INFORME.md`: el informe, legible desde el móvil en GitHub.
- `detecciones.csv` y `seguimiento.csv`: los datos en bruto.

La programación solo se activa cuando el workflow está en la rama principal (`main`).
También se puede lanzar a mano desde la pestaña *Actions* → *Radar memecoins* → *Run workflow*.

## En tu ordenador

```bash
pip install pandas tabulate
python radar.py ciclo --cada 300     # cada 5 minutos, datos en datos_radar/
python radar.py informe              # regenerar solo el informe
```

## Cómo leer los resultados

- **No saques conclusiones de grupos con menos de 30 tokens** (el informe los marca).
- Lo que importa es `regla_$_por_50`: la ganancia o pérdida media por apuesta de $50 ya
  descontados los costes. Si el grupo *pasa* del filtro no es claramente positivo tras
  cientos de tokens, el filtro no tiene ventaja.
- Limitaciones:
  - Solo ve lo que listan las APIs públicas, y con minutos de retraso respecto a los bots.
  - RugCheck y la ficha de holders se consultan como mucho para 30 tokens nuevos por escaneo, y
    las carteras para 15,
    por los límites de las APIs. El dato de holders de GeckoTerminal puede tener minutos u
    horas de antigüedad (columna `holders_antig_min`).
  - Las narrativas se deducen solo del nombre: no hay acceso a X/Twitter ni a Telegram.
  - Si un token cambia de pool (por ejemplo, de pump.fun a PumpSwap), el radar junta las
    velas de los dos pools.
