import math
from collections.abc import Sequence

from app.geo.haversine import distancia_geodesica
from app.geo.projecao import distancia_projetada
from app.models.evento import Evento
from app.models.resultado import ParMaisProximo


def forca_bruta(pontos: Sequence[Evento]) -> ParMaisProximo:
    """Compara todos os n(n − 1)/2 pares no plano projetado. Θ(n²)."""
    if len(pontos) < 2:
        raise ValueError("São necessários pelo menos 2 eventos")

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

    a, b = melhor
    return ParMaisProximo(a, b, menor, distancia_geodesica(a, b), comparacoes)
