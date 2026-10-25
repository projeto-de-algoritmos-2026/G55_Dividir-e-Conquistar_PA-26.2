"""Peças compartilhadas pelas duas versões de divisão e conquista do par mais próximo."""

from collections.abc import Sequence
from dataclasses import dataclass

from app.algorithms.mergesort import mergesort
from app.geo.haversine import distancia_geodesica
from app.geo.projecao import distancia_projetada
from app.models.evento import Evento
from app.models.passo import PassoRecursao
from app.models.resultado import ParMaisProximo

# Lema de empacotamento: na faixa ordenada por y, basta olhar os 7 seguintes
VIZINHOS_NA_FAIXA = 7


def chave_x(evento: Evento) -> tuple[float, float, str]:
    return evento.x, evento.y, evento.id


def chave_y(evento: Evento) -> tuple[float, float, str]:
    return evento.y, evento.x, evento.id


def ordenar_por_x(eventos: Sequence[Evento]) -> list[Evento]:
    return mergesort(eventos, chave=chave_x)


def validar_entrada(eventos: Sequence[Evento]) -> None:
    if len(eventos) < 2:
        raise ValueError("São necessários pelo menos 2 eventos")


@dataclass
class Melhor:
    distancia: float
    a: Evento
    b: Evento


def menor_dos_lados(esquerda: Melhor, direita: Melhor) -> Melhor:
    # Em empate, fica o da esquerda
    melhor = esquerda if esquerda.distancia <= direita.distancia else direita
    return Melhor(melhor.distancia, melhor.a, melhor.b)


def na_faixa(evento: Evento, reta_l: float, delta: float) -> bool:
    return abs(evento.x - reta_l) < delta


def varrer_faixa(
    faixa_y: Sequence[Evento],
    delta: float,
    melhor: Melhor,
    comparados: list[tuple[str, str, float]] | None = None,
) -> int:
    """Compara cada ponto da faixa com até 7 seguintes em y e atualiza `melhor`.

    Para quando a diferença em y chega a δ: dali em diante nenhum ponto pode
    estar a menos de δ. Devolve o número de distâncias calculadas.
    """
    comparacoes = 0
    for i, p in enumerate(faixa_y):
        for j in range(i + 1, min(i + 1 + VIZINHOS_NA_FAIXA, len(faixa_y))):
            q = faixa_y[j]
            if q.y - p.y >= delta:
                break
            distancia = distancia_projetada(p, q)
            comparacoes += 1
            if comparados is not None:
                comparados.append((p.id, q.id, distancia))
            if distancia < melhor.distancia:
                melhor.distancia, melhor.a, melhor.b = distancia, p, q
    return comparacoes


def passo_base(subproblema: Sequence[Evento], profundidade: int, melhor: Melhor) -> PassoRecursao:
    return PassoRecursao(
        profundidade=profundidade,
        tipo="base",
        ids=tuple(evento.id for evento in subproblema),
        reta_l=None,
        delta_esquerdo=None,
        delta_direito=None,
        delta=melhor.distancia,
        faixa=(),
        comparacoes_faixa=(),
        par=(melhor.a.id, melhor.b.id),
        distancia=melhor.distancia,
    )


def passo_combinacao(
    subproblema: Sequence[Evento],
    profundidade: int,
    reta_l: float,
    esquerda: Melhor,
    direita: Melhor,
    faixa_y: Sequence[Evento],
    comparados: list[tuple[str, str, float]],
    melhor: Melhor,
) -> PassoRecursao:
    return PassoRecursao(
        profundidade=profundidade,
        tipo="combinacao",
        ids=tuple(evento.id for evento in subproblema),
        reta_l=reta_l,
        delta_esquerdo=esquerda.distancia,
        delta_direito=direita.distancia,
        delta=min(esquerda.distancia, direita.distancia),
        faixa=tuple(evento.id for evento in faixa_y),
        comparacoes_faixa=tuple(comparados),
        par=(melhor.a.id, melhor.b.id),
        distancia=melhor.distancia,
    )


def montar_resultado(melhor: Melhor, comparacoes: int) -> ParMaisProximo:
    return ParMaisProximo(
        melhor.a,
        melhor.b,
        melhor.distancia,
        distancia_geodesica(melhor.a, melhor.b),
        comparacoes,
    )
