from dataclasses import dataclass

from app.models.evento import Evento


@dataclass(frozen=True)
class ParMaisProximo:
    """Resposta padronizada de todas as versões do par mais próximo."""

    a: Evento
    b: Evento
    distancia_projetada_km: float
    distancia_geodesica_km: float
    comparacoes: int
