# Vigilancia automática

- `vigilante_binance.py`: revisa los anuncios de Binance (retiros y listados) y anota en `registro_papel.csv`
  la operación que dictan las reglas validadas (`cripto/INFORME_ECOSISTEMA.md`), para seguimiento EN PAPEL.
- Dos rutinas programadas en claude.ai:
  1. **Alertas Binance (cada hora):** corre el vigilante; si hay anuncio nuevo, avisa al celular y por correo y guarda el registro.
  2. **Resumen de mercado (lunes a viernes, antes de la apertura de NY):** calendario macro del día, noticias que mueven al NQ,
     resultados de empresas grandes, catalizadores cripto y estado del registro en papel.
