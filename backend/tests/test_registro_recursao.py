from functools import cache

import pytest

from app.algorithms.closest_pair_nlog2n import closest_pair_nlog2n
from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from tests.fabricas import VERSOES, pontos

TAMANHOS = [2, 3, 4, 5, 7, 8, 30, 100, 257]


@cache
def chamadas(n: int) -> int:
    """C(n): número de chamadas da recursão com divisão por posição e base n <= 3."""
    return 1 if n <= 3 else 1 + chamadas(n // 2) + chamadas(n - n // 2)


@cache
def profundidade_maxima(n: int) -> int:
    """D(n): a metade maior é a direita, com ⌈n/2⌉ pontos."""
    return 0 if n <= 3 else 1 + profundidade_maxima(n - n // 2)


def _instancia(n):
    return pontos(((i * 37) % 101 + i / 1000, (i * 59) % 103) for i in range(n))


def _registro(closest_pair, n):
    registro = []
    closest_pair(_instancia(n), registro=registro)
    return registro


@VERSOES
@pytest.mark.parametrize("n", TAMANHOS)
def test_quantidade_de_passos_e_profundidade(closest_pair, n):
    registro = _registro(closest_pair, n)

    assert len(registro) == chamadas(n)
    assert max(passo.profundidade for passo in registro) == profundidade_maxima(n)
    for d in range(profundidade_maxima(n) + 1):
        assert sum(passo.profundidade == d for passo in registro) <= 2**d


@VERSOES
@pytest.mark.parametrize("n", TAMANHOS)
def test_arvore_reconstruida_pela_pos_ordem(closest_pair, n):
    """Em pós-ordem, cada combinação consome os dois últimos subproblemas resolvidos."""
    pilha = []
    for passo in _registro(closest_pair, n):
        if passo.tipo == "combinacao":
            direita = pilha.pop()
            esquerda = pilha.pop()
            assert esquerda.profundidade == direita.profundidade == passo.profundidade + 1
            assert esquerda.ids + direita.ids == passo.ids
            assert passo.delta_esquerdo == esquerda.distancia
            assert passo.delta_direito == direita.distancia
        pilha.append(passo)

    (raiz,) = pilha
    assert raiz.profundidade == 0 and len(raiz.ids) == n


@pytest.mark.parametrize("n", TAMANHOS)
def test_as_duas_versoes_geram_a_mesma_arvore(n):
    def estrutura(registro):
        return [(p.profundidade, p.ids, p.reta_l, p.faixa, p.par, p.distancia) for p in registro]

    assert estrutura(_registro(closest_pair_nlogn, n)) == estrutura(_registro(closest_pair_nlog2n, n))
