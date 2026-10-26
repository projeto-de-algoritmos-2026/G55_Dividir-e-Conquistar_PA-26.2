import type { VerificacaoGeodesica } from '../types'
import { formatarDistancia, formatarInteiro } from '../utils/formatacao'

interface Props {
  verificacao: VerificacaoGeodesica
}

export default function SeloVerificacao({ verificacao }: Props) {
  const { status, diferenca_km, limite_eventos } = verificacao
  const estilos = {
    confirmado: {
      cor: 'border-confirmado text-confirmado',
      titulo: 'Confirmado na esfera',
      texto: 'A força bruta com Haversine, sem projeção, encontrou a mesma distância mínima.',
    },
    divergente: {
      cor: 'border-divergente text-divergente',
      titulo: 'Divergente',
      texto: `Na esfera existe um par ${formatarDistancia(diferenca_km ?? 0)} mais próximo: a projeção plana trocou a resposta.`,
    },
    nao_verificado: {
      cor: 'border-neutro text-neutro',
      titulo: 'Não verificado',
      texto: `A conferência na esfera só roda automaticamente até ${formatarInteiro(limite_eventos)} eventos. Use os filtros para reduzir o recorte.`,
    },
  }[status]

  return (
    <div className={`rounded border-l-4 bg-white px-3 py-2 ${estilos.cor}`}>
      <p className="text-sm font-semibold">{estilos.titulo}</p>
      <p className="mt-0.5 text-xs text-tinta-suave">{estilos.texto}</p>
    </div>
  )
}
