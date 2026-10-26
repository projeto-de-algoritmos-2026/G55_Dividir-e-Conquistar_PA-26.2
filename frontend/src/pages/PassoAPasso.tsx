import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import AvisoErro from '../components/AvisoErro'
import Carregando from '../components/Carregando'
import {
  buscarPassoAPasso,
  ErroApi,
  listarRegioes,
} from '../services/api'
import type { PassoAPasso as DadosPassoAPasso, PassoRecursao, Regiao } from '../types'

const LARGURA = 960
const ALTURA = 560
const MARGEM = 52
const VELOCIDADES = [
  { rotulo: '0,5×', milissegundos: 1400 },
  { rotulo: '1×', milissegundos: 850 },
  { rotulo: '1,5×', milissegundos: 560 },
  { rotulo: '2×', milissegundos: 400 },
]

type TipoEtapa = 'base' | 'divisao' | 'faixa' | 'comparacao' | 'resultado'

interface Etapa {
  passo: number
  tipo: TipoEtapa
  comparacao?: number
}

interface Filhos {
  esquerda: PassoRecursao | null
  direita: PassoRecursao | null
}

function criarEtapas(passos: PassoRecursao[]): Etapa[] {
  const etapas: Etapa[] = []
  passos.forEach((passo, indice) => {
    if (passo.tipo === 'base') {
      etapas.push({ passo: indice, tipo: 'base' })
      return
    }
    etapas.push({ passo: indice, tipo: 'divisao' }, { passo: indice, tipo: 'faixa' })
    passo.comparacoes_faixa.forEach((_, comparacao) => {
      etapas.push({ passo: indice, tipo: 'comparacao', comparacao })
    })
    etapas.push({ passo: indice, tipo: 'resultado' })
  })
  return etapas
}

function chaveIds(ids: string[]): string {
  return ids.join('\u0000')
}

function distancia(valor: number): string {
  return `${valor.toFixed(2)} km`
}

function textoEtapa(etapa: Etapa, passo: PassoRecursao): { titulo: string; explicacao: string } {
  switch (etapa.tipo) {
    case 'base':
      return {
        titulo: 'Caso base: comparar diretamente',
        explicacao:
          'Com até três eventos, o algoritmo calcula a distância de cada par e guarda o mais próximo deste pequeno grupo.',
      }
    case 'divisao':
      return {
        titulo: 'Dividir e combinar os lados',
        explicacao:
          'A reta L separa os pontos por x. O melhor par de cada lado já foi encontrado; δ é a menor dessas duas distâncias.',
      }
    case 'faixa':
      return {
        titulo: 'Examinar a faixa de largura 2δ',
        explicacao:
          'Um par que cruza a reta só pode melhorar a resposta se os dois pontos estiverem a menos de δ de L. A faixa fica ordenada por y.',
      }
    case 'comparacao': {
      const comparacao = etapa.comparacao ?? 0
      const par = passo.comparacoes_faixa[comparacao]
      return {
        titulo: `Comparação ${comparacao + 1} de ${passo.comparacoes_faixa.length}`,
        explicacao: par
          ? `Na ordem por y, o algoritmo compara ${par.a} com ${par.b}: ${distancia(par.distancia)}. São considerados apenas os próximos 7 vizinhos.`
          : 'O algoritmo compara pontos próximos na ordem por y.',
      }
    }
    case 'resultado':
      return {
        titulo: 'Melhor par deste grupo',
        explicacao: `Depois da verificação da faixa, o melhor par é ${passo.par[0]} e ${passo.par[1]}, separados por ${distancia(passo.distancia)}.`,
      }
  }
}

function obterFilhos(passo: PassoRecursao, passos: PassoRecursao[]): Filhos {
  const meio = Math.floor(passo.ids.length / 2)
  const porIds = new Map(passos.map((item) => [chaveIds(item.ids), item]))
  return {
    esquerda: porIds.get(chaveIds(passo.ids.slice(0, meio))) ?? null,
    direita: porIds.get(chaveIds(passo.ids.slice(meio))) ?? null,
  }
}

function comoErroApi(erro: unknown): ErroApi {
  return erro instanceof ErroApi ? erro : new ErroApi(String(erro), null)
}

interface PropsDiagrama {
  dados: DadosPassoAPasso
  etapa: Etapa
  passo: PassoRecursao
  filhos: Filhos
}

function Diagrama({ dados, etapa, passo, filhos }: PropsDiagrama) {
  const coordenadas = useMemo(() => {
    const xs = dados.eventos.map((evento) => evento.x)
    const ys = dados.eventos.map((evento) => evento.y)
    const minimoX = Math.min(...xs)
    const maximoX = Math.max(...xs)
    const minimoY = Math.min(...ys)
    const maximoY = Math.max(...ys)
    const escalaX = (LARGURA - MARGEM * 2) / (maximoX - minimoX || 1)
    const escalaY = (ALTURA - MARGEM * 2) / (maximoY - minimoY || 1)
    const porId = new Map<string, { x: number; y: number }>()
    for (const evento of dados.eventos) {
      porId.set(evento.id, {
        x: MARGEM + (evento.x - minimoX) * escalaX,
        y: ALTURA - MARGEM - (evento.y - minimoY) * escalaY,
      })
    }
    return { porId, escalaX, escalaY, minimoX, maximoX, minimoY, maximoY }
  }, [dados.eventos])

  const ativos = new Set(passo.ids)
  const faixa = etapa.tipo === 'faixa' || etapa.tipo === 'comparacao' || etapa.tipo === 'resultado'
  const comparacoesConcluidas =
    etapa.tipo === 'comparacao' ? (etapa.comparacao ?? 0) + 1 : etapa.tipo === 'resultado' ? passo.comparacoes_faixa.length : 0
  const comparacaoAtual =
    etapa.tipo === 'comparacao' ? passo.comparacoes_faixa[etapa.comparacao ?? 0] : null
  const [idA, idB] =
    etapa.tipo === 'resultado' || etapa.tipo === 'base' ? passo.par : [null, null]
  const xReta = passo.reta_l === null
    ? null
    : MARGEM + (passo.reta_l - coordenadas.minimoX) * coordenadas.escalaX
  const meiaFaixa = passo.delta * coordenadas.escalaX
  const faixaEsquerda = xReta === null ? 0 : Math.max(MARGEM, xReta - meiaFaixa)
  const faixaDireita = xReta === null ? 0 : Math.min(LARGURA - MARGEM, xReta + meiaFaixa)
  const idFaixa = new Map(passo.faixa.map((id, indice) => [id, indice + 1]))

  function desenharPar(ids: string[], classe: string, chave: string) {
    if (ids.length < 2) return null
    const a = coordenadas.porId.get(ids[0])
    const b = coordenadas.porId.get(ids[1])
    if (!a || !b) return null
    return (
      <g key={chave} className={classe}>
        <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} strokeWidth="3" />
        <circle cx={(a.x + b.x) / 2} cy={(a.y + b.y) / 2} r="5" />
      </g>
    )
  }

  return (
    <div className="min-w-0">
      <div className="overflow-hidden rounded-lg border border-grade bg-white p-2 sm:p-4">
        <svg
          viewBox={`0 0 ${LARGURA} ${ALTURA}`}
          role="img"
          aria-labelledby="titulo-diagrama descricao-diagrama"
          className="h-auto max-h-[min(62vh,620px)] w-full"
        >
          <title id="titulo-diagrama">Recursão do algoritmo Closest Pair</title>
          <desc id="descricao-diagrama">
            Pontos em coordenadas projetadas em quilômetros, reta de divisão, faixa de busca e comparações reais do algoritmo.
          </desc>
          <defs>
            <pattern id="grade-diagrama" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#e2e8e5" strokeWidth="1" />
            </pattern>
          </defs>
          <rect x="0" y="0" width={LARGURA} height={ALTURA} fill="url(#grade-diagrama)" />

          {faixa && xReta !== null && (
            <rect
              x={faixaEsquerda}
              y={MARGEM}
              width={faixaDireita - faixaEsquerda}
              height={ALTURA - MARGEM * 2}
              fill="#f5c451"
              fillOpacity=".24"
            />
          )}

          {xReta !== null && (
            <g>
              <line
                x1={xReta}
                y1={MARGEM}
                x2={xReta}
                y2={ALTURA - MARGEM}
                stroke="#c1272d"
                strokeWidth="2"
                strokeDasharray="8 6"
              />
              <text x={xReta + 7} y={MARGEM + 17} fill="#a51e24" fontSize="14" fontWeight="700">
                L = {passo.reta_l?.toFixed(2)} km
              </text>
            </g>
          )}

          {desenharPar(filhos.esquerda?.par ?? [], 'par-esquerdo', 'par-esquerdo')}
          {desenharPar(filhos.direita?.par ?? [], 'par-direito', 'par-direito')}
          {passo.comparacoes_faixa.slice(0, comparacoesConcluidas).map((comparacao, indice) =>
            desenharPar([comparacao.a, comparacao.b], 'par-comparado', `comparacao-${indice}`),
          )}
          {comparacaoAtual &&
            desenharPar([comparacaoAtual.a, comparacaoAtual.b], 'par-atual', 'par-atual')}
          {idA && idB && desenharPar([idA, idB], 'par-resultado', 'par-resultado')}

          {dados.eventos.map((evento) => {
            const ponto = coordenadas.porId.get(evento.id)
            if (!ponto) return null
            const dentro = ativos.has(evento.id)
            const numero = faixa ? idFaixa.get(evento.id) : undefined
            return (
              <g key={evento.id} opacity={dentro ? 1 : 0.18}>
                <title>
                  {evento.id} — x: {evento.x.toFixed(2)} km, y: {evento.y.toFixed(2)} km
                </title>
                <circle
                  cx={ponto.x}
                  cy={ponto.y}
                  r={numero ? 7 : dentro ? 5 : 3.5}
                  fill={numero ? '#f5c451' : dentro ? '#3d6a86' : '#9aa8a1'}
                  stroke={numero ? '#8a5a00' : 'white'}
                  strokeWidth="1.5"
                />
                {numero && (
                  <text
                    x={ponto.x}
                    y={ponto.y + 3.5}
                    textAnchor="middle"
                    fontSize="9"
                    fontWeight="700"
                    fill="#382500"
                  >
                    {numero}
                  </text>
                )}
              </g>
            )
          })}

          <line x1={MARGEM} y1={ALTURA - MARGEM} x2={LARGURA - MARGEM} y2={ALTURA - MARGEM} stroke="#52616b" />
          <line x1={MARGEM} y1={MARGEM} x2={MARGEM} y2={ALTURA - MARGEM} stroke="#52616b" />
          <text x={LARGURA - MARGEM} y={ALTURA - 15} textAnchor="end" fill="#4f5f6a" fontSize="13">
            x projetado ({coordenadas.minimoX.toFixed(0)} a {coordenadas.maximoX.toFixed(0)} km)
          </text>
          <text
            x="17"
            y={ALTURA / 2}
            transform={`rotate(-90 17 ${ALTURA / 2})`}
            textAnchor="middle"
            fill="#4f5f6a"
            fontSize="13"
          >
            y projetado ({coordenadas.minimoY.toFixed(0)} a {coordenadas.maximoY.toFixed(0)} km)
          </text>
        </svg>
      </div>
      <style>{`
        .par-esquerdo line, .par-direito line { stroke: #2e7d4f; }
        .par-esquerdo circle, .par-direito circle { fill: #2e7d4f; }
        .par-direito { opacity: .7; }
        .par-comparado line { stroke: #d19a22; stroke-width: 1.5; stroke-dasharray: 4 4; }
        .par-comparado circle { fill: #d19a22; }
        .par-atual line, .par-resultado line { stroke: #c1272d; stroke-width: 3.5; }
        .par-atual circle, .par-resultado circle { fill: #c1272d; }
      `}</style>
      {faixa && (
        <p className="mt-2 text-xs text-tinta-suave">
          A faixa sombreada representa |x − L| &lt; δ. A numeração sobre os pontos segue a ordem crescente de y.
        </p>
      )}
      {etapa.tipo === 'comparacao' && comparacaoAtual && (
        <p className="mt-1 text-sm font-semibold text-registro">
          Comparando {comparacaoAtual.a} ↔ {comparacaoAtual.b}: {distancia(comparacaoAtual.distancia)}
        </p>
      )}
    </div>
  )
}

export default function PassoAPasso() {
  const [regioes, setRegioes] = useState<Regiao[]>([])
  const [regiaoId, setRegiaoId] = useState('')
  const [tamanho, setTamanho] = useState(30)
  const [semente, setSemente] = useState(42)
  const [dados, setDados] = useState<DadosPassoAPasso | null>(null)
  const [indice, setIndice] = useState(0)
  const [velocidade, setVelocidade] = useState(VELOCIDADES[1].milissegundos)
  const [reproduzindo, setReproduzindo] = useState(false)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<ErroApi | null>(null)
  const requisicaoAtual = useRef(0)

  const etapas = useMemo(() => (dados ? criarEtapas(dados.passos) : []), [dados])
  const etapa = etapas[indice]
  const passo = etapa && dados ? dados.passos[etapa.passo] : null
  const filhos = useMemo(
    () => (passo && dados ? obterFilhos(passo, dados.passos) : { esquerda: null, direita: null }),
    [passo, dados],
  )
  const descricao = etapa && passo ? textoEtapa(etapa, passo) : null

  const carregar = useCallback(async (id: string, n: number, seed: number) => {
    const numero = ++requisicaoAtual.current
    setCarregando(true)
    setErro(null)
    setReproduzindo(false)
    setDados(null)
    try {
      const resposta = await buscarPassoAPasso({
        regiao_id: id,
        tamanho_amostra: n,
        semente: seed,
      })
      if (numero === requisicaoAtual.current) {
        setDados(resposta)
        setIndice(0)
      }
    } catch (e) {
      if (numero === requisicaoAtual.current) setErro(comoErroApi(e))
    } finally {
      if (numero === requisicaoAtual.current) setCarregando(false)
    }
  }, [])

  useEffect(() => {
    let ativo = true
    void listarRegioes()
      .then((lista) => {
        if (!ativo) return
        setRegioes(lista)
        const inicial = lista[0]?.id ?? ''
        setRegiaoId(inicial)
        if (inicial) void carregar(inicial, 30, 42)
      })
      .catch((e: unknown) => {
        if (ativo) setErro(comoErroApi(e))
      })
    return () => {
      ativo = false
      requisicaoAtual.current += 1
    }
  }, [carregar])

  useEffect(() => {
    if (!reproduzindo) return
    const temporizador = window.setInterval(() => {
      if (indice >= etapas.length - 1) {
        setReproduzindo(false)
      } else {
        setIndice(indice + 1)
      }
    }, velocidade)
    return () => window.clearInterval(temporizador)
  }, [reproduzindo, velocidade, etapas.length, indice])

  function gerar(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (regiaoId) void carregar(regiaoId, tamanho, semente)
  }

  function avancar() {
    setReproduzindo(false)
    setIndice((atual) => Math.min(atual + 1, etapas.length - 1))
  }

  function voltar() {
    setReproduzindo(false)
    setIndice((atual) => Math.max(atual - 1, 0))
  }

  function reiniciar() {
    setReproduzindo(false)
    setIndice(0)
  }

  function reproduzirOuPausar() {
    if (reproduzindo) {
      setReproduzindo(false)
      return
    }
    if (indice >= etapas.length - 1) setIndice(0)
    setReproduzindo(true)
  }

  return (
    <main className="h-full overflow-y-auto">
      <div className="mx-auto max-w-[1600px] p-4 sm:p-6">
        <header className="mb-4">
          <p className="text-xs font-bold uppercase tracking-[.18em] text-epicentro">Modo didático</p>
          <h1 className="mt-1 text-2xl font-bold">Passo a Passo</h1>
          <p className="mt-1 max-w-3xl text-sm text-tinta-suave">
            Acompanhe a execução real do Closest Pair sobre uma amostra de terremotos projetados em quilômetros.
          </p>
        </header>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
          <section className="min-w-0 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-grade bg-white px-4 py-3 text-sm">
              {dados ? (
                <>
                  <span className="font-semibold">{regioes.find((regiao) => regiao.id === dados.regiao_id)?.nome ?? dados.regiao_id}</span>
                  <span>{dados.n_amostra} pontos na amostra de {dados.n_filtrados} eventos</span>
                  <span>{dados.passos.length} chamadas recursivas</span>
                </>
              ) : (
                <span>Escolha uma região e gere uma demonstração.</span>
              )}
            </div>

            {erro && <AvisoErro erro={erro} aoFechar={() => setErro(null)} />}
            {carregando ? (
              <div className="rounded-lg border border-grade bg-white p-8 text-center">
                <Carregando texto="Executando o algoritmo e registrando a recursão..." />
              </div>
            ) : dados && etapa && passo && descricao ? (
              <>
                <Diagrama dados={dados} etapa={etapa} passo={passo} filhos={filhos} />

                <section className="rounded-lg border border-grade bg-white p-4" aria-live="polite">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-epicentro">
                        Etapa {indice + 1} de {etapas.length} · profundidade {passo.profundidade}
                      </p>
                      <h2 className="mt-1 text-lg font-bold">{descricao.titulo}</h2>
                      <p className="mt-1 max-w-4xl text-sm leading-relaxed text-tinta-suave">
                        {descricao.explicacao}
                      </p>
                    </div>
                    <span className="rounded bg-papel px-3 py-1.5 text-sm font-semibold">
                      {`δ = ${distancia(passo.delta)}`}
                    </span>
                  </div>

                  {passo.tipo === 'combinacao' && (
                    <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-sm">
                      <span className="text-confirmado">
                        Lado esquerdo:{' '}
                        {filhos.esquerda
                          ? `${filhos.esquerda.par[0]} ↔ ${filhos.esquerda.par[1]} (${distancia(filhos.esquerda.distancia)})`
                          : '—'}
                      </span>
                      <span className="text-confirmado">
                        Lado direito:{' '}
                        {filhos.direita
                          ? `${filhos.direita.par[0]} ↔ ${filhos.direita.par[1]} (${distancia(filhos.direita.distancia)})`
                          : '—'}
                      </span>
                      <span className="text-tinta-suave">
                        {comparacoesConcluidas(etapa, passo)} de {passo.comparacoes_faixa.length} comparações na faixa
                      </span>
                    </div>
                  )}

                  <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-grade pt-3">
                    <button
                      type="button"
                      onClick={reiniciar}
                      disabled={indice === 0 && !reproduzindo}
                      className="rounded border border-grade px-3 py-2 text-sm font-medium hover:bg-papel disabled:opacity-40"
                    >
                      Reiniciar
                    </button>
                    <button
                      type="button"
                      onClick={voltar}
                      disabled={indice === 0}
                      className="rounded border border-grade px-3 py-2 text-sm font-medium hover:bg-papel disabled:opacity-40"
                    >
                      ← Voltar
                    </button>
                    <button
                      type="button"
                      onClick={reproduzirOuPausar}
                      disabled={etapas.length < 2}
                      className="rounded bg-tinta px-4 py-2 text-sm font-semibold text-papel hover:bg-tinta/90 disabled:opacity-40"
                    >
                      {reproduzindo ? 'Pausar' : indice === etapas.length - 1 ? 'Reproduzir de novo' : 'Reproduzir'}
                    </button>
                    <button
                      type="button"
                      onClick={avancar}
                      disabled={indice >= etapas.length - 1}
                      className="rounded border border-grade px-3 py-2 text-sm font-medium hover:bg-papel disabled:opacity-40"
                    >
                      Avançar →
                    </button>
                    <label className="ml-auto flex items-center gap-2 text-sm text-tinta-suave">
                      Velocidade
                      <select
                        value={velocidade}
                        onChange={(e) => setVelocidade(Number(e.target.value))}
                        className="rounded border border-grade bg-white px-2 py-2 text-tinta"
                      >
                        {VELOCIDADES.map((opcao) => (
                          <option key={opcao.milissegundos} value={opcao.milissegundos}>
                            {opcao.rotulo}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                </section>
              </>
            ) : (
              <div className="rounded-lg border border-grade bg-white p-8 text-center text-sm text-tinta-suave">
                A demonstração será exibida aqui.
              </div>
            )}
          </section>

          <aside className="space-y-4">
            <form onSubmit={gerar} className="space-y-3 rounded-lg border border-grade bg-white p-4">
              <h2 className="font-bold">Configurar amostra</h2>
              <label className="block text-sm font-medium">
                Região
                <select
                  value={regiaoId}
                  onChange={(e) => setRegiaoId(e.target.value)}
                  className="mt-1 w-full rounded border border-grade bg-white px-3 py-2"
                  disabled={carregando || regioes.length === 0}
                >
                  {regioes.map((regiao) => (
                    <option key={regiao.id} value={regiao.id}>
                      {regiao.nome}
                    </option>
                  ))}
                </select>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className="text-sm font-medium">
                  Pontos (2–200)
                  <input
                    type="number"
                    min={2}
                    max={200}
                    value={tamanho}
                    onChange={(e) => setTamanho(Number(e.target.value))}
                    className="mt-1 w-full rounded border border-grade bg-white px-3 py-2"
                    disabled={carregando}
                  />
                </label>
                <label className="text-sm font-medium">
                  Semente
                  <input
                    type="number"
                    value={semente}
                    onChange={(e) => setSemente(Number(e.target.value))}
                    className="mt-1 w-full rounded border border-grade bg-white px-3 py-2"
                    disabled={carregando}
                  />
                </label>
              </div>
              <button
                type="submit"
                disabled={!regiaoId || carregando || !Number.isInteger(tamanho) || tamanho < 2 || tamanho > 200}
                className="w-full rounded bg-epicentro px-3 py-2.5 text-sm font-semibold text-white hover:bg-epicentro/90 disabled:opacity-50"
              >
                {carregando ? 'Gerando...' : 'Gerar demonstração'}
              </button>
              <p className="text-xs leading-relaxed text-tinta-suave">
                A amostra é sorteada dos eventos reais da região. A mesma semente reproduz a mesma execução.
              </p>
            </form>

            <section className="rounded-lg border border-grade bg-white p-4">
              <h2 className="font-bold">Legenda</h2>
              <ul className="mt-3 space-y-2.5 text-sm text-tinta-suave">
                <li className="flex gap-2"><span className="text-epicentro">●</span><span>Pontos do grupo atual; pontos apagados pertencem a outras chamadas da recursão.</span></li>
                <li className="flex gap-2"><span className="text-registro">┆</span><span>Reta L: divide os eventos por coordenada x.</span></li>
                <li className="flex gap-2"><span className="text-confirmado">━</span><span>Pares vencedores encontrados nos lados esquerdo e direito.</span></li>
                <li className="flex gap-2"><span className="text-amber-700">■</span><span>Faixa sombreada de largura 2δ; números indicam a ordem por y.</span></li>
                <li className="flex gap-2"><span className="text-registro">━</span><span>Linha vermelha: comparação atual ou melhor par do grupo.</span></li>
              </ul>
              {dados && passo && (
                <div className="mt-4 border-t border-grade pt-3 text-sm">
                  <p className="font-semibold">Pontos da faixa em ordem de y</p>
                  {passo.faixa.length === 0 ? (
                    <p className="mt-1 text-xs text-tinta-suave">Esta chamada não tem pontos na faixa.</p>
                  ) : (
                    <ol className="mt-2 max-h-52 space-y-1 overflow-y-auto pr-1 text-xs">
                      {passo.faixa.map((id, indiceFaixa) => {
                        const evento = dados.eventos.find((item) => item.id === id)
                        return (
                          <li key={id} className="numeros flex justify-between gap-2">
                            <span className="shrink-0 font-semibold">{indiceFaixa + 1}. {id}</span>
                            {evento && (
                              <span className="text-right text-tinta-suave">
                                x {evento.x.toFixed(2)}, y {evento.y.toFixed(2)} km
                              </span>
                            )}
                          </li>
                        )
                      })}
                    </ol>
                  )}
                </div>
              )}
            </section>

            {dados && passo && (
              <details className="rounded-lg border border-grade bg-white p-4 text-sm">
                <summary className="cursor-pointer font-bold">
                  Coordenadas projetadas dos {passo.ids.length} pontos deste grupo
                </summary>
                <ol className="mt-3 max-h-56 space-y-1 overflow-y-auto pr-1 text-xs">
                  {passo.ids.map((id, indicePonto) => {
                    const evento = dados.eventos.find((item) => item.id === id)
                    return (
                      <li key={id} className="numeros flex justify-between gap-2">
                        <span className="shrink-0 font-semibold">{indicePonto + 1}. {id}</span>
                        <span className="text-right text-tinta-suave">
                          {evento ? `x ${evento.x.toFixed(2)}, y ${evento.y.toFixed(2)} km` : ''}
                        </span>
                      </li>
                    )
                  })}
                </ol>
              </details>
            )}

            {dados && (
              <section className="rounded-lg border border-grade bg-white p-4 text-sm">
                <h2 className="font-bold">Resultado final da amostra</h2>
                <p className="mt-2">
                  <span className="font-semibold">{dados.resultado.par[0]}</span>
                  {' ↔ '}
                  <span className="font-semibold">{dados.resultado.par[1]}</span>
                </p>
                <p className="mt-1 text-tinta-suave">
                  Distância projetada: {distancia(dados.resultado.distancia_projetada_km)}
                </p>
                <p className="mt-1 text-xs text-tinta-suave">
                  A execução completa realizou {dados.resultado.comparacoes} comparações.
                </p>
              </section>
            )}
          </aside>
        </div>
      </div>
    </main>
  )
}

function comparacoesConcluidas(etapa: Etapa, passo: PassoRecursao): number {
  if (etapa.tipo === 'comparacao') return (etapa.comparacao ?? 0) + 1
  return etapa.tipo === 'resultado' ? passo.comparacoes_faixa.length : 0
}
