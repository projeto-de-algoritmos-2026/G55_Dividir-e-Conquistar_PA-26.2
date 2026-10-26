"""Execução cronometrada das três versões do par mais próximo."""

import random
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from app.algorithms.closest_pair_nlog2n import closest_pair_nlog2n
from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.algorithms.forca_bruta import forca_bruta
from app.models.evento import Evento
from app.models.resultado import ParMaisProximo


@dataclass(frozen=True)
class Algoritmo:
    id: str
    nome: str
    complexidade: str
    funcao: Callable[[Sequence[Evento]], ParMaisProximo]


ALGORITMOS: dict[str, Algoritmo] = {
    algoritmo.id: algoritmo
    for algoritmo in (
        Algoritmo("forca_bruta", "Força bruta", "Θ(n²)", forca_bruta),
        Algoritmo("closest_pair_nlog2n", "Closest-Pair", "O(n log² n)", closest_pair_nlog2n),
        Algoritmo("closest_pair_nlogn", "Sort_and_Closest-Pair", "O(n log n)", closest_pair_nlogn),
    )
}


def cronometrar(
    funcao: Callable[[Sequence[Evento]], ParMaisProximo], eventos: Sequence[Evento]
) -> tuple[ParMaisProximo, float]:
    inicio = time.perf_counter()
    resultado = funcao(eventos)
    return resultado, (time.perf_counter() - inicio) * 1000


@dataclass(frozen=True)
class Execucao:
    algoritmo: Algoritmo
    resultado: ParMaisProximo | None = None
    tempo_ms: float | None = None
    motivo: str | None = None


def comparar(eventos: Sequence[Evento], limite_forca_bruta: int) -> list[Execucao]:
    """Roda as três versões; a força bruta fica de fora acima do limite."""
    execucoes = []
    for algoritmo in ALGORITMOS.values():
        if algoritmo.id == "forca_bruta" and len(eventos) > limite_forca_bruta:
            motivo = f"não executada: {len(eventos)} eventos, acima do limite de {limite_forca_bruta}"
            execucoes.append(Execucao(algoritmo, motivo=motivo))
            continue
        resultado, tempo_ms = cronometrar(algoritmo.funcao, eventos)
        execucoes.append(Execucao(algoritmo, resultado, tempo_ms))
    return execucoes


def amostrar(eventos: Sequence[Evento], tamanho: int, semente: int) -> list[Evento]:
    """Amostra reprodutível, mantendo a ordem original dos eventos."""
    if len(eventos) <= tamanho:
        return list(eventos)
    escolhidos = set(random.Random(semente).sample(range(len(eventos)), tamanho))
    return [evento for i, evento in enumerate(eventos) if i in escolhidos]
