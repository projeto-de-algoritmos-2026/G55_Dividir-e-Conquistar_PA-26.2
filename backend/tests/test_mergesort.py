import random

import pytest

from app.algorithms.merge import merge
from app.algorithms.mergesort import mergesort


@pytest.mark.parametrize(
    "entrada",
    [[], [1], [1, 2, 3, 4], [4, 3, 2, 1], [3, 1, 3, 2, 1, 3], [-2.5, 0, -7, 10.1]],
)
def test_casos_basicos(entrada):
    assert mergesort(entrada) == sorted(entrada)


def test_mil_aleatorios_iguais_ao_sorted():
    gerador = random.Random(42)
    entrada = [gerador.randint(-500, 500) for _ in range(1000)]

    assert mergesort(entrada) == sorted(entrada)


def test_estavel_em_chaves_iguais():
    entrada = [("b", 1), ("a", 2), ("c", 1), ("d", 2), ("e", 1)]

    resultado = mergesort(entrada, chave=lambda par: par[1])

    assert resultado == [("b", 1), ("c", 1), ("e", 1), ("a", 2), ("d", 2)]


def test_chave_em_tupla_desempata():
    pontos = [(2, 5, "c"), (1, 9, "b"), (2, 1, "a"), (1, 9, "a")]

    assert mergesort(pontos, chave=lambda p: (p[0], p[1], p[2])) == sorted(pontos)


def test_nao_modifica_a_entrada():
    entrada = [3, 1, 2]
    mergesort(entrada)

    assert entrada == [3, 1, 2]


def test_merge_intercala():
    assert merge([1, 4, 6], [2, 3, 7, 8]) == [1, 2, 3, 4, 6, 7, 8]


def test_merge_com_lado_vazio():
    assert merge([], [1, 2]) == [1, 2]
    assert merge([1, 2], []) == [1, 2]


def test_merge_em_empate_toma_da_esquerda():
    esquerda = [(1, "esq")]
    direita = [(1, "dir")]

    assert merge(esquerda, direita, chave=lambda par: par[0]) == [(1, "esq"), (1, "dir")]
