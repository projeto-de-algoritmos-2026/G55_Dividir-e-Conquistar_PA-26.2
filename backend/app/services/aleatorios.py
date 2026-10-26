"""Instâncias aleatórias reprodutíveis para validar o Closest Pair contra a força bruta."""

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.algorithms.closest_pair_nlog2n import closest_pair_nlog2n
from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.algorithms.forca_bruta import forca_bruta
from app.models.evento import Evento

DATA_FIXA = datetime(2024, 1, 1, tzinfo=timezone.utc)


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


DISTRIBUICOES = {
    "uniforme": _uniforme,
    "aglomerados": _aglomerados,
    "grade": _grade,
    "colunas": _colunas,
}


def gerar_instancia(semente: int, n_max: int) -> tuple[str, list[Evento]]:
    """Distribuição escolhida pela semente; n sorteado em [2, n_max]."""
    gerador = random.Random(semente)
    nome = list(DISTRIBUICOES)[semente % len(DISTRIBUICOES)]
    n = gerador.randint(2, n_max)
    eventos = [
        Evento(f"p{i}", DATA_FIXA, 0.0, 0.0, 0.0, 0.0, "aleatório", float(x), float(y))
        for i, (x, y) in enumerate(DISTRIBUICOES[nome](gerador, n))
    ]
    return nome, eventos


@dataclass(frozen=True)
class Falha:
    semente: int
    distribuicao: str
    n: int
    algoritmo: str
    esperado: float
    obtido: float


@dataclass
class RelatorioAleatorio:
    instancias: int = 0
    aprovadas: int = 0
    falhas: list[Falha] = field(default_factory=list)


def validar_aleatorio(instancias: int, n_max: int, semente_inicial: int = 0) -> RelatorioAleatorio:
    relatorio = RelatorioAleatorio()
    for semente in range(semente_inicial, semente_inicial + instancias):
        nome, eventos = gerar_instancia(semente, n_max)
        esperado = forca_bruta(eventos).distancia_projetada_km
        aprovada = True
        for versao in (closest_pair_nlogn, closest_pair_nlog2n):
            obtido = versao(eventos).distancia_projetada_km
            if obtido != esperado:
                aprovada = False
                relatorio.falhas.append(
                    Falha(semente, nome, len(eventos), versao.__name__, esperado, obtido)
                )
        relatorio.instancias += 1
        relatorio.aprovadas += aprovada
    return relatorio
