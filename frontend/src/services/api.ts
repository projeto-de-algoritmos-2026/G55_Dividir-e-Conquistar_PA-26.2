import type { RespostaSaude } from '../types'

async function obterJson<T>(caminho: string): Promise<T> {
  const resposta = await fetch(`/api${caminho}`)
  if (!resposta.ok) {
    throw new Error(`Erro ${resposta.status} ao acessar ${caminho}`)
  }
  return resposta.json() as Promise<T>
}

export function buscarSaude(): Promise<RespostaSaude> {
  return obterJson<RespostaSaude>('/saude')
}
