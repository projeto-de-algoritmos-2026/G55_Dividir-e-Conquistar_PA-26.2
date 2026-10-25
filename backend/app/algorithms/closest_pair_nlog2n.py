"""Closest-Pair em O(n log² n): a faixa é reordenada por y a cada chamada.

T(n) = 2T(n/2) + O(n log n)
"""

from collections.abc import Sequence

from app.algorithms.closest_pair_comum import (
    Melhor,
    chave_y,
    menor_dos_lados,
    montar_resultado,
    na_faixa,
    ordenar_por_x,
    passo_base,
    passo_combinacao,
    validar_entrada,
    varrer_faixa,
)
from app.algorithms.forca_bruta import par_forca_bruta
from app.algorithms.mergesort import mergesort
from app.models.evento import Evento
from app.models.passo import PassoRecursao
from app.models.resultado import ParMaisProximo


def closest_pair_nlog2n(
    eventos: Sequence[Evento], registro: list[PassoRecursao] | None = None
) -> ParMaisProximo:
    """Par mais próximo no plano projetado. Se `registro` for uma lista, recebe os passos."""
    validar_entrada(eventos)
    px = ordenar_por_x(eventos)
    melhor, comparacoes = _resolver(px, 0, len(px), 0, registro)
    return montar_resultado(melhor, comparacoes)


def _resolver(
    px: list[Evento],
    inicio: int,
    fim: int,
    profundidade: int,
    registro: list[PassoRecursao] | None,
) -> tuple[Melhor, int]:
    """Resolve px[inicio:fim], já ordenado por x. Devolve o melhor par e as comparações."""
    if fim - inicio <= 3:
        distancia, a, b, comparacoes = par_forca_bruta(px[inicio:fim])
        melhor = Melhor(distancia, a, b)
        if registro is not None:
            registro.append(passo_base(px[inicio:fim], profundidade, melhor))
        return melhor, comparacoes

    # Divide pela posição, não pelo valor de x: empates em x não atrapalham
    meio = (inicio + fim) // 2
    reta_l = (px[meio - 1].x + px[meio].x) / 2

    esquerda, comparacoes_esq = _resolver(px, inicio, meio, profundidade + 1, registro)
    direita, comparacoes_dir = _resolver(px, meio, fim, profundidade + 1, registro)
    melhor = menor_dos_lados(esquerda, direita)
    delta = melhor.distancia

    faixa_y = mergesort(
        [evento for evento in px[inicio:fim] if na_faixa(evento, reta_l, delta)], chave=chave_y
    )
    comparados = [] if registro is not None else None
    comparacoes_faixa = varrer_faixa(faixa_y, delta, melhor, comparados)

    if registro is not None:
        registro.append(
            passo_combinacao(
                px[inicio:fim], profundidade, reta_l, esquerda, direita, faixa_y, comparados, melhor
            )
        )
    return melhor, comparacoes_esq + comparacoes_dir + comparacoes_faixa
