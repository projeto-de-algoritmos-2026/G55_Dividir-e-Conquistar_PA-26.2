import { useCallback, useEffect, useRef, useState } from 'react'
import AvisoErro from '../components/AvisoErro'
import Carregando from '../components/Carregando'
import FormularioFiltros from '../components/FormularioFiltros'
import MapaEventos from '../components/MapaEventos'
import PainelPar from '../components/PainelPar'
import SeletorRegiao from '../components/SeletorRegiao'
import { buscarParMaisProximo, ErroApi, importarCatalogo, listarEventos, listarRegioes } from '../services/api'
import type { Evento, Filtros, ParMaisProximo, Regiao } from '../types'
import { FILTROS_VAZIOS, paraFiltros, type ValoresFiltros } from '../utils/filtros'
import { formatarInteiro } from '../utils/formatacao'

function comoErroApi(erro: unknown): ErroApi {
  return erro instanceof ErroApi ? erro : new ErroApi(String(erro), null)
}

export default function Mapa() {
  const [regioes, setRegioes] = useState<Regiao[]>([])
  const [regiaoId, setRegiaoId] = useState('')
  const [valoresFiltros, setValoresFiltros] = useState<ValoresFiltros>(FILTROS_VAZIOS)
  const [eventos, setEventos] = useState<Evento[]>([])
  const [par, setPar] = useState<ParMaisProximo | null>(null)
  const [carregandoEventos, setCarregandoEventos] = useState(false)
  const [calculando, setCalculando] = useState(false)
  const [importando, setImportando] = useState(false)
  const [erro, setErro] = useState<ErroApi | null>(null)
  const [pedidoEnquadrar, setPedidoEnquadrar] = useState(0)
  // Descarta respostas atrasadas quando o usuário troca de região no meio do caminho
  const ultimaRequisicao = useRef(0)

  const regiao = regioes.find((r) => r.id === regiaoId)

  const carregarRegioes = useCallback(async (selecionar?: string) => {
    try {
      const lista = await listarRegioes()
      setRegioes(lista)
      setRegiaoId((atual) => selecionar ?? (atual || lista[0]?.id || ''))
    } catch (e) {
      setErro(comoErroApi(e))
    }
  }, [])

  useEffect(() => {
    void carregarRegioes()
  }, [carregarRegioes])

  const carregarEventos = useCallback(async (id: string, filtros: Filtros) => {
    const numero = ++ultimaRequisicao.current
    setCarregandoEventos(true)
    try {
      const lista = await listarEventos(id, filtros)
      if (numero === ultimaRequisicao.current) setEventos(lista.eventos)
    } catch (e) {
      if (numero === ultimaRequisicao.current) setErro(comoErroApi(e))
    } finally {
      if (numero === ultimaRequisicao.current) setCarregandoEventos(false)
    }
  }, [])

  // Ao trocar de região, mostra os eventos dela com os filtros atuais e limpa o resultado
  useEffect(() => {
    if (!regiaoId) return
    setPar(null)
    setErro(null)
    void carregarEventos(regiaoId, paraFiltros(valoresFiltros))
    // Filtros só se aplicam ao clicar no botão
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [regiaoId, carregarEventos])

  async function encontrarPar(e: React.FormEvent) {
    e.preventDefault()
    if (!regiaoId) return
    const filtros = paraFiltros(valoresFiltros)
    setErro(null)
    setPar(null)
    setCalculando(true)
    try {
      const [resultado] = await Promise.all([
        buscarParMaisProximo({ regiao_id: regiaoId, ...filtros }),
        carregarEventos(regiaoId, filtros),
      ])
      setPar(resultado)
    } catch (erroPar) {
      setErro(comoErroApi(erroPar))
    } finally {
      setCalculando(false)
    }
  }

  async function importar(arquivo: File) {
    setErro(null)
    setImportando(true)
    try {
      const resposta = await importarCatalogo(arquivo)
      await carregarRegioes(resposta.regiao.id)
    } catch (e) {
      setErro(comoErroApi(e))
    } finally {
      setImportando(false)
    }
  }

  return (
    <div className="flex h-full">
      <aside className="papel-quadriculado w-[380px] shrink-0 overflow-y-auto border-r border-grade">
        <form onSubmit={encontrarPar} className="space-y-5 p-5">
          {regioes.length === 0 && !erro ? (
            <Carregando texto="Carregando regiões..." />
          ) : (
            <SeletorRegiao
              regioes={regioes}
              regiaoId={regiaoId}
              aoEscolher={setRegiaoId}
              aoImportar={importar}
              importando={importando}
            />
          )}

          <FormularioFiltros valores={valoresFiltros} regiao={regiao} aoMudar={setValoresFiltros} />

          <button
            type="submit"
            disabled={!regiaoId || calculando}
            className="w-full rounded bg-tinta px-4 py-2.5 text-sm font-semibold text-papel hover:bg-tinta/90 disabled:bg-tinta-suave"
          >
            {calculando ? 'Procurando o par...' : 'Encontrar Par Mais Próximo'}
          </button>

          {erro && <AvisoErro erro={erro} aoFechar={() => setErro(null)} />}

          {par ? (
            <PainelPar par={par} />
          ) : (
            !calculando &&
            regiao && (
              <p className="text-sm text-tinta-suave">
                Clique no botão para encontrar, entre os {formatarInteiro(eventos.length)} eventos do mapa, os
                dois epicentros mais próximos um do outro.
              </p>
            )
          )}
        </form>
      </aside>

      <main className="relative min-w-0 flex-1">
        <MapaEventos caixa={regiao?.caixa} eventos={eventos} par={par} pedidoEnquadrar={pedidoEnquadrar} />
        <div className="pointer-events-none absolute inset-x-0 top-3 z-[1000] flex justify-center">
          <div className="pointer-events-auto flex items-center gap-3 rounded bg-white/95 px-3 py-1.5 text-sm shadow-sm">
            {carregandoEventos ? (
              <Carregando texto="Carregando eventos..." />
            ) : (
              <span className="numeros">
                {formatarInteiro(eventos.length)} eventos{regiao ? ` em ${regiao.nome}` : ''}
              </span>
            )}
            {regiao && (
              <button
                type="button"
                onClick={() => setPedidoEnquadrar((n) => n + 1)}
                className="font-medium text-epicentro hover:underline"
              >
                Ver região inteira
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
