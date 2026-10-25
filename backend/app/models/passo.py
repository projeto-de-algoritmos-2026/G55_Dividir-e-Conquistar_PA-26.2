from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class PassoRecursao:
    """Uma chamada da recursão do Closest Pair, gravada ao terminar (pós-ordem).

    Os eventos são referenciados pelo id para facilitar a serialização na API.
    """

    profundidade: int
    tipo: Literal["base", "combinacao"]
    ids: tuple[str, ...]  # eventos do subproblema, em ordem de x
    reta_l: float | None  # None no caso base
    delta_esquerdo: float | None
    delta_direito: float | None
    delta: float  # menor distância antes da faixa (no caso base, a do próprio subproblema)
    faixa: tuple[str, ...]  # eventos a menos de δ da reta L, em ordem de y
    comparacoes_faixa: tuple[tuple[str, str, float], ...]
    par: tuple[str, str]  # melhor par do subproblema ao fim do passo
    distancia: float
