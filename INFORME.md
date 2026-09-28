# Informe del radar de memecoins

Generado: 2026-09-28 00:12 UTC

- Tokens registrados: **407** (desde 2026-09-27 18:07)
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

Fotos de tokens que ya subían un 50% o más: **234**; seguidas de un desplome (caída a un 40% o menos en 30 min): **8**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

_Menos de 20 desplomes registrados: todavía no se puede concluir nada._

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |               169 | 0%                   | 12%                  |
| Ticket medio < $30 (volumen de microcompras) |               192 | 3%                   | 5%                   |
| Más de 8 compradores por vendedor (5 min)    |                 2 | 100%                 | 3%                   |
| Subida de más del 100% en 1 h                |                57 | 12%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |                 0 | -                    | 3%                   |
| Aceleración final                            |                 0 | -                    | 3%                   |
| Más vendedores que compradores (5 min)       |               182 | 1%                   | 13%                  |
| Ya multiplicó x5 o más desde la detección    |                63 | 0%                   | 5%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra    |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor      | mc_mayor   | mint_mayor                                   |
|:-----------|------------:|---------------------:|:------------------|:-----------|:-----------|:---------------------------------------------|
| moin       |          20 |                    9 | x18               | moin       | 1183K      | 5mdbw1mfaB7JbejXdijFwybaUbV7SUzDJcAjKmxTeSmH |
| vault      |           9 |                   23 | x3                | X VAULT    | 155K       | Cxsg5L8SpnesZQZjtjKieyCHLBEXpLPNzFX9aoj9pump |
| gacha      |           7 |                    3 | x19               | GACHA      | 422K       | E1LY7wpf89QtKee6gVzWiJxRVJh8strksQTCqPiyNErH |
| claudechan |           7 |                    0 | x56               | CLAUDECHAN | 474K       | DmgujFb6P3NJfgLyFhJhcwnUBNQJ7QSBLwtNvy3vi4J9 |
| buns       |           6 |                    0 | x48               | BUNS       | 499K       | 2YrzLLfojLVezr4oRx4D6VYeG2ehJHoPLs5Zbt1AATSv |
| inu        |           5 |                    0 | x40               | inu        | 126K       | 9L4xAusWTDaHxbA54ZRQGeqM5UZrHyysjx5qnTVvyApT |
| vbucks     |           5 |                    0 | x40               | VBUCKS     | 132K       | G3EZu7t5T4zy9bgbdKe7YbtNfBzL3nePcMr6JeaYsw1t |
| kaeru      |           5 |                    0 | x40               | Kaeru      | 39K        | 839S6B1bpfNA48eSRut25ytrnVJQVd2AAYCPj9Xgpump |
| ocelot     |           5 |                    0 | x40               | Ocelot     | 149K       | FdjkMLM79vWtvaDYU83xkXoZAPnhdKpicZmyFQQ89RSN |
| zmr        |           4 |                    0 | x32               | zmr        | 176K       | 9inZTWscKifF835pUztDZmF77wBe2d16n3cJd97ZE4UJ |

## Narrativas activas (últimas 2 h)

| narrativa   |   tokens_nuevos | lider      | mc_lider   | catalizador                                            | mint_lider                                   |
|:------------|----------------:|:-----------|:-----------|:-------------------------------------------------------|:---------------------------------------------|
| ia          |              12 | CLAUDECHAN | 114K       |                                                        | L3AkrXzxvigXwefBR5ov87BMsKVJTss76kDk8tLHihr  |
| cripto      |               4 | SNOWMOON   | 107K       |                                                        | 9hJPqv4skc13qXXfoxudGqpUe8ByMUKnRoiVNUHnwhL  |
| videojuegos |               3 | GTA 6 Coin | 1114K      | Lanzamiento de GTA 6 (previsto) (en 53 días)           | GHNJY8WowhxAFneGs3oXoFV5EpiScmNAZrnAuxN5pump |
| animales    |               2 | Bdfbull    | 122K       |                                                        | F1CZsBwru1KGc4wZHem9oAjna2xkBJ3DbS4db9QvBAGS |
| elon        |               1 | Elon Coin  | 474K       |                                                        | Cfctf6xtNf96tM8jKmEZYAYmjjnpaEQH4gxeJP34pump |
| politica    |               1 | BARRON     | 422K       | Elecciones de mitad de mandato en EE. UU. (en 37 días) | UTM3Ub28s6JKWVjcCr2Z4n5cWtdCXnGZq9H3EZ1pump  |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

| ts    | simbolo   | narrativa   | mc   | liq   |   edad_min |   compradores_h1 |   vendedores_h1 |   top10_pct |   carteras_buenas | mint                                         |
|:------|:----------|:------------|:-----|:------|-----------:|-----------------:|----------------:|------------:|------------------:|:---------------------------------------------|
| 23:14 | INSTA     |             | 350K | 56K   |       10.2 |              500 |             338 |     30.9162 |                 0 | 6UhUkSBc9RBB9gVJcjCWtcQv4t771rQF7bdn2qK7pump |
