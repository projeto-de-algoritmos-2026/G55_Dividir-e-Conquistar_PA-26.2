import type {
  ErroCampo,
  ErroLinhaImportacao,
  Filtros,
  ImportacaoResposta,
  ListaEventos,
  ParMaisProximo,
  PassoAPasso,
  Regiao,
  RequisicaoCalculo,
  RequisicaoPassoAPasso,
  RespostaSaude,
} from '../types'

const MENSAGEM_SEM_SERVIDOR =
  'Não foi possível falar com o servidor. Confira se o backend está rodando na porta 8000.'

/** Erro da API já traduzido para exibir ao usuário. */
export class ErroApi extends Error {
  readonly status: number | null
  readonly campos: ErroCampo[]
  readonly linhas: ErroLinhaImportacao[]

  constructor(
    mensagem: string,
    status: number | null,
    campos: ErroCampo[] = [],
    linhas: ErroLinhaImportacao[] = [],
  ) {
    super(mensagem)
    this.name = 'ErroApi'
    this.status = status
    this.campos = campos
    this.linhas = linhas
  }
}

async function lerErro(resposta: Response): Promise<ErroApi> {
  const corpo: unknown = await resposta.json().catch(() => null)
  if (corpo && typeof corpo === 'object' && 'detail' in corpo) {
    const { detail, erros } = corpo as { detail: unknown; erros?: ErroLinhaImportacao[] }
    if (Array.isArray(detail)) {
      const campos = detail as ErroCampo[]
      const mensagem = campos.map((c) => `${c.campo.split('.').pop()}: ${c.mensagem}`).join('; ')
      return new ErroApi(mensagem, resposta.status, campos)
    }
    return new ErroApi(String(detail), resposta.status, [], erros ?? [])
  }
  // Sem JSON: o proxy do Vite responde assim quando o backend está fora do ar
  if (resposta.status >= 500) return new ErroApi(MENSAGEM_SEM_SERVIDOR, resposta.status)
  return new ErroApi(`Erro ${resposta.status} ao falar com o servidor`, resposta.status)
}

async function requisitar<T>(caminho: string, opcoes?: RequestInit): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(`/api${caminho}`, opcoes)
  } catch {
    throw new ErroApi(MENSAGEM_SEM_SERVIDOR, null)
  }
  if (!resposta.ok) throw await lerErro(resposta)
  return resposta.json() as Promise<T>
}

function postarJson<T>(caminho: string, corpo: unknown): Promise<T> {
  return requisitar<T>(caminho, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  })
}

/** Remove campos vazios para não mandar filtros que o usuário não preencheu. */
function semVazios<T extends object>(objeto: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(objeto).filter(([, valor]) => valor !== undefined && valor !== ''),
  ) as Partial<T>
}

export function buscarSaude(): Promise<RespostaSaude> {
  return requisitar<RespostaSaude>('/saude')
}

export function listarRegioes(): Promise<Regiao[]> {
  return requisitar<Regiao[]>('/regioes')
}

export function listarEventos(regiaoId: string, filtros: Filtros): Promise<ListaEventos> {
  const consulta = new URLSearchParams(
    Object.entries(semVazios(filtros)).map(([chave, valor]) => [chave, String(valor)]),
  )
  const sufixo = consulta.size ? `?${consulta}` : ''
  return requisitar<ListaEventos>(`/regioes/${encodeURIComponent(regiaoId)}/eventos${sufixo}`)
}

export function importarCatalogo(arquivo: File): Promise<ImportacaoResposta> {
  const formulario = new FormData()
  formulario.append('arquivo', arquivo)
  return requisitar<ImportacaoResposta>('/catalogos/importar', { method: 'POST', body: formulario })
}

export function buscarParMaisProximo(requisicao: RequisicaoCalculo): Promise<ParMaisProximo> {
  return postarJson<ParMaisProximo>('/par-mais-proximo', semVazios(requisicao))
}

export function buscarPassoAPasso(requisicao: RequisicaoPassoAPasso): Promise<PassoAPasso> {
  return postarJson<PassoAPasso>('/passo-a-passo', semVazios(requisicao))
}
