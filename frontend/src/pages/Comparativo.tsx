import { useEffect, useRef, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import AvisoErro from '../components/AvisoErro'
import Carregando from '../components/Carregando'
import { buscarBenchmark, compararAlgoritmos, ErroApi, listarRegioes } from '../services/api'
import type { Benchmark, Comparativo as DadosComparativo, Regiao } from '../types'

const TAMANHOS_BENCHMARK = [100, 500, 1_000, 2_000, 5_000, 10_000, 20_000]
const CORES: Record<string, string> = {
  forca_bruta: '#c1272d',
  closest_pair_nlog2n: '#d19a22',
  closest_pair_nlogn: '#2e7d4f',
}

function comoErroApi(erro: unknown): ErroApi {
  return erro instanceof ErroApi ? erro : new ErroApi(String(erro), null)
}

function formatarTempo(valor: number | null): string {
  if (valor === null) return '—'
  if (valor < 1) return `${(valor * 1000).toFixed(0)} µs`
  if (valor < 1000) return `${valor.toFixed(2)} ms`
  return `${(valor / 1000).toFixed(2)} s`
}

function formatarInteiro(valor: number): string {
  return new Intl.NumberFormat('pt-BR').format(valor)
}

function nomeAlgoritmo(id: string): string {
  if (id === 'forca_bruta') return 'Força bruta · Θ(n²)'
  if (id === 'closest_pair_nlog2n') return 'Closest-Pair · O(n log² n)'
  return 'Sort_and_Closest-Pair · O(n log n)'
}

interface PontoGrafico {
  n: number
  [chave: string]: number | null
}

function criarSerie(benchmark: Benchmark): PontoGrafico[] {
  const porTamanho = new Map<number, PontoGrafico>()
  for (const medicao of benchmark.medicoes) {
    let ponto = porTamanho.get(medicao.n)
    if (!ponto) {
      ponto = { n: medicao.n }
      porTamanho.set(medicao.n, ponto)
    }
    ponto[`${medicao.algoritmo}_tempo_ms`] = medicao.tempo_medio_ms
    ponto[`${medicao.algoritmo}_comparacoes`] = medicao.comparacoes_medias
  }
  return [...porTamanho.values()].sort((a, b) => a.n - b.n)
}

interface GraficoProps {
  dados: PontoGrafico[]
  metrica: 'tempo_ms' | 'comparacoes'
  titulo: string
}

function Grafico({ dados, metrica, titulo }: GraficoProps) {
  const algoritmos = Object.keys(CORES)
  const formatarValor = (valor: number) =>
    metrica === 'tempo_ms' ? formatarTempo(valor) : formatarInteiro(valor)

  return (
    <section className="min-w-0 rounded-lg border border-grade bg-white p-4">
      <h2 className="font-bold">{titulo}</h2>
      <div className="mt-3 h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dados} margin={{ top: 8, right: 24, bottom: 8, left: 12 }}>
            <CartesianGrid stroke="#dfe6e2" strokeDasharray="3 3" />
            <XAxis
              dataKey="n"
              type="number"
              scale="log"
              domain={['dataMin', 'dataMax']}
              tickFormatter={formatarInteiro}
              name="Pontos"
              allowDuplicatedCategory={false}
            />
            <YAxis
              scale="log"
              domain={['auto', 'auto']}
              tickFormatter={(valor: number) => formatarValor(valor)}
              width={82}
            />
            <Tooltip
              formatter={(valor, nome) => [formatarValor(Number(valor)), nomeAlgoritmo(String(nome))]}
              labelFormatter={(valor) => `${formatarInteiro(Number(valor))} pontos`}
            />
            <Legend formatter={(valor) => nomeAlgoritmo(String(valor))} />
            {algoritmos.map((algoritmo) => (
              <Line
                key={algoritmo}
                type="monotone"
                dataKey={`${algoritmo}_${metrica}`}
                name={algoritmo}
                stroke={CORES[algoritmo]}
                strokeWidth={2.5}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}

export default function Comparativo() {
  const [regioes, setRegioes] = useState<Regiao[]>([])
  const [regiaoId, setRegiaoId] = useState('')
  const [comparativo, setComparativo] = useState<DadosComparativo | null>(null)
  const [benchmark, setBenchmark] = useState<Benchmark | null>(null)
  const [carregandoRegioes, setCarregandoRegioes] = useState(true)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<ErroApi | null>(null)
  const requisicaoAtual = useRef(0)

  useEffect(() => {
    let ativo = true
    void listarRegioes()
      .then((lista) => {
        if (!ativo) return
        setRegioes(lista)
        setRegiaoId(lista[0]?.id ?? '')
      })
      .catch((e: unknown) => {
        if (ativo) setErro(comoErroApi(e))
      })
      .finally(() => {
        if (ativo) setCarregandoRegioes(false)
      })
    return () => {
      ativo = false
      requisicaoAtual.current += 1
    }
  }, [])

  async function executar() {
    if (!regiaoId) return
    const numero = ++requisicaoAtual.current
    setCarregando(true)
    setErro(null)
    try {
      const [resultado, medicoes] = await Promise.all([
        compararAlgoritmos({ regiao_id: regiaoId }),
        buscarBenchmark(TAMANHOS_BENCHMARK, 3, 42),
      ])
      if (numero === requisicaoAtual.current) {
        setComparativo(resultado)
        setBenchmark(medicoes)
      }
    } catch (e) {
      if (numero === requisicaoAtual.current) setErro(comoErroApi(e))
    } finally {
      if (numero === requisicaoAtual.current) setCarregando(false)
    }
  }

  const serie = benchmark ? criarSerie(benchmark) : []

  return (
    <main className="h-full overflow-y-auto">
      <div className="mx-auto max-w-[1500px] space-y-5 p-4 sm:p-6">
        <header>
          <p className="text-xs font-bold uppercase tracking-[.18em] text-epicentro">Medição experimental</p>
          <h1 className="mt-1 text-2xl font-bold">Comparativo de algoritmos</h1>
          <p className="mt-1 max-w-4xl text-sm text-tinta-suave">
            Compare os três algoritmos na mesma região e observe tempo e comparações em instâncias sintéticas reproduzíveis.
          </p>
        </header>

        <section className="flex flex-wrap items-end gap-3 rounded-lg border border-grade bg-white p-4">
          <label className="min-w-56 flex-1 text-sm font-medium">
            Catálogo para comparar
            <select
              value={regiaoId}
              onChange={(e) => setRegiaoId(e.target.value)}
              disabled={carregandoRegioes || carregando || regioes.length === 0}
              className="mt-1 w-full rounded border border-grade bg-white px-3 py-2"
            >
              {regioes.map((regiao) => (
                <option key={regiao.id} value={regiao.id}>
                  {regiao.nome}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => void executar()}
            disabled={!regiaoId || carregando || carregandoRegioes}
            className="rounded bg-tinta px-4 py-2.5 text-sm font-semibold text-papel hover:bg-tinta/90 disabled:opacity-50"
          >
            {carregando ? 'Executando medições...' : 'Executar comparativo'}
          </button>
          <p className="basis-full text-xs text-tinta-suave">
            O benchmark usa 3 repetições, semente 42 e amostras de 100 a 20.000 pontos. A força bruta é omitida acima de 2.000.
          </p>
        </section>

        {erro && <AvisoErro erro={erro} aoFechar={() => setErro(null)} />}
        {carregando && (
          <div className="rounded-lg border border-grade bg-white p-5">
            <Carregando texto="Comparando algoritmos e medindo instâncias sintéticas..." />
          </div>
        )}

        {comparativo && (
          <section className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-lg font-bold">
                  Catálogo: {regioes.find((regiao) => regiao.id === comparativo.regiao_id)?.nome ?? comparativo.regiao_id}
                </h2>
                <p className="text-sm text-tinta-suave">
                  {formatarInteiro(comparativo.n)} eventos comparados com os mesmos dados projetados.
                </p>
              </div>
              <span
                className={`rounded px-3 py-1.5 text-sm font-semibold ${
                  comparativo.mesma_distancia ? 'bg-confirmado/10 text-confirmado' : 'bg-divergente/10 text-divergente'
                }`}
              >
                {comparativo.mesma_distancia ? 'Mesma distância mínima' : 'Verifique os resultados'}
              </span>
            </div>
            <div className="overflow-x-auto rounded-lg border border-grade bg-white">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-papel text-xs uppercase tracking-wide text-tinta-suave">
                  <tr>
                    <th className="px-4 py-3">Algoritmo</th>
                    <th className="px-4 py-3">Tempo</th>
                    <th className="px-4 py-3">Comparações</th>
                    <th className="px-4 py-3">Distância projetada</th>
                    <th className="px-4 py-3">Situação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-grade">
                  {comparativo.itens.map((item) => (
                    <tr key={item.algoritmo}>
                      <td className="px-4 py-3">
                        <div className="font-semibold">{item.nome}</div>
                        <div className="text-xs text-tinta-suave">{item.complexidade}</div>
                      </td>
                      <td className="numeros px-4 py-3">{formatarTempo(item.tempo_ms)}</td>
                      <td className="numeros px-4 py-3">
                        {item.comparacoes === null ? '—' : formatarInteiro(item.comparacoes)}
                      </td>
                      <td className="numeros px-4 py-3">
                        {item.distancia_projetada_km === null
                          ? '—'
                          : `${item.distancia_projetada_km.toFixed(4)} km`}
                      </td>
                      <td className="px-4 py-3">
                        {item.executado ? (
                          <span className="text-confirmado">Executado</span>
                        ) : (
                          <span className="text-tinta-suave" title={item.motivo ?? undefined}>
                            Não executado · limite
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {benchmark && (
          <>
            <section className="rounded-lg border border-grade bg-white p-4 text-sm text-tinta-suave">
              Benchmark sintético da região do Japão, semente {benchmark.semente}, média de{' '}
              {benchmark.repeticoes} repetições. A força bruta é medida até n ={' '}
              {formatarInteiro(benchmark.teto_forca_bruta)}; cada algoritmo rápido usa os mesmos pontos para cada n.
            </section>
            <div className="grid gap-4 xl:grid-cols-2">
              <Grafico dados={serie} metrica="tempo_ms" titulo="Tempo médio por quantidade de pontos" />
              <Grafico dados={serie} metrica="comparacoes" titulo="Comparações por quantidade de pontos" />
            </div>
            <section className="rounded-lg border border-grade bg-white p-4 text-sm leading-relaxed text-tinta-suave">
              <h2 className="font-bold text-tinta">Leitura das curvas</h2>
              <p className="mt-1">
                A força bruta cresce quadraticamente. O Closest-Pair reordena a faixa em cada nível e tem custo
                O(n log² n); o Sort_and_Closest-Pair mantém os pontos ordenados por y e tem custo O(n log n).
                As curvas refletem medições desta máquina e não substituem a análise assintótica.
              </p>
            </section>
          </>
        )}
      </div>
    </main>
  )
}
