# SismoPar

**Conteúdo da Disciplina:** Dividir e Conquistar<br>

## Alunos

| Foto | Nome | Matrícula |
| :---: | :--- | ---: |
| ![Gabriel Lima](https://github.com/gabriel-lima258.png?size=100) | **Gabriel Lima** | 222037610 |
| ![Mateus Bastos](https://github.com/MateuSansete.png?size=100) | **Mateus Bastos** | 211062240 |

---

## Sobre

**SismoPar** é um analisador de proximidade entre terremotos que responde, sobre dados sísmicos reais, a uma pergunta simples: entre milhares de abalos registrados em uma região, quais dois aconteceram mais perto um do outro?

Epicentros muito próximos costumam indicar réplicas de um mesmo evento ou segmentos ativos de uma mesma falha geológica. Com catálogos de dezenas de milhares de eventos, comparar todos os pares custa Θ(n²) e se torna lento. O projeto aplica o algoritmo de divisão e conquista para o **par de pontos mais próximos** (*Closest Pair*), que resolve o mesmo problema em O(n log n).

O projeto responde a três perguntas distintas:

1. **Qual o par de terremotos mais próximo em uma região e período?**
   Resolvido pelo *Sort_and_Closest-Pair* em O(n log n), com verificação contra força bruta.

2. **Quanto a divisão e conquista ganha na prática?**
   Três versões do mesmo problema rodam sobre os mesmos dados: força bruta Θ(n²), divisão e conquista com reordenação da faixa O(n log² n) e divisão e conquista com merge por y O(n log n). O confronto empírico entre elas é o núcleo analítico do trabalho.

3. **Como o algoritmo chega na resposta?**
   Um modo didático reproduz a recursão passo a passo: a reta divisória L, as soluções de cada lado, o valor de δ, a faixa de largura 2δ e as comparações com no máximo 7 vizinhos.

### O diferencial: a Terra não é um plano

O algoritmo de Closest Pair assume pontos no plano euclidiano. Terremotos, porém, são registrados em latitude e longitude, sobre uma superfície praticamente esférica. Um grau de longitude mede cerca de 111 km no Equador e encolhe à medida que se aproxima dos polos. Aplicar o algoritmo diretamente sobre graus produz respostas erradas.

O SismoPar trata a geometria em duas camadas, e a diferença entre elas é parte da análise:

- **Projeção local:** os eventos de uma região são projetados para um plano em quilômetros pela projeção azimutal equidistante, centrada no centro da região. As distâncias a partir do centro são preservadas exatamente, e a distorção entre os demais pontos é pequena em escala regional. O algoritmo roda sobre essas coordenadas planas e é **comprovadamente ótimo no plano projetado**.
- **Validação geodésica:** o par encontrado tem sua distância recalculada pela fórmula de Haversine, e, para instâncias de tamanho moderado, uma força bruta geodésica verifica se a projeção alterou a resposta.

Toda resposta da aplicação informa a distância projetada, a distância geodésica e o status da verificação (`confirmado`, `nao_verificado` ou `divergente`). Mostrar até onde vale a hipótese do plano, em vez de ignorá-la, é parte do trabalho. As demonstrações formais estão em [`docs/provas_formais.md`](./docs/provas_formais.md).

**Escopo:** o projeto trabalha com regiões de alcance regional. A análise global, que exigiria o problema em três dimensões sobre a esfera unitária, fica registrada como trabalho futuro.

### Público e aplicação

A saída é um mapa interativo com os epicentros da região, o par mais próximo destacado e um painel com magnitude, profundidade, data e distância entre os dois eventos. O modo didático transforma a execução do algoritmo em uma animação legível **para quem não conhece o algoritmo**.

---

## Funcionalidades e Algoritmos

### Algoritmos implementados

| # | Algoritmo | Estratégia | Complexidade | Papel no projeto | Status |
|:-:|---|---|:-:|---|:-:|
| 1 | **Mergesort** | Divisão e conquista | O(n log n) | Ordenação inicial por x e base do merge por y | Concluído |
| 2 | **Força bruta (plano)** | Comparação de todos os pares | Θ(n²) | Verificador e linha de base do benchmark | Concluído |
| 3 | **Closest-Pair** | Divisão e conquista, reordenando a faixa por y a cada chamada | O(n log² n) | Versão intermediária para comparação | Concluído |
| 4 | **Sort_and_Closest-Pair** | Divisão e conquista, cada chamada devolve os pontos ordenados por y | O(n log n) | Algoritmo principal | Concluído |
| 5 | **Força bruta geodésica** | Comparação de todos os pares com Haversine | Θ(n²) | Validação do efeito da projeção | Concluído |

#### 1. Mergesort

Implementação própria, sem uso das funções de ordenação da linguagem nos algoritmos principais. Ordena os eventos por x uma única vez antes da recursão e fornece a rotina de merge usada pelo algoritmo 4.

#### 2. Força bruta (plano)

Calcula a distância entre todos os n(n − 1)/2 pares de pontos projetados. Serve como oráculo nos testes e como linha de base no benchmark.

#### 3. Closest-Pair (O(n log² n))

Divide os pontos por uma reta vertical L, resolve cada metade recursivamente, define δ como a menor das duas distâncias, descarta os pontos a mais de δ de L, ordena a faixa restante por y e compara cada ponto com os próximos 7. A reordenação da faixa em cada chamada gera a recorrência T(n) = 2T(n/2) + O(n log n).

#### 4. Sort_and_Closest-Pair (O(n log n))

Mesma estratégia, mas cada chamada recursiva devolve também a lista de pontos ordenada por y. A ordenação da faixa vira um merge linear de duas listas já ordenadas, e a recorrência cai para T(n) = 2T(n/2) + O(n). A corretude depende do lema de empacotamento: na faixa 2δ, dois pontos separados por 7 ou mais posições na ordem por y distam pelo menos δ.

#### 5. Força bruta geodésica

Repete a força bruta usando a distância de Haversine sobre latitude e longitude originais. Permite medir, em dados reais, se a projeção plana mudou o par vencedor.

### Funcionalidades da aplicação

- [x] Download de catálogos do USGS por região, período e magnitude mínima
- [x] Catálogos de exemplo versionados no repositório para uso offline
- [x] Importação de catálogo próprio em CSV (formato USGS), com validação por linha e coluna
- [x] Filtros por período, magnitude mínima e profundidade máxima
- [x] Projeção azimutal equidistante por região, com distâncias em quilômetros
- [x] Tratamento de empates em x e de epicentros coincidentes
- [x] Mapa interativo com todos os epicentros e o par mais próximo destacado
- [x] Painel do par com magnitude, profundidade, data, local e distância
- [x] Indicador de verificação geodésica em todo resultado
- [ ] Modo didático com animação passo a passo da recursão (reta L, δ, faixa 2δ, comparações)
- [ ] Painel comparativo entre força bruta, O(n log² n) e O(n log n), com tempo e número de comparações
- [ ] Gráfico de tempo de execução por tamanho de entrada
- [x] Verificador contra força bruta em instâncias aleatórias
- [x] Gerador de instâncias sintéticas para teste de desempenho

---

## Tecnologias Utilizadas

### Frontend

| Tecnologia | Uso |
|---|---|
| **React 19** | Construção da interface |
| **TypeScript** | Tipagem estática dos modelos de evento e de passo da recursão |
| **Vite** | Bundler e servidor de desenvolvimento |
| **Tailwind CSS 4** | Estilização dos painéis e componentes |
| **React Router** | Navegação entre as telas |
| **Leaflet** e **React Leaflet** | Mapa interativo com base do OpenStreetMap |
| **SVG** | Animação do modo didático em coordenadas projetadas |
| **Recharts** | Gráficos do benchmark e do comparativo |

### Backend

| Tecnologia | Uso |
|---|---|
| **Python 3.12** | Linguagem dos algoritmos |
| **uv** | Gerenciamento do Python, do ambiente virtual e das dependências |
| **FastAPI** | API REST que expõe os endpoints de cálculo |
| **Pydantic** | Validação dos payloads de entrada |
| **pyproj** | Projeção azimutal equidistante |
| **httpx** | Download dos catálogos do USGS |
| **pytest** | Testes unitários e verificação contra força bruta |
| **Uvicorn** | Servidor ASGI |

### Infraestrutura

| Tecnologia | Uso |
|---|---|
| **Docker** e **Docker Compose** | Execução de backend e frontend com um único comando |

### Fonte dos dados

Catálogo ComCat do **USGS** (*United States Geological Survey*), consultado pelo FDSN Event Web Service, público e sem chave de acesso. O serviço limita cada consulta a 20.000 eventos, por isso o script de download divide períodos longos em janelas menores.

---

## Estrutura do Projeto

```
G55_DividirConquistar_PA-26.2/
├── backend/
│   ├── app/
│   │   ├── algorithms/     # mergesort, força bruta e closest pair (um arquivo por algoritmo)
│   │   ├── geo/            # projeção azimutal equidistante e Haversine
│   │   ├── models/         # Evento, ParMaisProximo, PassoRecursao e schemas da API
│   │   ├── services/       # carregamento de catálogos, filtros e comparador
│   │   ├── routers/        # endpoints FastAPI
│   │   ├── data/           # catálogos USGS em CSV por região
│   │   └── main.py
│   ├── tests/
│   ├── scripts/            # download do USGS, gerador sintético, benchmark e validação
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api.ts
│   │   ├── types/index.ts
│   │   └── utils/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── provas_formais.md
│   ├── analise_experimental.md
│   ├── dados/              # dados brutos que sustentam a análise experimental
│   └── img/                # capturas de tela
├── docker-compose.yml
└── README.md
```

---

## Instalação e Execução

### 1. Clonando o Repositório

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G55_DividirConquistar_PA-26.2.git
cd G55_DividirConquistar_PA-26.2
```

### 2. Rodando com Docker (recomendado)

Pré-requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/), ou Docker Engine com o plugin Compose v2.

```bash
docker compose up --build
```

Quando os dois serviços estiverem no ar:

| Endereço | Conteúdo |
|---|---|
| `http://localhost:5173` | Interface do SismoPar |
| `http://localhost:8000/docs` | Documentação interativa da API |

Para parar, use `Ctrl+C` ou, em outro terminal, `docker compose down`.

**Testes e scripts dentro do container:**

```bash
# Suíte completa de testes, incluindo a verificação contra força bruta
docker compose run --rm backend uv run pytest

# Download de um catálogo do USGS
docker compose run --rm backend uv run python scripts/baixar_catalogo.py --regiao japao --inicio 2024-01-01 --fim 2024-12-31 --mag-min 2.5

# Benchmark das três versões do algoritmo
docker compose run --rm backend uv run python scripts/benchmark.py
```

### 3. Rodando sem Docker

Pré-requisitos: [uv](https://docs.astral.sh/uv/), que instala o Python 3.12 automaticamente, e Node.js 20.19 ou superior.

**Backend**, em um terminal:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

**Frontend**, em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

**Testes e scripts sem Docker**, a partir de `backend/`:

```bash
uv run pytest
uv run python scripts/baixar_catalogo.py --regiao japao --inicio 2024-01-01 --fim 2024-12-31 --mag-min 2.5
uv run python scripts/benchmark.py
```

---

## Uso

1. Acesse `http://localhost:5173` com o backend em execução.
2. Selecione a região na lista ou carregue seu próprio catálogo em CSV.
3. Ajuste os filtros de período, magnitude mínima e profundidade máxima.
4. Clique em **"Encontrar Par Mais Próximo"**. A aplicação irá:
   - Projetar os epicentros para o plano da região.
   - Executar o Sort_and_Closest-Pair e destacar o par no mapa.
   - Exibir as distâncias projetada e geodésica e o status da verificação.
5. Use a aba **"Passo a Passo"** para assistir à recursão animada sobre uma amostra dos eventos.
6. Use a aba **"Comparativo"** para comparar força bruta, O(n log² n) e O(n log n) sobre os mesmos dados.

### API

Todas as rotas estão documentadas, com exemplos prontos para testar, em `http://localhost:8000/docs`. Erros de validação voltam em português, com o campo e a mensagem.

| Método e rota | O que responde |
|---|---|
| `GET /api/saude` | Confirma que a API está no ar |
| `GET /api/regioes` | Regiões e catálogos importados, com caixa, centro, período e número de eventos |
| `GET /api/regioes/{id}/eventos` | Eventos da região, com filtros opcionais na consulta (`inicio`, `fim`, `magnitude_min`, `profundidade_max`) |
| `POST /api/catalogos/importar` | Importa um CSV próprio (campo `arquivo`, formato USGS); fica só em memória e devolve um id |
| `POST /api/par-mais-proximo` | Par mais próximo (O(n log n)), distâncias projetada e geodésica, comparações, tempo e verificação geodésica |
| `POST /api/passo-a-passo` | Registro da recursão sobre uma amostra (`tamanho_amostra`, `semente`), para o modo didático |
| `POST /api/comparativo` | As três versões sobre os mesmos eventos, com tempo e número de comparações |
| `POST /api/validar` | As duas versões de divisão e conquista contra a força bruta em instâncias aleatórias |
| `GET /api/benchmark` | Tempo médio e comparações para n crescente (`tamanhos`, `repeticoes`, `semente`) |

As rotas `POST` de cálculo recebem o mesmo corpo. Só `regiao_id` é obrigatório; as datas são inclusivas. O id devolvido pela importação vale como `regiao_id`.

```json
{
  "regiao_id": "turquia",
  "inicio": "2023-01-01",
  "fim": "2023-12-31",
  "magnitude_min": 4.0,
  "profundidade_max": 700
}
```

O campo `verificacao_geodesica.status` do par mais próximo vale `confirmado` (a força bruta com Haversine achou a mesma distância mínima na esfera), `divergente` (a projeção mudou o par) ou `nao_verificado` (acima do limite de tamanho).

**Limites** (em [`backend/app/limites.py`](./backend/app/limites.py)):

| Limite | Valor |
|---|--:|
| Verificação geodésica automática | 3.000 eventos |
| Amostra do passo a passo | 200 eventos (padrão 30) |
| Força bruta no comparativo | 10.000 eventos |
| Benchmark ao vivo | n ≤ 20.000, força bruta até 2.000, até 5 repetições |
| Importação | 10 MB por arquivo, 10 catálogos em memória, caixa de até 45° |

---

## Análise Experimental

Pendente.

---

## Screenshots

Pendente.

---

## Apresentação

Pendente.

---

## Referências

- KLEINBERG, Jon; TARDOS, Éva. *Algorithm Design*. Boston: Pearson, 2006. Capítulo 5: Divide and Conquer.
- CORMEN, Thomas H. et al. *Introduction to Algorithms*. 4. ed. Cambridge: MIT Press, 2022. Capítulo 33: Computational Geometry.
- SHAMOS, Michael Ian; HOEY, Dan. Closest-point problems. *16th Annual Symposium on Foundations of Computer Science*, 1975.
- SNYDER, John P. *Map Projections: A Working Manual*. U.S. Geological Survey Professional Paper 1395, 1987.
- U.S. GEOLOGICAL SURVEY. *API Documentation: Earthquake Catalog*. Disponível em: https://earthquake.usgs.gov/fdsnws/event/1/.
- Material da disciplina Projeto de Algoritmos, FGA/UnB, 2026.2.

---

## Licença

Projeto acadêmico desenvolvido para a disciplina Projeto de Algoritmos da Universidade de Brasília, campus Gama.
