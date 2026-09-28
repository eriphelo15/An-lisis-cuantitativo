# Informe del radar de memecoins

Generado: 2026-09-28 00:21 UTC

- Tokens registrados: **411** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **0** (el primero llega 24 h después de la primera detección)
- Pasan el filtro v1: **9**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## Últimas alertas del vigía (6 h)

| ts    | simbolo   | narrativa   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:----------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 23:57 | acute     |             |        3.4 | 16K  |              278 |             189 | 3x1A8ty18mycnq5eiYMVn49NG4tzC9W8KvSZUbHUpump |    nan |
| 23:54 | AINU      |             |        5   | 10K  |               56 |              37 | 3cgNRQRToBpqtGhvRztndJBDXSiZP3Y2FFt2uQxCpump |    nan |
| 23:47 | Neartkt   |             |        2   | 86K  |               99 |              26 | 5Lz1som5aA9iGkSCvoom5TvE5gLu4iBn5Le8n3Yupump |    nan |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **316**; seguidas de un desplome (caída a un 40% o menos en 30 min): **12**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

_Menos de 20 desplomes registrados: todavía no se puede concluir nada._

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |               233 | 0%                   | 14%                  |
| Ticket medio < $30 (volumen de microcompras) |               263 | 3%                   | 8%                   |
| Más de 8 compradores por vendedor (5 min)    |                 2 | 100%                 | 3%                   |
| Subida de más del 100% en 1 h                |                74 | 14%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |                 0 | -                    | 4%                   |
| Aceleración final                            |                 1 | 0%                   | 4%                   |
| Más vendedores que compradores (5 min)       |               252 | 0%                   | 17%                  |
| Ya multiplicó x5 o más desde la detección    |                86 | 2%                   | 4%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra    |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor      | mc_mayor   | mint_mayor                                   |
|:-----------|------------:|---------------------:|:------------------|:-----------|:-----------|:---------------------------------------------|
| moin       |          18 |                   11 | x13               | moin       | 324K       | BdeQbxD9v9JkKam8r9P3wz317rn7jDu7MHGczVw2LZ8m |
| claudechan |           7 |                    0 | x56               | CLAUDECHAN | 474K       | DmgujFb6P3NJfgLyFhJhcwnUBNQJ7QSBLwtNvy3vi4J9 |
| buns       |           6 |                    0 | x48               | BUNS       | 499K       | 2YrzLLfojLVezr4oRx4D6VYeG2ehJHoPLs5Zbt1AATSv |
| inu        |           5 |                    0 | x40               | inu        | 126K       | 9L4xAusWTDaHxbA54ZRQGeqM5UZrHyysjx5qnTVvyApT |
| vbucks     |           5 |                    0 | x40               | VBUCKS     | 132K       | G3EZu7t5T4zy9bgbdKe7YbtNfBzL3nePcMr6JeaYsw1t |
| kaeru      |           5 |                    0 | x40               | Kaeru      | 39K        | 839S6B1bpfNA48eSRut25ytrnVJQVd2AAYCPj9Xgpump |
| ocelot     |           5 |                    0 | x40               | Ocelot     | 149K       | FdjkMLM79vWtvaDYU83xkXoZAPnhdKpicZmyFQQ89RSN |
| zmr        |           4 |                    0 | x32               | zmr        | 176K       | 9inZTWscKifF835pUztDZmF77wBe2d16n3cJd97ZE4UJ |
| pkmn50     |           4 |                    0 | x32               | PKMN50     | 114K       | BcpRdQiNzwGRJLbtrUwKrLCWAVwm8Bm1KKbGYtUohoyG |
| gta        |           4 |                    0 | x32               | GTA 6 Coin | 1114K      | GHNJY8WowhxAFneGs3oXoFV5EpiScmNAZrnAuxN5pump |

## Narrativas activas (últimas 2 h)

| narrativa   |   tokens_nuevos | lider      | mc_lider   | catalizador                                            | mint_lider                                   |
|:------------|----------------:|:-----------|:-----------|:-------------------------------------------------------|:---------------------------------------------|
| ia          |              12 | CLAUDECHAN | 114K       |                                                        | L3AkrXzxvigXwefBR5ov87BMsKVJTss76kDk8tLHihr  |
| cripto      |               4 | SNOWMOON   | 107K       |                                                        | 9hJPqv4skc13qXXfoxudGqpUe8ByMUKnRoiVNUHnwhL  |
| animales    |               2 | Bdfbull    | 122K       |                                                        | F1CZsBwru1KGc4wZHem9oAjna2xkBJ3DbS4db9QvBAGS |
| videojuegos |               2 | GTA 6 Coin | 438K       | Lanzamiento de GTA 6 (previsto) (en 53 días)           | WnFL5YYoGzCskdFxowXBv2j4cjT5xcD6iNdD8dWpump  |
| elon        |               1 | Elon Coin  | 474K       |                                                        | Cfctf6xtNf96tM8jKmEZYAYmjjnpaEQH4gxeJP34pump |
| politica    |               1 | BARRON     | 422K       | Elecciones de mitad de mandato en EE. UU. (en 37 días) | UTM3Ub28s6JKWVjcCr2Z4n5cWtdCXnGZq9H3EZ1pump  |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

Ninguno.
