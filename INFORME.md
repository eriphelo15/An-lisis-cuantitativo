# Informe del radar de memecoins

Generado: 2026-09-28 22:36 UTC

- Tokens registrados: **2000** (desde 2026-09-27 18:07)
- Con resultado a 24 h: **294**
- Pasan el filtro v1: **47**
- Resultados en dólares por cada apuesta de $50, con 3% de costes en la entrada y en la salida:
  - `regla_$_por_50` (24 h): vender 50% a 2x, 20% a 5x, 20% a 10x; stop a -50%.
  - `tendencia_$_por_50` (7 días): vender 1/3 a 3x y el resto con stop móvil del 50% desde el máximo. Es la que puede capturar las subidas grandes.
  - `10x_7d` / `50x_7d`: % de tokens cuyo máximo en 7 días llegó a 10x / 50x.

## ¿Funciona el filtro?

### Todos los tokens

| todos   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| todos   | 294 | 73%           | 40%          | -100%         |           -19.72 |      0 | -        | -        | -                    |         |

### Filtro v1

| filtro_v1   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no pasa     | 286 | 73%           | 40%          | -100%         |           -19.35 |      0 | -        | -        | -                    |                 |
| pasa        |   8 | 75%           | 25%          | -100%         |           -32.34 |      0 | -        | -        | -                    | muestra pequeña |

### Alertas tempranas del vigía (2-15 min de vida) frente al escaneo

|                                   | 0      |
|:----------------------------------|:-------|
| ('escaneo', 'n')                  | 294    |
| ('escaneo', 'muertos_24h')        | 73%    |
| ('escaneo', 'tocaron_2x')         | 40%    |
| ('escaneo', 'mediana_24h')        | -100%  |
| ('escaneo', 'regla_$_por_50')     | -19.72 |
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

| motivo                 |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| compras_desbalanceadas |  61 | 95%           | 46%          | -100%         |           -12.87 |      0 | -        | -        | -                    |         |
| holders_concentrados   | 134 | 70%           | 47%          | -100%         |           -15.57 |      0 | -        | -        | -                    |         |
| liquidez_anomala       | 107 | 79%           | 37%          | -100%         |           -21.28 |      0 | -        | -        | -                    |         |
| mc_fuera_rango         | 160 | 61%           | 35%          | -100%         |           -19.21 |      0 | -        | -        | -                    |         |
| nombre_clonado         | 172 | 78%           | 42%          | -100%         |           -22.36 |      0 | -        | -        | -                    |         |
| peligro_rugcheck       | 174 | 86%           | 38%          | -100%         |           -22.74 |      0 | -        | -        | -                    |         |
| pocos_compradores      |  45 | 62%           | 26%          | -100%         |           -22.9  |      0 | -        | -        | -                    |         |
| presion_venta          |  56 | 64%           | 40%          | -100%         |           -21.59 |      0 | -        | -        | -                    |         |
| volumen_inflado        |  72 | 69%           | 40%          | -100%         |           -18.3  |      0 | -        | -        | -                    |         |

## Narrativas

### Por narrativa

|                                         | 0               |
|:----------------------------------------|:----------------|
| ('animales', 'n')                       | 5               |
| ('animales', 'muertos_24h')             | 80%             |
| ('animales', 'tocaron_2x')              | 33%             |
| ('animales', 'mediana_24h')             | -100%           |
| ('animales', 'regla_$_por_50')          | -40.59          |
| ('animales', 'n_7d')                    | 0               |
| ('animales', '10x_7d')                  | -               |
| ('animales', '50x_7d')                  | -               |
| ('animales', 'tendencia_$_por_50')      | -               |
| ('animales', 'aviso')                   | muestra pequeña |
| ('celebridades', 'n')                   | 4               |
| ('celebridades', 'muertos_24h')         | 100%            |
| ('celebridades', 'tocaron_2x')          | 50%             |
| ('celebridades', 'mediana_24h')         | -100%           |
| ('celebridades', 'regla_$_por_50')      | -2.85           |
| ('celebridades', 'n_7d')                | 0               |
| ('celebridades', '10x_7d')              | -               |
| ('celebridades', '50x_7d')              | -               |
| ('celebridades', 'tendencia_$_por_50')  | -               |
| ('celebridades', 'aviso')               | muestra pequeña |
| ('cripto', 'n')                         | 6               |
| ('cripto', 'muertos_24h')               | 67%             |
| ('cripto', 'tocaron_2x')                | 50%             |
| ('cripto', 'mediana_24h')               | -100%           |
| ('cripto', 'regla_$_por_50')            | +12.73          |
| ('cripto', 'n_7d')                      | 0               |
| ('cripto', '10x_7d')                    | -               |
| ('cripto', '50x_7d')                    | -               |
| ('cripto', 'tendencia_$_por_50')        | -               |
| ('cripto', 'aviso')                     | muestra pequeña |
| ('elon', 'n')                           | 1               |
| ('elon', 'muertos_24h')                 | 100%            |
| ('elon', 'tocaron_2x')                  | 100%            |
| ('elon', 'mediana_24h')                 | -100%           |
| ('elon', 'regla_$_por_50')              | -2.86           |
| ('elon', 'n_7d')                        | 0               |
| ('elon', '10x_7d')                      | -               |
| ('elon', '50x_7d')                      | -               |
| ('elon', 'tendencia_$_por_50')          | -               |
| ('elon', 'aviso')                       | muestra pequeña |
| ('festividades', 'n')                   | 0               |
| ('ia', 'n')                             | 12              |
| ('ia', 'muertos_24h')                   | 92%             |
| ('ia', 'tocaron_2x')                    | 42%             |
| ('ia', 'mediana_24h')                   | -100%           |
| ('ia', 'regla_$_por_50')                | -28.27          |
| ('ia', 'n_7d')                          | 0               |
| ('ia', '10x_7d')                        | -               |
| ('ia', '50x_7d')                        | -               |
| ('ia', 'tendencia_$_por_50')            | -               |
| ('ia', 'aviso')                         | muestra pequeña |
| ('noticias_cripto', 'n')                | 0               |
| ('politica', 'n')                       | 10              |
| ('politica', 'muertos_24h')             | 70%             |
| ('politica', 'tocaron_2x')              | 62%             |
| ('politica', 'mediana_24h')             | -100%           |
| ('politica', 'regla_$_por_50')          | -13.47          |
| ('politica', 'n_7d')                    | 0               |
| ('politica', '10x_7d')                  | -               |
| ('politica', '50x_7d')                  | -               |
| ('politica', 'tendencia_$_por_50')      | -               |
| ('politica', 'aviso')                   | muestra pequeña |
| ('sin narrativa', 'n')                  | 251             |
| ('sin narrativa', 'muertos_24h')        | 71%             |
| ('sin narrativa', 'tocaron_2x')         | 38%             |
| ('sin narrativa', 'mediana_24h')        | -100%           |
| ('sin narrativa', 'regla_$_por_50')     | -20.25          |
| ('sin narrativa', 'n_7d')               | 0               |
| ('sin narrativa', '10x_7d')             | -               |
| ('sin narrativa', '50x_7d')             | -               |
| ('sin narrativa', 'tendencia_$_por_50') | -               |
| ('sin narrativa', 'aviso')              |                 |
| ('videojuegos', 'n')                    | 5               |
| ('videojuegos', 'muertos_24h')          | 80%             |
| ('videojuegos', 'tocaron_2x')           | 50%             |
| ('videojuegos', 'mediana_24h')          | -100%           |
| ('videojuegos', 'regla_$_por_50')       | -19.94          |
| ('videojuegos', 'n_7d')                 | 0               |
| ('videojuegos', '10x_7d')               | -               |
| ('videojuegos', '50x_7d')               | -               |
| ('videojuegos', 'tendencia_$_por_50')   | -               |
| ('videojuegos', 'aviso')                | muestra pequeña |

### Líder de su narrativa frente a seguidores y clones

| papel_en_narrativa   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| líder                |  12 | 100%          | 58%          | -100%         |            -6.7  |      0 | -        | -        | -                    | muestra pequeña |
| seguidor/clon        |  31 | 74%           | 46%          | -100%         |           -20.69 |      0 | -        | -        | -                    |                 |
| sin narrativa        | 251 | 71%           | 38%          | -100%         |           -20.25 |      0 | -        | -        | -                    |                 |

### Calor de la narrativa (tokens con el mismo tema en el escaneo)

| calor   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 1 token |   6 | 100%          | 50%          | -100%         |           -26.4  |      0 | -        | -        | -                    | muestra pequeña |
| 2-3     |   7 | 100%          | 71%          | -100%         |            20.8  |      0 | -        | -        | -                    | muestra pequeña |
| 4-8     |  18 | 72%           | 57%          | -100%         |           -27.84 |      0 | -        | -        | -                    | muestra pequeña |
| 9+      |  12 | 75%           | 27%          | -100%         |           -17.91 |      0 | -        | -        | -                    | muestra pequeña |

### Con catalizador próximo

| con_catalizador   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| no                | 279 | 73%           | 39%          | -100%         |           -19.92 |      0 | -        | -        | -                    |                 |
| sí                |  15 | 73%           | 58%          | -100%         |           -15.79 |      0 | -        | -        | -                    | muestra pequeña |

### Tokens del escaneo que comparten palabra con él

| calor_palabra_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| única            | 123 | 69%           | 40%          | -100%         |           -15.23 |      0 | -        | -        | -                    |         |
| 2 tokens         |  33 | 67%           | 38%          | -100%         |           -25.02 |      0 | -        | -        | -                    |         |
| 3-4              |  34 | 76%           | 41%          | -100%         |           -21.04 |      0 | -        | -        | -                    |         |
| 5+               |  85 | 78%           | 37%          | -100%         |           -26.38 |      0 | -        | -        | -                    |         |

## Carteras inteligentes

Cartera con buen historial: 3 tokens o más comprados antes de detectarlos y al menos el 50% llegaron a 2x. Solo cuenta el historial que se conocía en el momento de cada detección.

### Carteras con buen historial entre los compradores

|                                     | 0      |
|:------------------------------------|:-------|
| ('0', 'n')                          | 210    |
| ('0', 'muertos_24h')                | 73%    |
| ('0', 'tocaron_2x')                 | 44%    |
| ('0', 'mediana_24h')                | -100%  |
| ('0', 'regla_$_por_50')             | -17.68 |
| ('0', 'n_7d')                       | 0      |
| ('0', '10x_7d')                     | -      |
| ('0', '50x_7d')                     | -      |
| ('0', 'tendencia_$_por_50')         | -      |
| ('0', 'aviso')                      |        |
| ('1', 'n')                          | 0      |
| ('2+', 'n')                         | 0      |
| ('sin datos', 'n')                  | 84     |
| ('sin datos', 'muertos_24h')        | 71%    |
| ('sin datos', 'tocaron_2x')         | 30%    |
| ('sin datos', 'mediana_24h')        | -100%  |
| ('sin datos', 'regla_$_por_50')     | -24.88 |
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
| 8pgtJMGLJkGSo2qngKUnDtjEGVVmfJM1onRieJYdbPwb |        4 | 100%         | 75%       | 0%                |
| 9KBFYgtJ7Pomou2G7qwqVk5ATqf6fFT5ADhq8HfrKLDE |        4 | 100%         | 75%       | 0%                |
| CQobSAZab6bok6VU6iwKAhwgXZUEF8oLy8gv6DSW9SU  |        4 | 100%         | 75%       | 0%                |
| CqrwxeCMchk4DWkT4JMw6BYq42f6QNVeGUSpn8fW3rRR |        4 | 100%         | 75%       | 0%                |
| EZ9PDDvSi6JhwBumh3Ufx2A3qAvrhPRx5cVzNANWKWe2 |        4 | 100%         | 75%       | 0%                |
| GFrTtWdMTjWfynEVNmU2vkqSAQBG2RRs8EpZMJbn4wMf |        4 | 100%         | 75%       | 0%                |
| HJF1KEDP6qrRmETVrXLXzojpQ9hBi9MfL9hoVrfiH8hr |        4 | 100%         | 75%       | 0%                |
| Hh4afzozYWN9ud4CGN4fr4iZ6t2xqEfwRY1VXtaoY7A6 |        4 | 100%         | 75%       | 0%                |
| 2VJ72AwxbPaPtnASaKuR2XnwTf9C4SfCs5EsrA1z4Mt2 |        3 | 100%         | 100%      | 0%                |
| 2nZkKfvGJesQuTYeBu1MELyVRXpZSSv7ZGnnD7y2pwSP |        3 | 100%         | 67%       | 0%                |
| 3HDxwa3PNrTDb6vawzSib4xfmLG7x7BioViR9caemw4d |        3 | 100%         | 100%      | 0%                |

## Holders

### % del suministro en los 10 mayores holders

| top10_holders   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15%            |   2 | 100%          | 50%          | -100%         |           -49.85 |      0 | -        | -        | -                    | muestra pequeña |
| 15-25%          |  16 | 88%           | 31%          | -100%         |           -27.53 |      0 | -        | -        | -                    | muestra pequeña |
| 25-35%          |  16 | 44%           | 44%          | -85%          |            -7.04 |      0 | -        | -        | -                    | muestra pequeña |
| 35-50%          |  24 | 58%           | 57%          | -100%         |           -15.27 |      0 | -        | -        | -                    | muestra pequeña |
| >50%            | 109 | 72%           | 45%          | -100%         |           -15.31 |      0 | -        | -        | -                    |                 |

### Número de holders

| num_holders   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <100          |  19 | 47%           | 40%          | -90%          |            -4.03 |      0 | -        | -        | -                    | muestra pequeña |
| 100-300       |  46 | 54%           | 43%          | -100%         |           -14.85 |      0 | -        | -        | -                    |                 |
| 300-1K        |  51 | 80%           | 53%          | -100%         |           -23.08 |      0 | -        | -        | -                    |                 |
| 1K-3K         |  41 | 83%           | 41%          | -100%         |           -20.56 |      0 | -        | -        | -                    |                 |
| 3K+           |  11 | 73%           | 36%          | -100%         |             5.83 |      0 | -        | -        | -                    | muestra pequeña |

### GT Score

| gt_score_   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <30         | 108 | 76%           | 26%          | -100%         |           -29.39 |      0 | -        | -        | -                    |                 |
| 30-45       | 114 | 73%           | 53%          | -100%         |           -12.08 |      0 | -        | -        | -                    |                 |
| 45-60       |  36 | 75%           | 44%          | -100%         |            -8.34 |      0 | -        | -        | -                    |                 |
| 60+         |   1 | 0%            | 0%           | -79%          |           -32.17 |      0 | -        | -        | -                    | muestra pequeña |

## Señales por separado

### Edad al detectarlo

| edad      |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <15 min   | 242 | 74%           | 40%          | -100%         |           -21.52 |      0 | -        | -        | -                    |                 |
| 15-30 min |  11 | 64%           | 56%          | -100%         |            -8.5  |      0 | -        | -        | -                    | muestra pequeña |
| 30-60 min |  11 | 82%           | 30%          | -100%         |           -35.99 |      0 | -        | -        | -                    | muestra pequeña |
| 1-3 h     |  10 | 80%           | 20%          | -100%         |           -20.04 |      0 | -        | -        | -                    | muestra pequeña |
| 3-24 h    |  15 | 47%           | 47%          | -87%          |            13.02 |      0 | -        | -        | -                    | muestra pequeña |

### Capitalización al detectarlo

| cap       |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:----------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| <50K      | 150 | 59%           | 36%          | -100%         |           -19.45 |      0 | -        | -        | -                    |                 |
| 50-150K   |  74 | 91%           | 46%          | -100%         |           -26.61 |      0 | -        | -        | -                    |                 |
| 150-500K  |  43 | 77%           | 40%          | -100%         |           -12.01 |      0 | -        | -        | -                    |                 |
| 500K-1.5M |  17 | 100%          | 53%          | -100%         |           -14.91 |      0 | -        | -        | -                    | muestra pequeña |
| >1.5M     |  10 | 80%           | 30%          | -100%         |           -15.85 |      0 | -        | -        | -                    | muestra pequeña |

### Compradores / vendedores (1 h)

| compradores_vs_vendedores   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:----------------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| <1.2                        |  56 | 64%           | 40%          | -100%         |           -21.59 |      0 | -        | -        | -                    |         |
| 1.2-3                       |  96 | 55%           | 40%          | -100%         |           -18.63 |      0 | -        | -        | -                    |         |
| 3-8                         |  81 | 83%           | 35%          | -100%         |           -25.13 |      0 | -        | -        | -                    |         |
| >8                          |  61 | 95%           | 46%          | -100%         |           -12.87 |      0 | -        | -        | -                    |         |

### Volumen de 1 h / capitalización

| volumen_vs_cap   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:-----------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| <0.5             | 118 | 85%           | 32%          | -100%         |           -30.54 |      0 | -        | -        | -                    |         |
| 0.5-1            |  30 | 70%           | 46%          | -100%         |            -2.75 |      0 | -        | -        | -                    |         |
| 1-3              |  74 | 58%           | 51%          | -100%         |           -10.81 |      0 | -        | -        | -                    |         |
| >3               |  72 | 69%           | 40%          | -100%         |           -18.3  |      0 | -        | -        | -                    |         |

### Peligros de RugCheck

| peligros_rugcheck   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:--------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 0                   | 112 | 54%           | 41%          | -100%         |           -14.75 |      0 | -        | -        | -                    |                 |
| 1                   | 141 | 90%           | 39%          | -100%         |           -21.86 |      0 | -        | -        | -                    |                 |
| 2+                  |  33 | 70%           | 29%          | -100%         |           -27.42 |      0 | -        | -        | -                    |                 |
| sin datos           |   8 | 50%           | 57%          | -85%          |           -28.31 |      0 | -        | -        | -                    | muestra pequeña |

### Liquidez bloqueada (RugCheck): con 0% el creador puede retirarla

| liquidez_bloqueada   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso           |
|:---------------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:----------------|
| 0%                   |  96 | 77%           | 32%          | -100%         |           -26.85 |      0 | -        | -        | -                    |                 |
| parcial              |  81 | 79%           | 50%          | -100%         |           -11.33 |      0 | -        | -        | -                    |                 |
| 100%                 | 109 | 66%           | 37%          | -100%         |           -19.57 |      0 | -        | -        | -                    |                 |
| sin datos            |   8 | 50%           | 57%          | -85%          |           -28.31 |      0 | -        | -        | -                    | muestra pequeña |

### Puntuación (quintiles)

| puntuacion_q   |   n | muertos_24h   | tocaron_2x   | mediana_24h   |   regla_$_por_50 |   n_7d | 10x_7d   | 50x_7d   | tendencia_$_por_50   | aviso   |
|:---------------|----:|:--------------|:-------------|:--------------|-----------------:|-------:|:---------|:---------|:---------------------|:--------|
| Q1 (baja)      |  82 | 76%           | 26%          | -100%         |           -32.19 |      0 | -        | -        | -                    |         |
| Q2             |  73 | 78%           | 42%          | -100%         |           -17.66 |      0 | -        | -        | -                    |         |
| Q3             |  49 | 69%           | 38%          | -100%         |           -11.54 |      0 | -        | -        | -                    |         |
| Q4             |  32 | 59%           | 35%          | -100%         |           -24.42 |      0 | -        | -        | -                    |         |
| Q5 (alta)      |  58 | 72%           | 55%          | -100%         |           -11.11 |      0 | -        | -        | -                    |         |

### DEX

|                                           | 0               |
|:------------------------------------------|:----------------|
| ('letsbonk-fun', 'n')                     | 0               |
| ('meteora', 'n')                          | 0               |
| ('meteora-damm-v2', 'n')                  | 43              |
| ('meteora-damm-v2', 'muertos_24h')        | 86%             |
| ('meteora-damm-v2', 'tocaron_2x')         | 26%             |
| ('meteora-damm-v2', 'mediana_24h')        | -100%           |
| ('meteora-damm-v2', 'regla_$_por_50')     | -34.22          |
| ('meteora-damm-v2', 'n_7d')               | 0               |
| ('meteora-damm-v2', '10x_7d')             | -               |
| ('meteora-damm-v2', '50x_7d')             | -               |
| ('meteora-damm-v2', 'tendencia_$_por_50') | -               |
| ('meteora-damm-v2', 'aviso')              |                 |
| ('meteora-dbc', 'n')                      | 19              |
| ('meteora-dbc', 'muertos_24h')            | 58%             |
| ('meteora-dbc', 'tocaron_2x')             | 21%             |
| ('meteora-dbc', 'mediana_24h')            | -100%           |
| ('meteora-dbc', 'regla_$_por_50')         | -24.79          |
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
| ('pump-fun', 'n')                         | 36              |
| ('pump-fun', 'muertos_24h')               | 25%             |
| ('pump-fun', 'tocaron_2x')                | 42%             |
| ('pump-fun', 'mediana_24h')               | -84%            |
| ('pump-fun', 'regla_$_por_50')            | -13.52          |
| ('pump-fun', 'n_7d')                      | 0               |
| ('pump-fun', '10x_7d')                    | -               |
| ('pump-fun', '50x_7d')                    | -               |
| ('pump-fun', 'tendencia_$_por_50')        | -               |
| ('pump-fun', 'aviso')                     |                 |
| ('pumpswap', 'n')                         | 192             |
| ('pumpswap', 'muertos_24h')               | 82%             |
| ('pumpswap', 'tocaron_2x')                | 43%             |
| ('pumpswap', 'mediana_24h')               | -100%           |
| ('pumpswap', 'regla_$_por_50')            | -18.47          |
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

- 30m: 56% vivos (n=1925)
- 1h: 49% vivos (n=1929)
- 6h: 36% vivos (n=1542)
- 24h: 27% vivos (n=294)

## Supervivientes (tokens de 3 a 120 días que despiertan)

Aún no hay supervivientes (se buscan una vez por hora).

## Últimas alertas del vigía (6 h)

| ts    | simbolo    | narrativa   | prioridad   |   edad_min | mc   |   compradores_m5 |   vendedores_m5 | mint                                         |   x_1h |
|:------|:-----------|:------------|:------------|-----------:|:-----|-----------------:|----------------:|:---------------------------------------------|-------:|
| 22:33 | PUMPTOBER  | cripto      | vetada      |        3   | 46K  |               61 |              25 | D37sbd3C3dqgnQ4TGWtxksMp6gRjmP1C7K3ib9wLpump | nan    |
| 22:33 | PUPI       |             | vetada      |       15   | 29K  |               46 |              32 | DXrrBJMjK3xAV7YvuWAg42aeJHck3GmJmcN78HfDpump | nan    |
| 22:31 | Carla      |             | vetada      |        3.4 | 14K  |               80 |              54 | 3PjwCqfGMR8CXZbcPEbGTSPQGduizdoVz4N1RQmJd8Uv | nan    |
| 22:31 | LMT        | politica    | alta        |        3.3 | 17K  |               84 |              62 | HcjPrHdESBJioSMj3HZbHbH7nUsUdcPyjQrPwYZGpump | nan    |
| 22:31 | epsteinu   |             | vetada      |        3   | 17K  |              148 |              73 | AZ8jS8apTnvge18otci45VrJJQKbL3v8DWJNEJEwpump | nan    |
| 22:29 | Merrylegs  |             | vetada      |        4   | 45K  |              694 |             363 | 9t4nAuTyS6QLStW1vTxMLf7899b9UF1tmmhRCLbApump | nan    |
| 22:27 | KP         |             | vetada      |        2.8 | 83K  |              387 |             108 | CmWxjebLZa3VohM2QhPcN2VVhwkLqnytksqDiaJwKZ3E | nan    |
| 22:27 | BOCK       |             | vetada      |        3.7 | 15K  |               57 |              26 | 95iVDfEQkHtS734cuseXLJ8oXtrP1LV1gA7uyRB7bonk | nan    |
| 22:22 | loria      |             | vetada      |        3.5 | 23K  |               51 |              31 | FK2LDCsv29toyvzBWLsHoo12BY74ErrCpMWwAmbBxMJY | nan    |
| 22:22 | なごやし       |             | vetada      |        3.4 | 29K  |              291 |              73 | HSPehHbS5idzDTfgxz6ZvidREsMFm8dh1YTUmXkUT7xC | nan    |
| 22:22 | IRA        |             | vetada      |        4.8 | 19K  |              105 |              53 | F9XfvHQ4MWiX6FVQKHwBM6q7gaxCqEv5WEhjTC2rpump | nan    |
| 22:18 | NIG        |             | vetada      |        2.6 | 9K   |               92 |              41 | 5xMtGqn7wqtePKzqJqEDaFd9JH7TAtdr9aPM125qpump | nan    |
| 22:18 | FOGLARE    |             | vetada      |        2.2 | 83K  |              425 |             128 | 3RWZTDUyhdksQdtCB4wpZH9Qj2rStinhABJUpheopump | nan    |
| 22:14 | PIMP       |             | vetada      |        3.8 | 44K  |               68 |              40 | DX9mc4dYccjkQ8wkHpLtL1ybvELU2peKGNEqsDzqpump | nan    |
| 22:10 | Coinlator  |             | vetada      |        4.7 | 95K  |              387 |             269 | 7dbey6My9ksrNqcRbfwEkMBT98L1PYqke3FhQcv9pump | nan    |
| 22:03 | SHALAB     |             | alta        |       13.8 | 13K  |               94 |              35 | AoPXbQcvyVnA348eRd88f27twD8sLuUXM1MNxHpnpump | nan    |
| 22:03 | YN         |             | vetada      |        2.9 | 11K  |              245 |             155 | EEfgQNgGzWsh5irrkPTS49CTpPt9nGzKrSTXr8oWjnLy | nan    |
| 21:59 | PATHJAV    |             | vetada      |        4.3 | 83K  |              135 |              36 | 2CJcgwnrKeH9PZXirAkgEBfw7V114zAeLR6GPVyFbonk | nan    |
| 21:59 | SLOTVINE   |             | baja        |        4   | 34K  |              359 |              97 | BHwrSxQX9G6bBd8773mJVRenuPow5USmP98kq453pump | nan    |
| 21:57 | MATRIX     |             | vetada      |        2.8 | 90K  |              524 |             328 | H4gAMBFkfzhn51phWA7M9XCi3duFobaBz89rY38Epump | nan    |
| 21:54 | FINE       |             | vetada      |        2.7 | 17K  |              368 |             100 | 2aMF4mRqtFTjiqPzpWUWkSiYuevPNdX1jxt3B93RR1gT | nan    |
| 21:54 | Loomer     |             | vetada      |        2.5 | 86K  |              970 |             596 | 4JUv66RqP9ed78ajpNpuTbC1rGGgQwBwei4agQtGanTb | nan    |
| 21:48 | Dungkey    |             | vetada      |        3.3 | 76K  |              131 |              36 | 29CWCFZHnrasVuhJWsQmmzAYEAXev9mj73VRq5FMmoon | nan    |
| 21:48 | HIGGSFIELD | ia          | alta        |        3.1 | 13K  |               65 |              42 | EnyHpAEKC3yxczpC9ib2WGUKBCExTFLgB3pQQaGhpump | nan    |
| 21:46 | MOON       | cripto      | vetada      |       11.5 | 21K  |              127 |              38 | Ex17UpeY1VjphPbeLrwrdQSjR39g9QdmksfavERUHeXX | nan    |
| 21:44 | pud        |             | vetada      |        2.2 | 20K  |              655 |             443 | 2nhnxwuAXBAiD5Dcga8AtwKeXPkMA7spEu1CeGUpvHpG | nan    |
| 21:38 | Gtray      |             | vetada      |        3.8 | 81K  |              152 |              46 | FUsWtFFzjG8MAhVNtzv7ohgdBHsgNnpGEu3MGF3bonk  | nan    |
| 21:36 | HAMSTR     |             | vetada      |        5.8 | 11K  |               65 |              43 | 5GFoqsbyNqAZi79iisdQW9bBFLP5yR9BqJA3sx8SEYbt | nan    |
| 21:27 | ENCORE     |             | vetada      |        2.2 | 142K |               90 |              24 | AfZxVCPC9p6nT5uCLBUHEyAxnK7LHEr5UPAfEHb7moon | nan    |
| 21:25 | Novita     |             | alta        |        2.5 | 15K  |              210 |             153 | 2K6byUNcQcXAUHpnNjq2UvjAmUZc8XrA3GQb5MDvtqSu |   0.22 |
| 21:25 | PILLNAMES  |             | vetada      |        2.6 | 11K  |              140 |             102 | 5WTkGBaJCCJk3RLATBJKpD3rzMaQWsFPqXMxAxHFpump |   0.34 |
| 21:25 | dwog       |             | baja        |        2.3 | 9K   |              101 |              71 | 332w4TZ6gYWCpGaVoQ34BKG6QoTzS7s3L6AkjgDQZ6Hd |   0.37 |
| 21:25 | SPORT      |             | baja        |        2.9 | 9K   |              203 |             134 | HjrAxGSsFyKwDL7UyYdEJa7NjU6SsvZm77KRe31ipump |   0.4  |
| 21:23 | TAMA       |             | vetada      |        5   | 15K  |              198 |             128 | sUccrFL84carhdbYXUkTeKkU2eiXT5kY5KDmR6Vpump  |   0.22 |
| 21:21 | UP         |             | vetada      |        2.5 | 14K  |               77 |              54 | BGNLnqbCZrRWcFYewgUe3eoZuTWXdr6SVWF2VVLj1nqi |   0.25 |
| 21:20 | BUTTERS    |             | vetada      |        3.4 | 18K  |              232 |              78 | FxqKHgX8qhYT1qiojpYLDJPuFmpd6uZsVPAfB8nBZckW |   0    |
| 21:20 | Parcel     |             | vetada      |        2.4 | 38K  |              439 |             109 | 47v8RTn4E3vS38BvaumuWFLjkMXEqckUtFfh8GRNpump |   0    |
| 21:20 | BROOD      |             | vetada      |        5.9 | 9K   |              382 |             213 | 4fk4pdVqFFobEkZXHLET5BviRYTC71zCgpepKDJGpump |   0.35 |
| 21:17 | botchain   |             | vetada      |        2.6 | 90K  |              306 |             222 | DjFCHHoJfNGkLZRs6D49CCsneui1vwym5NX8vAiepump |   0    |
| 21:16 | gotchi     |             | vetada      |        2   | 24K  |              131 |              87 | 2DW3jtBhRnrTMeopJyTsLBWfkwFm4NkH8QdR8YS7pump |   0.41 |
| 21:13 | PUTE       | elon        | alta        |        4.1 | 14K  |              185 |             111 | A3zuVVEJFqQS44ZgF1K9y86vFn2LgJBC6BPpqurFpump |   0.36 |
| 21:13 | 天才交易员      |             | vetada      |        9.3 | 49K  |              339 |              63 | 97XZamAKV9s3RtybN7cuk6oD4kW7i5ZS4z99V1n1V7vh |   0.14 |
| 21:09 | PIPS       | cripto      | baja        |        3.1 | 13K  |              188 |             123 | FpPeaDbprm7JHAxghi98czirmRw3aWRbigefbsTKpump |   0.25 |
| 21:07 | SUPERTAKE  |             | vetada      |        3.4 | 81K  |              662 |             368 | WNnpLo7Mjx3mGw5Vu41EyXUd4CCyJyVHoXVkGdMxpLU  |   0.19 |
| 21:01 | REPOING    |             | vetada      |        2.2 | 15K  |              265 |              76 | Cg82oWFeMvjEqGseFriaGfYGfMHmsBykgtCwdp7DkJUX |   0    |
| 20:55 | Daifuku    | animales    | baja        |        2.5 | 9K   |               45 |              30 | GC4fSFRYrsEA47HFYnUraDkx9fXLBuWc6tgoDQMShs1d |   0.4  |
| 20:52 | PENNY      | cripto      | baja        |        2   | 13K  |              331 |             226 | FXoxRGx1jEHVY2VWMrwkSmrUrT8XwpH9ePikQsjapump |   0.29 |
| 20:47 | AI6        |             | vetada      |        2.4 | 314K |             1476 |             771 | DKxXdaMC1so182urvrrnhs6V6fGTrttPS8br6JuEpump |   0.66 |
| 20:44 | AGSHLD     |             | vetada      |        2.9 | 77K  |              111 |              26 | GxQymQf6heKhkJMEWo7vgGjGE4w9P4SufgNAvivYbonk |   0    |
| 20:44 | BRIDGE     |             | vetada      |        2   | 16K  |              297 |             108 | AgtkJoUnsjTJFx6EAgVW9Bfbm9uJoWuJRagSLMifqqPw |   0    |
| 20:42 | meme/acc   | cripto      | alta        |        4   | 11K  |               56 |              33 | GL68bnTmd6upLw1iHDNdvkBRcEb7VKDCz5woH6Jupump |   0.31 |
| 20:40 | LOBBY      |             | baja        |        4   | 11K  |               92 |              51 | 5Z5WvVb6ZV5mwVJu3yoPoFeQFJ9jfERR2iXjg4nXpump |   0.42 |
| 20:37 | KYLE       |             | vetada      |        2.9 | 18K  |              444 |             308 | ALXXnx7apbbnoYe8D8Sgfhac4QEcfQEQuctWeNi82ha8 |   0.29 |
| 20:31 | FROSTY     |             | vetada      |        2.6 | 16K  |              362 |             262 | 6xjdmD4NyXAHEVfXt2s8oPFree4Eci2EThL1oDQypump |   0.17 |
| 20:28 | HOOK       |             | vetada      |        2.4 | 17K  |               59 |              29 | 66UokDvAUWuT8DiX1JxAyisx3uo4nErZYQocXTowQm2G |   0.29 |
| 20:28 | Spend      |             | vetada      |        2.7 | 29K  |              372 |             193 | AMVBZPNtnDSgHoNZYRKjPQHPXFQogrRjTnUfxodopump |   0.15 |
| 20:28 | PICK       |             | vetada      |        2.4 | 28K  |              244 |             149 | EFzc9krvFrc3SbPKrUabiKxtrWNsDbXGUMZt5VtowoFX |   0.12 |
| 20:20 | INUINK     |             | vetada      |        3.3 | 245K |               82 |              20 | 9k7NgXqiJ7tvLtiB6HXdJHnKZZynFz46AB6Eg4Uwpump |   1.29 |
| 20:04 | BridgePad  |             | vetada      |        3.3 | 9K   |              199 |             147 | CQA5Hm11M4p24FkAndoSVnXKGBEnHkRqbfhCDXzBpump |   0.42 |
| 20:02 | Goldbid    |             | vetada      |        3.6 | 73K  |               60 |              17 | 9UjQYT8BTZbgYQVYpLLiSsZ1b4f9UeWfQFBMiV67pump |   0    |
| 20:02 | PAYDAY     |             | vetada      |        2.8 | 35K  |              490 |             137 | BQKQeoxCEwyn4kPyEpJ88NqBaEELG6fLKufRCsvMpump |   0    |
| 20:01 | D/TRUMP    | politica    | vetada      |        2.6 | 30K  |              126 |              86 | BTgenoGircCT23iFM7EzKf9jaf2LFnfh9K6sfpz6pump |   0    |
| 19:56 | Nibs       |             | vetada      |       14   | 9K   |               40 |              21 | DVx9ULhL3e7xQsGagXgkxdZoWTVorYgDbe33ydqyFhyN |   0.8  |
| 19:54 | PIPE/ACC   |             | vetada      |        2.4 | 17K  |              309 |             173 | 3rNV2pmns8nCpx5NjSTwoBxARwQs21BgsdwjxXdfpump |   0    |
| 19:52 | ipfs       |             | vetada      |        2.4 | 31K  |              622 |             363 | DSudLYZaGrxPFhQydNEDELTt4aDC9bhetA4yG8utpump |   0.12 |
| 19:44 | Bronbell   |             | vetada      |        2.7 | 73K  |               99 |              20 | Ad3kZ8FJKiZw7qYL6amZsEq4tscCq5cUvYte4XQAmoon |   0    |
| 19:43 | MOTEPAID   | ia          | alta        |        2.1 | 9K   |              117 |              73 | GZR6rd4rVd2wtKh7cFUTW8KB8Z4wMHro6vg1BCcLpump |   0.28 |
| 19:40 | Entry      |             | vetada      |        3   | 8K   |               62 |              37 | EP4FsbkhEBpAH1mcseYtZXLv6KSNehtPRRixj3fapump |   0.4  |
| 19:40 | 世界末日       |             | vetada      |        4   | 22K  |              209 |              27 | BorCApfhv7enbjDuRxd9CxA1Ucy7b9CZrbcQWJLu3zU9 |   1.88 |
| 19:29 | GAMEZ      |             | baja        |        8.9 | 8K   |               76 |              49 | 5QJfwezvP4jCpBJk2MnPk5EvGx57znhZNzewbpUBuZwJ |   1.72 |
| 19:29 | LUMI       |             | vetada      |        3.8 | 25K  |              140 |              70 | 7dMdLxaSg4JLXdhtG28wx7wGPUKMQbK4NUdAoXePpump |   0.24 |
| 19:28 | WRIT       |             | vetada      |        2.1 | 20K  |              170 |             115 | writr2gAJwSvyPLYtxJJT7jCTqFvmCfxk6Xg6qpq8pq  |   0.2  |
| 19:22 | FROINKCAT  |             | vetada      |       12.5 | 249K |              309 |             105 | 8VxaJHWP9NGYVDeYexGXXbmpmoiVXNvspjqtkbZUpump |   0    |
| 19:15 | fomome     |             | vetada      |        2.2 | 15K  |              192 |              78 | GYMnLJmPTxriy27NPa1GyF6wZkpQpWDGDpxF4dBRkBx  |   0    |
| 19:12 | Tehc       |             | vetada      |        2.3 | 14K  |               95 |              36 | DWvE2aXXTUvCWtrcN4w9eVySP7KNhJbUUz3HsEHXYyW1 |   0    |
| 19:09 | JEETTARA   | cripto      | baja        |        2   | 9K   |              143 |              84 | qyLr3k8yBZz5Lj3aV3uzmkqpGyyBqLyyfJ3ugbvpump  |   1.1  |
| 19:08 | CCAT       |             | vetada      |        2.9 | 86K  |              735 |             451 | H7YEgWhVSWW1HAJomtsBTmSpaBRCoD9V17BvwEyipump |   0    |
| 19:08 | Fo         |             | vetada      |        3.8 | 15K  |              222 |             170 | Bken2392oK2zoS9S4711KR7Mm8m5ynaftZc2SUPxFHjY |   0.46 |
| 19:05 | SARP       |             | vetada      |        3.7 | 245K |               63 |              43 | 53gTSW4WFgrRHgQCtf5CyXgrEBNyNWHobYBAhqQJpump |   1    |
| 19:05 | LEFTCURVE  |             | vetada      |        3.6 | 15K  |              382 |              79 | Hsu6bApBpA71odJDPx3pcpYuyDUN4Pi6cKx7pYGDiSJq |   0    |
| 19:05 | SMUDGE     |             | vetada      |        6.1 | 9K   |              115 |              71 | Af22pLvYvP5Tt8RyqdevgYefVujAa9eLNsa4rpDupump |   0.34 |
| 19:03 | AMC        |             | vetada      |        5.7 | 145K |              492 |              65 | 8LPQXVXwXrpCeSbBiVR7fjKEVb1iSptKvFLRKVKdpump |   1.69 |
| 18:57 | p/xmr      |             | vetada      |        3.4 | 20K  |              357 |             232 | u9uhxHwAn5K5jcuB25QEXBX7XBPArFSTkTQg7F1nuCA  |   0.29 |
| 18:54 | CRACKED    | cripto      | baja        |        2.4 | 9K   |              152 |              68 | KMxqn3LHW8aVBK4rmphAqYcEnBVcYzLqzKJ8vyCpump  |   0.37 |
| 18:51 | Parrot     |             | vetada      |        7.7 | 16K  |               80 |              47 | 7DsTxrXyApdqySsJC59drq9gZfuLWF93Wv5Th5uhpump |   0.21 |
| 18:46 | VOM        |             | vetada      |        2.9 | 11K  |               95 |              63 | 683rxoY4Xtg2Xb7PQidPbv66NuyDyM1bMTQzJTDFpump |   0.36 |
| 18:44 | LIFT       |             | vetada      |        3.5 | 148K |              246 |             115 | 2URzCYAiUypdmbiKBUv2xGLbaRxxNUFryhawJKTamoon |   0    |
| 18:44 | Joe        |             | vetada      |        2.2 | 145K |              178 |              26 | 3i5xUxZm4gYN8gZMSZd3xhMxVS3vdGn33ETjK3g9ADhY |   0    |
| 18:38 | AgentPaid  | ia          | alta        |        6.1 | 13K  |               64 |              39 | EsceEf93ytUGvepAcY71fahRcFE4bZSkz2M2X7dPpump |   0.33 |
| 18:37 | FLY        |             | vetada      |        2.5 | 14K  |              385 |             155 | CJqg1CXuBAETr7mAJuuM7vf7bJsTWmmy4SuzLGsnpump |   0.19 |
| 18:34 | Cluely     |             | baja        |        2.2 | 17K  |               97 |              46 | 8vHheszLT8RHMqTLwuE4BnY7GwT3YPBSW4rFqopmbbiC |   0.33 |
| 18:33 | Streampay  |             | baja        |        6.5 | 12K  |               80 |              58 | Hqi51M7x3bQw8XnNbTQZ6btZAdqvj9w5CFkCjFLqpump |   0.3  |
| 18:29 | Miurafrg   |             | vetada      |        2.2 | 68K  |               75 |              19 | D7gwqhNVvz698hNoWwQQgkJeZ9pS8fwdUzu8om7imoon |   0    |
| 18:29 | PFC        |             | vetada      |        2   | 51K  |              947 |             497 | 5bpnsoZ3HgwGs42Tyd6nEK9s9MCQhhDjVmUveqgbmyJK |   0.11 |
| 18:29 | pill       |             | vetada      |        3.4 | 15K  |              289 |             220 | 77VDJkKqNDZQZTuoZ5cqtKyLP1PyjMonwfcLvdEwhHJq |   0.22 |
| 18:24 | BRAIN      |             | vetada      |        2.7 | 76K  |              394 |             110 | B7HbqBEFJaxWYKUPoMvcTQraxZf9prpr1qJQFr47NVUi |   0    |
| 18:24 | FRENS      |             | vetada      |        2.6 | 11K  |               65 |              39 | 85oYxESrgDPDkEQNt8n65mYfArfSD7LqevYtfSXaSpCV |   0.3  |
| 18:24 | BRAIN      |             | vetada      |        2.5 | 27K  |              213 |              54 | CaWLh6nbv1N1UtwJqkvJvdrZKivKczjxKXqF1u5SNS9p |   0    |
| 18:20 | NALA       | animales    | alta        |        6.1 | 11K  |               75 |              45 | H74zH4LnbC3Juxvzvo6GdfLzrepoG2FXoK6R7fi9pump |   0.46 |
| 18:13 | MTMEI      |             | vetada      |        2.2 | 100K |              507 |             178 | JCDe5ecFTfbLoY1fmVcMZ6G4bMho25xEknzF2M8hpump |   0    |
| 18:09 | Trailer    |             | vetada      |        4.5 | 15K  |               73 |              54 | 6TLpr7zsrg6e6vT8hNuEoUK7xw47NcFHGGXGCAbYSTNK |   0.22 |
| 18:05 | Tiangong   |             | vetada      |        2.7 | 85K  |               96 |              23 | DWvCu4VXyck6hFxVpLyxAmrQ61pXr6K6yd3WmNcAmoon |   0    |
| 18:05 | WATCH      |             | vetada      |        2.6 | 45K  |              200 |              67 | 51GGCsVPuMSkrWkJM4r8wBz6HVPBqVXVpP1unSDgpump |   0    |
| 18:03 | MSUKE/ACC  |             | vetada      |        2.6 | 13K  |              388 |             239 | FatepgpFaFkkLQF7Vo3KKWTN4U3rfdeM8crg5v2Mpump |   0.2  |
| 17:58 | cbADA      |             | vetada      |        2   | 328K |               43 |              25 | cbADAmv9issuPfhFwyQG3xac4DGPd1LDSt1oz7vwJsg  |   0.98 |
| 17:58 | ZELUM      |             | baja        |        2.3 | 9K   |              147 |              83 | GifXoMHe5L3jed2Hqf3vCjMNZgM495fbaWM61Nx2pump |   0.37 |
| 17:58 | Dared      |             | baja        |        3.8 | 9K   |              205 |             134 | CUZ2CR3FMmjxbknvCBknyxTV1RVBMUcwSfmun1j4pump |   0.44 |
| 17:55 | π3.1415926 |             | vetada      |        3.8 | 27K  |              239 |              41 | 2id5EcKDfWBWzw73K3aKZX78hWVDdVQTzRt5XNGVWDZA |   0    |
| 17:44 | Bukas      |             | vetada      |        3.4 | 81K  |              105 |              27 | 7aH6UCFfaybr54aMg11twnugg3b3ZgDjfsAoGZhsBAGS |   0    |
| 17:44 | FORKABLE   |             | baja        |        2.9 | 9K   |              172 |             127 | 3kFEyXL67H6MDx4FUJezhATxuHzfCF7i5bu6C6dwpump |   0.41 |
| 17:42 | SHALOM     |             | vetada      |        2.4 | 14K  |              384 |             295 | 4NHE99TsK5J9Y7VwywjyZtPt2fphr7UiFFSpbpQ5Dfp9 |   0.53 |
| 17:42 | SHALOM     |             | vetada      |        2.5 | 17K  |              290 |             104 | wboyC3dMG9RTvHm1nz3iGPAPsQcptDzGkRgEPikZC59  |   0    |
| 17:36 | ZLM        |             | vetada      |        2.4 | 16K  |              242 |             172 | 4P7DXwmeVj3rg4nZb9ySCfzSJSrEsvFjUYRmymuPpump |   0.24 |
| 17:34 | ETCH       |             | vetada      |        2.1 | 9K   |              206 |             138 | J8fAUfigwW9XHwmEXYwpAp9Yp1JTRYN8qrYE63Npump  |   0.38 |
| 17:33 | PSYCHO     |             | vetada      |        2.7 | 24K  |              740 |             525 | 9hvub8ZabGxr2AiJprc65tP92fe2cx6mhwyUemrYpump |   0.15 |
| 17:32 | Instbot    |             | vetada      |        2.1 | 66K  |               62 |              27 | drqoky7HYTxq32MqzXZEWakLrMizD81HCWSkB7gmoon  |   0    |
| 17:31 | STUPIDINU  |             | vetada      |        6.6 | 73K  |               91 |              46 | CCU9jkaWPRjdsKuTRJa7gJZ22Qf1gXSZQiDV69JNG5W3 |   0.27 |
| 17:22 | ESACLD     |             | vetada      |        2.5 | 75K  |               65 |              24 | 5q7gBEad2FfCqP1SL1PC4dLLoEBUEBPBMc7BJ3m4BAGS |   0    |
| 17:22 | BotBook    | ia          | alta        |        2.6 | 19K  |               94 |              70 | 7n7dS5Dk7YjaKKDzb5e9gPK3Md6mziTLsBA3mJYu6gnV |   2.83 |
| 17:20 | Appshare   |             | vetada      |        2.5 | 47K  |              450 |             252 | GgzBN4bbyHbeh2MaVoHWcKHrjZuUQKUQC2bnamJJpump |   1    |
| 17:09 | TANK       |             | vetada      |        3.4 | 17K  |              404 |             107 | CvQEwhBwTKTa4cWhMPYFWkRzpCDX4H54Qok5CHCZxgEv |   0    |
| 17:07 | anoncoin   |             | vetada      |        3.2 | 11K  |               52 |              25 | 6z92xw4oCWRxo9ynBEfpu5ksxEHVMuYN5VK6Wj7Lpump |   2.78 |
| 17:06 | MUNI       |             | vetada      |        2.2 | 11K  |               83 |              55 | H12pRhhNmRLoPV1PTwbk5KRTLeU3h5w4bgHQQ42pump  |   0.19 |
| 17:06 | Fern       |             | vetada      |        2   | 13K  |              216 |              93 | 2rQXt9syrCKheKtE22RRiQHMZKuP2xXGBc8v9vmwR25m |   0    |
| 17:04 | Vikings    |             | vetada      |        3.4 | 120K |              464 |              64 | 7jjHtz8aGsz9H9KXidDcenJMhczMUi1FoECuHfsRpump |   0    |
| 17:04 | BLEP       |             | baja        |        4.2 | 16K  |               52 |              12 | BSFQ37GMvBNL82PpRV2ALi7zM8FiXdQkAoTXxo6epump |   0.99 |
| 17:03 | Nowzad     |             | vetada      |        2.6 | 20K  |              225 |              99 | Fqwgkjvj3Wv4bdWkXHmER2HX7BfeexPvSKpQp17pPvCD |   0    |
| 17:02 | WIKIMEDIA  |             | vetada      |        2.3 | 12K  |               87 |              15 | AmT4eGZYQsiYP74NGxP9Jm96QGRvDG7qb7yTCBBfo9fB |   0    |
| 17:01 | AIPAD      |             | vetada      |        2.8 | 32K  |              194 |             144 | 8sTosJHKWWXQg8KSniVtusHsBFtGYi1wwY2qagGpump  |   0.1  |
| 17:01 | Ibbot      |             | vetada      |        2.4 | 73K  |               44 |              10 | DeLAbMAoCb8UpsYvbtc6NkcUVwJV9dGDqbmv8r9fbonk |   0    |
| 17:01 | PEARLS     |             | vetada      |        2.5 | 25K  |              168 |              51 | 5UB3nKLQSbs7AtvxRZBt6oW2CbCN7jSMwDRcwX21KA3y |   0    |
| 16:59 | love       |             | vetada      |        2.1 | 9K   |              268 |             206 | 7kcF4nkRSjGv7VbueJ7oh9AwyHDQ1rLZ4YdDoiREtbyz |   0.69 |
| 16:52 | HANDLEIT   |             | vetada      |        2.2 | 70K  |              168 |              23 | MVxpV6jr9HCSvzT2NWYd6VZsKzeGmHsfLx3DmPdBaib  |   0    |
| 16:52 | fatgirls   |             | vetada      |        2.1 | 32K  |              169 |             126 | AiZQ8kDQpTDvx1oS8B2W7Abn5YNX1yp6FMe3Pwxqpump |   0    |
| 16:52 | ROAR       |             | vetada      |        2.4 | 24K  |              296 |              64 | 7H7AV27MPyfpxBGzv348yUx6ujuW4hNcCSVtkAnNE2PH |   1.08 |
| 16:44 | ITCH       |             | vetada      |        6.1 | 43K  |               85 |              64 | 2SWXLespX4sC3rzMnbS4pXyUt6aVqSaZK8X7fg8ppump |   0.86 |
| 16:43 | WAVEBOX    |             | vetada      |        4.4 | 88K  |               81 |              29 | B3iCnfSDQ62XKz59qCWZyid4gcYFcizKj9sisWyBAGS  |   0    |
| 16:43 | HEXUMLITE  | animales    | alta        |        5.9 | 10K  |               50 |              30 | HoyhNp6vs2G6c2zQbnjGGmnGggdo9158v3kk7AQfKZ8k |   0.56 |

## Señales de desplome (cuándo salir)

Fotos de tokens que ya subían un 50% o más: **22329**; seguidas de un desplome (caída a un 40% o menos en 30 min): **476**. Cada fila compara cuántas veces llegó un desplome con la señal activa frente a sin ella: si la señal lo anticipa, el primer % es mucho mayor.

| señal                                        |   fotos_con_señal | desplome_con_señal   | desplome_sin_señal   |
|:---------------------------------------------|------------------:|:---------------------|:---------------------|
| Liquidez < 3% de la capitalización           |             18257 | 1%                   | 9%                   |
| Ticket medio < $30 (volumen de microcompras) |             20184 | 1%                   | 9%                   |
| Más de 8 compradores por vendedor (5 min)    |               125 | 10%                  | 2%                   |
| Subida de más del 100% en 1 h                |              2304 | 13%                  | 1%                   |
| Escalera: 30 min subiendo sin retrocesos     |               251 | 47%                  | 2%                   |
| Aceleración final                            |               306 | 16%                  | 2%                   |
| Más vendedores que compradores (5 min)       |             20009 | 1%                   | 15%                  |
| Ya multiplicó x5 o más desde la detección    |              7671 | 2%                   | 2%                   |

## Palabras calientes (últimas 3 h)

Palabras que aparecen en muchos más tokens nuevos de lo normal: temas que se están calentando aunque no estén en la lista de narrativas.

| palabra   |   tokens_3h |   tokens_24h_previas | veces_lo_normal   | mayor   | mc_mayor   | mint_mayor                                   |
|:----------|------------:|---------------------:|:------------------|:--------|:-----------|:---------------------------------------------|
| hooked    |          11 |                    0 | x88               | HOOKED  | 1751K      | Ehc1F8gmT6LEAcKinBexJzwAoisaAB69JNAhX8XFjymC |
| xmr       |           7 |                    5 | x11               | p/xmr   | 61K        | B5R7Xt9pXBHDAs2jkJ67nM2Wwch1napBsdzMxk56qpJk |
| clones    |           4 |                    0 | x32               | CLONES  | 1112K      | 5RJGBaFrTcTrmu5HuukxHxKeqpmRWf346YxQ1kXGetRs |

## Narrativas activas (últimas 2 h)

| narrativa    |   tokens_nuevos | lider     | mc_lider   | catalizador                                            | mint_lider                                   |
|:-------------|----------------:|:----------|:-----------|:-------------------------------------------------------|:---------------------------------------------|
| ia           |               5 | GEMINI    | 473K       |                                                        | 3UpGi1tqGwEUEt9PcMKBbyake2VjqMn1BpWrNSvMpump |
| cripto       |               5 | MOON      | 21K        |                                                        | Ex17UpeY1VjphPbeLrwrdQSjR39g9QdmksfavERUHeXX |
| animales     |               3 | CATCLONES | 263K       |                                                        | GKokAG4oSBvTjPpKYyktPm5SgdhQ5Y4zJ3AnUEFpump  |
| celebridades |               2 | SPEED     | 58K        |                                                        | HNPHA2mBEgCdn1UV5j8W3Z8yRodsN72DpKpMLhjgvVBY |
| elon         |               1 | PUTE      | 14K        |                                                        | A3zuVVEJFqQS44ZgF1K9y86vFn2LgJBC6BPpqurFpump |
| politica     |               1 | LMT       | 17K        | Elecciones de mitad de mandato en EE. UU. (en 36 días) | HcjPrHdESBJioSMj3HZbHbH7nUsUdcPyjQrPwYZGpump |

## Pasan el filtro en la última hora

Solo son candidatos para vigilar mientras el filtro no demuestre ventaja. Comprueba el contrato en rugcheck.xyz antes de hacer nada.

Ninguno.
