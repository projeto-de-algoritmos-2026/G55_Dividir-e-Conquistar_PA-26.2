import { useRef } from 'react'
import type { Regiao } from '../types'
import { formatarInteiro } from '../utils/formatacao'

interface Props {
  regioes: Regiao[]
  regiaoId: string
  aoEscolher: (id: string) => void
  aoImportar: (arquivo: File) => void
  importando: boolean
}

export default function SeletorRegiao({ regioes, regiaoId, aoEscolher, aoImportar, importando }: Props) {
  const entrada = useRef<HTMLInputElement>(null)
  const predefinidas = regioes.filter((r) => !r.importado)
  const importadas = regioes.filter((r) => r.importado)
  const rotulo = (r: Regiao) => `${r.nome} (${formatarInteiro(r.total_eventos)} eventos)`

  return (
    <div className="space-y-2">
      <label htmlFor="regiao" className="block text-sm font-semibold">
        Região
      </label>
      <select
        id="regiao"
        value={regiaoId}
        onChange={(e) => aoEscolher(e.target.value)}
        className="w-full rounded border border-grade bg-white px-3 py-2 text-sm"
      >
        <optgroup label="Catálogos do USGS, 2020 a 2024">
          {predefinidas.map((r) => (
            <option key={r.id} value={r.id}>
              {rotulo(r)}
            </option>
          ))}
        </optgroup>
        {importadas.length > 0 && (
          <optgroup label="Importados nesta sessão">
            {importadas.map((r) => (
              <option key={r.id} value={r.id}>
                {rotulo(r)}
              </option>
            ))}
          </optgroup>
        )}
      </select>

      <input
        ref={entrada}
        type="file"
        accept=".csv,text/csv"
        className="hidden"
        onChange={(e) => {
          const arquivo = e.target.files?.[0]
          if (arquivo) aoImportar(arquivo)
          e.target.value = ''
        }}
      />
      <button
        type="button"
        disabled={importando}
        onClick={() => entrada.current?.click()}
        className="text-sm font-medium text-epicentro underline-offset-2 hover:underline disabled:text-tinta-suave"
      >
        {importando ? 'Importando catálogo...' : 'Importar meu catálogo em CSV'}
      </button>
    </div>
  )
}
