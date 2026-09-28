# Informe del radar de memecoins

Generado: 2026-09-28 20:55 UTC

- Tokens registrados: **1909** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **128**
- Pasan el filtro v1: **46**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## ¿Funciona el filtro?

### Todos los tokens

| todos   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| todos   | 128 | 70%           | 41%          | -100%         |           -17.16 |      0 | -        | -        | -                    |         |

### Filtro v1

| filtro_v1   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no pasa     | 123 | 70%           | 42%          | -100%         |           -16.37 |      0 | -        | -        | -                    |                 |
| pasa        |   5 | 80%           | 20%          | -100%         |           -35.89 |      0 | -        | -        | -                    | muestra pequeña |

### Alertas tempranas del vigía (2-15 min de vida) frente al escaneo

|                                   | 0      |
|:----------------------------------|:-------|
| ('escaneo', 'n')                  | 128    |
| ('escaneo', 'muertos_24h')        | 70%    |
| ('escaneo', 'tocaron_2x')         | 41%    |
| ('escaneo', 'mediana_24h')        | -100%  |
| ('escaneo', 'regla_$_por_50')     | -17.16 |
| ('escaneo', 'n_7d')               | 0      |
| ('escaneo', '10x_7d')             | -      |
| ('escaneo', '50x_7d')             | -      |
| ('escaneo', 'tendencia_$_por_50') | -      |
| ('escaneo', 'aviso')              |        |
| ('vigia', 'n')                    | 0      |

### Alertas con tema, sin tema y vetadas

| tema                          |   n |
|:------------------------------|----:|
| antes de separar              |   0 |
| con tema relevante (avisadas) |   0 |
| sin tema (silenciosas)        |   0 |
| vetadas (no avisadas)         |   0 |

### Qué habría pasado con los vetados, por veto (si les va bien, el veto sobra)

| veto                             |   n |
|:---------------------------------|----:|
| Copycat token                    |   0 |
| Creator history of rugged tokens |   0 |
| Freeze Authority still enabled   |   0 |
| Mint Authority still enabled     |   0 |
| Single holder ownership          |   0 |
| Top 10 holders high ownership    |   0 |
| holders_concentrados             |   0 |
| liquidez_mayor_que_cap           |   0 |
| liquidez_sin_bloquear            |   0 |
| peligro_rugcheck                 |   0 |
| poca_liquidez_para_su_cap        |   0 |

### Por motivo de descarte (un token puede tener varios)

| motivo                 |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:-----------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| compras_desbalanceadas |  32 | 97%           | 52%          | -100%         |            -3.95 |      0 | -        | -        | -                    |                 |
| holders_concentrados   |  56 | 66%           | 48%          | -100%         |           -11.02 |      0 | -        | -        | -                    |                 |
| liquidez_anomala       |  37 | 84%           | 45%          | -100%         |           -16.8  |      0 | -        | -        | -                    |                 |
| mc_fuera_rango         |  57 | 58%           | 35%          | -100%         |           -15.98 |      0 | -        | -        | -                    |                 |
| nombre_clonado         |  63 | 76%           | 46%          | -100%         |           -19.8  |      0 | -        | -        | -                    |                 |
| peligro_rugcheck       |  65 | 86%           | 42%          | -100%         |           -15.56 |      0 | -        | -        | -                    |                 |
| pocos_compradores      |  18 | 56%           | 27%          | -100%         |           -27.65 |      0 | -        | -        | -                    | muestra pequeña |
| presion_venta          |  31 | 65%           | 48%          | -100%         |           -22.79 |      0 | -        | -        | -                    |                 |
| volumen_inflado        |  34 | 68%           | 47%          | -100%         |            -9.74 |      0 | -        | -        | -                    |                 |

## Narrativas

### Por narrativa

|                                         | 0               |
|:----------------------------------------|:----------------|
| ('animales', 'n')                       | 0               |
| ('celebridades', 'n')                   | 3               |
| ('celebridades', 'muertos_24h')         | 100%            |
| ('celebridades', 'tocaron_2x')          | 67%             |
| ('celebridades', 'mediana_24h')         | -100%           |
| ('celebridades', 'regla_$_por_50')      | +12.81          |
| ('celebridades', 'n_7d')                | 0               |
| ('celebridades', '10x_7d')              | -               |
| ('celebridades', '50x_7d')              | -               |
| ('celebridades', 'tendencia_$_por_50')  | -               |
| ('celebridades', 'aviso')               | muestra pequeña |
| ('cripto', 'n')                         | 3               |
| ('cripto', 'muertos_24h')               | 67%             |
| ('cripto', 'tocaron_2x')                | 67%             |
| ('cripto', 'mediana_24h')               | -100%           |
| ('cripto', 'regla_$_por_50')            | -2.96           |
| ('cripto', 'n_7d')                      | 0               |
| ('cripto', '10x_7d')                    | -               |
| ('cripto', '50x_7d')                    | -               |
| ('cripto', 'tendencia_$_por_50')        | -               |
| ('cripto', 'aviso')                     | muestra pequeña |
| ('elon', 'n')                           | 0               |
| ('festividades', 'n')                   | 0               |
| ('ia', 'n')                             | 8               |
| ('ia', 'muertos_24h')                   | 88%             |
| ('ia', 'tocaron_2x')                    | 38%             |
| ('ia', 'mediana_24h')                   | -100%           |
| ('ia', 'regla_$_por_50')                | -31.56          |
| ('ia', 'n_7d')                          | 0               |
| ('ia', '10x_7d')                        | -               |
| ('ia', '50x_7d')                        | -               |
| ('ia', 'tendencia_$_por_50')            | -               |
| ('ia', 'aviso')                         | muestra pequeña |
| ('noticias_cripto', 'n')                | 0               |
| ('politica', 'n')                       | 8               |
| ('politica', 'muertos_24h')             | 62%             |
| ('politica', 'tocaron_2x')              | 67%             |
| ('politica', 'mediana_24h')             | -100%           |
| ('politica', 'regla_$_por_50')          | -29.93          |
| ('politica', 'n_7d')                    | 0               |
| ('politica', '10x_7d')                  | -               |
| ('politica', '50x_7d')                  | -               |
| ('politica', 'tendencia_$_por_50')      | -               |
| ('politica', 'aviso')                   | muestra pequeña |
| ('sin narrativa', 'n')                  | 106             |
| ('sin narrativa', 'muertos_24h')        | 69%             |
| ('sin narrativa', 'tocaron_2x')         | 38%             |
| ('sin narrativa', 'mediana_24h')        | -100%           |
| ('sin narrativa', 'regla_$_por_50')     | -16.46          |
| ('sin narrativa', 'n_7d')               | 0               |
| ('sin narrativa', '10x_7d')             | -               |
| ('sin narrativa', '50x_7d')             | -               |
| ('sin narrativa', 'tendencia_$_por_50') | -               |
| ('sin narrativa', 'aviso')              |                 |
| ('videojuegos', 'n')                    | 0               |

### Líder de su narrativa frente a seguidores y clones

| papel_en_narrativa   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| líder                |   6 | 100%          | 67%          | -100%         |           -10.5  |      0 | -        | -        | -                    | muestra pequeña |
| seguidor/clon        |  16 | 69%           | 50%          | -100%         |           -24.63 |      0 | -        | -        | -                    | muestra pequeña |
| sin narrativa        | 106 | 69%           | 38%          | -100%         |           -16.46 |      0 | -        | -        | -                    |                 |

### Calor de la narrativa (tokens con el mismo tema en el escaneo)

| calor   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 1 token |   3 | 100%          | 67%          | -100%         |           -18.56 |      0 | -        | -        | -                    | muestra pequeña |
| 2-3     |   3 | 100%          | 67%          | -100%         |             5.36 |      0 | -        | -        | -                    | muestra pequeña |
| 4-8     |   9 | 56%           | 71%          | -100%         |           -23.78 |      0 | -        | -        | -                    | muestra pequeña |
| 9+      |   7 | 86%           | 29%          | -100%         |           -28.95 |      0 | -        | -        | -                    | muestra pequeña |

### Con catalizador próximo

| con_catalizador   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no                | 120 | 71%           | 40%          | -100%         |           -16.4  |      0 | -        | -        | -                    |                 |
| sí                |   8 | 62%           | 67%          | -100%         |           -29.93 |      0 | -        | -        | -                    | muestra pequeña |

### Tokens del escaneo que comparten palabra con él

| calor_palabra_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| única            |  61 | 66%           | 36%          | -100%         |           -17.8  |      0 | -        | -        | -                    |                 |
| 2 tokens         |  16 | 81%           | 43%          | -100%         |           -18.92 |      0 | -        | -        | -                    | muestra pequeña |
| 3-4              |  10 | 60%           | 62%          | -100%         |             9.75 |      0 | -        | -        | -                    | muestra pequeña |
| 5+               |  36 | 75%           | 42%          | -100%         |           -25.82 |      0 | -        | -        | -                    |                 |

## Carteras inteligentes

Cartera con buen historial: 3 tokens o más comprados antes de detectarlos y al menos el 50% llegaron a 2x. Solo cuenta el historial que se conocía en el momento de cada detección.

### Carteras con buen historial entre los compradores

| carteras_buenas_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| 0                  |  78 | 73%           | 47%          | -100%         |            -17.5 |      0 | -        | -        | -                    |         |
| sin datos          |  50 | 66%           | 33%          | -100%         |            -16.6 |      0 | -        | -        | -                    |         |

### Mejores carteras

| cartera                                      |   tokens | tocaron_2x   | muertos   | llegaron_10x_7d   |
|:---------------------------------------------|---------:|:-------------|:----------|:------------------|
| 2V5GGJESvAwRkEveyjaFtky12cmWvWRydv9xg9DEuH53 |        3 | 67%          | 100%      | 0%                |
| 2ntthoK38GPjecFGNmT2mguPkcvJfCcPGLYaL3wHt9Pj |        3 | 67%          | 33%       | 0%                |
| 3U5MpMu7hCALYG9PyRsSLo1KzNdvEN9iLZVXxDVepoGK |        3 | 67%          | 100%      | 0%                |
| 3yzxVb8xUwtRPBLLAvNcYBNkNmKw4NgXHhQz67DzocLj |        3 | 67%          | 100%      | 0%                |
| 4NoFqu9NSwHzdKz5hV3iC6d29q3grGHBm9kyBiNCzV5K |        3 | 67%          | 100%      | 0%                |
| 59EHMioCgrqtpLCZ7fMf9buSRFpYyRJDbssUdPBHTbZ7 |        3 | 67%          | 100%      | 0%                |
| 5UkmHsjZUHtSfh1hq93rDGN7Tq8pzfAtccbVZpqsKyPo |        3 | 67%          | 100%      | 0%                |
| 5ZRU4xzKEqgD9U8qdJDFivete7PFYM5knV2zLohEr7Xg |        3 | 67%          | 100%      | 0%                |
| 5xA5vSdPVLxnvhBwqGzRprR49221DZjdLdXzzDwkXam4 |        3 | 67%          | 100%      | 0%                |
| 6Dx95TsCk5kEXLttbEo2Pt2tv77cZ4WbXVEnTwJpNih7 |        3 | 67%          | 100%      | 0%                |
| 6c7CqiBF5qaMt2KacTFrGYqn27k3VfNBx7sJ2k7CBkDy |        3 | 67%          | 100%      | 0%                |
| 7BNaxx6KdUYrjACNQZ9He26NBFoFxujQMAfNLnArLGH5 |        3 | 67%          | 0%        | 0%                |
| 7BccHibm59wFTiJCrFYpUgw7jV4aPVU6kCjoiLtqj72i |        3 | 67%          | 100%      | 0%                |
| 7SMpABfZgmE6fudC2BErbMXu4Bdtszos99Ms1JFR19kz |        3 | 67%          | 100%      | 0%                |
| 7Zy19zRNaZ2T8L7KEcZPsPT67mU376w2sAN1BSTKC1Rt |        3 | 67%          | 100%      | 0%                |

## Holders

### % del suministro en los 10 mayores holders

| top10_holders   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15%            |   1 | 100%          | 100%         | -100%         |           -49.89 |      0 | -        | -        | -                    | muestra pequeña |
| 15-25%          |  12 | 83%           | 25%          | -100%         |           -27.99 |      0 | -        | -        | -                    | muestra pequeña |
| 25-35%          |  11 | 45%           | 45%          | -87%          |            -5.28 |      0 | -        | -        | -                    | muestra pequeña |
| 35-50%          |  10 | 50%           | 60%          | -92%          |            -1.04 |      0 | -        | -        | -                    | muestra pequeña |
| >50%            |  45 | 69%           | 45%          | -100%         |           -12.41 |      0 | -        | -        | -                    |                 |

### Número de holders

| num_holders   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <100          |   7 | 29%           | 60%          | -88%          |           -16.62 |      0 | -        | -        | -                    | muestra pequeña |
| 100-300       |  18 | 50%           | 50%          | -94%          |            -3.95 |      0 | -        | -        | -                    | muestra pequeña |
| 300-1K        |  16 | 75%           | 44%          | -100%         |           -24.58 |      0 | -        | -        | -                    | muestra pequeña |
| 1K-3K         |  28 | 79%           | 42%          | -100%         |           -19.65 |      0 | -        | -        | -                    | muestra pequeña |
| 3K+           |  11 | 73%           | 36%          | -100%         |             5.83 |      0 | -        | -        | -                    | muestra pequeña |

### GT Score

| gt_score_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <30         |  27 | 70%           | 33%          | -100%         |           -24.67 |      0 | -        | -        | -                    | muestra pequeña |
| 30-45       |  48 | 73%           | 48%          | -100%         |           -11.83 |      0 | -        | -        | -                    |                 |
| 45-60       |  29 | 72%           | 45%          | -100%         |            -7.78 |      0 | -        | -        | -                    | muestra pequeña |
| 60+         |   1 | 0%            | 0%           | -79%          |           -32.17 |      0 | -        | -        | -                    | muestra pequeña |

## Señales por separado

### Edad al detectarlo

| edad      |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15 min   |  85 | 72%           | 41%          | -100%         |           -19.96 |      0 | -        | -        | -                    |                 |
| 15-30 min |   8 | 50%           | 67%          | -94%          |           -17.61 |      0 | -        | -        | -                    | muestra pequeña |
| 30-60 min |  11 | 82%           | 30%          | -100%         |           -35.99 |      0 | -        | -        | -                    | muestra pequeña |
| 1-3 h     |   9 | 78%           | 22%          | -100%         |           -16.71 |      0 | -        | -        | -                    | muestra pequeña |
| 3-24 h    |  13 | 54%           | 54%          | -100%         |            19.41 |      0 | -        | -        | -                    | muestra pequeña |

### Capitalización al detectarlo

| cap       |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <50K      |  48 | 52%           | 36%          | -100%         |           -16.32 |      0 | -        | -        | -                    |                 |
| 50-150K   |  35 | 86%           | 50%          | -100%         |           -23.53 |      0 | -        | -        | -                    |                 |
| 150-500K  |  26 | 65%           | 40%          | -100%         |            -9.18 |      0 | -        | -        | -                    | muestra pequeña |
| 500K-1.5M |  10 | 100%          | 50%          | -100%         |           -23.4  |      0 | -        | -        | -                    | muestra pequeña |
| >1.5M     |   9 | 89%           | 33%          | -100%         |           -14.22 |      0 | -        | -        | -                    | muestra pequeña |

### Compradores / vendedores (1 h)

| compradores_vs_vendedores   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <1.2                        |  31 | 65%           | 48%          | -100%         |           -22.79 |      0 | -        | -        | -                    |                 |
| 1.2-3                       |  37 | 43%           | 38%          | -89%          |           -14.11 |      0 | -        | -        | -                    |                 |
| 3-8                         |  28 | 82%           | 26%          | -100%         |           -30.53 |      0 | -        | -        | -                    | muestra pequeña |
| >8                          |  32 | 97%           | 52%          | -100%         |            -3.95 |      0 | -        | -        | -                    |                 |

### Volumen de 1 h / capitalización

| volumen_vs_cap   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <0.5             |  58 | 84%           | 28%          | -100%         |           -30.61 |      0 | -        | -        | -                    |                 |
| 0.5-1            |   9 | 56%           | 38%          | -100%         |           -23.64 |      0 | -        | -        | -                    | muestra pequeña |
| 1-3              |  27 | 48%           | 62%          | -90%          |             2.83 |      0 | -        | -        | -                    | muestra pequeña |
| >3               |  34 | 68%           | 47%          | -100%         |            -9.74 |      0 | -        | -        | -                    |                 |

### Peligros de RugCheck

| peligros_rugcheck   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 0                   |  55 | 55%           | 38%          | -100%         |           -17.55 |      0 | -        | -        | -                    |                 |
| 1                   |  56 | 91%           | 42%          | -100%         |           -20.45 |      0 | -        | -        | -                    |                 |
| 2+                  |   9 | 56%           | 43%          | -100%         |            17.48 |      0 | -        | -        | -                    | muestra pequeña |
| sin datos           |   8 | 50%           | 57%          | -85%          |           -28.31 |      0 | -        | -        | -                    | muestra pequeña |

### Liquidez bloqueada (RugCheck): con 0% el creador puede retirarla

| liquidez_bloqueada   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 0%                   |  35 | 77%           | 42%          | -100%         |           -19.1  |      0 | -        | -        | -                    |                 |
| parcial              |  38 | 68%           | 47%          | -100%         |            -3.99 |      0 | -        | -        | -                    |                 |
| 100%                 |  47 | 70%           | 33%          | -100%         |           -25.08 |      0 | -        | -        | -                    |                 |
| sin datos            |   8 | 50%           | 57%          | -85%          |           -28.31 |      0 | -        | -        | -                    | muestra pequeña |

### Puntuación (quintiles)

| puntuacion_q   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| Q1 (baja)      |  28 | 71%           | 36%          | -100%         |           -27.2  |      0 | -        | -        | -                    | muestra pequeña |
| Q2             |  31 | 71%           | 30%          | -100%         |           -24.37 |      0 | -        | -        | -                    |                 |
| Q3             |  22 | 77%           | 57%          | -100%         |             5.81 |      0 | -        | -        | -                    | muestra pequeña |
| Q4             |  19 | 68%           | 33%          | -100%         |           -29.58 |      0 | -        | -        | -                    | muestra pequeña |
| Q5 (alta)      |  28 | 64%           | 50%          | -100%         |           -10.09 |      0 | -        | -        | -                    | muestra pequeña |

### DEX

|                                           | 0               |
|:------------------------------------------|:----------------|
| ('meteora', 'n')                          | 0               |
| ('meteora-damm-v2', 'n')                  | 6               |
| ('meteora-damm-v2', 'muertos_24h')        | 83%             |
| ('meteora-damm-v2', 'tocaron_2x')         | 75%             |
| ('meteora-damm-v2', 'mediana_24h')        | -100%           |
| ('meteora-damm-v2', 'regla_$_por_50')     | +5.21           |
| ('meteora-damm-v2', 'n_7d')               | 0               |
| ('meteora-damm-v2', '10x_7d')             | -               |
| ('meteora-damm-v2', '50x_7d')             | -               |
| ('meteora-damm-v2', 'tendencia_$_por_50') | -               |
| ('meteora-damm-v2', 'aviso')              | muestra pequeña |
| ('meteora-dbc', 'n')                      | 10              |
| ('meteora-dbc', 'muertos_24h')            | 70%             |
| ('meteora-dbc', 'tocaron_2x')             | 29%             |
| ('meteora-dbc', 'mediana_24h')            | -100%           |
| ('meteora-dbc', 'regla_$_por_50')         | -44.05          |
| ('meteora-dbc', 'n_7d')                   | 0               |
| ('meteora-dbc', '10x_7d')                 | -               |
| ('meteora-dbc', '50x_7d')                 | -               |
| ('meteora-dbc', 'tendencia_$_por_50')     | -               |
| ('meteora-dbc', 'aviso')                  | muestra pequeña |
| ('moonshot', 'n')                         | 0               |
| ('orca', 'n')                             | 1               |
| ('orca', 'muertos_24h')                   | 0%              |
| ('orca', 'tocaron_2x')                    | 100%            |
| ('orca', 'mediana_24h')                   | +233%           |
| ('orca', 'regla_$_por_50')                | +91.11          |
| ('orca', 'n_7d')                          | 0               |
| ('orca', '10x_7d')                        | -               |
| ('orca', '50x_7d')                        | -               |
| ('orca', 'tendencia_$_por_50')            | -               |
| ('orca', 'aviso')                         | muestra pequeña |
| ('pump-fun', 'n')                         | 12              |
| ('pump-fun', 'muertos_24h')               | 8%              |
| ('pump-fun', 'tocaron_2x')                | 33%             |
| ('pump-fun', 'mediana_24h')               | -79%            |
| ('pump-fun', 'regla_$_por_50')            | -22.02          |
| ('pump-fun', 'n_7d')                      | 0               |
| ('pump-fun', '10x_7d')                    | -               |
| ('pump-fun', '50x_7d')                    | -               |
| ('pump-fun', 'tendencia_$_por_50')        | -               |
| ('pump-fun', 'aviso')                     | muestra pequeña |
| ('pumpswap', 'n')                         | 96              |
| ('pumpswap', 'muertos_24h')               | 80%             |
| ('pumpswap', 'tocaron_2x')                | 41%             |
| ('pumpswap', 'mediana_24h')               | -100%           |
| ('pumpswap', 'regla_$_por_50')            | -17.11          |
| ('pumpswap', 'n_7d')                      | 0               |
| ('pumpswap', '10x_7d')                    | -               |
| ('pumpswap', '50x_7d')                    | -               |
| ('pumpswap', 'tendencia_$_por_50')        | -               |
| ('pumpswap', 'aviso')                     |                 |
| ('raydium', 'n')                          | 2               |
| ('raydium', 'muertos_24h')                | 0%              |
| ('raydium', 'tocaron_2x')                 | 50%             |
| ('raydium', 'mediana_24h')                | -46%            |
| ('raydium', 'regla_$_por_50')             | +11.84          |
| ('raydium', 'n_7d')                       | 0               |
| ('raydium', '10x_7d')                     | -               |
| ('raydium', '50x_7d')                     | -               |
| ('raydium', 'tendencia_$_por_50')         | -               |
| ('raydium', 'aviso')                      | muestra pequeña |
| ('raydium-clmm', 'n')                     | 1               |
| ('raydium-clmm', 'muertos_24h')           | 0%              |
| ('raydium-clmm', 'tocaron_2x')            | 0%              |
| ('raydium-clmm', 'mediana_24h')           | -80%            |
| ('raydium-clmm', 'regla_$_por_50')        | -26.48          |
| ('raydium-clmm', 'n_7d')                  | 0               |
| ('raydium-clmm', '10x_7d')                | -               |
| ('raydium-clmm', '50x_7d')                | -               |
| ('raydium-clmm', 'tendencia_$_por_50')    | -               |
| ('raydium-clmm', 'aviso')                 | muestra pequeña |
| ('raydium-launchlab', 'n')                | 0               |
| ('stonkfun', 'n')                         | 0               |

## Supervivencia por horizonte

- 30m: 56% vivos (n=1842)
- 1h: 49% vivos (n=1835)
- 6h: 36% vivos (n=1372)
- 24h: 30% vivos (n=128)

## Supervivientes (tokens de 3 a 120 días que despiertan)

Aún no hay supervivientes (se buscan una vez por hora).

## Últimas alertas del vigía (6 h)

| ts    | simbolo     | narrativa   | prioridad   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:------------|:------------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 20:52 | PENNY       | cripto      | baja        |        2   | 13K  |              331 |             226 | FXoxRGx1jEHVY2VWMrwkSmrUrT8XwpH9ePikQsjapump | nan    |
| 20:47 | AI6         |             | vetada      |        2.4 | 314K |             1476 |             771 | DKxXdaMC1so182urvrrnhs6V6fGTrttPS8br6JuEpump | nan    |
| 20:44 | BRIDGE      |             | vetada      |        2   | 16K  |              297 |             108 | AgtkJoUnsjTJFx6EAgVW9Bfbm9uJoWuJRagSLMifqqPw | nan    |
| 20:44 | AGSHLD      |             | vetada      |        2.9 | 77K  |              111 |              26 | GxQymQf6heKhkJMEWo7vgGjGE4w9P4SufgNAvivYbonk | nan    |
| 20:42 | meme/acc    | cripto      | alta        |        4   | 11K  |               56 |              33 | GL68bnTmd6upLw1iHDNdvkBRcEb7VKDCz5woH6Jupump | nan    |
| 20:40 | LOBBY       |             | baja        |        4   | 11K  |               92 |              51 | 5Z5WvVb6ZV5mwVJu3yoPoFeQFJ9jfERR2iXjg4nXpump | nan    |
| 20:37 | KYLE        |             | vetada      |        2.9 | 18K  |              444 |             308 | ALXXnx7apbbnoYe8D8Sgfhac4QEcfQEQuctWeNi82ha8 | nan    |
| 20:31 | FROSTY      |             | vetada      |        2.6 | 16K  |              362 |             262 | 6xjdmD4NyXAHEVfXt2s8oPFree4Eci2EThL1oDQypump | nan    |
| 20:28 | Spend       |             | vetada      |        2.7 | 29K  |              372 |             193 | AMVBZPNtnDSgHoNZYRKjPQHPXFQogrRjTnUfxodopump | nan    |
| 20:28 | HOOK        |             | vetada      |        2.4 | 17K  |               59 |              29 | 66UokDvAUWuT8DiX1JxAyisx3uo4nErZYQocXTowQm2G | nan    |
| 20:28 | PICK        |             | vetada      |        2.4 | 28K  |              244 |             149 | EFzc9krvFrc3SbPKrUabiKxtrWNsDbXGUMZt5VtowoFX | nan    |
| 20:20 | INUINK      |             | vetada      |        3.3 | 245K |               82 |              20 | 9k7NgXqiJ7tvLtiB6HXdJHnKZZynFz46AB6Eg4Uwpump | nan    |
| 20:04 | BridgePad   |             | vetada      |        3.3 | 9K   |              199 |             147 | CQA5Hm11M4p24FkAndoSVnXKGBEnHkRqbfhCDXzBpump | nan    |
| 20:02 | PAYDAY      |             | vetada      |        2.8 | 35K  |              490 |             137 | BQKQeoxCEwyn4kPyEpJ88NqBaEELG6fLKufRCsvMpump | nan    |
| 20:02 | Goldbid     |             | vetada      |        3.6 | 73K  |               60 |              17 | 9UjQYT8BTZbgYQVYpLLiSsZ1b4f9UeWfQFBMiV67pump | nan    |
| 20:01 | D/TRUMP     | politica    | vetada      |        2.6 | 30K  |              126 |              86 | BTgenoGircCT23iFM7EzKf9jaf2LFnfh9K6sfpz6pump | nan    |
| 19:56 | Nibs        |             | vetada      |       14   | 9K   |               40 |              21 | DVx9ULhL3e7xQsGagXgkxdZoWTVorYgDbe33ydqyFhyN | nan    |
| 19:54 | PIPE/ACC    |             | vetada      |        2.4 | 17K  |              309 |             173 | 3rNV2pmns8nCpx5NjSTwoBxARwQs21BgsdwjxXdfpump | nan    |
| 19:52 | ipfs        |             | vetada      |        2.4 | 31K  |              622 |             363 | DSudLYZaGrxPFhQydNEDELTt4aDC9bhetA4yG8utpump | nan    |
| 19:44 | Bronbell    |             | vetada      |        2.7 | 73K  |               99 |              20 | Ad3kZ8FJKiZw7qYL6amZsEq4tscCq5cUvYte4XQAmoon |   0    |
| 19:43 | MOTEPAID    | ia          | alta        |        2.1 | 9K   |              117 |              73 | GZR6rd4rVd2wtKh7cFUTW8KB8Z4wMHro6vg1BCcLpump |   0.28 |
| 19:40 | 世界末日        |             | vetada      |        4   | 22K  |              209 |              27 | BorCApfhv7enbjDuRxd9CxA1Ucy7b9CZrbcQWJLu3zU9 |   1.88 |
| 19:40 | Entry       |             | vetada      |        3   | 8K   |               62 |              37 | EP4FsbkhEBpAH1mcseYtZXLv6KSNehtPRRixj3fapump |   0.4  |
| 19:29 | LUMI        |             | vetada      |        3.8 | 25K  |              140 |              70 | 7dMdLxaSg4JLXdhtG28wx7wGPUKMQbK4NUdAoXePpump |   0.24 |
| 19:29 | GAMEZ       |             | baja        |        8.9 | 8K   |               76 |              49 | 5QJfwezvP4jCpBJk2MnPk5EvGx57znhZNzewbpUBuZwJ |   1.72 |
| 19:28 | WRIT        |             | vetada      |        2.1 | 20K  |              170 |             115 | writr2gAJwSvyPLYtxJJT7jCTqFvmCfxk6Xg6qpq8pq  |   0.2  |
| 19:22 | FROINKCAT   |             | vetada      |       12.5 | 249K |              309 |             105 | 8VxaJHWP9NGYVDeYexGXXbmpmoiVXNvspjqtkbZUpump |   0    |
| 19:15 | fomome      |             | vetada      |        2.2 | 15K  |              192 |              78 | GYMnLJmPTxriy27NPa1GyF6wZkpQpWDGDpxF4dBRkBx  |   0    |
| 19:12 | Tehc        |             | vetada      |        2.3 | 14K  |               95 |              36 | DWvE2aXXTUvCWtrcN4w9eVySP7KNhJbUUz3HsEHXYyW1 |   0    |
| 19:09 | JEETTARA    | cripto      | baja        |        2   | 9K   |              143 |              84 | qyLr3k8yBZz5Lj3aV3uzmkqpGyyBqLyyfJ3ugbvpump  |   1.1  |
| 19:08 | CCAT        |             | vetada      |        2.9 | 86K  |              735 |             451 | H7YEgWhVSWW1HAJomtsBTmSpaBRCoD9V17BvwEyipump |   0    |
| 19:08 | Fo          |             | vetada      |        3.8 | 15K  |              222 |             170 | Bken2392oK2zoS9S4711KR7Mm8m5ynaftZc2SUPxFHjY |   0.46 |
| 19:05 | SARP        |             | vetada      |        3.7 | 245K |               63 |              43 | 53gTSW4WFgrRHgQCtf5CyXgrEBNyNWHobYBAhqQJpump |   1    |
| 19:05 | SMUDGE      |             | vetada      |        6.1 | 9K   |              115 |              71 | Af22pLvYvP5Tt8RyqdevgYefVujAa9eLNsa4rpDupump |   0.34 |
| 19:05 | LEFTCURVE   |             | vetada      |        3.6 | 15K  |              382 |              79 | Hsu6bApBpA71odJDPx3pcpYuyDUN4Pi6cKx7pYGDiSJq |   0    |
| 19:03 | AMC         |             | vetada      |        5.7 | 145K |              492 |              65 | 8LPQXVXwXrpCeSbBiVR7fjKEVb1iSptKvFLRKVKdpump |   1.69 |
| 18:57 | p/xmr       |             | vetada      |        3.4 | 20K  |              357 |             232 | u9uhxHwAn5K5jcuB25QEXBX7XBPArFSTkTQg7F1nuCA  |   0.29 |
| 18:54 | CRACKED     | cripto      | baja        |        2.4 | 9K   |              152 |              68 | KMxqn3LHW8aVBK4rmphAqYcEnBVcYzLqzKJ8vyCpump  |   0.37 |
| 18:51 | Parrot      |             | vetada      |        7.7 | 16K  |               80 |              47 | 7DsTxrXyApdqySsJC59drq9gZfuLWF93Wv5Th5uhpump |   0.21 |
| 18:46 | VOM         |             | vetada      |        2.9 | 11K  |               95 |              63 | 683rxoY4Xtg2Xb7PQidPbv66NuyDyM1bMTQzJTDFpump |   0.36 |
| 18:44 | Joe         |             | vetada      |        2.2 | 145K |              178 |              26 | 3i5xUxZm4gYN8gZMSZd3xhMxVS3vdGn33ETjK3g9ADhY |   0    |
| 18:44 | LIFT        |             | vetada      |        3.5 | 148K |              246 |             115 | 2URzCYAiUypdmbiKBUv2xGLbaRxxNUFryhawJKTamoon |   0    |
| 18:38 | AgentPaid   | ia          | alta        |        6.1 | 13K  |               64 |              39 | EsceEf93ytUGvepAcY71fahRcFE4bZSkz2M2X7dPpump |   0.33 |
| 18:37 | FLY         |             | vetada      |        2.5 | 14K  |              385 |             155 | CJqg1CXuBAETr7mAJuuM7vf7bJsTWmmy4SuzLGsnpump |   0.19 |
| 18:34 | Cluely      |             | baja        |        2.2 | 17K  |               97 |              46 | 8vHheszLT8RHMqTLwuE4BnY7GwT3YPBSW4rFqopmbbiC |   0.33 |
| 18:33 | Streampay   |             | baja        |        6.5 | 12K  |               80 |              58 | Hqi51M7x3bQw8XnNbTQZ6btZAdqvj9w5CFkCjFLqpump |   0.3  |
| 18:29 | PFC         |             | vetada      |        2   | 51K  |              947 |             497 | 5bpnsoZ3HgwGs42Tyd6nEK9s9MCQhhDjVmUveqgbmyJK |   0.11 |
| 18:29 | pill        |             | vetada      |        3.4 | 15K  |              289 |             220 | 77VDJkKqNDZQZTuoZ5cqtKyLP1PyjMonwfcLvdEwhHJq |   0.22 |
| 18:29 | Miurafrg    |             | vetada      |        2.2 | 68K  |               75 |              19 | D7gwqhNVvz698hNoWwQQgkJeZ9pS8fwdUzu8om7imoon |   0    |
| 18:24 | BRAIN       |             | vetada      |        2.7 | 76K  |              394 |             110 | B7HbqBEFJaxWYKUPoMvcTQraxZf9prpr1qJQFr47NVUi |   0    |
| 18:24 | FRENS       |             | vetada      |        2.6 | 11K  |               65 |              39 | 85oYxESrgDPDkEQNt8n65mYfArfSD7LqevYtfSXaSpCV |   0.3  |
| 18:24 | BRAIN       |             | vetada      |        2.5 | 27K  |              213 |              54 | CaWLh6nbv1N1UtwJqkvJvdrZKivKczjxKXqF1u5SNS9p |   0    |
| 18:20 | NALA        | animales    | alta        |        6.1 | 11K  |               75 |              45 | H74zH4LnbC3Juxvzvo6GdfLzrepoG2FXoK6R7fi9pump |   0.46 |
| 18:13 | MTMEI       |             | vetada      |        2.2 | 100K |              507 |             178 | JCDe5ecFTfbLoY1fmVcMZ6G4bMho25xEknzF2M8hpump |   0    |
| 18:09 | Trailer     |             | vetada      |        4.5 | 15K  |               73 |              54 | 6TLpr7zsrg6e6vT8hNuEoUK7xw47NcFHGGXGCAbYSTNK |   0.22 |
| 18:05 | Tiangong    |             | vetada      |        2.7 | 85K  |               96 |              23 | DWvCu4VXyck6hFxVpLyxAmrQ61pXr6K6yd3WmNcAmoon |   0    |
| 18:05 | WATCH       |             | vetada      |        2.6 | 45K  |              200 |              67 | 51GGCsVPuMSkrWkJM4r8wBz6HVPBqVXVpP1unSDgpump |   0    |
| 18:03 | MSUKE/ACC   |             | vetada      |        2.6 | 13K  |              388 |             239 | FatepgpFaFkkLQF7Vo3KKWTN4U3rfdeM8crg5v2Mpump |   0.2  |
| 17:58 | cbADA       |             | vetada      |        2   | 328K |               43 |              25 | cbADAmv9issuPfhFwyQG3xac4DGPd1LDSt1oz7vwJsg  |   0.98 |
| 17:58 | Dared       |             | baja        |        3.8 | 9K   |              205 |             134 | CUZ2CR3FMmjxbknvCBknyxTV1RVBMUcwSfmun1j4pump |   0.44 |
| 17:58 | ZELUM       |             | baja        |        2.3 | 9K   |              147 |              83 | GifXoMHe5L3jed2Hqf3vCjMNZgM495fbaWM61Nx2pump |   0.37 |
| 17:55 | π3.1415926  |             | vetada      |        3.8 | 27K  |              239 |              41 | 2id5EcKDfWBWzw73K3aKZX78hWVDdVQTzRt5XNGVWDZA |   0    |
| 17:44 | FORKABLE    |             | baja        |        2.9 | 9K   |              172 |             127 | 3kFEyXL67H6MDx4FUJezhATxuHzfCF7i5bu6C6dwpump |   0.41 |
| 17:44 | Bukas       |             | vetada      |        3.4 | 81K  |              105 |              27 | 7aH6UCFfaybr54aMg11twnugg3b3ZgDjfsAoGZhsBAGS |   0    |
| 17:42 | SHALOM      |             | vetada      |        2.4 | 14K  |              384 |             295 | 4NHE99TsK5J9Y7VwywjyZtPt2fphr7UiFFSpbpQ5Dfp9 |   0.53 |
| 17:42 | SHALOM      |             | vetada      |        2.5 | 17K  |              290 |             104 | wboyC3dMG9RTvHm1nz3iGPAPsQcptDzGkRgEPikZC59  |   0    |
| 17:36 | ZLM         |             | vetada      |        2.4 | 16K  |              242 |             172 | 4P7DXwmeVj3rg4nZb9ySCfzSJSrEsvFjUYRmymuPpump |   0.24 |
| 17:34 | ETCH        |             | vetada      |        2.1 | 9K   |              206 |             138 | J8fAUfigwW9XHwmEXYwpAp9Yp1JTRYN8qrYE63Npump  |   0.38 |
| 17:33 | PSYCHO      |             | vetada      |        2.7 | 24K  |              740 |             525 | 9hvub8ZabGxr2AiJprc65tP92fe2cx6mhwyUemrYpump |   0.15 |
| 17:32 | Instbot     |             | vetada      |        2.1 | 66K  |               62 |              27 | drqoky7HYTxq32MqzXZEWakLrMizD81HCWSkB7gmoon  |   0    |
| 17:31 | STUPIDINU   |             | vetada      |        6.6 | 73K  |               91 |              46 | CCU9jkaWPRjdsKuTRJa7gJZ22Qf1gXSZQiDV69JNG5W3 |   0.27 |
| 17:22 | ESACLD      |             | vetada      |        2.5 | 75K  |               65 |              24 | 5q7gBEad2FfCqP1SL1PC4dLLoEBUEBPBMc7BJ3m4BAGS |   0    |
| 17:22 | BotBook     | ia          | alta        |        2.6 | 19K  |               94 |              70 | 7n7dS5Dk7YjaKKDzb5e9gPK3Md6mziTLsBA3mJYu6gnV |   2.83 |
| 17:20 | Appshare    |             | vetada      |        2.5 | 47K  |              450 |             252 | GgzBN4bbyHbeh2MaVoHWcKHrjZuUQKUQC2bnamJJpump |   1    |
| 17:09 | TANK        |             | vetada      |        3.4 | 17K  |              404 |             107 | CvQEwhBwTKTa4cWhMPYFWkRzpCDX4H54Qok5CHCZxgEv |   0    |
| 17:07 | anoncoin    |             | vetada      |        3.2 | 11K  |               52 |              25 | 6z92xw4oCWRxo9ynBEfpu5ksxEHVMuYN5VK6Wj7Lpump |   2.78 |
| 17:06 | MUNI        |             | vetada      |        2.2 | 11K  |               83 |              55 | H12pRhhNmRLoPV1PTwbk5KRTLeU3h5w4bgHQQ42pump  |   0.19 |
| 17:06 | Fern        |             | vetada      |        2   | 13K  |              216 |              93 | 2rQXt9syrCKheKtE22RRiQHMZKuP2xXGBc8v9vmwR25m |   0    |
| 17:04 | BLEP        |             | baja        |        4.2 | 16K  |               52 |              12 | BSFQ37GMvBNL82PpRV2ALi7zM8FiXdQkAoTXxo6epump |   0.99 |
| 17:04 | Vikings     |             | vetada      |        3.4 | 120K |              464 |              64 | 7jjHtz8aGsz9H9KXidDcenJMhczMUi1FoECuHfsRpump |   0    |
| 17:03 | Nowzad      |             | vetada      |        2.6 | 20K  |              225 |              99 | Fqwgkjvj3Wv4bdWkXHmER2HX7BfeexPvSKpQp17pPvCD |   0    |
| 17:02 | WIKIMEDIA   |             | vetada      |        2.3 | 12K  |               87 |              15 | AmT4eGZYQsiYP74NGxP9Jm96QGRvDG7qb7yTCBBfo9fB |   0    |
| 17:01 | AIPAD       |             | vetada      |        2.8 | 32K  |              194 |             144 | 8sTosJHKWWXQg8KSniVtusHsBFtGYi1wwY2qagGpump  |   0.1  |
| 17:01 | PEARLS      |             | vetada      |        2.5 | 25K  |              168 |              51 | 5UB3nKLQSbs7AtvxRZBt6oW2CbCN7jSMwDRcwX21KA3y |   0    |
| 17:01 | Ibbot       |             | vetada      |        2.4 | 73K  |               44 |              10 | DeLAbMAoCb8UpsYvbtc6NkcUVwJV9dGDqbmv8r9fbonk |   0    |
| 16:59 | love        |             | vetada      |        2.1 | 9K   |              268 |             206 | 7kcF4nkRSjGv7VbueJ7oh9AwyHDQ1rLZ4YdDoiREtbyz |   0.69 |
| 16:52 | fatgirls    |             | vetada      |        2.1 | 32K  |              169 |             126 | AiZQ8kDQpTDvx1oS8B2W7Abn5YNX1yp6FMe3Pwxqpump |   0    |
| 16:52 | ROAR        |             | vetada      |        2.4 | 24K  |              296 |              64 | 7H7AV27MPyfpxBGzv348yUx6ujuW4hNcCSVtkAnNE2PH |   1.08 |
| 16:52 | HANDLEIT    |             | vetada      |        2.2 | 70K  |              168 |              23 | MVxpV6jr9HCSvzT2NWYd6VZsKzeGmHsfLx3DmPdBaib  |   0    |
| 16:44 | ITCH        |             | vetada      |        6.1 | 43K  |               85 |              64 | 2SWXLespX4sC3rzMnbS4pXyUt6aVqSaZK8X7fg8ppump |   0.86 |
| 16:43 | WAVEBOX     |             | vetada      |        4.4 | 88K  |               81 |              29 | B3iCnfSDQ62XKz59qCWZyid4gcYFcizKj9sisWyBAGS  |   0    |
| 16:43 | HEXUMLITE   | animales    | alta        |        5.9 | 10K  |               50 |              30 | HoyhNp6vs2G6c2zQbnjGGmnGggdo9158v3kk7AQfKZ8k |   0.56 |
| 16:32 | DINOP       |             | vetada      |        3.6 | 79K  |               52 |              10 | 87hDkuFeKGg1s8iyMhvy2Tj8QSVamRZ8S4vADcUqmoon |   0    |
| 16:29 | [0]         |             | vetada      |       11   | 10K  |               69 |              25 | 5Awkz8gZk7rMabaVkKKJpMFZiiAZz2GaPHE23CPWpump |   0.34 |
| 16:27 | tPAID       |             | vetada      |        3.2 | 18K  |              100 |              67 | EaJNWKv11TD3WbDCKe2i5mUYTeT11Tbycvcgy64Epump |   0.21 |
| 16:23 | Avaxpad     |             | vetada      |        2.9 | 14K  |              105 |              61 | 7GHogUsFe62JN4scPwCXfVYPL4U8ZK9jhZqc8J7Epump |   0.29 |
| 16:23 | STILL       |             | vetada      |        2.9 | 120K |              978 |             718 | 7qLn9eW3CHiCMJWokv4Kxmgs4daSnnRE4hxAzqqFpump |   0.46 |
| 16:23 | STILLS      |             | vetada      |        2.9 | 19K  |              306 |             226 | A9kLprZkibNwg6ndCNDKUjQTSBhLetjaF1fZ2mnmRyq4 |   0.39 |
| 16:23 | HOODRICH    |             | vetada      |        2.1 | 86K  |              294 |             155 | Dz732sy9sP94UQyg33p4MuTUpe4GwRibHkLmm9mxpump |   0    |
| 16:16 | Swball      |             | vetada      |        3.2 | 77K  |               49 |              15 | CxEMeB1f3THNn49xYjbczBUYG7Vpr4Th3qKuFfpHbonk |   0    |
| 16:16 | RIFT        |             | baja        |        3   | 12K  |              152 |              91 | BMvV8tPoir8YUdYcHDLUAWDw7erxgL8ivdSXzH6WuxU  |   0.32 |
| 16:11 | Voltbox     |             | vetada      |        9   | 81K  |               91 |              25 | DicH1cvxQESgSm4i2Hojdjvoekzfa9o3FeUcE4YDbonk |   0    |
| 16:09 | MCASH       |             | vetada      |        7.8 | 8K   |              111 |              52 | GTZo5jRqt1rib4FUe3v9mprBx1H9vSswpSTVrTiEQxkP |   1.47 |
| 16:04 | HYPNOSIS    |             | baja        |        3.9 | 11K  |              202 |             130 | DjpZBPDv1Nbt2EQFtBvsnCVNGDARUrR7ZLaG3ThNpump |   0.29 |
| 16:04 | fatbear     | animales    | vetada      |        4.7 | 109K |              394 |             275 | 3hrakqTZceuodL7E5T3gpVcZjCaFFpuS7uxb4X59bijQ |   0.16 |
| 16:01 | USA250      |             | vetada      |        4   | 352K |              459 |              97 | 4M8ZCic3qyxbDM5yC8hMFW3ogHn8q9UCC3v6QGSppump |   0    |
| 16:01 | HDEX        |             | vetada      |        2.9 | 30K  |              249 |             107 | EhNF7NoYa47UByaW6CAjobuoX7aia3LFAxNupFMLpump |   0.15 |
| 15:59 | Groyper     |             | vetada      |       11.1 | 19K  |               60 |              38 | 73TkrTrbUrEGp17j7yVWrQ2MN2wRMUCmH8WQTShLXa6X |   0.21 |
| 15:58 | RLUSD       |             | vetada      |        4.6 | 224K |              183 |              44 | GQgpzXBbJsqeMuTtNdBpbnicyTQ6dRgSaoKeaNipump  |   6.78 |
| 15:51 | PNN         |             | alta        |        3.4 | 10K  |              131 |              86 | 8AT9M77r2VmPeLyxX92NACuFoshghj323WG8AX77pump |   0.37 |
| 15:49 | TIDALENS    |             | vetada      |        2.9 | 8K   |              111 |              77 | 9EVA2KZi77fLb6gzHXv54CRvFBJ7MbGqFbKQoKcwpump |   0.37 |
| 15:49 | worm        |             | vetada      |        2.2 | 12K  |              316 |             219 | D73WxcQ9H7fbvr6tQTmpeMUgD7FTKExMTPkfhuifworm |   0.29 |
| 15:41 | Inufluencer |             | vetada      |       13.8 | 8K   |               47 |              29 | FusmN7ysBDEqmFYFErf5jnRA3TbEDdBeshP4tGgBWK2L |   0.33 |
| 15:41 | STRM        |             | baja        |        3   | 10K  |              103 |              58 | 9hfm75vATGR7qhfJAX3MGvf5U8qyTSLrsycy4gAYpump |   0.34 |
| 15:38 | Rillkin     |             | baja        |        3.1 | 9K   |               73 |              38 | 2xmG2kZCyw7Up9p8wfLLD431Zs6dxErFtPQCx6Djpump |   1.66 |
| 15:38 | Mewania     |             | vetada      |        2.5 | 359K |               83 |              23 | 2xwekhGkoiYFCGs6eEYcJhSmjMqt1bXvMKJ2dKbZpump |   0    |
| 15:31 | IRL         |             | vetada      |        2.1 | 17K  |              312 |              84 | CYnjTog1LKuGUYVYbFVBXCwbXCwebkBGLfLhiHEsNQE7 |   0    |
| 15:31 | HIDE        |             | vetada      |        3.9 | 14K  |              167 |              97 | HpZuLjEo7ETnxh9xJjiYfAqy7Rt4781sqhqtkw6Epump |   0.23 |
| 15:25 | RIOKICK     |             | vetada      |        4   | 85K  |              180 |              35 | 7rQtAochc6Jqaz5Xt7o5hcYkBKfU882sGFu65zGnbonk |   0    |
| 15:18 | FANTASY     |             | vetada      |        4.9 | 20K  |              310 |              68 | 4gSk6ra1GuzpCC7tz1zy7abDXhi9KhcZNoiFUhpNDbH6 |   0    |
| 15:17 | SUSHIPEDIA  |             | vetada      |        5.4 | 39K  |              171 |              94 | 12V4dwQdN1foGHqHF5VzWDjy9bsquYpELHsp34Jjpump |   0    |
| 15:06 | Payload     |             | vetada      |        6.5 | 12K  |              147 |              88 | LJiu7kzDBph34hssquz1SyzntC5pYs3zy4qkM6Apump  |   0.56 |
| 14:58 | KIRO        | cripto      | alta        |        3.6 | 11K  |              101 |              71 | Gppu32ydA72X6CSH7aJcgkZjWpExFhU47E4xbwBxxiiU |   0.33 |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **19934**; seguidas de un desplome (caída a un 40% o menos en 30 min): **453**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |             16119 | 1%                   | 9%                   |
| Ticket medio < $30 (volumen de microcompras) |             17889 | 2%                   | 9%                   |
| Más de 8 compradores por vendedor (5 min)    |               121 | 10%                  | 2%                   |
| Subida de más del 100% en 1 h                |              2246 | 13%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |               248 | 47%                  | 2%                   |
| Aceleración final                            |               298 | 15%                  | 2%                   |
| Más vendedores que compradores (5 min)       |             17708 | 1%                   | 15%                  |
| Ya multiplicó x5 o más desde la detección    |              6526 | 2%                   | 2%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra   |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor   | mc_mayor   | mint_mayor                                   |
|:----------|------------:|---------------------:|:------------------|:--------|:-----------|:---------------------------------------------|
| joe       |          13 |                    0 | x104              | Joe     | 215K       | 3YWbeb3gozGGQFNSv384BeZqTexPMmNns5vvjb7Kpump |
| xmr       |          11 |                    1 | x88               | p/xmr   | 110K       | Ha6sAPb47FivNhMa5PEsPxL7pTEUtdLLeccNZugXuE4P |
| froink    |          11 |                   19 | x5                | FROINK  | 71K        | SfM8BPoJ7w8Hxt6yQ9wfMJg9c85E1NsUMtPAV5yYMMU  |
| stuve     |           6 |                    0 | x48               | stuve   | 82K        | 2UqTTzgS3ChM3ysww33dbYSPCpDR2Arsc9fpPEnR7MZ3 |
| stoxes    |           3 |                    1 | x24               | STOXES  | 615K       | AfVUPhruMtJuFVtPj4u8kvpNbNEuy7VQ3ME5eAHq9999 |
| persona   |           3 |                    0 | x24               | PERSONA | 194K       | 7mP77b3RoMo69FJAh8xARRynAttK4DKzBKst2tqy2tiZ |
| brain     |           3 |                    0 | x24               | BRAIN   | 76K        | B7HbqBEFJaxWYKUPoMvcTQraxZf9prpr1qJQFr47NVUi |
| memes     |           3 |                    1 | x24               | Memes   | 21K        | 7dACCWZXF4Lr9ftxFpi7TJk7a3hcPpUwGPAcTuXDpump |
| frocat    |           3 |                    1 | x24               | FROCAT  | 134K       | FCoXFnRQsHtb2rPReJUrtkPD8qBm8UVbXNdHx49spump |
| ufo       |           3 |                    0 | x24               | UFO     | 45K        | 72zhBuPwcQjqtetbkeoCa7hTDCARkhBn52wNisaLzEa1 |

## Narrativas activas (últimas 2 h)

| narrativa    |   tokens_nuevos | lider   | mc_lider   | catalizador   | mint_lider                                   |
|:-------------|----------------:|:--------|:-----------|:--------------|:---------------------------------------------|
| ia           |               6 | ChatGPT | 489K       |               | E4uMkXeYPKE5kqEcbh4b87dMHcDpmqjMDqstV8dqpump |
| cripto       |               4 | Memes   | 11K        |               | 8HpwLmm6e8XVj3svDyL9qX3cJZKRtmYwRm4LKo8ppqMw |
| elon         |               2 | ELON    | 59K        |               | G3Q54rUP9TG1dF6kXBR6C5Cx42DEMParySxCUzEfxK9p |
| celebridades |               1 | MrBeast | 493K       |               | EprCL3UMk9wABAM2A6ZNfhwfpmpJS8BweVDxPPPfpump |
| politica     |               1 | D/TRUMP | 30K        |               | BTgenoGircCT23iFM7EzKf9jaf2LFnfh9K6sfpz6pump |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

Ninguno.
