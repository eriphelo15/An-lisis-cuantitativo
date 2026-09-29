# Informe del radar de memecoins

Generado: 2026-09-29 01:41 UTC

- Tokens registrados: **2068** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **488**
- Pasan el filtro v1: **47**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## ¿Funciona el filtro?

### Todos los tokens

| todos   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| todos   | 488 | 74%           | 39%          | -100%         |           -22.38 |      0 | -        | -        | -                    |         |

### Filtro v1

| filtro_v1   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no pasa     | 473 | 74%           | 39%          | -100%         |           -22.43 |      0 | -        | -        | -                    |                 |
| pasa        |  15 | 87%           | 53%          | -100%         |           -20.86 |      0 | -        | -        | -                    | muestra pequeña |

### Alertas tempranas del vigía (2-15 min de vida) frente al escaneo

| origen   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| escaneo  | 477 | 75%           | 40%          | -100%         |           -21.99 |      0 | -        | -        | -                    |                 |
| vigia    |  11 | 55%           | 20%          | -100%         |           -38.51 |      0 | -        | -        | -                    | muestra pequeña |

### Alertas con tema, sin tema y vetadas

|                                            | 0               |
|:-------------------------------------------|:----------------|
| ('antes de separar', 'n')                  | 11              |
| ('antes de separar', 'muertos_24h')        | 55%             |
| ('antes de separar', 'tocaron_2x')         | 20%             |
| ('antes de separar', 'mediana_24h')        | -100%           |
| ('antes de separar', 'regla_$_por_50')     | -38.51          |
| ('antes de separar', 'n_7d')               | 0               |
| ('antes de separar', '10x_7d')             | -               |
| ('antes de separar', '50x_7d')             | -               |
| ('antes de separar', 'tendencia_$_por_50') | -               |
| ('antes de separar', 'aviso')              | muestra pequeña |
| ('con tema relevante (avisadas)', 'n')     | 0               |
| ('sin tema (silenciosas)', 'n')            | 0               |
| ('vetadas (no avisadas)', 'n')             | 0               |

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

| motivo                 |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| compras_desbalanceadas |  98 | 93%           | 42%          | -100%         |           -17.09 |      0 | -        | -        | -                    |         |
| holders_concentrados   | 194 | 70%           | 47%          | -100%         |           -16.61 |      0 | -        | -        | -                    |         |
| liquidez_anomala       | 176 | 83%           | 35%          | -100%         |           -26.86 |      0 | -        | -        | -                    |         |
| mc_fuera_rango         | 267 | 64%           | 33%          | -100%         |           -25.25 |      0 | -        | -        | -                    |         |
| nombre_clonado         | 306 | 79%           | 41%          | -100%         |           -23.27 |      0 | -        | -        | -                    |         |
| peligro_rugcheck       | 236 | 87%           | 37%          | -100%         |           -26.59 |      0 | -        | -        | -                    |         |
| pocos_compradores      |  67 | 64%           | 20%          | -100%         |           -29.15 |      0 | -        | -        | -                    |         |
| presion_venta          |  82 | 67%           | 39%          | -100%         |           -26.19 |      0 | -        | -        | -                    |         |
| volumen_inflado        | 123 | 72%           | 38%          | -100%         |           -21.25 |      0 | -        | -        | -                    |         |

## Narrativas

### Por narrativa

|                                         | 0               |
|:----------------------------------------|:----------------|
| ('animales', 'n')                       | 6               |
| ('animales', 'muertos_24h')             | 83%             |
| ('animales', 'tocaron_2x')              | 25%             |
| ('animales', 'mediana_24h')             | -100%           |
| ('animales', 'regla_$_por_50')          | -42.16          |
| ('animales', 'n_7d')                    | 0               |
| ('animales', '10x_7d')                  | -               |
| ('animales', '50x_7d')                  | -               |
| ('animales', 'tendencia_$_por_50')      | -               |
| ('animales', 'aviso')                   | muestra pequeña |
| ('celebridades', 'n')                   | 6               |
| ('celebridades', 'muertos_24h')         | 100%            |
| ('celebridades', 'tocaron_2x')          | 50%             |
| ('celebridades', 'mediana_24h')         | -100%           |
| ('celebridades', 'regla_$_por_50')      | +12.84          |
| ('celebridades', 'n_7d')                | 0               |
| ('celebridades', '10x_7d')              | -               |
| ('celebridades', '50x_7d')              | -               |
| ('celebridades', 'tendencia_$_por_50')  | -               |
| ('celebridades', 'aviso')               | muestra pequeña |
| ('cripto', 'n')                         | 14              |
| ('cripto', 'muertos_24h')               | 71%             |
| ('cripto', 'tocaron_2x')                | 50%             |
| ('cripto', 'mediana_24h')               | -100%           |
| ('cripto', 'regla_$_por_50')            | -13.51          |
| ('cripto', 'n_7d')                      | 0               |
| ('cripto', '10x_7d')                    | -               |
| ('cripto', '50x_7d')                    | -               |
| ('cripto', 'tendencia_$_por_50')        | -               |
| ('cripto', 'aviso')                     | muestra pequeña |
| ('elon', 'n')                           | 3               |
| ('elon', 'muertos_24h')                 | 100%            |
| ('elon', 'tocaron_2x')                  | 67%             |
| ('elon', 'mediana_24h')                 | -100%           |
| ('elon', 'regla_$_por_50')              | -26.37          |
| ('elon', 'n_7d')                        | 0               |
| ('elon', '10x_7d')                      | -               |
| ('elon', '50x_7d')                      | -               |
| ('elon', 'tendencia_$_por_50')          | -               |
| ('elon', 'aviso')                       | muestra pequeña |
| ('festividades', 'n')                   | 0               |
| ('ia', 'n')                             | 28              |
| ('ia', 'muertos_24h')                   | 71%             |
| ('ia', 'tocaron_2x')                    | 41%             |
| ('ia', 'mediana_24h')                   | -100%           |
| ('ia', 'regla_$_por_50')                | -24.87          |
| ('ia', 'n_7d')                          | 0               |
| ('ia', '10x_7d')                        | -               |
| ('ia', '50x_7d')                        | -               |
| ('ia', 'tendencia_$_por_50')            | -               |
| ('ia', 'aviso')                         | muestra pequeña |
| ('noticias_cripto', 'n')                | 0               |
| ('politica', 'n')                       | 12              |
| ('politica', 'muertos_24h')             | 75%             |
| ('politica', 'tocaron_2x')              | 70%             |
| ('politica', 'mediana_24h')             | -100%           |
| ('politica', 'regla_$_por_50')          | +1.28           |
| ('politica', 'n_7d')                    | 0               |
| ('politica', '10x_7d')                  | -               |
| ('politica', '50x_7d')                  | -               |
| ('politica', 'tendencia_$_por_50')      | -               |
| ('politica', 'aviso')                   | muestra pequeña |
| ('sin narrativa', 'n')                  | 411             |
| ('sin narrativa', 'muertos_24h')        | 74%             |
| ('sin narrativa', 'tocaron_2x')         | 38%             |
| ('sin narrativa', 'mediana_24h')        | -100%           |
| ('sin narrativa', 'regla_$_por_50')     | -23.56          |
| ('sin narrativa', 'n_7d')               | 0               |
| ('sin narrativa', '10x_7d')             | -               |
| ('sin narrativa', '50x_7d')             | -               |
| ('sin narrativa', 'tendencia_$_por_50') | -               |
| ('sin narrativa', 'aviso')              |                 |
| ('videojuegos', 'n')                    | 8               |
| ('videojuegos', 'muertos_24h')          | 88%             |
| ('videojuegos', 'tocaron_2x')           | 57%             |
| ('videojuegos', 'mediana_24h')          | -100%           |
| ('videojuegos', 'regla_$_por_50')       | -13.54          |
| ('videojuegos', 'n_7d')                 | 0               |
| ('videojuegos', '10x_7d')               | -               |
| ('videojuegos', '50x_7d')               | -               |
| ('videojuegos', 'tendencia_$_por_50')   | -               |
| ('videojuegos', 'aviso')                | muestra pequeña |

### Líder de su narrativa frente a seguidores y clones

| papel_en_narrativa   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| líder                |  22 | 100%          | 55%          | -100%         |           -10.31 |      0 | -        | -        | -                    | muestra pequeña |
| seguidor/clon        |  55 | 69%           | 47%          | -100%         |           -18.55 |      0 | -        | -        | -                    |                 |
| sin narrativa        | 411 | 74%           | 38%          | -100%         |           -23.56 |      0 | -        | -        | -                    |                 |

### Calor de la narrativa (tokens con el mismo tema en el escaneo)

| calor   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 1 token |   9 | 100%          | 56%          | -100%         |           -18.55 |      0 | -        | -        | -                    | muestra pequeña |
| 2-3     |  16 | 100%          | 75%          | -100%         |            13.35 |      0 | -        | -        | -                    | muestra pequeña |
| 4-8     |  32 | 66%           | 37%          | -100%         |           -29.39 |      0 | -        | -        | -                    |                 |
| 9+      |  20 | 70%           | 42%          | -100%         |           -18.74 |      0 | -        | -        | -                    | muestra pequeña |

### Con catalizador próximo

| con_catalizador   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no                | 468 | 74%           | 38%          | -100%         |           -23.11 |      0 | -        | -        | -                    |                 |
| sí                |  20 | 80%           | 65%          | -100%         |            -4.96 |      0 | -        | -        | -                    | muestra pequeña |

### Tokens del escaneo que comparten palabra con él

| calor_palabra_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| única            | 191 | 72%           | 42%          | -100%         |           -19.26 |      0 | -        | -        | -                    |         |
| 2 tokens         |  56 | 66%           | 37%          | -100%         |           -20.76 |      0 | -        | -        | -                    |         |
| 3-4              |  74 | 77%           | 38%          | -100%         |           -23.97 |      0 | -        | -        | -                    |         |
| 5+               | 121 | 79%           | 36%          | -100%         |           -26.87 |      0 | -        | -        | -                    |         |

## Carteras inteligentes

Cartera con buen historial: 3 tokens o más comprados antes de detectarlos y al menos el 50% llegaron a 2x. Solo cuenta el historial que se conocía en el momento de cada detección.

### Carteras con buen historial entre los compradores

|                                     | 0      |
|:------------------------------------|:-------|
| ('0', 'n')                          | 291    |
| ('0', 'muertos_24h')                | 73%    |
| ('0', 'tocaron_2x')                 | 46%    |
| ('0', 'mediana_24h')                | -100%  |
| ('0', 'regla_$_por_50')             | -18.18 |
| ('0', 'n_7d')                       | 0      |
| ('0', '10x_7d')                     | -      |
| ('0', '50x_7d')                     | -      |
| ('0', 'tendencia_$_por_50')         | -      |
| ('0', 'aviso')                      |        |
| ('1', 'n')                          | 0      |
| ('2+', 'n')                         | 0      |
| ('sin datos', 'n')                  | 197    |
| ('sin datos', 'muertos_24h')        | 77%    |
| ('sin datos', 'tocaron_2x')         | 31%    |
| ('sin datos', 'mediana_24h')        | -100%  |
| ('sin datos', 'regla_$_por_50')     | -28.53 |
| ('sin datos', 'n_7d')               | 0      |
| ('sin datos', '10x_7d')             | -      |
| ('sin datos', '50x_7d')             | -      |
| ('sin datos', 'tendencia_$_por_50') | -      |
| ('sin datos', 'aviso')              |        |

### Mejores carteras

| cartera                                      |   tokens | tocaron_2x   | muertos   | llegaron_10x_7d   |
|:---------------------------------------------|---------:|:-------------|:----------|:------------------|
| 3v6zEUW1FGaz9g3xResPBes4X2gaRzEveMmrooGGvf5p |        4 | 100%         | 75%       | 0%                |
| 5KeUcivVXR5MEgLDFQp5Pxfenxv32UDSXKnhFYdGtJWJ |        4 | 100%         | 75%       | 0%                |
| 78wNNt8ReH3qh6dumg1iuUBMaKwJJQQLkAT845tKCCM6 |        4 | 100%         | 75%       | 0%                |
| 7XYBUpVjP9m6MxGDyZjrwTPn8rMQzFKVnQh8Q4pF3iJu |        4 | 100%         | 75%       | 0%                |
| 83QUyCk5XiotBd2MKe7pprzwwW8vg6RNXwDHomGv3jpV |        4 | 100%         | 100%      | 0%                |
| 8pgtJMGLJkGSo2qngKUnDtjEGVVmfJM1onRieJYdbPwb |        4 | 100%         | 75%       | 0%                |
| 9KBFYgtJ7Pomou2G7qwqVk5ATqf6fFT5ADhq8HfrKLDE |        4 | 100%         | 75%       | 0%                |
| CQobSAZab6bok6VU6iwKAhwgXZUEF8oLy8gv6DSW9SU  |        4 | 100%         | 75%       | 0%                |
| CqrwxeCMchk4DWkT4JMw6BYq42f6QNVeGUSpn8fW3rRR |        4 | 100%         | 75%       | 0%                |
| EZ9PDDvSi6JhwBumh3Ufx2A3qAvrhPRx5cVzNANWKWe2 |        4 | 100%         | 75%       | 0%                |
| GFrTtWdMTjWfynEVNmU2vkqSAQBG2RRs8EpZMJbn4wMf |        4 | 100%         | 75%       | 0%                |
| HJF1KEDP6qrRmETVrXLXzojpQ9hBi9MfL9hoVrfiH8hr |        4 | 100%         | 75%       | 0%                |
| Hh4afzozYWN9ud4CGN4fr4iZ6t2xqEfwRY1VXtaoY7A6 |        4 | 100%         | 75%       | 0%                |
| 28zQhQW2RPvSNvEqEQWrxJHH8FGawuKVzwxzk6dxKeSD |        3 | 100%         | 100%      | 0%                |
| 2VJ72AwxbPaPtnASaKuR2XnwTf9C4SfCs5EsrA1z4Mt2 |        3 | 100%         | 100%      | 0%                |

## Holders

### % del suministro en los 10 mayores holders

| top10_holders   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15%            |   2 | 100%          | 50%          | -100%         |           -49.85 |      0 | -        | -        | -                    | muestra pequeña |
| 15-25%          |  19 | 89%           | 32%          | -100%         |           -19.37 |      0 | -        | -        | -                    | muestra pequeña |
| 25-35%          |  17 | 47%           | 47%          | -87%          |            -6.16 |      0 | -        | -        | -                    | muestra pequeña |
| 35-50%          |  27 | 56%           | 54%          | -100%         |           -14.52 |      0 | -        | -        | -                    | muestra pequeña |
| >50%            | 166 | 72%           | 46%          | -100%         |           -16.75 |      0 | -        | -        | -                    |                 |

### Número de holders

| num_holders   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <100          |  36 | 56%           | 48%          | -100%         |            -4.89 |      0 | -        | -        | -                    |                 |
| 100-300       |  73 | 60%           | 43%          | -100%         |           -17.63 |      0 | -        | -        | -                    |                 |
| 300-1K        |  63 | 78%           | 52%          | -100%         |           -21.53 |      0 | -        | -        | -                    |                 |
| 1K-3K         |  49 | 86%           | 41%          | -100%         |           -20.74 |      0 | -        | -        | -                    |                 |
| 3K+           |  11 | 73%           | 36%          | -100%         |             5.83 |      0 | -        | -        | -                    | muestra pequeña |

### GT Score

| gt_score_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <30         | 161 | 73%           | 26%          | -100%         |           -30.84 |      0 | -        | -        | -                    |                 |
| 30-45       | 165 | 73%           | 52%          | -100%         |           -14.4  |      0 | -        | -        | -                    |                 |
| 45-60       |  41 | 78%           | 46%          | -100%         |            -9.1  |      0 | -        | -        | -                    |                 |
| 60+         |   1 | 0%            | 0%           | -79%          |           -32.17 |      0 | -        | -        | -                    | muestra pequeña |

## Señales por separado

### Edad al detectarlo

| edad      |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15 min   | 424 | 75%           | 39%          | -100%         |           -24.97 |      0 | -        | -        | -                    |                 |
| 15-30 min |  13 | 62%           | 55%          | -100%         |             2.23 |      0 | -        | -        | -                    | muestra pequeña |
| 30-60 min |  18 | 83%           | 47%          | -100%         |           -15.54 |      0 | -        | -        | -                    | muestra pequeña |
| 1-3 h     |  11 | 82%           | 27%          | -100%         |           -18.49 |      0 | -        | -        | -                    | muestra pequeña |
| 3-24 h    |  16 | 44%           | 50%          | -83%          |            16.18 |      0 | -        | -        | -                    | muestra pequeña |

### Capitalización al detectarlo

| cap       |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <50K      | 257 | 63%           | 33%          | -100%         |           -25.63 |      0 | -        | -        | -                    |                 |
| 50-150K   | 120 | 88%           | 43%          | -100%         |           -28.74 |      0 | -        | -        | -                    |                 |
| 150-500K  |  77 | 82%           | 49%          | -100%         |            -4.94 |      0 | -        | -        | -                    |                 |
| 500K-1.5M |  24 | 100%          | 58%          | -100%         |           -17.1  |      0 | -        | -        | -                    | muestra pequeña |
| >1.5M     |  10 | 80%           | 30%          | -100%         |           -15.85 |      0 | -        | -        | -                    | muestra pequeña |

### Compradores / vendedores (1 h)

| compradores_vs_vendedores   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:----------------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| <1.2                        |  82 | 67%           | 39%          | -100%         |           -26.19 |      0 | -        | -        | -                    |         |
| 1.2-3                       | 160 | 53%           | 39%          | -100%         |           -21.28 |      0 | -        | -        | -                    |         |
| 3-8                         | 148 | 89%           | 39%          | -100%         |           -25.05 |      0 | -        | -        | -                    |         |
| >8                          |  98 | 93%           | 42%          | -100%         |           -17.09 |      0 | -        | -        | -                    |         |

### Volumen de 1 h / capitalización

| volumen_vs_cap   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| <0.5             | 203 | 87%           | 32%          | -100%         |           -32.62 |      0 | -        | -        | -                    |         |
| 0.5-1            |  52 | 69%           | 42%          | -100%         |            -9.03 |      0 | -        | -        | -                    |         |
| 1-3              | 110 | 55%           | 53%          | -100%         |           -11.31 |      0 | -        | -        | -                    |         |
| >3               | 123 | 72%           | 38%          | -100%         |           -21.25 |      0 | -        | -        | -                    |         |

### Peligros de RugCheck

| peligros_rugcheck   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:--------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| 0                   | 162 | 53%           | 43%          | -100%         |           -14.38 |      0 | -        | -        | -                    |         |
| 1                   | 189 | 90%           | 37%          | -100%         |           -25.21 |      0 | -        | -        | -                    |         |
| 2+                  |  47 | 74%           | 32%          | -100%         |           -33.31 |      0 | -        | -        | -                    |         |
| sin datos           |  90 | 79%           | 38%          | -100%         |           -26.3  |      0 | -        | -        | -                    |         |

### Liquidez bloqueada (RugCheck): con 0% el creador puede retirarla

| liquidez_bloqueada   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| 0%                   | 134 | 78%           | 30%          | -100%         |           -30.87 |      0 | -        | -        | -                    |         |
| parcial              | 109 | 82%           | 47%          | -100%         |           -15.62 |      0 | -        | -        | -                    |         |
| 100%                 | 155 | 63%           | 41%          | -100%         |           -17.97 |      0 | -        | -        | -                    |         |
| sin datos            |  90 | 79%           | 38%          | -100%         |           -26.3  |      0 | -        | -        | -                    |         |

### Puntuación (quintiles)

| puntuacion_q   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:---------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| Q1 (baja)      | 125 | 79%           | 28%          | -100%         |           -32.72 |      0 | -        | -        | -                    |         |
| Q2             | 108 | 74%           | 40%          | -100%         |           -26.02 |      0 | -        | -        | -                    |         |
| Q3             |  80 | 66%           | 35%          | -100%         |           -19.02 |      0 | -        | -        | -                    |         |
| Q4             |  67 | 69%           | 39%          | -100%         |           -22.35 |      0 | -        | -        | -                    |         |
| Q5 (alta)      | 108 | 79%           | 52%          | -100%         |           -10.65 |      0 | -        | -        | -                    |         |

### DEX

|                                           | 0               |
|:------------------------------------------|:----------------|
| ('bags-fm', 'n')                          | 0               |
| ('letsbonk-fun', 'n')                     | 0               |
| ('meteora', 'n')                          | 0               |
| ('meteora-damm-v2', 'n')                  | 74              |
| ('meteora-damm-v2', 'muertos_24h')        | 89%             |
| ('meteora-damm-v2', 'tocaron_2x')         | 29%             |
| ('meteora-damm-v2', 'mediana_24h')        | -100%           |
| ('meteora-damm-v2', 'regla_$_por_50')     | -34.73          |
| ('meteora-damm-v2', 'n_7d')               | 0               |
| ('meteora-damm-v2', '10x_7d')             | -               |
| ('meteora-damm-v2', '50x_7d')             | -               |
| ('meteora-damm-v2', 'tendencia_$_por_50') | -               |
| ('meteora-damm-v2', 'aviso')              |                 |
| ('meteora-dbc', 'n')                      | 25              |
| ('meteora-dbc', 'muertos_24h')            | 64%             |
| ('meteora-dbc', 'tocaron_2x')             | 21%             |
| ('meteora-dbc', 'mediana_24h')            | -100%           |
| ('meteora-dbc', 'regla_$_por_50')         | -28.74          |
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
| ('pump-fun', 'n')                         | 65              |
| ('pump-fun', 'muertos_24h')               | 23%             |
| ('pump-fun', 'tocaron_2x')                | 37%             |
| ('pump-fun', 'mediana_24h')               | -82%            |
| ('pump-fun', 'regla_$_por_50')            | -18.97          |
| ('pump-fun', 'n_7d')                      | 0               |
| ('pump-fun', '10x_7d')                    | -               |
| ('pump-fun', '50x_7d')                    | -               |
| ('pump-fun', 'tendencia_$_por_50')        | -               |
| ('pump-fun', 'aviso')                     |                 |
| ('pumpswap', 'n')                         | 318             |
| ('pumpswap', 'muertos_24h')               | 84%             |
| ('pumpswap', 'tocaron_2x')                | 42%             |
| ('pumpswap', 'mediana_24h')               | -100%           |
| ('pumpswap', 'regla_$_por_50')            | -20.94          |
| ('pumpswap', 'n_7d')                      | 0               |
| ('pumpswap', '10x_7d')                    | -               |
| ('pumpswap', '50x_7d')                    | -               |
| ('pumpswap', 'tendencia_$_por_50')        | -               |
| ('pumpswap', 'aviso')                     |                 |
| ('raydium', 'n')                          | 3               |
| ('raydium', 'muertos_24h')                | 0%              |
| ('raydium', 'tocaron_2x')                 | 67%             |
| ('raydium', 'mediana_24h')                | -69%            |
| ('raydium', 'regla_$_por_50')             | +24.87          |
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
| ('stonkfun', 'n')                         | 1               |
| ('stonkfun', 'muertos_24h')               | 0%              |
| ('stonkfun', 'tocaron_2x')                | 100%            |
| ('stonkfun', 'mediana_24h')               | -85%            |
| ('stonkfun', 'regla_$_por_50')            | +7.26           |
| ('stonkfun', 'n_7d')                      | 0               |
| ('stonkfun', '10x_7d')                    | -               |
| ('stonkfun', '50x_7d')                    | -               |
| ('stonkfun', 'tendencia_$_por_50')        | -               |
| ('stonkfun', 'aviso')                     | muestra pequeña |

## Supervivencia por horizonte

- 30m: 56% vivos (n=1990)
- 1h: 49% vivos (n=2010)
- 6h: 34% vivos (n=1863)
- 24h: 26% vivos (n=488)

## Supervivientes (tokens de 3 a 120 días que despiertan)

Aún no hay supervivientes (se buscan una vez por hora).

## Últimas alertas del vigía (6 h)

| ts    | simbolo     | narrativa   | prioridad   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:------------|:------------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 01:36 | bwg         |             | vetada      |        2.3 | 21K  |              480 |             365 | AifdDLDaUbVSeewQaGqLYh94fZpzRg4nmSBT2WGUjSK6 | nan    |
| 01:32 | zCATS       |             | vetada      |        5   | 18K  |              224 |             150 | EV5vDywehbcqyuwVRCF1ewV3W2Am7e1X51pWVWFrpump | nan    |
| 01:29 | Nacho       |             | vetada      |        6.2 | 11K  |              112 |              64 | 5tFFZveFzVnc4hcuNvXGgjCy6uSSumu86cnz9BLapump | nan    |
| 01:26 | PARASITE    |             | vetada      |        9.1 | 71K  |              261 |             165 | 3kmygWKZBkCYrgZHKfiuB9UFKTcDLTFFsKo3BWpmpump | nan    |
| 01:22 | GPEPE       | animales    | vetada      |        3.9 | 10K  |               55 |              22 | 6wKf8fGVjAuvUMLqXc9Poop15kG5R3XBNJS3nq6Apump | nan    |
| 01:22 | 笑笑牛         |             | vetada      |        3.4 | 90K  |               60 |              33 | E2h2zFtNzzKtJznxNCu1F26xCBpMVCkDRxHgaiE72H5e | nan    |
| 01:16 | Adventures  |             | vetada      |        3.6 | 15K  |              256 |              67 | 8xbSqRfjKPxFwkVG5egnDxq4hVwZnFDY1D2hbnF8H4o1 | nan    |
| 01:12 | KAIRO       |             | vetada      |        4.9 | 18K  |              362 |              58 | FNvEtxM7fu6K4JGZwbiHTPLY7PpYjjHQwQTqHrKhz3Ad | nan    |
| 01:08 | CHRLSCRL    |             | vetada      |        3.3 | 90K  |              156 |              35 | AM1y6BqRP6vkt54Tn9Q6FrcugjJ8xXFGEMBRQiKoBAGS | nan    |
| 01:06 | JEET        |             | vetada      |        4.1 | 19K  |              183 |             126 | 94mo6yYt5z9t31TjS257coYsRX7b7KPTKWVRzAnuLECr | nan    |
| 01:01 | SBC         |             | vetada      |        4.7 | 25K  |              153 |             109 | ArV7g2VBDHTUvfJTwCPYzzPJRozHbdS94QigVPuFpump | nan    |
| 01:00 | Pillys      |             | baja        |        8.8 | 14K  |               51 |              38 | E2U8r19SNWMGjhNc93NSgv26zE7DkVfXdgUEacESpump | nan    |
| 00:57 | MINESOFT    |             | vetada      |        3.9 | 18K  |               45 |              33 | 96Mxn6NiP1GjXAxwuAvv7qgsBciqdQUmAuSJ6zXtpump | nan    |
| 00:55 | CAVO        |             | vetada      |        3.7 | 29K  |              245 |             146 | imKHMmk6bC7MK15NUKJx6RX8aFyAVZ5dVkBgDTCpump  | nan    |
| 00:52 | illusion    |             | vetada      |        3.3 | 56K  |              254 |             156 | Bxz3haSgqQPx6JGqay1K8cfpAjDqmqLzhjkWKE5fpump | nan    |
| 00:52 | STARCRWN    |             | vetada      |        2.8 | 74K  |               55 |              18 | CtpBPGJUWsoeQPdaXjkUj3WyXzaXPrkwH6o4ojoupump | nan    |
| 00:50 | stillwet    |             | vetada      |        3.9 | 40K  |              344 |              46 | 85f5LpJhRdPnqYCQxMQRsDkqBX61ji2VG3Fucyy4bQyr | nan    |
| 00:43 | shiboo      | animales    | vetada      |        3.4 | 10K  |              249 |             178 | ibcCTSui26aRuqVwWsibkDSVVitaVtFdTcHjhDapump  | nan    |
| 00:43 | COCKHERO    |             | vetada      |        3.2 | 61K  |              526 |              79 | A6KqvSgDXjG5PW3KiKJH9CT5xHPSVQEoxVzQppfVbHaS | nan    |
| 00:38 | BUNTRUMP    | politica    | vetada      |        3.2 | 212K |              106 |              29 | EqWgdTpMWHGm8ivNn3Cc7HA2fKKfQXnq77vumrq4KX4X | nan    |
| 00:32 | Kretina     |             | vetada      |        3.8 | 85K  |               93 |              21 | 7pLvXn5waVE55voQfq6tVW7HiiRkK9NMfQhxGCubpump |   0    |
| 00:26 | cocainu     |             | vetada      |        2.2 | 22K  |              319 |             137 | G7qVGuAs11R76BiLnba76pvWGQXdmVcjcWgUp3GFpump |   0.23 |
| 00:26 | Murphy      |             | vetada      |        7.3 | 267K |               75 |              54 | 5v3BV2UAbrmRgpRqJG2UaZcCJTo6MHdmoQYAFULuYeHz |   2.42 |
| 00:13 | Tommie      |             | baja        |        3.3 | 15K  |              149 |              84 | 3WPCvB8RshheEUEYLHiF3GusrseiaBfMDsVmTVR3pump |   2.25 |
| 00:13 | HOTNUTS     |             | vetada      |        3.1 | 20K  |              519 |             103 | wSeTcspXGWciAhw7trRJAeSYB7nEoAuPeKXgRYRZ7WQ  |   1.15 |
| 23:55 | CANDACE     |             | vetada      |       12.5 | 93K  |               72 |              49 | GrXMbn56JtFngA2FgoXenJG5HeD1GhvFnjyFPWbfpump |   0.19 |
| 23:55 | Unbox       |             | vetada      |        5.5 | 11K  |               78 |              44 | N1kCpRuU94iRGRNqe5ZiUqHa9w9kaMWgZ56kpXUpump  |   1.8  |
| 23:52 | BAGSPAY     |             | vetada      |        2.6 | 53K  |              511 |              64 | AMaR7sGJoLXWTWxTh8wcT6FT1pgC3YvPbnU7BXKBdthZ |   0    |
| 23:47 | ANTH        |             | vetada      |        2.9 | 16K  |               90 |              64 | 8HQDosKAfeJE5wjV5sWm9fv1KgaVTFNZdYsP5mJqASTb |   0.32 |
| 23:43 | RuneChain   |             | baja        |       11.1 | 12K  |               64 |              40 | 7SpVU1kJEDtrQexRWgZy64ZXnHjhHyimRjB2zmHZpump |   0.55 |
| 23:41 | trickle     |             | vetada      |        3.6 | 53K  |              263 |             153 | 7SDWbs81JV89HeC4jNbZ15yczLCTZa2RvHg5z4Lrpump |   0    |
| 23:38 | HALLOWINU   |             | baja        |        4.1 | 16K  |              195 |             110 | WApCdQftZcRUNHN9S2XvmrqeRtRASE3EZxnwuNJpump  |   3.49 |
| 23:30 | LAYER       |             | vetada      |       13.9 | 9K   |               50 |              31 | ACPsyMv2mwGCbk6ygBTzmyXFrPtcwuqiZvQgSL37pump |   0.39 |
| 23:30 | KILLMASK    |             | vetada      |        3   | 17K  |              129 |              63 | Ewsw5WxVXDF5zVhUUo8KVkGee5c4kyHhpqQKoGE5pump |   0    |
| 23:26 | wif/acc     | animales    | vetada      |        3   | 24K  |              471 |             287 | 6PdE9hMCZFRwsdC4qUrQtfQN1XGwGLGPmFky1ZNQpump |   0.17 |
| 23:24 | PUMPBLOX    | cripto      | vetada      |        2.9 | 15K  |              300 |             189 | 6wACL4rfquHHw7XNPDYwrKWELQRXZjfANTafqecPpump |   0.55 |
| 23:22 | ACHACL      |             | vetada      |        6.2 | 85K  |               81 |              23 | BH3i5c4wtzmnx5GAxK7SZDqnw3ycYMNmhezvLcknmoon |   0    |
| 23:15 | FOMOWEEN    |             | baja        |        2.8 | 11K  |              223 |             145 | DoipyvkFiAYXGHwKcKC5ahfWJTuaDenGwAW7TgTzpump |   0.3  |
| 23:13 | SHL0MS      |             | vetada      |        6.9 | 11K  |               47 |              19 | BhaQEvju9852hiJiFs9Y2ecGRb37oUfE9dAA8pLSBAGS |   0.42 |
| 23:11 | Caterpillar |             | vetada      |       13.8 | 34K  |               95 |              64 | CpbSCWm8SzJas65wiKT51mJaePiKZnAUTg9p6DLqr7oT |   0.1  |
| 23:10 | PUMPGO      | cripto      | vetada      |       10   | 151K |              173 |              24 | Fdzxru91oKvcmTz7rK67B5S2HoEGWd4UErdThEx7pump |   0    |
| 23:06 | Krater      |             | baja        |        6.4 | 9K   |               52 |              31 | m5q3JpMtohBRhW2mGnzCj287NkMNCJHZjMepSkHXtos  |   1.23 |
| 22:51 | Ouroboros   |             | baja        |        5.2 | 9K   |               81 |              55 | 8BTPgeMzB1RJvjboWGDEgyssEJZ9GiHfWT13tGk5mWL3 |   0.27 |
| 22:51 | Swordgirl   |             | vetada      |        5   | 10K  |              132 |              58 | EgbNLcoQX56RDXZiKpbR5QouRU7eE9n64n24AjC3pump |   0.36 |
| 22:51 | OUROBOROS   |             | vetada      |        5.6 | 16K  |              138 |              96 | 8WWryGjcJ2Dv4rJGm9MNzvJw5WNp9vZeVgnY6RcW5uKe |   0.19 |
| 22:51 | Kitty       |             | vetada      |        4.7 | 27K  |              234 |              40 | C6BtpFKSxCRsDxPeY9aEVZaxXephu5gqZj9mfePAynAa |   0    |
| 22:35 | MEDCUP      |             | vetada      |        3.8 | 73K  |              205 |              52 | BX1TZRDW9HKqYtLpMiModBdcDeNazYgseVcFyK3obonk |   0    |
| 22:33 | PUMPTOBER   | cripto      | vetada      |        3   | 46K  |               61 |              25 | D37sbd3C3dqgnQ4TGWtxksMp6gRjmP1C7K3ib9wLpump |   0    |
| 22:33 | PUPI        |             | vetada      |       15   | 29K  |               46 |              32 | DXrrBJMjK3xAV7YvuWAg42aeJHck3GmJmcN78HfDpump |   4.41 |
| 22:31 | epsteinu    |             | vetada      |        3   | 17K  |              148 |              73 | AZ8jS8apTnvge18otci45VrJJQKbL3v8DWJNEJEwpump |   0.21 |
| 22:31 | LMT         | politica    | alta        |        3.3 | 17K  |               84 |              62 | HcjPrHdESBJioSMj3HZbHbH7nUsUdcPyjQrPwYZGpump |   0    |
| 22:31 | Carla       |             | vetada      |        3.4 | 14K  |               80 |              54 | 3PjwCqfGMR8CXZbcPEbGTSPQGduizdoVz4N1RQmJd8Uv |   4.13 |
| 22:29 | Merrylegs   |             | vetada      |        4   | 45K  |              694 |             363 | 9t4nAuTyS6QLStW1vTxMLf7899b9UF1tmmhRCLbApump |   0.21 |
| 22:27 | KP          |             | vetada      |        2.8 | 83K  |              387 |             108 | CmWxjebLZa3VohM2QhPcN2VVhwkLqnytksqDiaJwKZ3E |   0    |
| 22:27 | BOCK        |             | vetada      |        3.7 | 15K  |               57 |              26 | 95iVDfEQkHtS734cuseXLJ8oXtrP1LV1gA7uyRB7bonk |   0.23 |
| 22:22 | なごやし        |             | vetada      |        3.4 | 29K  |              291 |              73 | HSPehHbS5idzDTfgxz6ZvidREsMFm8dh1YTUmXkUT7xC |   0    |
| 22:22 | IRA         |             | vetada      |        4.8 | 19K  |              105 |              53 | F9XfvHQ4MWiX6FVQKHwBM6q7gaxCqEv5WEhjTC2rpump |   0.2  |
| 22:22 | loria       |             | vetada      |        3.5 | 23K  |               51 |              31 | FK2LDCsv29toyvzBWLsHoo12BY74ErrCpMWwAmbBxMJY |   0.12 |
| 22:18 | FOGLARE     |             | vetada      |        2.2 | 83K  |              425 |             128 | 3RWZTDUyhdksQdtCB4wpZH9Qj2rStinhABJUpheopump |   0    |
| 22:18 | NIG         |             | vetada      |        2.6 | 9K   |               92 |              41 | 5xMtGqn7wqtePKzqJqEDaFd9JH7TAtdr9aPM125qpump |   0.37 |
| 22:14 | PIMP        |             | vetada      |        3.8 | 44K  |               68 |              40 | DX9mc4dYccjkQ8wkHpLtL1ybvELU2peKGNEqsDzqpump |   0.13 |
| 22:10 | Coinlator   |             | vetada      |        4.7 | 95K  |              387 |             269 | 7dbey6My9ksrNqcRbfwEkMBT98L1PYqke3FhQcv9pump |   0    |
| 22:03 | YN          |             | vetada      |        2.9 | 11K  |              245 |             155 | EEfgQNgGzWsh5irrkPTS49CTpPt9nGzKrSTXr8oWjnLy |   0.26 |
| 22:03 | SHALAB      |             | alta        |       13.8 | 13K  |               94 |              35 | AoPXbQcvyVnA348eRd88f27twD8sLuUXM1MNxHpnpump |   0.26 |
| 21:59 | PATHJAV     |             | vetada      |        4.3 | 83K  |              135 |              36 | 2CJcgwnrKeH9PZXirAkgEBfw7V114zAeLR6GPVyFbonk |   0    |
| 21:59 | SLOTVINE    |             | baja        |        4   | 34K  |              359 |              97 | BHwrSxQX9G6bBd8773mJVRenuPow5USmP98kq453pump |   0    |
| 21:57 | MATRIX      |             | vetada      |        2.8 | 90K  |              524 |             328 | H4gAMBFkfzhn51phWA7M9XCi3duFobaBz89rY38Epump |   0    |
| 21:54 | FINE        |             | vetada      |        2.7 | 17K  |              368 |             100 | 2aMF4mRqtFTjiqPzpWUWkSiYuevPNdX1jxt3B93RR1gT |   0    |
| 21:54 | Loomer      |             | vetada      |        2.5 | 86K  |              970 |             596 | 4JUv66RqP9ed78ajpNpuTbC1rGGgQwBwei4agQtGanTb |   1.79 |
| 21:48 | Dungkey     |             | vetada      |        3.3 | 76K  |              131 |              36 | 29CWCFZHnrasVuhJWsQmmzAYEAXev9mj73VRq5FMmoon |   0    |
| 21:48 | HIGGSFIELD  | ia          | alta        |        3.1 | 13K  |               65 |              42 | EnyHpAEKC3yxczpC9ib2WGUKBCExTFLgB3pQQaGhpump |   0.26 |
| 21:46 | MOON        | cripto      | vetada      |       11.5 | 21K  |              127 |              38 | Ex17UpeY1VjphPbeLrwrdQSjR39g9QdmksfavERUHeXX |   0    |
| 21:44 | pud         |             | vetada      |        2.2 | 20K  |              655 |             443 | 2nhnxwuAXBAiD5Dcga8AtwKeXPkMA7spEu1CeGUpvHpG |   0.19 |
| 21:38 | Gtray       |             | vetada      |        3.8 | 81K  |              152 |              46 | FUsWtFFzjG8MAhVNtzv7ohgdBHsgNnpGEu3MGF3bonk  |   0    |
| 21:36 | HAMSTR      |             | vetada      |        5.8 | 11K  |               65 |              43 | 5GFoqsbyNqAZi79iisdQW9bBFLP5yR9BqJA3sx8SEYbt |   0.56 |
| 21:27 | ENCORE      |             | vetada      |        2.2 | 142K |               90 |              24 | AfZxVCPC9p6nT5uCLBUHEyAxnK7LHEr5UPAfEHb7moon |   0    |
| 21:25 | SPORT       |             | baja        |        2.9 | 9K   |              203 |             134 | HjrAxGSsFyKwDL7UyYdEJa7NjU6SsvZm77KRe31ipump |   0.4  |
| 21:25 | Novita      |             | alta        |        2.5 | 15K  |              210 |             153 | 2K6byUNcQcXAUHpnNjq2UvjAmUZc8XrA3GQb5MDvtqSu |   0.22 |
| 21:25 | PILLNAMES   |             | vetada      |        2.6 | 11K  |              140 |             102 | 5WTkGBaJCCJk3RLATBJKpD3rzMaQWsFPqXMxAxHFpump |   0.34 |
| 21:25 | dwog        |             | baja        |        2.3 | 9K   |              101 |              71 | 332w4TZ6gYWCpGaVoQ34BKG6QoTzS7s3L6AkjgDQZ6Hd |   0.37 |
| 21:23 | TAMA        |             | vetada      |        5   | 15K  |              198 |             128 | sUccrFL84carhdbYXUkTeKkU2eiXT5kY5KDmR6Vpump  |   0.22 |
| 21:21 | UP          |             | vetada      |        2.5 | 14K  |               77 |              54 | BGNLnqbCZrRWcFYewgUe3eoZuTWXdr6SVWF2VVLj1nqi |   0.25 |
| 21:20 | Parcel      |             | vetada      |        2.4 | 38K  |              439 |             109 | 47v8RTn4E3vS38BvaumuWFLjkMXEqckUtFfh8GRNpump |   0    |
| 21:20 | BUTTERS     |             | vetada      |        3.4 | 18K  |              232 |              78 | FxqKHgX8qhYT1qiojpYLDJPuFmpd6uZsVPAfB8nBZckW |   0    |
| 21:20 | BROOD       |             | vetada      |        5.9 | 9K   |              382 |             213 | 4fk4pdVqFFobEkZXHLET5BviRYTC71zCgpepKDJGpump |   0.35 |
| 21:17 | botchain    |             | vetada      |        2.6 | 90K  |              306 |             222 | DjFCHHoJfNGkLZRs6D49CCsneui1vwym5NX8vAiepump |   0    |
| 21:16 | gotchi      |             | vetada      |        2   | 24K  |              131 |              87 | 2DW3jtBhRnrTMeopJyTsLBWfkwFm4NkH8QdR8YS7pump |   0.41 |
| 21:13 | PUTE        | elon        | alta        |        4.1 | 14K  |              185 |             111 | A3zuVVEJFqQS44ZgF1K9y86vFn2LgJBC6BPpqurFpump |   0.36 |
| 21:13 | 天才交易员       |             | vetada      |        9.3 | 49K  |              339 |              63 | 97XZamAKV9s3RtybN7cuk6oD4kW7i5ZS4z99V1n1V7vh |   0.14 |
| 21:09 | PIPS        | cripto      | baja        |        3.1 | 13K  |              188 |             123 | FpPeaDbprm7JHAxghi98czirmRw3aWRbigefbsTKpump |   0.25 |
| 21:07 | SUPERTAKE   |             | vetada      |        3.4 | 81K  |              662 |             368 | WNnpLo7Mjx3mGw5Vu41EyXUd4CCyJyVHoXVkGdMxpLU  |   0.19 |
| 21:01 | REPOING     |             | vetada      |        2.2 | 15K  |              265 |              76 | Cg82oWFeMvjEqGseFriaGfYGfMHmsBykgtCwdp7DkJUX |   0    |
| 20:55 | Daifuku     | animales    | baja        |        2.5 | 9K   |               45 |              30 | GC4fSFRYrsEA47HFYnUraDkx9fXLBuWc6tgoDQMShs1d |   0.4  |
| 20:52 | PENNY       | cripto      | baja        |        2   | 13K  |              331 |             226 | FXoxRGx1jEHVY2VWMrwkSmrUrT8XwpH9ePikQsjapump |   0.29 |
| 20:47 | AI6         |             | vetada      |        2.4 | 314K |             1476 |             771 | DKxXdaMC1so182urvrrnhs6V6fGTrttPS8br6JuEpump |   0.66 |
| 20:44 | BRIDGE      |             | vetada      |        2   | 16K  |              297 |             108 | AgtkJoUnsjTJFx6EAgVW9Bfbm9uJoWuJRagSLMifqqPw |   0    |
| 20:44 | AGSHLD      |             | vetada      |        2.9 | 77K  |              111 |              26 | GxQymQf6heKhkJMEWo7vgGjGE4w9P4SufgNAvivYbonk |   0    |
| 20:42 | meme/acc    | cripto      | alta        |        4   | 11K  |               56 |              33 | GL68bnTmd6upLw1iHDNdvkBRcEb7VKDCz5woH6Jupump |   0.31 |
| 20:40 | LOBBY       |             | baja        |        4   | 11K  |               92 |              51 | 5Z5WvVb6ZV5mwVJu3yoPoFeQFJ9jfERR2iXjg4nXpump |   0.42 |
| 20:37 | KYLE        |             | vetada      |        2.9 | 18K  |              444 |             308 | ALXXnx7apbbnoYe8D8Sgfhac4QEcfQEQuctWeNi82ha8 |   0.29 |
| 20:31 | FROSTY      |             | vetada      |        2.6 | 16K  |              362 |             262 | 6xjdmD4NyXAHEVfXt2s8oPFree4Eci2EThL1oDQypump |   0.17 |
| 20:28 | HOOK        |             | vetada      |        2.4 | 17K  |               59 |              29 | 66UokDvAUWuT8DiX1JxAyisx3uo4nErZYQocXTowQm2G |   0.29 |
| 20:28 | Spend       |             | vetada      |        2.7 | 29K  |              372 |             193 | AMVBZPNtnDSgHoNZYRKjPQHPXFQogrRjTnUfxodopump |   0.15 |
| 20:28 | PICK        |             | vetada      |        2.4 | 28K  |              244 |             149 | EFzc9krvFrc3SbPKrUabiKxtrWNsDbXGUMZt5VtowoFX |   0.12 |
| 20:20 | INUINK      |             | vetada      |        3.3 | 245K |               82 |              20 | 9k7NgXqiJ7tvLtiB6HXdJHnKZZynFz46AB6Eg4Uwpump |   1.29 |
| 20:04 | BridgePad   |             | vetada      |        3.3 | 9K   |              199 |             147 | CQA5Hm11M4p24FkAndoSVnXKGBEnHkRqbfhCDXzBpump |   0.42 |
| 20:02 | Goldbid     |             | vetada      |        3.6 | 73K  |               60 |              17 | 9UjQYT8BTZbgYQVYpLLiSsZ1b4f9UeWfQFBMiV67pump |   0    |
| 20:02 | PAYDAY      |             | vetada      |        2.8 | 35K  |              490 |             137 | BQKQeoxCEwyn4kPyEpJ88NqBaEELG6fLKufRCsvMpump |   0    |
| 20:01 | D/TRUMP     | politica    | vetada      |        2.6 | 30K  |              126 |              86 | BTgenoGircCT23iFM7EzKf9jaf2LFnfh9K6sfpz6pump |   0    |
| 19:56 | Nibs        |             | vetada      |       14   | 9K   |               40 |              21 | DVx9ULhL3e7xQsGagXgkxdZoWTVorYgDbe33ydqyFhyN |   0.8  |
| 19:54 | PIPE/ACC    |             | vetada      |        2.4 | 17K  |              309 |             173 | 3rNV2pmns8nCpx5NjSTwoBxARwQs21BgsdwjxXdfpump |   0    |
| 19:52 | ipfs        |             | vetada      |        2.4 | 31K  |              622 |             363 | DSudLYZaGrxPFhQydNEDELTt4aDC9bhetA4yG8utpump |   0.12 |
| 19:44 | Bronbell    |             | vetada      |        2.7 | 73K  |               99 |              20 | Ad3kZ8FJKiZw7qYL6amZsEq4tscCq5cUvYte4XQAmoon |   0    |
| 19:43 | MOTEPAID    | ia          | alta        |        2.1 | 9K   |              117 |              73 | GZR6rd4rVd2wtKh7cFUTW8KB8Z4wMHro6vg1BCcLpump |   0.28 |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **23702**; seguidas de un desplome (caída a un 40% o menos en 30 min): **479**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |             19522 | 1%                   | 9%                   |
| Ticket medio < $30 (volumen de microcompras) |             21517 | 1%                   | 8%                   |
| Más de 8 compradores por vendedor (5 min)    |               126 | 10%                  | 2%                   |
| Subida de más del 100% en 1 h                |              2315 | 13%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |               252 | 46%                  | 2%                   |
| Aceleración final                            |               308 | 16%                  | 2%                   |
| Más vendedores que compradores (5 min)       |             21350 | 1%                   | 14%                  |
| Ya multiplicó x5 o más desde la detección    |              8361 | 2%                   | 2%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra   |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor   | mc_mayor   | mint_mayor                                   |
|:----------|------------:|---------------------:|:------------------|:--------|:-----------|:---------------------------------------------|
| zubit     |           3 |                    0 | x24               | Zubit   | 53K        | 42p4A4qKML7aPaUiCHpt5utFa4ozuhxPDtG4D2wDntma |

## Narrativas activas (últimas 2 h)

| narrativa   |   tokens_nuevos | lider    | mc_lider   | catalizador   | mint_lider                                   |
|:------------|----------------:|:---------|:-----------|:--------------|:---------------------------------------------|
| animales    |               2 | GPEPE    | 10K        |               | 6wKf8fGVjAuvUMLqXc9Poop15kG5R3XBNJS3nq6Apump |
| politica    |               1 | BUNTRUMP | 212K       |               | EqWgdTpMWHGm8ivNn3Cc7HA2fKKfQXnq77vumrq4KX4X |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

Ninguno.
