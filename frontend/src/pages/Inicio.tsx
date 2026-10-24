import { useEffect, useState } from 'react'
import { buscarSaude } from '../services/api'

type EstadoBackend =
  | { tipo: 'carregando' }
  | { tipo: 'ok'; servico: string }
  | { tipo: 'erro'; mensagem: string }

export default function Inicio() {
  const [estado, setEstado] = useState<EstadoBackend>({ tipo: 'carregando' })

  useEffect(() => {
    buscarSaude()
      .then((saude) => setEstado({ tipo: 'ok', servico: saude.servico }))
      .catch((erro: Error) => setEstado({ tipo: 'erro', mensagem: erro.message }))
  }, [])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 p-8">
      <h1 className="text-4xl font-bold text-slate-900">SismoPar</h1>
      <p className="text-slate-600">Par de terremotos mais próximo por divisão e conquista</p>

      {estado.tipo === 'carregando' && (
        <span className="rounded-full bg-slate-200 px-4 py-1 text-sm text-slate-700">
          Verificando backend...
        </span>
      )}
      {estado.tipo === 'ok' && (
        <span className="rounded-full bg-emerald-100 px-4 py-1 text-sm text-emerald-800">
          Backend: ok ({estado.servico})
        </span>
      )}
      {estado.tipo === 'erro' && (
        <span className="rounded-full bg-red-100 px-4 py-1 text-sm text-red-800">
          Backend indisponível: {estado.mensagem}
        </span>
      )}
    </main>
  )
}
