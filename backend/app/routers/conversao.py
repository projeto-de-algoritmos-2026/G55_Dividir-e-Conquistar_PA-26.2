"""Conversão dos objetos internos para os schemas de saída."""

from app.models.evento import Evento
from app.models.passo import PassoRecursao
from app.models.resultado import ParMaisProximo
from app.models.schemas import (
    Caixa,
    ComparacaoFaixa,
    Coordenada,
    EventoSaida,
    PassoSaida,
    RegiaoSaida,
    ResultadoResumo,
)
from app.services.repositorio import Catalogo


def evento_saida(evento: Evento) -> EventoSaida:
    return EventoSaida.model_validate(evento)


def regiao_saida(catalogo: Catalogo) -> RegiaoSaida:
    regiao, eventos = catalogo.regiao, catalogo.eventos
    latitude, longitude = regiao.centro
    return RegiaoSaida(
        id=catalogo.id,
        nome=catalogo.nome,
        importado=catalogo.importado,
        caixa=Caixa(
            lat_min=regiao.lat_min,
            lat_max=regiao.lat_max,
            lon_min=regiao.lon_min,
            lon_max=regiao.lon_max,
        ),
        centro=Coordenada(latitude=latitude, longitude=longitude),
        total_eventos=len(eventos),
        inicio=min(e.data for e in eventos).date() if eventos else None,
        fim=max(e.data for e in eventos).date() if eventos else None,
        magnitude_min=min(e.magnitude for e in eventos) if eventos else None,
        magnitude_max=max(e.magnitude for e in eventos) if eventos else None,
        profundidade_max=max(e.profundidade for e in eventos) if eventos else None,
    )


def resumo(resultado: ParMaisProximo) -> ResultadoResumo:
    return ResultadoResumo(
        par=[resultado.a.id, resultado.b.id],
        distancia_projetada_km=resultado.distancia_projetada_km,
        distancia_geodesica_km=resultado.distancia_geodesica_km,
        comparacoes=resultado.comparacoes,
    )


def passo_saida(passo: PassoRecursao) -> PassoSaida:
    return PassoSaida(
        profundidade=passo.profundidade,
        tipo=passo.tipo,
        ids=list(passo.ids),
        reta_l=passo.reta_l,
        delta_esquerdo=passo.delta_esquerdo,
        delta_direito=passo.delta_direito,
        delta=passo.delta,
        faixa=list(passo.faixa),
        comparacoes_faixa=[
            ComparacaoFaixa(a=a, b=b, distancia=distancia)
            for a, b, distancia in passo.comparacoes_faixa
        ],
        par=list(passo.par),
        distancia=passo.distancia,
    )
