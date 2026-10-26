// Espelho dos schemas da API (backend/app/models/schemas.py)

export interface RespostaSaude {
  status: string
  servico: string
}

export interface Caixa {
  lat_min: number
  lat_max: number
  lon_min: number
  lon_max: number
}

export interface Coordenada {
  latitude: number
  longitude: number
}

export interface Regiao {
  id: string
  nome: string
  importado: boolean
  caixa: Caixa
  centro: Coordenada
  total_eventos: number
  inicio: string | null
  fim: string | null
  magnitude_min: number | null
  magnitude_max: number | null
  profundidade_max: number | null
}

export interface Evento {
  id: string
  data: string
  latitude: number
  longitude: number
  /** km */
  profundidade: number
  magnitude: number
  local: string
  /** coordenadas projetadas, km */
  x: number
  y: number
}

export interface ListaEventos {
  regiao_id: string
  total: number
  eventos: Evento[]
}

export interface Filtros {
  inicio?: string
  fim?: string
  magnitude_min?: number
  profundidade_max?: number
}

export interface RequisicaoCalculo extends Filtros {
  regiao_id: string
}

export type StatusVerificacao = 'confirmado' | 'nao_verificado' | 'divergente'

export interface VerificacaoGeodesica {
  status: StatusVerificacao
  limite_eventos: number
  par_geodesico: string[] | null
  distancia_geodesica_minima_km: number | null
  diferenca_km: number | null
}

export interface ParMaisProximo {
  regiao_id: string
  algoritmo: string
  n: number
  a: Evento
  b: Evento
  distancia_projetada_km: number
  distancia_geodesica_km: number
  comparacoes: number
  tempo_ms: number
  verificacao_geodesica: VerificacaoGeodesica
}

export interface ImportacaoResposta {
  regiao: Regiao
  mensagem: string
}

/** Erro de validação de requisição: {campo, mensagem} */
export interface ErroCampo {
  campo: string
  mensagem: string
}

/** Erro de linha/coluna de um CSV importado */
export interface ErroLinhaImportacao {
  linha: number
  coluna: string
  mensagem: string
}

// Próximas fases: passo a passo, comparativo, validação e benchmark

export interface ResultadoResumo {
  par: string[]
  distancia_projetada_km: number
  distancia_geodesica_km: number
  comparacoes: number
}

export interface ComparacaoFaixa {
  a: string
  b: string
  distancia: number
}

export interface PassoRecursao {
  profundidade: number
  tipo: 'base' | 'combinacao'
  ids: string[]
  reta_l: number | null
  delta_esquerdo: number | null
  delta_direito: number | null
  delta: number
  faixa: string[]
  comparacoes_faixa: ComparacaoFaixa[]
  par: string[]
  distancia: number
}

export interface RequisicaoPassoAPasso extends RequisicaoCalculo {
  tamanho_amostra?: number
  semente?: number
}

export interface PassoAPasso {
  regiao_id: string
  n_filtrados: number
  n_amostra: number
  semente: number
  eventos: Evento[]
  passos: PassoRecursao[]
  resultado: ResultadoResumo
}

export interface ItemComparativo {
  algoritmo: string
  nome: string
  complexidade: string
  executado: boolean
  motivo: string | null
  tempo_ms: number | null
  comparacoes: number | null
  distancia_projetada_km: number | null
  par: string[] | null
}

export interface Comparativo {
  regiao_id: string
  n: number
  itens: ItemComparativo[]
  mesma_distancia: boolean
}

export interface FalhaValidacao {
  semente: number
  distribuicao: string
  n: number
  algoritmo: string
  esperado: number
  obtido: number
}

export interface Validacao {
  instancias: number
  aprovadas: number
  falhas: FalhaValidacao[]
  tempo_ms: number
}

export interface MedicaoBenchmark {
  n: number
  algoritmo: string
  repeticoes: number
  tempos_ms: number[]
  tempo_medio_ms: number
  comparacoes_medias: number
}

export interface Benchmark {
  repeticoes: number
  semente: number
  teto_forca_bruta: number
  medicoes: MedicaoBenchmark[]
}
