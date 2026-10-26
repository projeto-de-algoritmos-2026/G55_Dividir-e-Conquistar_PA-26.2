# Análise experimental

## Metodologia

O benchmark foi executado com `uv run python scripts/benchmark.py`, a partir de
`backend/`. O script gera eventos sintéticos uniformes dentro da caixa da região
do Japão, usando a semente fixa 42, e os projeta para o plano em quilômetros
antes de iniciar o cronômetro. Para cada tamanho, os mesmos eventos projetados
são entregues às três implementações. Cada algoritmo é executado três vezes; o
CSV registra os três tempos individuais, a média e o número de comparações de
distâncias. O número de comparações é determinístico e validado entre as
repetições.

Os tamanhos medidos foram 100, 250, 500, 1.000, 2.000, 5.000, 10.000, 20.000,
50.000 e 100.000 pontos. A força bruta foi executada somente até n = 2.000; para
tamanhos maiores ela não aparece nos resultados. As operações de geração e
projeção dos pontos ficam fora do trecho cronometrado, que mede a chamada do
algoritmo.

Resultados brutos e parâmetros do ambiente estão em
[`dados/benchmark.csv`](./dados/benchmark.csv) e
[`dados/benchmark_metadados.json`](./dados/benchmark_metadados.json). Os
gráficos SVG são gerados junto com o benchmark:

- [Tempo médio por tamanho](./img/benchmark_tempo.svg)
- [Número de comparações por tamanho](./img/benchmark_comparacoes.svg)

Para repetir o experimento com a configuração padrão, execute o comando acima.
É possível especificar outros tamanhos com `--tamanhos`, alterar a semente com
`--semente` ou o número de execuções com `--repeticoes`. A força bruta continua
limitada a 2.000 pontos.

## Resultados medidos

Execução registrada em Python 3.12.3, Linux x86_64 (kernel 7.0.0-38-generic,
glibc 2.39), com semente 42 e três repetições. Tempos em milissegundos; os
valores foram arredondados para três casas nesta tabela. A tabela completa,
incluindo cada repetição, está no CSV.

| n | Força bruta (ms / comparações) | Closest-Pair O(n log² n) (ms / comparações) | Sort_and_Closest-Pair O(n log n) (ms / comparações) |
|---:|---:|---:|---:|
| 100 | 0,391 / 4.950 | 0,303 / 132 | 0,320 / 132 |
| 500 | 11,427 / 124.750 | 2,260 / 718 | 2,106 / 718 |
| 2.000 | 187,116 / 1.999.000 | 11,221 / 3.032 | 9,915 / 3.032 |
| 5.000 | — | 30,873 / 7.774 | 27,258 / 7.774 |
| 10.000 | — | 71,404 / 15.584 | 63,045 / 15.584 |
| 20.000 | — | 149,932 / 31.833 | 136,836 / 31.833 |
| 50.000 | — | 422,393 / 83.173 | 385,719 / 83.173 |
| 100.000 | — | 912,228 / 166.770 | 889,638 / 166.770 |

O travessão significa que a força bruta não foi executada acima do teto, não que
seu tempo seja zero. Em n = 2.000, a força bruta calculou exatamente
`n(n − 1)/2 = 1.999.000` pares. Em n = 100.000, as versões rápidas terminaram
em menos de um segundo por execução nesta máquina.

## Relação com a complexidade teórica

A curva de comparações da força bruta cresce quadraticamente, como previsto por
`Θ(n²)`. Os dois algoritmos de divisão e conquista fazem bem menos comparações
de distância nos tamanhos medidos. Entre n = 100 e n = 100.000, o número
registrado para cada versão rápida passou de 132 para 166.770.

O contador representa somente avaliações de distância entre pares; ele não
conta comparações de coordenadas, ordenações ou operações de merge. Por isso,
as duas versões rápidas podem apresentar exatamente a mesma quantidade de
comparações de distância nos dados observados, embora tenham recorrências
diferentes: o Closest-Pair reordena a faixa por y a cada chamada e custa
`O(n log² n)`, enquanto Sort_and_Closest-Pair mantém a ordem por y via merge e
custa `O(n log n)`.

Os tempos acompanham o crescimento dos dois algoritmos rápidos, mas não
constituem prova das cotas assintóticas. No maior tamanho medido,
Sort_and_Closest-Pair levou 889,638 ms em média, contra 912,228 ms do
Closest-Pair. A diferença é pequena nesta implementação e nesta plataforma; os
custos constantes, o runtime e a distribuição uniforme dos pontos influenciam
os tempos observados. A força bruta já levou 187,116 ms para n = 2.000, motivo
para excluí-la dos tamanhos maiores.

## Efeito da projeção

O benchmark isola o custo dos algoritmos no plano: os pontos sintéticos são
projetados antes do cronômetro. Logo, as curvas de desempenho não medem o custo
da projeção nem a distorção geodésica.

A projeção azimutal equidistante preserva as distâncias do centro da região,
mas não todas as distâncias entre pontos fora dele. O relatório independente
de validação comparou o par plano com força bruta geodésica em 404 instâncias:
houve 2 divergências (uma subamostra real do Japão, com diferença de 0,000318
km, e uma instância sintética do Chile, com 0,007572 km). Os quatro catálogos
regionais completos tiveram zero divergências nesse ensaio. Esses resultados
são evidência experimental para os conjuntos testados, não uma garantia geral
de que a projeção nunca altere o par vencedor. Os dados e a metodologia estão
em [`dados/validacao_geodesica.md`](./dados/validacao_geodesica.md).
