"""500 instâncias aleatórias reprodutíveis: Closest Pair contra força bruta."""

import random

import pytest

from app.algorithms.closest_pair_nlog2n import closest_pair_nlog2n
from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.algorithms.forca_bruta import forca_bruta
from tests.fabricas import pontos

INSTANCIAS = 500


def _uniforme(gerador, n):
    return [(gerador.uniform(-500, 500), gerador.uniform(-500, 500)) for _ in range(n)]


def _aglomerados(gerador, n):
    # Poucos epicentros principais com réplicas em volta
    centros = [(gerador.uniform(-500, 500), gerador.uniform(-500, 500)) for _ in range(3)]
    return [
        (gerador.gauss(cx, 5), gerador.gauss(cy, 5))
        for cx, cy in (gerador.choice(centros) for _ in range(n))
    ]


def _grade(gerador, n):
    # Coordenadas inteiras pequenas: muitos empates de distância e pontos coincidentes
    return [(gerador.randint(0, 20), gerador.randint(0, 20)) for _ in range(n)]


def _colunas(gerador, n):
    # Poucos valores de x: muitos empates em x
    colunas = [gerador.uniform(-100, 100) for _ in range(4)]
    return [(gerador.choice(colunas), gerador.uniform(-500, 500)) for _ in range(n)]


DISTRIBUICOES = [_uniforme, _aglomerados, _grade, _colunas]


def test_500_instancias_aleatorias():
    falhas = []
    for semente in range(INSTANCIAS):
        gerador = random.Random(semente)
        distribuicao = DISTRIBUICOES[semente % len(DISTRIBUICOES)]
        n = gerador.randint(2, 300)
        eventos = pontos(distribuicao(gerador, n))

        esperado = forca_bruta(eventos).distancia_projetada_km
        for versao in (closest_pair_nlogn, closest_pair_nlog2n):
            obtido = versao(eventos).distancia_projetada_km
            if obtido != esperado:
                falhas.append(
                    f"semente={semente} {distribuicao.__name__} n={n} "
                    f"{versao.__name__}: {obtido} != {esperado}"
                )

    if falhas:
        pytest.fail(f"{len(falhas)} divergência(s):\n" + "\n".join(falhas[:20]))
