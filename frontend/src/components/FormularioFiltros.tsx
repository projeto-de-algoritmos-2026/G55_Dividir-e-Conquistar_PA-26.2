import type { Regiao } from '../types'
import type { ValoresFiltros } from '../utils/filtros'

interface Props {
  valores: ValoresFiltros
  regiao: Regiao | undefined
  aoMudar: (valores: ValoresFiltros) => void
}

const CAMPO = 'w-full rounded border border-grade bg-white px-2.5 py-1.5 text-sm numeros'

export default function FormularioFiltros({ valores, regiao, aoMudar }: Props) {
  const mudar = (campo: keyof ValoresFiltros) => (e: React.ChangeEvent<HTMLInputElement>) =>
    aoMudar({ ...valores, [campo]: e.target.value })

  return (
    <fieldset className="space-y-3">
      <legend className="mb-2 text-sm font-semibold">Filtros</legend>
      <div className="grid grid-cols-2 gap-3">
        <label className="space-y-1 text-xs text-tinta-suave">
          <span>De</span>
          <input
            type="date"
            value={valores.inicio}
            min={regiao?.inicio ?? undefined}
            max={regiao?.fim ?? undefined}
            onChange={mudar('inicio')}
            className={CAMPO}
          />
        </label>
        <label className="space-y-1 text-xs text-tinta-suave">
          <span>Até</span>
          <input
            type="date"
            value={valores.fim}
            min={regiao?.inicio ?? undefined}
            max={regiao?.fim ?? undefined}
            onChange={mudar('fim')}
            className={CAMPO}
          />
        </label>
        <label className="space-y-1 text-xs text-tinta-suave">
          <span>Magnitude mínima</span>
          <input
            type="number"
            step="0.1"
            min="0"
            max="10"
            inputMode="decimal"
            placeholder={regiao?.magnitude_min?.toString() ?? '2.5'}
            value={valores.magnitude_min}
            onChange={mudar('magnitude_min')}
            className={CAMPO}
          />
        </label>
        <label className="space-y-1 text-xs text-tinta-suave">
          <span>Profundidade máxima (km)</span>
          <input
            type="number"
            step="1"
            min="0"
            inputMode="decimal"
            placeholder={regiao?.profundidade_max ? Math.ceil(regiao.profundidade_max).toString() : '700'}
            value={valores.profundidade_max}
            onChange={mudar('profundidade_max')}
            className={CAMPO}
          />
        </label>
      </div>
      <p className="text-xs text-tinta-suave">Campos vazios não filtram. Datas em UTC, inclusivas.</p>
    </fieldset>
  )
}
