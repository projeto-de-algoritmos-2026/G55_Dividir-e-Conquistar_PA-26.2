import math
from collections.abc import Sequence

from app.geo.haversine import distancia_geodesica
from app.geo.projecao import distancia_projetada
from app.models.evento import Evento
from app.models.resultado import ParMaisProximo


def par_forca_bruta(pontos: Sequence[Evento]) -> tuple[float, Evento, Evento, int]:
    """Núcleo da força bruta: (distância, a, b, comparações). Também é o caso base do Closest Pair."""
    menor = math.inf
    melhor = (pontos[0], pontos[1])
    comparacoes = 0
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            distancia = distancia_projetada(pontos[i], pontos[j])
            comparacoes += 1
            # Estrito: em empate, mantém o primeiro par encontrado
            if distancia < menor:
                menor = distancia
                melhor = (pontos[i], pontos[j])
    return menor, melhor[0], melhor[1], comparacoes


def forca_bruta(pontos: Sequence[Evento]) -> ParMaisProximo:
    """Compara todos os n(n − 1)/2 pares no plano projetado. Θ(n²)."""
    if len(pontos) < 2:
        raise ValueError("São necessários pelo menos 2 eventos")

    distancia, a, b, comparacoes = par_forca_bruta(pontos)
    return ParMaisProximo(a, b, distancia, distancia_geodesica(a, b), comparacoes)
