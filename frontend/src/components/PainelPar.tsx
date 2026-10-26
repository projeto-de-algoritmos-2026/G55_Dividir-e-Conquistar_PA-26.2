import type { Evento, ParMaisProximo } from '../types'
import {
  formatarData,
  formatarDistancia,
  formatarIntervalo,
  formatarInteiro,
  formatarNumero,
  formatarTempo,
} from '../utils/formatacao'
import SeloVerificacao from './SeloVerificacao'

interface Props {
  par: ParMaisProximo
}

function CartaoEvento({ evento, rotulo }: { evento: Evento; rotulo: string }) {
  return (
    <article className="rounded border border-grade bg-white px-3 py-2.5">
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="text-sm font-semibold">{rotulo}</h3>
        <span className="numeros text-lg font-bold text-registro">M {formatarNumero(evento.magnitude, 1)}</span>
      </div>
      <p className="mt-0.5 text-sm leading-snug">{evento.local || 'Local não informado'}</p>
      <dl className="numeros mt-1.5 grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 text-xs text-tinta-suave">
        <dt>Data</dt>
        <dd className="text-tinta">{formatarData(evento.data)}</dd>
        <dt>Profundidade</dt>
        <dd className="text-tinta">{formatarNumero(evento.profundidade, 1)} km</dd>
        <dt>Id USGS</dt>
        <dd className="text-tinta">{evento.id}</dd>
      </dl>
    </article>
  )
}

export default function PainelPar({ par }: Props) {
  const metricas: [string, string][] = [
    ['Distância geodésica', formatarDistancia(par.distancia_geodesica_km)],
    ['Distância no plano', formatarDistancia(par.distancia_projetada_km)],
    ['Intervalo entre os dois', formatarIntervalo(par.a.data, par.b.data)],
    ['Eventos analisados', formatarInteiro(par.n)],
    ['Comparações de distância', formatarInteiro(par.comparacoes)],
    ['Tempo do algoritmo', formatarTempo(par.tempo_ms)],
  ]

  return (
    <section aria-label="Par mais próximo" className="space-y-3">
      <div>
        <h2 className="titulo text-lg font-bold">Par mais próximo</h2>
        <p className="numeros text-3xl font-bold tracking-tight text-registro">
          {formatarDistancia(par.distancia_geodesica_km)}
        </p>
        {par.distancia_geodesica_km === 0 && (
          <p className="text-xs text-tinta-suave">Os dois epicentros têm exatamente as mesmas coordenadas.</p>
        )}
      </div>

      <SeloVerificacao verificacao={par.verificacao_geodesica} />

      <div className="space-y-2">
        <CartaoEvento evento={par.a} rotulo="Evento A" />
        <CartaoEvento evento={par.b} rotulo="Evento B" />
      </div>

      <dl className="numeros grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
        {metricas.map(([rotulo, valor]) => (
          <div key={rotulo}>
            <dt className="text-tinta-suave">{rotulo}</dt>
            <dd className="text-sm font-semibold">{valor}</dd>
          </div>
        ))}
      </dl>
      <p className="text-xs text-tinta-suave">Calculado pelo {par.algoritmo}, O(n log n).</p>
    </section>
  )
}
