# Informe del radar de memecoins

Generado: 2026-09-28 08:20 UTC

- Tokens registrados: **795** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **0** (el primero llega 24 h después de la primera detección)
- Pasan el filtro v1: **26**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## Últimas alertas del vigía (6 h)

| ts    | simbolo    | narrativa   | prioridad   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:-----------|:------------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 08:16 | QORE       |             | vetada      |        2.1 | 9K   |               69 |              45 | 86iV4zs8jMGZjiaQaAcbNVTDBRjso8BCCGd5vezPpump | nan    |
| 08:13 | TAP        |             | vetada      |        3.2 | 17K  |              285 |             195 | 4q88gcME69yvfcbN3m4NSNczbmk3D61a7PE1bLcXpump | nan    |
| 08:10 | 1          |             | vetada      |        3   | 11K  |               73 |              48 | 3wQkX3N82NSxbND48RCUZPRu8roadhZa6QgW8yFNzdNx | nan    |
| 08:10 | MIST       |             | vetada      |        2.8 | 22K  |               47 |              35 | 4gTBywUgAUQUMBJHRogtuFgDv8tDfTqcqNKLVWhVk92N | nan    |
| 08:10 | 1000X      | cripto      | vetada      |        2.5 | 62K  |              184 |             134 | ELP7DpZvv41KzWewe513ZPBwTESsuxgzCJzh9zXn8WGd | nan    |
| 08:10 | MERVIN     |             | vetada      |        2.3 | 73K  |              192 |              94 | AASBPGtKrK3kGQoDgjDbMbhs5v6hy9N2tNyXWbdxpump | nan    |
| 07:57 | XOMUSDT    |             | vetada      |        3.9 | 91K  |               94 |              31 | HdkCkQHhVSTvi6WW5vaiabK7hzTVGsqdDCyyTeQphQLX | nan    |
| 07:53 | AXIOM      |             | vetada      |        7.3 | 64K  |              527 |             398 | HPmrRWHrbwWVzJiQfnxgPSRDDkD6ShMLnEN6VuEzvyEV | nan    |
| 07:46 | VAMPCAT    |             | vetada      |        2.1 | 31K  |              209 |              91 | 6RXHP4EsZjpV3DUXVv92SKq88rCZFW34UsuS6hpRdHPV | nan    |
| 07:37 | JSLING     |             | vetada      |        6.5 | 88K  |               88 |              31 | CBrb3vSehHm5DmTSu1ztF2FDAqJTZdH8pjQ9DaUHBAGS | nan    |
| 07:37 | UNPAID     |             | vetada      |        4.1 | 14K  |              578 |             117 | 2vcWNo27TBzq2PMZbAGhA2qr49xAVth3vcq6aX2cAb4F | nan    |
| 07:37 | UNPAID     |             | vetada      |        5.2 | 22K  |              537 |              76 | 6VxZuiD2Hzo5empJXQvLpAGVsFd7bKedt39XjfYtJ5JM | nan    |
| 07:34 | Gu Gua     |             | alta        |        2.4 | 10K  |              149 |              93 | 6ZE5JgWBm2qQ5p2yw6wnwAX8R6UqfiCoDSSjr1depump | nan    |
| 07:26 | ket        |             | vetada      |       12.9 | 12K  |               86 |              63 | J8Jr8JPXCeWvj3EeWctug1ixcZTVpPUaisHjoMtDpump | nan    |
| 07:19 | VantaCard  |             | vetada      |       12.6 | 16K  |              182 |              60 | 3jNVGYs3HCPmRnk12QWUVd1pzVckUx8dPyoaKW7zpump | nan    |
| 07:16 | PumpSite   | cripto      | baja        |        3.1 | 10K  |               91 |              47 | 8v9xeUv9cr56vfDbfAWpigs4xcPcsroBYJDZ6CQLpump | nan    |
| 07:12 | topless    |             | vetada      |        3.2 | 18K  |              416 |             104 | 4u1yNS74uK1HJwxEEgJJXEoFPpDNZTmT5pyLFEaGkkzR | nan    |
| 07:12 | Cnfact     |             | vetada      |        3.3 | 78K  |               86 |              24 | 5xX5PXEeBJouuhuFrcfJ6DCNFtb1F8Bq9NJTNCBjbonk | nan    |
| 07:02 | YON        |             | vetada      |        5.2 | 15K  |              184 |             115 | GEGEit5x2tGcLCDZFKVwr9fRKZs7984bQSkYHqf25G9Q |   0.25 |
| 06:54 | Jak        |             | vetada      |        2.6 | 14K  |              331 |             105 | FcrWnyw86GoZ8C1g9hZ2q93xkVVvCyKH39qnBVQ2VRDx |   0    |
| 06:54 | METER      |             | baja        |        2.5 | 9K   |              104 |              62 | Bxhohnh4Sv9VvdgEatVymFP9A6vzzfAfcP25ah8Zpump |   0.39 |
| 06:48 | GET        |             | vetada      |        2.7 | 17K  |              391 |             196 | 5iwLiBK2wkzGbjFj9LUrgcsa8N7LDKR4u7jTLj6Spump |   0    |
| 06:48 | NewGuy     |             | vetada      |        2.5 | 97K  |              538 |              78 | UToBuGdPZ1pNT7oUtwamQZ5FjXJx5FS8wRAFMEhwN7m  |   0    |
| 06:43 | MORTGAGE   |             | vetada      |        3.9 | 23K  |              478 |              96 | 9Wc55rosRJSFAktu7dxFYcPWDbBof136Lvq9euAre8FY |   5.34 |
| 06:40 | RIVER      |             | vetada      |        3   | 23K  |              167 |             116 | HBmnvSoG9QNT8QACD8WZsuTxjaFuqfw4EyrsGuE8pump |   0.17 |
| 06:40 | SCAT       |             | vetada      |       12.8 | 10K  |               85 |              62 | CrxQ3SHsP7qjy7REBRhjDn9i4keHX1PfqHvp2Hsy8XdG |   0.89 |
| 06:34 | swordcat   |             | baja        |        2.9 | 10K  |               80 |              58 | 4Px7VL8zi721aTYhd7osQKL2EYaVML8BW9Ak1p48scHR |   0.32 |
| 06:34 | riff       |             | baja        |        3.1 | 8K   |              136 |              92 | HzLbqtsTC7Jn8GMB4wKyRuACz7uauhfzH65vwRbJpump |   0.41 |
| 06:32 | Uaemeet    |             | vetada      |        2.2 | 77K  |              108 |              25 | AZrhe6A2Sjb4LJbswgdRXew3p76KGc29StFtMvBvmoon |   0    |
| 06:30 | TROLL      |             | vetada      |        3   | 16K  |               69 |              34 | GWNgs2VUfA7tTGnRn9FjCzMY7Xk27GeeiDkWM3txmePz |   0    |
| 06:26 | Paw        |             | alta        |        3.7 | 12K  |               41 |              20 | 4FZPCKj49LuaUJ5xKom9dYoQmm1Tt7F4yeyiHrpcnawu |   0.33 |
| 06:24 | BEAR       | animales    | vetada      |        3.4 | 23K  |              310 |             194 | AHUYfm3aoYEcDApfhfEVR9ernkoykAhfTJ51cZgspump |   0.19 |
| 06:20 | Abshld     |             | vetada      |        3.3 | 80K  |              107 |              22 | 2YBS8z611qZBSoBxiJ58wg926qDQy3r9odVxYFpbmoon |   0    |
| 06:17 | LEVERAGE   |             | vetada      |        8.1 | 75K  |              469 |             324 | BM2k8mJUbMthHoioykyUm2NjMrXvLBYhoXruwYLpump  |   2.16 |
| 06:12 | Shima      | cripto      | baja        |        5.5 | 9K   |              119 |              86 | B5NhBtmjmqFTyFSkYFSE8qPTP6GdMVmapZ4RtBoYpump |   0.37 |
| 06:10 | maro       |             | vetada      |        3.2 | 57K  |               51 |              37 | BqXVJDb2pAxmoa2PBCxDypNwnitdVXvwN5L51EC9maro |   0    |
| 06:08 | Redbull    | animales    | vetada      |        3.7 | 76K  |              239 |              49 | DFRPbHdZpxx8Q5Hp658pfkvrYgjKpY2QpQDvnhsmEjZF |   0    |
| 05:51 | PAKSPACE   |             | vetada      |        2.1 | 74K  |               80 |              27 | FVeMhWR4eUKryBPfeFrPhxEuRGd6kLsG1KudBHiPmoon |   0    |
| 05:51 | CROCS      |             | baja        |        2.2 | 11K  |               82 |              46 | Ees9nBcWavLJiE4P1inKwhXpNQSzL64zntyqWjpec6Dc |   9.32 |
| 05:47 | TREND      |             | vetada      |        3.3 | 24K  |              437 |             256 | 92W24gMTrfSmavNatTCBawaDMbEQ3NJnMY7chbMVpump |   0.61 |
| 05:37 | BBBYQ      |             | vetada      |        9.5 | 9K   |               66 |              47 | BzSCw6CEpcLyCZz59Y7pTLxRM2vpZaM1K14Pn946ps7q |   0.87 |
| 05:33 | FULLSEND   |             | vetada      |        3   | 279K |              151 |              68 | Dimo67L6c5qCe7nuXz925EzjbYNpxpL8HihGQPNmpump |   0.48 |
| 05:33 | 拼多多        |             | vetada      |        3.2 | 30K  |              286 |              40 | 2BT2Su86HVHxhygt6VxrWo9mdfnu3PJvsALLHzEMCtqh |   5.21 |
| 05:30 | tr/acc     |             | vetada      |        2   | 108K |              266 |             110 | DGXf3mT2TaHsfy1Cn2p9CCSxfKENNM3oHPoR59Uwpump |   0    |
| 05:30 | Gary       |             | baja        |        2.7 | 18K  |              194 |             116 | Ecx7uvbG63ETuZu4GZTzBmahadqgqDxryynzdTLwXff1 |   0.2  |
| 05:24 | VUCIC      |             |             |        2.9 | 79K  |              147 |              36 | D74JWCJ4x5GAhbEtvBVrtTPqZtBzgknJcGCmbnYVpump |   0    |
| 05:14 | FSD        |             |             |       13.5 | 24K  |               46 |              33 | HKgaE2JirCXudKEFm9JUTFDsV2hTx9sJoGr1tXnwpump |   0.61 |
| 05:06 | FIM        |             |             |        2.8 | 21K  |              403 |             104 | 3AaZhDQug7q7h6ZJtNUR5Y5j6u2isGi7huN9ni4Justq |   0    |
| 04:51 | BOETIX     |             |             |        5.2 | 78K  |               77 |              23 | 7T4GuSjCy5nEq3wPqCTk2XtUGS4rk7dDservu8fgpump |   0    |
| 04:51 | Pager      |             |             |        7.4 | 19K  |              247 |             174 | 5ztqMCrrowVmMUg46ZVYmQ9boV1FDTuUj7quo2cwpump |   0.21 |
| 04:51 | Minions    |             |             |        3.5 | 36K  |              374 |              77 | 89nk99jM9wo3tFuCoUbqrHpDHahcTQmGBD4k6EQKVTSj |   1.44 |
| 04:48 | SNARKSTR   |             |             |        2.5 | 16K  |              563 |              96 | 4Jswhn7SvsFgpzk2g88mVDnnc9aCLLMdUaD8QKYqwtXm |   0    |
| 04:48 | GRAYMATTER |             |             |        2   | 161K |             1002 |             613 | A2Kz4oAJvg9yuQR9znDicg8QvFDgrxaHp68ih3HCpump |   0.84 |
| 04:09 | ROBINPEPE  | animales    |             |        2.5 | 33K  |              288 |              52 | 8LqsJ5cewbg9AwiN6imdGZocNm3tiHqgnm8t5g3VLMip |   2.13 |
| 04:00 | 호냥이        |             |             |        2.5 | 8K   |               95 |              64 | BeYAs9VQV6zWpVbAfv9XcD14V4uohshVrGGDUJnHKiwn |   0.53 |
| 03:54 | LASTACC    |             |             |        3.4 | 93K  |              622 |             202 | DGBK6nsRRTrVrpqhdY4PkUgKJfZhw6kayf6RT8Lepump |   0.02 |
| 03:49 | BOOBS      |             |             |        2.2 | 19K  |              151 |              41 | HjyW96uXnDPyehceFGwAGpL21JKBuZArpFrBm2g9Rxgn |   1.84 |
| 03:32 | STAN       |             |             |        2.8 | 10K  |               45 |              24 | J6AY2pQgQqzNLPcCSzJVm8PcWz8GNZ919vBTpMf7pump |   0.43 |
| 03:12 | J          |             |             |        2.7 | 21K  |              319 |             103 | PezmauQpZfE3yNJo4P9ZKAo18ov6oedb2rdwbnTjJc1  |   1.04 |
| 03:12 | Tip        |             |             |        2.7 | 11K  |              259 |             182 | FLB7VyLWUyxjpYS3QonkaFcThVWcu82vHpvNU58mpump |   0.5  |
| 02:56 | SIRI       |             |             |        3.9 | 61K  |              326 |             242 | nspzEbY9m1rLDaHMw19RjEv1cUfX8k2c9t1nxXVpump  |   0.32 |
| 02:38 | ROGLOVE    |             |             |        2.6 | 87K  |              156 |              37 | GPjSdf5A2BuRX7n62tqfhZ4t4E31xzHKpT8eJM2ABAGS |   4.01 |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **6007**; seguidas de un desplome (caída a un 40% o menos en 30 min): **145**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |              4753 | 1%                   | 8%                   |
| Ticket medio < $30 (volumen de microcompras) |              5286 | 2%                   | 6%                   |
| Más de 8 compradores por vendedor (5 min)    |                21 | 19%                  | 2%                   |
| Subida de más del 100% en 1 h                |               620 | 12%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |                42 | 48%                  | 2%                   |
| Aceleración final                            |                98 | 14%                  | 2%                   |
| Más vendedores que compradores (5 min)       |              5284 | 1%                   | 13%                  |
| Ya multiplicó x5 o más desde la detección    |              1551 | 1%                   | 3%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra   |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor    | mc_mayor   | mint_mayor                                   |
|:----------|------------:|---------------------:|:------------------|:---------|:-----------|:---------------------------------------------|
| gary      |           5 |                    0 | x40               | Gary     | 20K        | DD6spR2Z75n5CbL72kz4xLciA6NJdD7rNuMzqjTAQGa6 |
| acc       |           4 |                    9 | x4                | tr/acc   | 108K       | DGXf3mT2TaHsfy1Cn2p9CCSxfKENNM3oHPoR59Uwpump |
| stonkinu  |           3 |                    0 | x24               | STONKINU | 47K        | 6bxgHRcxRjtapo8ex9FcwgKHPuNUzFHxtKxdir3jWgnK |
| topless   |           3 |                    0 | x24               | topless  | 47K        | 42UyjX29XykmpZHXf3Fg2D22TDsKkfzAMrJ1v4Hwpump |

## Narrativas activas (últimas 2 h)

| narrativa       |   tokens_nuevos | lider   | mc_lider   | catalizador   | mint_lider                                   |
|:----------------|----------------:|:--------|:-----------|:--------------|:---------------------------------------------|
| cripto          |               3 | 1000X   | 62K        |               | ELP7DpZvv41KzWewe513ZPBwTESsuxgzCJzh9zXn8WGd |
| animales        |               1 | BEAR    | 23K        |               | AHUYfm3aoYEcDApfhfEVR9ernkoykAhfTJ51cZgspump |
| elon            |               1 | ELON    | 425K       |               | H7TsCXbbAjbLfwYZnSdQcYsPpQ4CxQ4rKh7AP9dLpump |
| noticias_cripto |               1 | NEAR    | 67K        |               | 66oYkUSiVnmvxEmLBaWiGvd21hgPD6LcAduYUwKypjyp |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

| ts    | simbolo   | narrativa   | mc   | liq   |   edad_min |   compradores_h1 |   vendedores_h1 |   top10_pct |   carteras_buenas | mint                                         |
|:------|:----------|:------------|:-----|:------|-----------:|-----------------:|----------------:|------------:|------------------:|:---------------------------------------------|
| 07:52 | sol/acc   | cripto      | 65K  | 19K   |        0.7 |              118 |              36 |         nan |               nan | 2RNoh2sEmFvorpnw9wpK7CBPb7svgJvhEq37JTdRpump |
