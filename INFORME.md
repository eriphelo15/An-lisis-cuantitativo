# Informe del radar de memecoins

Generado: 2026-09-28 00:39 UTC

- Tokens registrados: **428** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **0** (el primero llega 24 h después de la primera detección)
- Pasan el filtro v1: **10**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## Últimas alertas del vigía (6 h)

| ts    | simbolo   | narrativa   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:----------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 00:27 | BOB       |             |        2.2 | 17K  |              578 |              75 | D9fzjmqsRfSKGLxtdM1NZX45URC8NieK3CgRae2ERPW8 |    nan |
| 00:24 | CAIRN     |             |        3.5 | 21K  |              198 |              72 | 2E6zwbWHBidtVe4dZhnRmaQhKaSxcAMzAF3LmGPTBWWS |    nan |
| 00:22 | wifsolcap |             |        3   | 14K  |              274 |             204 | 6jR9ve6bbAqbmWMV3LX8y1KJiYvyzcSM8S63WUUWpump |    nan |
| 00:22 | KOKOS     |             |        3.1 | 79K  |              713 |             478 | XrR9rqzFCBEcYoeyKrHV2uYFmEkwPCh6cxB3KuPCGd5  |    nan |
| 23:57 | acute     |             |        3.4 | 16K  |              278 |             189 | 3x1A8ty18mycnq5eiYMVn49NG4tzC9W8KvSZUbHUpump |    nan |
| 23:54 | AINU      |             |        5   | 10K  |               56 |              37 | 3cgNRQRToBpqtGhvRztndJBDXSiZP3Y2FFt2uQxCpump |    nan |
| 23:47 | Neartkt   |             |        2   | 86K  |               99 |              26 | 5Lz1som5aA9iGkSCvoom5TvE5gLu4iBn5Le8n3Yupump |    nan |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **478**; seguidas de un desplome (caída a un 40% o menos en 30 min): **12**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

_Menos de 20 desplomes registrados: todavía no se puede concluir nada._

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |               358 | 0%                   | 10%                  |
| Ticket medio < $30 (volumen de microcompras) |               398 | 2%                   | 5%                   |
| Más de 8 compradores por vendedor (5 min)    |                 2 | 100%                 | 2%                   |
| Subida de más del 100% en 1 h                |               102 | 10%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |                 2 | 0%                   | 3%                   |
| Aceleración final                            |                 6 | 0%                   | 3%                   |
| Más vendedores que compradores (5 min)       |               388 | 0%                   | 12%                  |
| Ya multiplicó x5 o más desde la detección    |               133 | 2%                   | 3%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra    |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor      | mc_mayor   | mint_mayor                                   |
|:-----------|------------:|---------------------:|:------------------|:-----------|:-----------|:---------------------------------------------|
| moin       |          16 |                   13 | x10               | moin       | 324K       | BdeQbxD9v9JkKam8r9P3wz317rn7jDu7MHGczVw2LZ8m |
| claudechan |           7 |                    0 | x56               | CLAUDECHAN | 474K       | DmgujFb6P3NJfgLyFhJhcwnUBNQJ7QSBLwtNvy3vi4J9 |
| buns       |           6 |                    0 | x48               | BUNS       | 499K       | 2YrzLLfojLVezr4oRx4D6VYeG2ehJHoPLs5Zbt1AATSv |
| zmr        |           6 |                    0 | x48               | zmr        | 176K       | 9inZTWscKifF835pUztDZmF77wBe2d16n3cJd97ZE4UJ |
| inu        |           5 |                    0 | x40               | inu        | 126K       | 9L4xAusWTDaHxbA54ZRQGeqM5UZrHyysjx5qnTVvyApT |
| vbucks     |           5 |                    0 | x40               | VBUCKS     | 132K       | G3EZu7t5T4zy9bgbdKe7YbtNfBzL3nePcMr6JeaYsw1t |
| ocelot     |           5 |                    0 | x40               | Ocelot     | 149K       | FdjkMLM79vWtvaDYU83xkXoZAPnhdKpicZmyFQQ89RSN |
| gta        |           4 |                    0 | x32               | GTA 6 Coin | 1114K      | GHNJY8WowhxAFneGs3oXoFV5EpiScmNAZrnAuxN5pump |
| wiffomo    |           3 |                    0 | x24               | wiffomo    | 160K       | FJGWEmtCEtvyviC8w86twWNiTcXwn7YiAoHmJgxWpump |
| pkmn50     |           3 |                    1 | x24               | PKMN50     | 114K       | BcpRdQiNzwGRJLbtrUwKrLCWAVwm8Bm1KKbGYtUohoyG |

## Narrativas activas (últimas 2 h)

| narrativa   |   tokens_nuevos | lider      | mc_lider   | catalizador                                            | mint_lider                                   |
|:------------|----------------:|:-----------|:-----------|:-------------------------------------------------------|:---------------------------------------------|
| ia          |              14 | CLAUDECHAN | 114K       |                                                        | L3AkrXzxvigXwefBR5ov87BMsKVJTss76kDk8tLHihr  |
| cripto      |               2 | SNOWMOON   | 107K       |                                                        | 9hJPqv4skc13qXXfoxudGqpUe8ByMUKnRoiVNUHnwhL  |
| videojuegos |               2 | GTA 6 Coin | 438K       | Lanzamiento de GTA 6 (previsto) (en 53 días)           | WnFL5YYoGzCskdFxowXBv2j4cjT5xcD6iNdD8dWpump  |
| animales    |               1 | Bdfbull    | 122K       |                                                        | F1CZsBwru1KGc4wZHem9oAjna2xkBJ3DbS4db9QvBAGS |
| elon        |               1 | Elon Coin  | 474K       |                                                        | Cfctf6xtNf96tM8jKmEZYAYmjjnpaEQH4gxeJP34pump |
| politica    |               1 | BARRON     | 422K       | Elecciones de mitad de mandato en EE. UU. (en 37 días) | UTM3Ub28s6JKWVjcCr2Z4n5cWtdCXnGZq9H3EZ1pump  |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

| ts    | simbolo   | narrativa   | mc   | liq   |   edad_min |   compradores_h1 |   vendedores_h1 |   top10_pct |   carteras_buenas | mint                                         |
|:------|:----------|:------------|:-----|:------|-----------:|-----------------:|----------------:|------------:|------------------:|:---------------------------------------------|
| 00:34 | SUPERCAPY |             | 115K | 32K   |        1.8 |              440 |              56 |         nan |               nan | 7hBLGsXj16vGPVpDiVrZsLmeWS8ZiGgsbwpYRAxVpump |
