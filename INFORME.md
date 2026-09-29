# Informe del radar de memecoins

Generado: 2026-09-29 03:23 UTC

- Tokens registrados: **2091** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **591**
- Pasan el filtro v1: **47**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## ¿Funciona el filtro?

### Todos los tokens

| todos   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| todos   | 591 | 75%           | 39%          | -100%         |            -23.2 |      0 | -        | -        | -                    |         |

### Filtro v1

| filtro_v1   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no pasa     | 573 | 74%           | 38%          | -100%         |           -23.4  |      0 | -        | -        | -                    |                 |
| pasa        |  18 | 89%           | 56%          | -100%         |           -16.94 |      0 | -        | -        | -                    | muestra pequeña |

### Alertas tempranas del vigía (2-15 min de vida) frente al escaneo

| origen   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| escaneo  | 567 | 75%           | 39%          | -100%         |           -22.87 |      0 | -        | -        | -                    |                 |
| vigia    |  24 | 58%           | 26%          | -100%         |           -30.72 |      0 | -        | -        | -                    | muestra pequeña |

### Alertas con tema, sin tema y vetadas

|                                            | 0               |
|:-------------------------------------------|:----------------|
| ('antes de separar', 'n')                  | 24              |
| ('antes de separar', 'muertos_24h')        | 58%             |
| ('antes de separar', 'tocaron_2x')         | 26%             |
| ('antes de separar', 'mediana_24h')        | -100%           |
| ('antes de separar', 'regla_$_por_50')     | -30.72          |
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
| compras_desbalanceadas | 119 | 93%           | 45%          | -100%         |           -17.08 |      0 | -        | -        | -                    |         |
| holders_concentrados   | 194 | 70%           | 47%          | -100%         |           -16.61 |      0 | -        | -        | -                    |         |
| liquidez_anomala       | 224 | 83%           | 36%          | -100%         |           -25.21 |      0 | -        | -        | -                    |         |
| mc_fuera_rango         | 341 | 65%           | 33%          | -100%         |           -25.43 |      0 | -        | -        | -                    |         |
| nombre_clonado         | 369 | 79%           | 40%          | -100%         |           -24.57 |      0 | -        | -        | -                    |         |
| peligro_rugcheck       | 244 | 87%           | 37%          | -100%         |           -26.28 |      0 | -        | -        | -                    |         |
| pocos_compradores      |  82 | 68%           | 21%          | -100%         |           -31.4  |      0 | -        | -        | -                    |         |
| presion_venta          |  94 | 70%           | 37%          | -100%         |           -27.52 |      0 | -        | -        | -                    |         |
| volumen_inflado        | 145 | 72%           | 38%          | -100%         |           -21.41 |      0 | -        | -        | -                    |         |

## Narrativas

### Por narrativa

|                                         | 0               |
|:----------------------------------------|:----------------|
| ('animales', 'n')                       | 8               |
| ('animales', 'muertos_24h')             | 88%             |
| ('animales', 'tocaron_2x')              | 33%             |
| ('animales', 'mediana_24h')             | -100%           |
| ('animales', 'regla_$_por_50')          | -32.36          |
| ('animales', 'n_7d')                    | 0               |
| ('animales', '10x_7d')                  | -               |
| ('animales', '50x_7d')                  | -               |
| ('animales', 'tendencia_$_por_50')      | -               |
| ('animales', 'aviso')                   | muestra pequeña |
| ('celebridades', 'n')                   | 9               |
| ('celebridades', 'muertos_24h')         | 100%            |
| ('celebridades', 'tocaron_2x')          | 56%             |
| ('celebridades', 'mediana_24h')         | -100%           |
| ('celebridades', 'regla_$_por_50')      | +2.41           |
| ('celebridades', 'n_7d')                | 0               |
| ('celebridades', '10x_7d')              | -               |
| ('celebridades', '50x_7d')              | -               |
| ('celebridades', 'tendencia_$_por_50')  | -               |
| ('celebridades', 'aviso')               | muestra pequeña |
| ('cripto', 'n')                         | 17              |
| ('cripto', 'muertos_24h')               | 71%             |
| ('cripto', 'tocaron_2x')                | 47%             |
| ('cripto', 'mediana_24h')               | -100%           |
| ('cripto', 'regla_$_por_50')            | -18.96          |
| ('cripto', 'n_7d')                      | 0               |
| ('cripto', '10x_7d')                    | -               |
| ('cripto', '50x_7d')                    | -               |
| ('cripto', 'tendencia_$_por_50')        | -               |
| ('cripto', 'aviso')                     | muestra pequeña |
| ('elon', 'n')                           | 5               |
| ('elon', 'muertos_24h')                 | 100%            |
| ('elon', 'tocaron_2x')                  | 80%             |
| ('elon', 'mediana_24h')                 | -100%           |
| ('elon', 'regla_$_por_50')              | -16.93          |
| ('elon', 'n_7d')                        | 0               |
| ('elon', '10x_7d')                      | -               |
| ('elon', '50x_7d')                      | -               |
| ('elon', 'tendencia_$_por_50')          | -               |
| ('elon', 'aviso')                       | muestra pequeña |
| ('festividades', 'n')                   | 0               |
| ('ia', 'n')                             | 32              |
| ('ia', 'muertos_24h')                   | 75%             |
| ('ia', 'tocaron_2x')                    | 40%             |
| ('ia', 'mediana_24h')                   | -100%           |
| ('ia', 'regla_$_por_50')                | -22.03          |
| ('ia', 'n_7d')                          | 0               |
| ('ia', '10x_7d')                        | -               |
| ('ia', '50x_7d')                        | -               |
| ('ia', 'tendencia_$_por_50')            | -               |
| ('ia', 'aviso')                         |                 |
| ('noticias_cripto', 'n')                | 0               |
| ('politica', 'n')                       | 15              |
| ('politica', 'muertos_24h')             | 80%             |
| ('politica', 'tocaron_2x')              | 58%             |
| ('politica', 'mediana_24h')             | -100%           |
| ('politica', 'regla_$_por_50')          | -9.71           |
| ('politica', 'n_7d')                    | 0               |
| ('politica', '10x_7d')                  | -               |
| ('politica', '50x_7d')                  | -               |
| ('politica', 'tendencia_$_por_50')      | -               |
| ('politica', 'aviso')                   | muestra pequeña |
| ('sin narrativa', 'n')                  | 496             |
| ('sin narrativa', 'muertos_24h')        | 73%             |
| ('sin narrativa', 'tocaron_2x')         | 36%             |
| ('sin narrativa', 'mediana_24h')        | -100%           |
| ('sin narrativa', 'regla_$_por_50')     | -24.42          |
| ('sin narrativa', 'n_7d')               | 0               |
| ('sin narrativa', '10x_7d')             | -               |
| ('sin narrativa', '50x_7d')             | -               |
| ('sin narrativa', 'tendencia_$_por_50') | -               |
| ('sin narrativa', 'aviso')              |                 |
| ('videojuegos', 'n')                    | 9               |
| ('videojuegos', 'muertos_24h')          | 89%             |
| ('videojuegos', 'tocaron_2x')           | 62%             |
| ('videojuegos', 'mediana_24h')          | -100%           |
| ('videojuegos', 'regla_$_por_50')       | -12.15          |
| ('videojuegos', 'n_7d')                 | 0               |
| ('videojuegos', '10x_7d')               | -               |
| ('videojuegos', '50x_7d')               | -               |
| ('videojuegos', 'tendencia_$_por_50')   | -               |
| ('videojuegos', 'aviso')                | muestra pequeña |

### Líder de su narrativa frente a seguidores y clones

| papel_en_narrativa   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| líder                |  34 | 100%          | 56%          | -100%         |           -17.31 |      0 | -        | -        | -                    |         |
| seguidor/clon        |  61 | 70%           | 45%          | -100%         |           -16.68 |      0 | -        | -        | -                    |         |
| sin narrativa        | 496 | 73%           | 36%          | -100%         |           -24.42 |      0 | -        | -        | -                    |         |

### Calor de la narrativa (tokens con el mismo tema en el escaneo)

| calor   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 1 token |  13 | 100%          | 58%          | -100%         |           -20.96 |      0 | -        | -        | -                    | muestra pequeña |
| 2-3     |  22 | 100%          | 73%          | -100%         |            11.16 |      0 | -        | -        | -                    | muestra pequeña |
| 4-8     |  38 | 71%           | 34%          | -100%         |           -32.83 |      0 | -        | -        | -                    |                 |
| 9+      |  20 | 70%           | 42%          | -100%         |           -18.74 |      0 | -        | -        | -                    | muestra pequeña |

### Con catalizador próximo

| con_catalizador   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no                | 567 | 74%           | 38%          | -100%         |           -23.72 |      0 | -        | -        | -                    |                 |
| sí                |  24 | 83%           | 60%          | -100%         |           -10.66 |      0 | -        | -        | -                    | muestra pequeña |

### Tokens del escaneo que comparten palabra con él

| calor_palabra_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| única            | 230 | 73%           | 42%          | -100%         |           -20.16 |      0 | -        | -        | -                    |         |
| 2 tokens         |  72 | 67%           | 38%          | -100%         |           -22.18 |      0 | -        | -        | -                    |         |
| 3-4              |  95 | 79%           | 36%          | -100%         |           -26.25 |      0 | -        | -        | -                    |         |
| 5+               | 130 | 78%           | 35%          | -100%         |           -27.3  |      0 | -        | -        | -                    |         |

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
| ('sin datos', 'n')                  | 300    |
| ('sin datos', 'muertos_24h')        | 77%    |
| ('sin datos', 'tocaron_2x')         | 32%    |
| ('sin datos', 'mediana_24h')        | -100%  |
| ('sin datos', 'regla_$_por_50')     | -28.03 |
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
| <30         | 172 | 73%           | 27%          | -100%         |           -30.21 |      0 | -        | -        | -                    |                 |
| 30-45       | 165 | 73%           | 52%          | -100%         |           -14.4  |      0 | -        | -        | -                    |                 |
| 45-60       |  41 | 78%           | 46%          | -100%         |            -9.1  |      0 | -        | -        | -                    |                 |
| 60+         |   1 | 0%            | 0%           | -79%          |           -32.17 |      0 | -        | -        | -                    | muestra pequeña |

## Señales por separado

### Edad al detectarlo

| edad      |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15 min   | 523 | 75%           | 38%          | -100%         |           -25.39 |      0 | -        | -        | -                    |                 |
| 15-30 min |  16 | 69%           | 50%          | -100%         |            -1.46 |      0 | -        | -        | -                    | muestra pequeña |
| 30-60 min |  19 | 84%           | 44%          | -100%         |           -17.35 |      0 | -        | -        | -                    | muestra pequeña |
| 1-3 h     |  11 | 82%           | 27%          | -100%         |           -18.49 |      0 | -        | -        | -                    | muestra pequeña |
| 3-24 h    |  16 | 44%           | 50%          | -83%          |            16.18 |      0 | -        | -        | -                    | muestra pequeña |

### Capitalización al detectarlo

| cap       |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <50K      | 331 | 65%           | 33%          | -100%         |           -25.73 |      0 | -        | -        | -                    |                 |
| 50-150K   | 134 | 87%           | 40%          | -100%         |           -29.68 |      0 | -        | -        | -                    |                 |
| 150-500K  |  88 | 84%           | 51%          | -100%         |            -6.18 |      0 | -        | -        | -                    |                 |
| 500K-1.5M |  28 | 100%          | 57%          | -100%         |           -20.96 |      0 | -        | -        | -                    | muestra pequeña |
| >1.5M     |  10 | 80%           | 30%          | -100%         |           -15.85 |      0 | -        | -        | -                    | muestra pequeña |

### Compradores / vendedores (1 h)

| compradores_vs_vendedores   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:----------------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| <1.2                        |  94 | 70%           | 37%          | -100%         |           -27.52 |      0 | -        | -        | -                    |         |
| 1.2-3                       | 194 | 51%           | 35%          | -100%         |           -22.6  |      0 | -        | -        | -                    |         |
| 3-8                         | 184 | 90%           | 39%          | -100%         |           -25.6  |      0 | -        | -        | -                    |         |
| >8                          | 119 | 93%           | 45%          | -100%         |           -17.08 |      0 | -        | -        | -                    |         |

### Volumen de 1 h / capitalización

| volumen_vs_cap   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| <0.5             | 250 | 88%           | 31%          | -100%         |           -33.58 |      0 | -        | -        | -                    |         |
| 0.5-1            |  62 | 68%           | 42%          | -100%         |            -8.96 |      0 | -        | -        | -                    |         |
| 1-3              | 134 | 55%           | 50%          | -100%         |           -12.51 |      0 | -        | -        | -                    |         |
| >3               | 145 | 72%           | 38%          | -100%         |           -21.41 |      0 | -        | -        | -                    |         |

### Peligros de RugCheck

| peligros_rugcheck   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:--------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| 0                   | 167 | 52%           | 42%          | -100%         |           -14.99 |      0 | -        | -        | -                    |         |
| 1                   | 197 | 90%           | 38%          | -100%         |           -24.89 |      0 | -        | -        | -                    |         |
| 2+                  |  47 | 74%           | 32%          | -100%         |           -33.31 |      0 | -        | -        | -                    |         |
| sin datos           | 180 | 78%           | 37%          | -100%         |           -26.9  |      0 | -        | -        | -                    |         |

### Liquidez bloqueada (RugCheck): con 0% el creador puede retirarla

| liquidez_bloqueada   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| 0%                   | 139 | 78%           | 31%          | -100%         |           -30.69 |      0 | -        | -        | -                    |         |
| parcial              | 113 | 82%           | 47%          | -100%         |           -15.52 |      0 | -        | -        | -                    |         |
| 100%                 | 159 | 62%           | 40%          | -100%         |           -18.35 |      0 | -        | -        | -                    |         |
| sin datos            | 180 | 78%           | 37%          | -100%         |           -26.9  |      0 | -        | -        | -                    |         |

### Puntuación (quintiles)

| puntuacion_q   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:---------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| Q1 (baja)      | 137 | 80%           | 27%          | -100%         |           -32.83 |      0 | -        | -        | -                    |         |
| Q2             | 122 | 71%           | 37%          | -100%         |           -27.03 |      0 | -        | -        | -                    |         |
| Q3             |  99 | 65%           | 33%          | -100%         |           -20.08 |      0 | -        | -        | -                    |         |
| Q4             |  99 | 75%           | 40%          | -100%         |           -23.81 |      0 | -        | -        | -                    |         |
| Q5 (alta)      | 134 | 80%           | 51%          | -100%         |           -12.67 |      0 | -        | -        | -                    |         |

### DEX

|                                           | 0               |
|:------------------------------------------|:----------------|
| ('bags-fm', 'n')                          | 0               |
| ('letsbonk-fun', 'n')                     | 0               |
| ('meteora', 'n')                          | 0               |
| ('meteora-damm-v2', 'n')                  | 88              |
| ('meteora-damm-v2', 'muertos_24h')        | 89%             |
| ('meteora-damm-v2', 'tocaron_2x')         | 29%             |
| ('meteora-damm-v2', 'mediana_24h')        | -100%           |
| ('meteora-damm-v2', 'regla_$_por_50')     | -34.24          |
| ('meteora-damm-v2', 'n_7d')               | 0               |
| ('meteora-damm-v2', '10x_7d')             | -               |
| ('meteora-damm-v2', '50x_7d')             | -               |
| ('meteora-damm-v2', 'tendencia_$_por_50') | -               |
| ('meteora-damm-v2', 'aviso')              |                 |
| ('meteora-dbc', 'n')                      | 33              |
| ('meteora-dbc', 'muertos_24h')            | 70%             |
| ('meteora-dbc', 'tocaron_2x')             | 22%             |
| ('meteora-dbc', 'mediana_24h')            | -100%           |
| ('meteora-dbc', 'regla_$_por_50')         | -29.48          |
| ('meteora-dbc', 'n_7d')                   | 0               |
| ('meteora-dbc', '10x_7d')                 | -               |
| ('meteora-dbc', '50x_7d')                 | -               |
| ('meteora-dbc', 'tendencia_$_por_50')     | -               |
| ('meteora-dbc', 'aviso')                  |                 |
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
| ('pump-fun', 'n')                         | 82              |
| ('pump-fun', 'muertos_24h')               | 20%             |
| ('pump-fun', 'tocaron_2x')                | 32%             |
| ('pump-fun', 'mediana_24h')               | -80%            |
| ('pump-fun', 'regla_$_por_50')            | -21.29          |
| ('pump-fun', 'n_7d')                      | 0               |
| ('pump-fun', '10x_7d')                    | -               |
| ('pump-fun', '50x_7d')                    | -               |
| ('pump-fun', 'tendencia_$_por_50')        | -               |
| ('pump-fun', 'aviso')                     |                 |
| ('pumpswap', 'n')                         | 381             |
| ('pumpswap', 'muertos_24h')               | 85%             |
| ('pumpswap', 'tocaron_2x')                | 42%             |
| ('pumpswap', 'mediana_24h')               | -100%           |
| ('pumpswap', 'regla_$_por_50')            | -21.51          |
| ('pumpswap', 'n_7d')                      | 0               |
| ('pumpswap', '10x_7d')                    | -               |
| ('pumpswap', '50x_7d')                    | -               |
| ('pumpswap', 'tendencia_$_por_50')        | -               |
| ('pumpswap', 'aviso')                     |                 |
| ('raydium', 'n')                          | 4               |
| ('raydium', 'muertos_24h')                | 25%             |
| ('raydium', 'tocaron_2x')                 | 50%             |
| ('raydium', 'mediana_24h')                | -69%            |
| ('raydium', 'regla_$_por_50')             | +8.12           |
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

- 30m: 56% vivos (n=2014)
- 1h: 49% vivos (n=2037)
- 6h: 34% vivos (n=1956)
- 24h: 25% vivos (n=591)

## Supervivientes (tokens de 3 a 120 días que despiertan)

Aún no hay supervivientes (se buscan una vez por hora).

## Últimas alertas del vigía (6 h)

| ts    | simbolo     | narrativa   | prioridad   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:------------|:------------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 03:09 | ZSOL        |             | vetada      |        3.6 | 13K  |              203 |              37 | B81iCiqBA8sTwsRMMqZF34wAZUVqJ9jYSEan6m9G4cdR | nan    |
| 03:04 | 卧槽泥马        |             | vetada      |        2.9 | 14K  |              456 |             101 | DGCW9x9o9ZTCTxRWqwXS7xACUB4zJGsTCdxqYvKw6ZRR | nan    |
| 03:04 | WOJAK       |             | baja        |       10   | 13K  |               75 |              40 | DHT1Ko1NcGu3wxmV3J8Vh5zbqWKxq5ustAgC2AWrpump | nan    |
| 03:02 | DUEL        |             | vetada      |        4.8 | 134K |              634 |             316 | 4aDtkCadyWomBewuynPi7Y8NR41dKXAmUMFYMLBxpump | nan    |
| 02:48 | MAGA        | politica    | vetada      |        3   | 140K |              240 |              54 | 3p3xFYzTqFDQ5jj7BiNb6hZJf4HhjWPgR3fLzKbSuTha | nan    |
| 02:48 | 后荡狗         |             | vetada      |        3   | 15K  |              500 |              98 | 5n8mwLeUWBBWjDCMnSmaaupX5sUA1HZSoK6u72KFEJEH | nan    |
| 02:45 | Duo         |             | vetada      |        4.6 | 29K  |              294 |             187 | 33boQwkhNhGNWGtixmqPLoKfoTUePZt4mV5Nb8Wdpump | nan    |
| 02:43 | LAMBO       |             | vetada      |        2.8 | 17K  |              172 |             116 | D6TcLMVJFxV9qmVP1ZDdt8HH3VwhwHPH2bJDFrhBjiN1 | nan    |
| 02:32 | PCAT        |             | vetada      |        2.7 | 21K  |              418 |             249 | 4kYsZeMw45RXoeJg8BjyeZVtwoTQ2LAEoZckwK1kpump | nan    |
| 02:29 | STARSIR     |             | vetada      |        4   | 80K  |              137 |              38 | 8yeVL1nrnAR3rXHNJAAPTV1R5XGEXT4T3LFpw1fwBAGS | nan    |
| 02:27 | RING        |             | vetada      |        2.4 | 15K  |              310 |              73 | Ekz9LzD8SxJTQ9b8roFxpEaLjmvqS2DsyzMcAHyuuw7Z | nan    |
| 02:26 | Don         |             | vetada      |        2.6 | 19K  |              121 |              84 | 8sctEogCWQ17uoL1JVD79nv2QnM8cXga6guUCXwfZRnU | nan    |
| 02:22 | fuckcat     |             | vetada      |        2.9 | 20K  |              386 |             221 | AS5hAgFnqfhqv1DiLyLidDHUtisZsFg4cVV95oTFpump | nan    |
| 02:17 | neet        |             | vetada      |        3.5 | 31K  |              387 |              52 | 5AyGSZCARYCUE863RYhcgu1gDfpbqk3aeSKKB4qnCMps | nan    |
| 02:10 | XLiquid     |             | vetada      |        3.3 | 14K  |              126 |              69 | 5iAu4jN91cSJ6vaXdZ8WiopNvxZ7KM4kTbKKB5duJLni |   0    |
| 02:10 | CASHED      |             | vetada      |        2.4 | 30K  |              166 |              91 | 367vwbRPVi2vgEZqdEwEoMYNo5ESdypuznPT3isdpump |   1.99 |
| 02:06 | 鹅次元         |             | vetada      |        5.8 | 31K  |              232 |              33 | 53EsmDnAKLfiTuDv7QLG4rjhwtF1b8bXTcid8yYaw6Vy |   2.83 |
| 01:59 | KODA        |             | vetada      |        7.9 | 20K  |               43 |              22 | A8QvRwVGoFuqBMzTHN5CRwf9Cu8sMiq9irELQLopump  |   0    |
| 01:49 | BACKED      |             | vetada      |        2.9 | 57K  |              276 |             164 | FJFZysCbtXXVCWYi1a6M7jcpURi2ytiFAeioBjYTpump |   0    |
| 01:47 | 庄欣如         |             | vetada      |        5.2 | 25K  |              537 |              82 | 2TDAGPHeKGgc6JGFLyuVehW7vV8qdzw4vJ1Pfu2okoko |   0    |
| 01:47 | JONKEY      |             | vetada      |        2.3 | 19K  |              165 |              69 | CGrUTkP8V25igZyvUrd6AYxqYy52ochsgBEEPcdHVifq |   0    |
| 01:36 | bwg         |             | vetada      |        2.3 | 21K  |              480 |             365 | AifdDLDaUbVSeewQaGqLYh94fZpzRg4nmSBT2WGUjSK6 |   0.15 |
| 01:32 | zCATS       |             | vetada      |        5   | 18K  |              224 |             150 | EV5vDywehbcqyuwVRCF1ewV3W2Am7e1X51pWVWFrpump |   0.3  |
| 01:29 | Nacho       |             | vetada      |        6.2 | 11K  |              112 |              64 | 5tFFZveFzVnc4hcuNvXGgjCy6uSSumu86cnz9BLapump |   0.26 |
| 01:26 | PARASITE    |             | vetada      |        9.1 | 71K  |              261 |             165 | 3kmygWKZBkCYrgZHKfiuB9UFKTcDLTFFsKo3BWpmpump |  24.93 |
| 01:22 | GPEPE       | animales    | vetada      |        3.9 | 10K  |               55 |              22 | 6wKf8fGVjAuvUMLqXc9Poop15kG5R3XBNJS3nq6Apump |   0.4  |
| 01:22 | 笑笑牛         |             | vetada      |        3.4 | 90K  |               60 |              33 | E2h2zFtNzzKtJznxNCu1F26xCBpMVCkDRxHgaiE72H5e |   0    |
| 01:16 | Adventures  |             | vetada      |        3.6 | 15K  |              256 |              67 | 8xbSqRfjKPxFwkVG5egnDxq4hVwZnFDY1D2hbnF8H4o1 |   0    |
| 01:12 | KAIRO       |             | vetada      |        4.9 | 18K  |              362 |              58 | FNvEtxM7fu6K4JGZwbiHTPLY7PpYjjHQwQTqHrKhz3Ad |   0    |
| 01:08 | CHRLSCRL    |             | vetada      |        3.3 | 90K  |              156 |              35 | AM1y6BqRP6vkt54Tn9Q6FrcugjJ8xXFGEMBRQiKoBAGS |   0    |
| 01:06 | JEET        |             | vetada      |        4.1 | 19K  |              183 |             126 | 94mo6yYt5z9t31TjS257coYsRX7b7KPTKWVRzAnuLECr |   2.66 |
| 01:01 | SBC         |             | vetada      |        4.7 | 25K  |              153 |             109 | ArV7g2VBDHTUvfJTwCPYzzPJRozHbdS94QigVPuFpump |   1.21 |
| 01:00 | Pillys      |             | baja        |        8.8 | 14K  |               51 |              38 | E2U8r19SNWMGjhNc93NSgv26zE7DkVfXdgUEacESpump |   0.26 |
| 00:57 | MINESOFT    |             | vetada      |        3.9 | 18K  |               45 |              33 | 96Mxn6NiP1GjXAxwuAvv7qgsBciqdQUmAuSJ6zXtpump |   0.25 |
| 00:55 | CAVO        |             | vetada      |        3.7 | 29K  |              245 |             146 | imKHMmk6bC7MK15NUKJx6RX8aFyAVZ5dVkBgDTCpump  |   0.1  |
| 00:52 | illusion    |             | vetada      |        3.3 | 56K  |              254 |             156 | Bxz3haSgqQPx6JGqay1K8cfpAjDqmqLzhjkWKE5fpump |   0    |
| 00:52 | STARCRWN    |             | vetada      |        2.8 | 74K  |               55 |              18 | CtpBPGJUWsoeQPdaXjkUj3WyXzaXPrkwH6o4ojoupump |   0    |
| 00:50 | stillwet    |             | vetada      |        3.9 | 40K  |              344 |              46 | 85f5LpJhRdPnqYCQxMQRsDkqBX61ji2VG3Fucyy4bQyr |   0    |
| 00:43 | shiboo      | animales    | vetada      |        3.4 | 10K  |              249 |             178 | ibcCTSui26aRuqVwWsibkDSVVitaVtFdTcHjhDapump  |   0.47 |
| 00:43 | COCKHERO    |             | vetada      |        3.2 | 61K  |              526 |              79 | A6KqvSgDXjG5PW3KiKJH9CT5xHPSVQEoxVzQppfVbHaS |   2.25 |
| 00:38 | BUNTRUMP    | politica    | vetada      |        3.2 | 212K |              106 |              29 | EqWgdTpMWHGm8ivNn3Cc7HA2fKKfQXnq77vumrq4KX4X |   0.43 |
| 00:32 | Kretina     |             | vetada      |        3.8 | 85K  |               93 |              21 | 7pLvXn5waVE55voQfq6tVW7HiiRkK9NMfQhxGCubpump |   0    |
| 00:26 | cocainu     |             | vetada      |        2.2 | 22K  |              319 |             137 | G7qVGuAs11R76BiLnba76pvWGQXdmVcjcWgUp3GFpump |   0.23 |
| 00:26 | Murphy      |             | vetada      |        7.3 | 267K |               75 |              54 | 5v3BV2UAbrmRgpRqJG2UaZcCJTo6MHdmoQYAFULuYeHz |   2.42 |
| 00:13 | HOTNUTS     |             | vetada      |        3.1 | 20K  |              519 |             103 | wSeTcspXGWciAhw7trRJAeSYB7nEoAuPeKXgRYRZ7WQ  |   1.15 |
| 00:13 | Tommie      |             | baja        |        3.3 | 15K  |              149 |              84 | 3WPCvB8RshheEUEYLHiF3GusrseiaBfMDsVmTVR3pump |   2.25 |
| 23:55 | CANDACE     |             | vetada      |       12.5 | 93K  |               72 |              49 | GrXMbn56JtFngA2FgoXenJG5HeD1GhvFnjyFPWbfpump |   0.19 |
| 23:55 | Unbox       |             | vetada      |        5.5 | 11K  |               78 |              44 | N1kCpRuU94iRGRNqe5ZiUqHa9w9kaMWgZ56kpXUpump  |   1.8  |
| 23:52 | BAGSPAY     |             | vetada      |        2.6 | 53K  |              511 |              64 | AMaR7sGJoLXWTWxTh8wcT6FT1pgC3YvPbnU7BXKBdthZ |   0    |
| 23:47 | ANTH        |             | vetada      |        2.9 | 16K  |               90 |              64 | 8HQDosKAfeJE5wjV5sWm9fv1KgaVTFNZdYsP5mJqASTb |   0.32 |
| 23:43 | RuneChain   |             | baja        |       11.1 | 12K  |               64 |              40 | 7SpVU1kJEDtrQexRWgZy64ZXnHjhHyimRjB2zmHZpump |   0.55 |
| 23:41 | trickle     |             | vetada      |        3.6 | 53K  |              263 |             153 | 7SDWbs81JV89HeC4jNbZ15yczLCTZa2RvHg5z4Lrpump |   0    |
| 23:38 | HALLOWINU   |             | baja        |        4.1 | 16K  |              195 |             110 | WApCdQftZcRUNHN9S2XvmrqeRtRASE3EZxnwuNJpump  |   3.49 |
| 23:30 | KILLMASK    |             | vetada      |        3   | 17K  |              129 |              63 | Ewsw5WxVXDF5zVhUUo8KVkGee5c4kyHhpqQKoGE5pump |   0    |
| 23:30 | LAYER       |             | vetada      |       13.9 | 9K   |               50 |              31 | ACPsyMv2mwGCbk6ygBTzmyXFrPtcwuqiZvQgSL37pump |   0.39 |
| 23:26 | wif/acc     | animales    | vetada      |        3   | 24K  |              471 |             287 | 6PdE9hMCZFRwsdC4qUrQtfQN1XGwGLGPmFky1ZNQpump |   0.17 |
| 23:24 | PUMPBLOX    | cripto      | vetada      |        2.9 | 15K  |              300 |             189 | 6wACL4rfquHHw7XNPDYwrKWELQRXZjfANTafqecPpump |   0.55 |
| 23:22 | ACHACL      |             | vetada      |        6.2 | 85K  |               81 |              23 | BH3i5c4wtzmnx5GAxK7SZDqnw3ycYMNmhezvLcknmoon |   0    |
| 23:15 | FOMOWEEN    |             | baja        |        2.8 | 11K  |              223 |             145 | DoipyvkFiAYXGHwKcKC5ahfWJTuaDenGwAW7TgTzpump |   0.3  |
| 23:13 | SHL0MS      |             | vetada      |        6.9 | 11K  |               47 |              19 | BhaQEvju9852hiJiFs9Y2ecGRb37oUfE9dAA8pLSBAGS |   0.42 |
| 23:11 | Caterpillar |             | vetada      |       13.8 | 34K  |               95 |              64 | CpbSCWm8SzJas65wiKT51mJaePiKZnAUTg9p6DLqr7oT |   0.1  |
| 23:10 | PUMPGO      | cripto      | vetada      |       10   | 151K |              173 |              24 | Fdzxru91oKvcmTz7rK67B5S2HoEGWd4UErdThEx7pump |   0    |
| 23:06 | Krater      |             | baja        |        6.4 | 9K   |               52 |              31 | m5q3JpMtohBRhW2mGnzCj287NkMNCJHZjMepSkHXtos  |   1.23 |
| 22:51 | Ouroboros   |             | baja        |        5.2 | 9K   |               81 |              55 | 8BTPgeMzB1RJvjboWGDEgyssEJZ9GiHfWT13tGk5mWL3 |   0.27 |
| 22:51 | Kitty       |             | vetada      |        4.7 | 27K  |              234 |              40 | C6BtpFKSxCRsDxPeY9aEVZaxXephu5gqZj9mfePAynAa |   0    |
| 22:51 | Swordgirl   |             | vetada      |        5   | 10K  |              132 |              58 | EgbNLcoQX56RDXZiKpbR5QouRU7eE9n64n24AjC3pump |   0.36 |
| 22:51 | OUROBOROS   |             | vetada      |        5.6 | 16K  |              138 |              96 | 8WWryGjcJ2Dv4rJGm9MNzvJw5WNp9vZeVgnY6RcW5uKe |   0.19 |
| 22:35 | MEDCUP      |             | vetada      |        3.8 | 73K  |              205 |              52 | BX1TZRDW9HKqYtLpMiModBdcDeNazYgseVcFyK3obonk |   0    |
| 22:33 | PUPI        |             | vetada      |       15   | 29K  |               46 |              32 | DXrrBJMjK3xAV7YvuWAg42aeJHck3GmJmcN78HfDpump |   4.41 |
| 22:33 | PUMPTOBER   | cripto      | vetada      |        3   | 46K  |               61 |              25 | D37sbd3C3dqgnQ4TGWtxksMp6gRjmP1C7K3ib9wLpump |   0    |
| 22:31 | Carla       |             | vetada      |        3.4 | 14K  |               80 |              54 | 3PjwCqfGMR8CXZbcPEbGTSPQGduizdoVz4N1RQmJd8Uv |   4.13 |
| 22:31 | epsteinu    |             | vetada      |        3   | 17K  |              148 |              73 | AZ8jS8apTnvge18otci45VrJJQKbL3v8DWJNEJEwpump |   0.21 |
| 22:31 | LMT         | politica    | alta        |        3.3 | 17K  |               84 |              62 | HcjPrHdESBJioSMj3HZbHbH7nUsUdcPyjQrPwYZGpump |   0    |
| 22:29 | Merrylegs   |             | vetada      |        4   | 45K  |              694 |             363 | 9t4nAuTyS6QLStW1vTxMLf7899b9UF1tmmhRCLbApump |   0.21 |
| 22:27 | KP          |             | vetada      |        2.8 | 83K  |              387 |             108 | CmWxjebLZa3VohM2QhPcN2VVhwkLqnytksqDiaJwKZ3E |   0    |
| 22:27 | BOCK        |             | vetada      |        3.7 | 15K  |               57 |              26 | 95iVDfEQkHtS734cuseXLJ8oXtrP1LV1gA7uyRB7bonk |   0.23 |
| 22:22 | IRA         |             | vetada      |        4.8 | 19K  |              105 |              53 | F9XfvHQ4MWiX6FVQKHwBM6q7gaxCqEv5WEhjTC2rpump |   0.2  |
| 22:22 | なごやし        |             | vetada      |        3.4 | 29K  |              291 |              73 | HSPehHbS5idzDTfgxz6ZvidREsMFm8dh1YTUmXkUT7xC |   0    |
| 22:22 | loria       |             | vetada      |        3.5 | 23K  |               51 |              31 | FK2LDCsv29toyvzBWLsHoo12BY74ErrCpMWwAmbBxMJY |   0.12 |
| 22:18 | FOGLARE     |             | vetada      |        2.2 | 83K  |              425 |             128 | 3RWZTDUyhdksQdtCB4wpZH9Qj2rStinhABJUpheopump |   0    |
| 22:18 | NIG         |             | vetada      |        2.6 | 9K   |               92 |              41 | 5xMtGqn7wqtePKzqJqEDaFd9JH7TAtdr9aPM125qpump |   0.37 |
| 22:14 | PIMP        |             | vetada      |        3.8 | 44K  |               68 |              40 | DX9mc4dYccjkQ8wkHpLtL1ybvELU2peKGNEqsDzqpump |   0.13 |
| 22:10 | Coinlator   |             | vetada      |        4.7 | 95K  |              387 |             269 | 7dbey6My9ksrNqcRbfwEkMBT98L1PYqke3FhQcv9pump |   0    |
| 22:03 | SHALAB      |             | alta        |       13.8 | 13K  |               94 |              35 | AoPXbQcvyVnA348eRd88f27twD8sLuUXM1MNxHpnpump |   0.26 |
| 22:03 | YN          |             | vetada      |        2.9 | 11K  |              245 |             155 | EEfgQNgGzWsh5irrkPTS49CTpPt9nGzKrSTXr8oWjnLy |   0.26 |
| 21:59 | SLOTVINE    |             | baja        |        4   | 34K  |              359 |              97 | BHwrSxQX9G6bBd8773mJVRenuPow5USmP98kq453pump |   0    |
| 21:59 | PATHJAV     |             | vetada      |        4.3 | 83K  |              135 |              36 | 2CJcgwnrKeH9PZXirAkgEBfw7V114zAeLR6GPVyFbonk |   0    |
| 21:57 | MATRIX      |             | vetada      |        2.8 | 90K  |              524 |             328 | H4gAMBFkfzhn51phWA7M9XCi3duFobaBz89rY38Epump |   0    |
| 21:54 | Loomer      |             | vetada      |        2.5 | 86K  |              970 |             596 | 4JUv66RqP9ed78ajpNpuTbC1rGGgQwBwei4agQtGanTb |   1.79 |
| 21:54 | FINE        |             | vetada      |        2.7 | 17K  |              368 |             100 | 2aMF4mRqtFTjiqPzpWUWkSiYuevPNdX1jxt3B93RR1gT |   0    |
| 21:48 | HIGGSFIELD  | ia          | alta        |        3.1 | 13K  |               65 |              42 | EnyHpAEKC3yxczpC9ib2WGUKBCExTFLgB3pQQaGhpump |   0.26 |
| 21:48 | Dungkey     |             | vetada      |        3.3 | 76K  |              131 |              36 | 29CWCFZHnrasVuhJWsQmmzAYEAXev9mj73VRq5FMmoon |   0    |
| 21:46 | MOON        | cripto      | vetada      |       11.5 | 21K  |              127 |              38 | Ex17UpeY1VjphPbeLrwrdQSjR39g9QdmksfavERUHeXX |   0    |
| 21:44 | pud         |             | vetada      |        2.2 | 20K  |              655 |             443 | 2nhnxwuAXBAiD5Dcga8AtwKeXPkMA7spEu1CeGUpvHpG |   0.19 |
| 21:38 | Gtray       |             | vetada      |        3.8 | 81K  |              152 |              46 | FUsWtFFzjG8MAhVNtzv7ohgdBHsgNnpGEu3MGF3bonk  |   0    |
| 21:36 | HAMSTR      |             | vetada      |        5.8 | 11K  |               65 |              43 | 5GFoqsbyNqAZi79iisdQW9bBFLP5yR9BqJA3sx8SEYbt |   0.56 |
| 21:27 | ENCORE      |             | vetada      |        2.2 | 142K |               90 |              24 | AfZxVCPC9p6nT5uCLBUHEyAxnK7LHEr5UPAfEHb7moon |   0    |
| 21:25 | PILLNAMES   |             | vetada      |        2.6 | 11K  |              140 |             102 | 5WTkGBaJCCJk3RLATBJKpD3rzMaQWsFPqXMxAxHFpump |   0.34 |
| 21:25 | SPORT       |             | baja        |        2.9 | 9K   |              203 |             134 | HjrAxGSsFyKwDL7UyYdEJa7NjU6SsvZm77KRe31ipump |   0.4  |
| 21:25 | dwog        |             | baja        |        2.3 | 9K   |              101 |              71 | 332w4TZ6gYWCpGaVoQ34BKG6QoTzS7s3L6AkjgDQZ6Hd |   0.37 |
| 21:25 | Novita      |             | alta        |        2.5 | 15K  |              210 |             153 | 2K6byUNcQcXAUHpnNjq2UvjAmUZc8XrA3GQb5MDvtqSu |   0.22 |
| 21:23 | TAMA        |             | vetada      |        5   | 15K  |              198 |             128 | sUccrFL84carhdbYXUkTeKkU2eiXT5kY5KDmR6Vpump  |   0.22 |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **24237**; seguidas de un desplome (caída a un 40% o menos en 30 min): **479**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |             20003 | 1%                   | 9%                   |
| Ticket medio < $30 (volumen de microcompras) |             22022 | 1%                   | 8%                   |
| Más de 8 compradores por vendedor (5 min)    |               127 | 10%                  | 2%                   |
| Subida de más del 100% en 1 h                |              2323 | 13%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |               252 | 46%                  | 2%                   |
| Aceleración final                            |               309 | 16%                  | 2%                   |
| Más vendedores que compradores (5 min)       |             21864 | 1%                   | 14%                  |
| Ya multiplicó x5 o más desde la detección    |              8602 | 2%                   | 2%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

Ninguna.

## Narrativas activas (últimas 2 h)

| narrativa   |   tokens_nuevos | lider   | mc_lider   | catalizador   | mint_lider                                   |
|:------------|----------------:|:--------|:-----------|:--------------|:---------------------------------------------|
| animales    |               1 | SIPEPE  | 21K        |               | 7bnJuhKHRvjMmMVyt9F2ZgpRujgJUkz1JgoXpwVJpump |
| politica    |               1 | MAGA    | 140K       |               | 3p3xFYzTqFDQ5jj7BiNb6hZJf4HhjWPgR3fLzKbSuTha |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

Ninguno.
