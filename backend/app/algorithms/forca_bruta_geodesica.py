import math
from collections.abc import Sequence

from app.geo.haversine import distancia_geodesica
from app.geo.projecao import distancia_projetada
from app.models.evento import Evento
from app.models.resultado import ParMaisProximo


def forca_bruta_geodesica(eventos: Sequence[Evento]) -> ParMaisProximo:
    """Compara todos os pares pela distância de Haversine, sem projeção. Θ(n²)."""
    if len(eventos) < 2:
        raise ValueError("São necessários pelo menos 2 eventos")

    menor = math.inf
    melhor = (eventos[0], eventos[1])
    comparacoes = 0
    for i in range(len(eventos)):
        for j in range(i + 1, len(eventos)):
            distancia = distancia_geodesica(eventos[i], eventos[j])
            comparacoes += 1
            # Estrito: em empate, mantém o primeiro par encontrado
            if distancia < menor:
                menor = distancia
                melhor = (eventos[i], eventos[j])

    a, b = melhor
    return ParMaisProximo(a, b, distancia_projetada(a, b), menor, comparacoes)
