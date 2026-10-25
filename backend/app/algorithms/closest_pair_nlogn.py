"""Sort_and_Closest-Pair em O(n log n): cada chamada devolve seus pontos ordenados por y.

A ordenação da faixa vira um merge linear de duas listas já ordenadas.
T(n) = 2T(n/2) + O(n)
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
from app.algorithms.merge import merge
from app.algorithms.mergesort import mergesort
from app.models.evento import Evento
from app.models.passo import PassoRecursao
from app.models.resultado import ParMaisProximo


def closest_pair_nlogn(
    eventos: Sequence[Evento], registro: list[PassoRecursao] | None = None
) -> ParMaisProximo:
    """Par mais próximo no plano projetado. Se `registro` for uma lista, recebe os passos."""
    validar_entrada(eventos)
    px = ordenar_por_x(eventos)
    melhor, comparacoes, _ = _resolver(px, 0, len(px), 0, registro)
    return montar_resultado(melhor, comparacoes)


def _resolver(
    px: list[Evento],
    inicio: int,
    fim: int,
    profundidade: int,
    registro: list[PassoRecursao] | None,
) -> tuple[Melhor, int, list[Evento]]:
    """Resolve px[inicio:fim]. Devolve o melhor par, as comparações e os pontos ordenados por y."""
    if fim - inicio <= 3:
        distancia, a, b, comparacoes = par_forca_bruta(px[inicio:fim])
        melhor = Melhor(distancia, a, b)
        if registro is not None:
            registro.append(passo_base(px[inicio:fim], profundidade, melhor))
        return melhor, comparacoes, mergesort(px[inicio:fim], chave=chave_y)

    # Divide pela posição, não pelo valor de x: empates em x não atrapalham
    meio = (inicio + fim) // 2
    reta_l = (px[meio - 1].x + px[meio].x) / 2

    esquerda, comparacoes_esq, esq_y = _resolver(px, inicio, meio, profundidade + 1, registro)
    direita, comparacoes_dir, dir_y = _resolver(px, meio, fim, profundidade + 1, registro)
    melhor = menor_dos_lados(esquerda, direita)
    delta = melhor.distancia

    py = merge(esq_y, dir_y, chave=chave_y)
    # Filtrar uma lista ordenada por y preserva a ordem: a faixa já sai pronta
    faixa_y = [evento for evento in py if na_faixa(evento, reta_l, delta)]
    comparados = [] if registro is not None else None
    comparacoes_faixa = varrer_faixa(faixa_y, delta, melhor, comparados)

    if registro is not None:
        registro.append(
            passo_combinacao(
                px[inicio:fim], profundidade, reta_l, esquerda, direita, faixa_y, comparados, melhor
            )
        )
    return melhor, comparacoes_esq + comparacoes_dir + comparacoes_faixa, py
