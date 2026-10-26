import L from 'leaflet'
import { useEffect, useMemo } from 'react'
import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip, useMap } from 'react-leaflet'
import type { Caixa, Evento, ParMaisProximo } from '../types'
import { formatarData, formatarDistancia, formatarNumero, raioPorMagnitude } from '../utils/formatacao'

interface Props {
  caixa: Caixa | undefined
  eventos: Evento[]
  par: ParMaisProximo | null
  /** Muda a cada clique em "Ver região inteira" */
  pedidoEnquadrar: number
}

const COR_EPICENTRO = '#3d6a86'
const COR_REGISTRO = '#c1272d'

function limitesDaCaixa(caixa: Caixa): L.LatLngBoundsExpression {
  return [
    [caixa.lat_min, caixa.lon_min],
    [caixa.lat_max, caixa.lon_max],
  ]
}

/** Popup montado com textContent: o local vem de CSV importado e não é confiável. */
function conteudoPopup(evento: Evento): HTMLElement {
  const raiz = document.createElement('div')
  const linhas: [string, string][] = [
    [`M ${formatarNumero(evento.magnitude, 1)}`, evento.local || 'Local não informado'],
    ['Data', formatarData(evento.data)],
    ['Profundidade', `${formatarNumero(evento.profundidade, 1)} km`],
  ]
  linhas.forEach(([rotulo, valor], i) => {
    const p = document.createElement('p')
    p.style.margin = '0'
    const forte = document.createElement('strong')
    forte.textContent = `${rotulo} `
    p.append(forte, valor)
    if (i === 0) p.style.marginBottom = '4px'
    raiz.append(p)
  })
  return raiz
}

/** Milhares de epicentros: camada imperativa no canvas, bem mais leve que um componente por ponto. */
function CamadaEventos({ eventos }: { eventos: Evento[] }) {
  const mapa = useMap()
  useEffect(() => {
    const renderizador = L.canvas({ padding: 0.5 })
    const camada = L.layerGroup(
      eventos.map((evento) =>
        L.circleMarker([evento.latitude, evento.longitude], {
          renderer: renderizador,
          radius: raioPorMagnitude(evento.magnitude),
          color: COR_EPICENTRO,
          weight: 1,
          fillColor: COR_EPICENTRO,
          fillOpacity: 0.25,
        }).bindPopup(() => conteudoPopup(evento)),
      ),
    ).addTo(mapa)
    return () => {
      camada.remove()
    }
  }, [mapa, eventos])
  return null
}

function Enquadramento({ caixa, par, pedidoEnquadrar }: Omit<Props, 'eventos'>) {
  const mapa = useMap()

  useEffect(() => {
    if (caixa) mapa.fitBounds(limitesDaCaixa(caixa), { padding: [16, 16] })
  }, [mapa, caixa, pedidoEnquadrar])

  useEffect(() => {
    if (!par) return
    const limites = L.latLngBounds([
      [par.a.latitude, par.a.longitude],
      [par.b.latitude, par.b.longitude],
    ])
    // Os pares reais ficam a dezenas de metros: nenhum zoom os separa, então o
    // limite mantém à vista os eventos vizinhos (réplicas, a falha) em volta do par
    mapa.flyToBounds(limites, { maxZoom: 10, padding: [80, 80], duration: 1.2 })
  }, [mapa, par])

  return null
}

function ParDestacado({ par }: { par: ParMaisProximo }) {
  const pontos: [number, number][] = [
    [par.a.latitude, par.a.longitude],
    [par.b.latitude, par.b.longitude],
  ]
  return (
    <>
      <Polyline positions={pontos} pathOptions={{ color: COR_REGISTRO, weight: 3 }}>
        <Tooltip permanent direction="top" className="rotulo-distancia" offset={[0, -8]}>
          {formatarDistancia(par.distancia_geodesica_km)}
        </Tooltip>
      </Polyline>
      {[par.a, par.b].map((evento, i) => (
        <CircleMarker
          key={evento.id}
          center={pontos[i]}
          radius={raioPorMagnitude(evento.magnitude) + 3}
          pathOptions={{ color: COR_REGISTRO, weight: 2.5, fillColor: COR_REGISTRO, fillOpacity: 0.55 }}
        >
          <Tooltip direction="right" offset={[8, 0]}>
            {i === 0 ? 'Evento A' : 'Evento B'}: M {formatarNumero(evento.magnitude, 1)}
          </Tooltip>
        </CircleMarker>
      ))}
    </>
  )
}

export default function MapaEventos({ caixa, eventos, par, pedidoEnquadrar }: Props) {
  const centroInicial = useMemo<[number, number]>(() => [20, 0], [])
  return (
    <MapContainer center={centroInicial} zoom={2} preferCanvas className="h-full w-full" worldCopyJump>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <CamadaEventos eventos={eventos} />
      {par && <ParDestacado par={par} />}
      <Enquadramento caixa={caixa} par={par} pedidoEnquadrar={pedidoEnquadrar} />
    </MapContainer>
  )
}
