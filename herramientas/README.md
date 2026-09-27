# Herramientas

## ficha_dilucion.py — ficha de dilución de una small cap en segundos
```
python3 herramientas/ficha_dilucion.py APUS            # una acción
python3 herramientas/ficha_dilucion.py AEMD GIPR APUS  # varias
```
Requisitos: Python 3 con `yfinance` (`pip install yfinance`). No necesita claves: usa SEC EDGAR (gratis) y Yahoo.
Guarda cada ficha en `fichas/TICKER_fecha.md`.

Contenido: tamaño y precio (rotación del float), caja usable / quema / runway, going concern, patrimonio,
acciones potenciales, fragmentos clave del último 10-Q/10-K (caja restringida, ATM, contra-split, convertibles
tóxicas, warrants, hechos posteriores), warrants con precio de ejercicio ajustado por contra-splits vs. precio actual,
registros y ventas de acciones (S-1/S-3/EFFECT/424B), 8-K de 60 días con Items y palabras clave, avisos de Nasdaq,
y la lectura final "¿puede vender acciones HOY?".

Limitaciones: es automática (búsquedas de texto); confirma los números clave en los enlaces. Las ventas por ATM se
conocen con retraso, los 8-K pueden tardar 4 días hábiles y las notas de prensa no siempre están en EDGAR.
Empresas extranjeras que reportan con 20-F/6-K tienen menos datos.
