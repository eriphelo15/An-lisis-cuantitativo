# Informe del radar de memecoins

Generado: 2026-09-28 01:15 UTC

- Tokens registrados: **479** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **0** (el primero llega 24 h después de la primera detección)
- Pasan el filtro v1: **15**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## Últimas alertas del vigía (6 h)

| ts    | simbolo    | narrativa   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:-----------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 01:08 | CRYPTCATCH |             |        8.9 | 10K  |              126 |              89 | GsHERzUtQkkuymwJyp2KyCf82oXqQKcYXQmRq5Gupump | nan    |
| 01:00 | x/acc      |             |        3.6 | 135K |              339 |              59 | C5zyCRUo23yLHDfcYWWTZNVh4yxWgQ8PFr1zx1Zrpump | nan    |
| 00:42 | KARDASHEV  |             |        2.7 | 20K  |              497 |             105 | HpScdB92mtrJZSK53Cz5G9HPBB5eHztoxNJk87ZDifv6 | nan    |
| 00:27 | BOB        |             |        2.2 | 17K  |              578 |              75 | D9fzjmqsRfSKGLxtdM1NZX45URC8NieK3CgRae2ERPW8 | nan    |
| 00:24 | CAIRN      |             |        3.5 | 21K  |              198 |              72 | 2E6zwbWHBidtVe4dZhnRmaQhKaSxcAMzAF3LmGPTBWWS | nan    |
| 00:22 | wifsolcap  |             |        3   | 14K  |              274 |             204 | 6jR9ve6bbAqbmWMV3LX8y1KJiYvyzcSM8S63WUUWpump | nan    |
| 00:22 | KOKOS      |             |        3.1 | 79K  |              713 |             478 | XrR9rqzFCBEcYoeyKrHV2uYFmEkwPCh6cxB3KuPCGd5  | nan    |
| 23:57 | acute      |             |        3.4 | 16K  |              278 |             189 | 3x1A8ty18mycnq5eiYMVn49NG4tzC9W8KvSZUbHUpump |   0.22 |
| 23:54 | AINU       |             |        5   | 10K  |               56 |              37 | 3cgNRQRToBpqtGhvRztndJBDXSiZP3Y2FFt2uQxCpump |   0.35 |
| 23:47 | Neartkt    |             |        2   | 86K  |               99 |              26 | 5Lz1som5aA9iGkSCvoom5TvE5gLu4iBn5Le8n3Yupump |   1.02 |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **805**; seguidas de un desplome (caída a un 40% o menos en 30 min): **18**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

_Menos de 20 desplomes registrados: todavía no se puede concluir nada._

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |               614 | 0%                   | 9%                   |
| Ticket medio < $30 (volumen de microcompras) |               671 | 1%                   | 7%                   |
| Más de 8 compradores por vendedor (5 min)    |                 3 | 67%                  | 2%                   |
| Subida de más del 100% en 1 h                |               143 | 10%                  | 0%                   |
| Escalera: 30 min subiendo sin retrocesos     |                10 | 20%                  | 2%                   |
| Aceleración final                            |                14 | 7%                   | 2%                   |
| Más vendedores que compradores (5 min)       |               667 | 0%                   | 12%                  |
| Ya multiplicó x5 o más desde la detección    |               233 | 2%                   | 2%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra    |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor      | mc_mayor   | mint_mayor                                   |
|:-----------|------------:|---------------------:|:------------------|:-----------|:-----------|:---------------------------------------------|
| moin       |          14 |                   18 | x6                | moin       | 294K       | Ezuzp2wDKjgRqFFmZFpVfoQCqymH7FGoMrVNYp6NvRa  |
| zmr        |          10 |                    0 | x80               | zmr        | 265K       | DBorvZYRJMBHqrYGaVaLMhiRkQWe6BwP1Rth7SGysk6Q |
| claudechan |           7 |                    0 | x56               | CLAUDECHAN | 474K       | DmgujFb6P3NJfgLyFhJhcwnUBNQJ7QSBLwtNvy3vi4J9 |
| buns       |           6 |                    0 | x48               | BUNS       | 499K       | 2YrzLLfojLVezr4oRx4D6VYeG2ehJHoPLs5Zbt1AATSv |
| bob        |           5 |                    0 | x40               | BOB        | 247K       | E4vwseNWpkBxzNxyv3msVLCzYHU5SXrj1QWXEycypump |
| gta        |           4 |                    1 | x32               | GTA 6 Coin | 1114K      | GHNJY8WowhxAFneGs3oXoFV5EpiScmNAZrnAuxN5pump |
| kardashev  |           4 |                    0 | x32               | KARDASHEV  | 191K       | AmaM7N43JBicpcHDbVKyGeuTjtnNhJ2yZTdWqoZpCX8b |
| soa        |           4 |                    0 | x32               | SOA        | 190K       | 8mVQTa7yuhGEaQR1hNNuS5NkJUHz8YjTxuFmFM9BoQu5 |
| acc        |           4 |                    0 | x32               | x/acc      | 135K       | C5zyCRUo23yLHDfcYWWTZNVh4yxWgQ8PFr1zx1Zrpump |
| moinu      |           3 |                    0 | x24               | moinu      | 49K        | EHukM8oGcpeiu89NYA5kyiCCh963i7eEKBoyiotT4Bq7 |

## Narrativas activas (últimas 2 h)

| narrativa    |   tokens_nuevos | lider      | mc_lider   | catalizador                                            | mint_lider                                   |
|:-------------|----------------:|:-----------|:-----------|:-------------------------------------------------------|:---------------------------------------------|
| ia           |               8 | CLAUDECHAN | 114K       |                                                        | L3AkrXzxvigXwefBR5ov87BMsKVJTss76kDk8tLHihr  |
| cripto       |               4 | SNOWMOON   | 107K       |                                                        | 9hJPqv4skc13qXXfoxudGqpUe8ByMUKnRoiVNUHnwhL  |
| celebridades |               2 | MrBeast    | 511K       |                                                        | eAmQZ7qQrZGJPSP5dfoVudyTwvZ2QhqKaWzRgAVpump  |
| animales     |               1 | Bdfbull    | 122K       |                                                        | F1CZsBwru1KGc4wZHem9oAjna2xkBJ3DbS4db9QvBAGS |
| elon         |               1 | ELON       | 458K       |                                                        | TvQvxBNfyuYQozqK4ycpFfW5hcKsBE3xVc7ww1Ypump  |
| politica     |               1 | TRUMPx     | 699K       | Elecciones de mitad de mandato en EE. UU. (en 36 días) | Us5JCsdrW3Cd2KsgH1iVyDzVyDfkhj4ozsYLmpzpump  |
| videojuegos  |               1 | GTA 6 Coin | 448K       | Lanzamiento de GTA 6 (previsto) (en 52 días)           | 4cUKzTFun2ptVPYSoY9nYQavFz8tGz42SPuDdgVypump |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

| ts    | simbolo   | narrativa   | mc    | liq   |   edad_min |   compradores_h1 |   vendedores_h1 |   top10_pct |   carteras_buenas | mint                                         |
|:------|:----------|:------------|:------|:------|-----------:|-----------------:|----------------:|------------:|------------------:|:---------------------------------------------|
| 00:34 | SUPERCAPY |             | 115K  | 32K   |        1.8 |              440 |              56 |         nan |               nan | 7hBLGsXj16vGPVpDiVrZsLmeWS8ZiGgsbwpYRAxVpump |
| 00:52 | Nike      |             | 1126K | 97K   |       48.4 |             2416 |            1006 |         nan |               nan | 8VFj2ikwauFPGzDjVWW9Y17SWXSQdCQYx2FkJJ7Tpump |
| 00:52 | Apple     |             | 615K  | 71K   |       13.9 |             2394 |             369 |         nan |               nan | 32YJiYMgHpDRkQzkdwPFw7XPUKtPyZJVK1Yz3fMPpump |
| 01:02 | ETH       | cripto      | 413K  | 58K   |        8.6 |             2229 |             693 |         nan |               nan | DYPy21Mz1s9b8QarCfM4gtE4G1iSQd8oGzRhJaAPpump |
| 01:02 | TRUMPx    | politica    | 699K  | 83K   |        5.9 |              233 |              76 |         nan |               nan | Us5JCsdrW3Cd2KsgH1iVyDzVyDfkhj4ozsYLmpzpump  |
| 01:00 | x/acc     |             | 135K  | 32K   |        3.6 |             1092 |             189 |         nan |               nan | C5zyCRUo23yLHDfcYWWTZNVh4yxWgQ8PFr1zx1Zrpump |
