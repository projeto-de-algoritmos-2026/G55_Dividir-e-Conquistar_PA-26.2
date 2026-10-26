import type { ErroApi } from '../services/api'

interface Props {
  erro: ErroApi
  aoFechar?: () => void
}

/** Faixa de erro: a mensagem da API e, se houver, os erros por linha do CSV. */
export default function AvisoErro({ erro, aoFechar }: Props) {
  return (
    <div role="alert" className="rounded border border-registro/40 bg-white px-3 py-2.5 text-sm">
      <div className="flex items-start justify-between gap-3">
        <p className="font-medium text-registro">{erro.message}</p>
        {aoFechar && (
          <button
            type="button"
            onClick={aoFechar}
            className="shrink-0 text-tinta-suave hover:text-tinta"
            aria-label="Fechar aviso"
          >
            ✕
          </button>
        )}
      </div>
      {erro.linhas.length > 0 && (
        <ul className="numeros mt-2 max-h-32 space-y-0.5 overflow-y-auto text-xs text-tinta-suave">
          {erro.linhas.map((linha, i) => (
            <li key={i}>
              Linha {linha.linha}, coluna {linha.coluna}: {linha.mensagem}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
