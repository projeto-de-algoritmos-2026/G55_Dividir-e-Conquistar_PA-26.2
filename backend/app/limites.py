"""Limites da API, reunidos para ficarem visíveis e fáceis de ajustar."""

# Força bruta Haversine automática no par mais próximo (~1,4 s com 3.000 eventos)
LIMITE_VERIFICACAO_GEODESICA = 3_000

# Amostra do modo didático
TAMANHO_PADRAO_PASSO_A_PASSO = 30
LIMITE_PASSO_A_PASSO = 200

# Força bruta no comparativo (Califórnia completa, 7.714 eventos, leva ~2 s)
LIMITE_FORCA_BRUTA_COMPARATIVO = 10_000

# Importação de catálogo próprio
LIMITE_IMPORTACAO_BYTES = 10 * 1024 * 1024
LIMITE_CATALOGOS_IMPORTADOS = 10
LIMITE_ERROS_EXIBIDOS = 50
# Escopo regional: caixa maior que isso fica fora da hipótese do plano
LIMITE_EXTENSAO_GRAUS = 45.0

# Validação aleatória
LIMITE_INSTANCIAS_VALIDACAO = 200
LIMITE_N_VALIDACAO = 500

# Benchmark ao vivo (n grandes ficam no scripts/benchmark.py)
LIMITE_N_BENCHMARK = 20_000
LIMITE_FORCA_BRUTA_BENCHMARK = 2_000
LIMITE_REPETICOES_BENCHMARK = 5
