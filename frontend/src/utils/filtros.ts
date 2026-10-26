import type { Filtros } from '../types'

/** Valores do formulário, como texto: vazio significa "sem filtro". */
export interface ValoresFiltros {
  inicio: string
  fim: string
  magnitude_min: string
  profundidade_max: string
}

export const FILTROS_VAZIOS: ValoresFiltros = {
  inicio: '',
  fim: '',
  magnitude_min: '',
  profundidade_max: '',
}

export function paraFiltros(valores: ValoresFiltros): Filtros {
  const numero = (texto: string) => (texto.trim() === '' ? undefined : Number(texto.replace(',', '.')))
  return {
    inicio: valores.inicio || undefined,
    fim: valores.fim || undefined,
    magnitude_min: numero(valores.magnitude_min),
    profundidade_max: numero(valores.profundidade_max),
  }
}
