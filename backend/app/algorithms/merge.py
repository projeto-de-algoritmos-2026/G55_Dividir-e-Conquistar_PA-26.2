from collections.abc import Callable, Sequence
from typing import Any, TypeVar

T = TypeVar("T")


def identidade(item: Any) -> Any:
    return item


def merge(
    esquerda: Sequence[T], direita: Sequence[T], chave: Callable[[T], Any] = identidade
) -> list[T]:
    """Intercala duas listas já ordenadas por `chave` em tempo linear.

    Em caso de empate o item da esquerda vem primeiro, o que torna o
    Mergesort estável.
    """
    resultado: list[T] = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if chave(esquerda[i]) <= chave(direita[j]):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado
