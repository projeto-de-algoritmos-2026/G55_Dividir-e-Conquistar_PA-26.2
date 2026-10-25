from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from app.algorithms.merge import identidade, merge

T = TypeVar("T")


def mergesort(itens: Sequence[T], chave: Callable[[T], Any] = identidade) -> list[T]:
    """Ordena por `chave` em O(n log n), de forma estável, sem alterar a entrada."""
    if len(itens) <= 1:
        return list(itens)
    meio = len(itens) // 2
    return merge(mergesort(itens[:meio], chave), mergesort(itens[meio:], chave), chave)
