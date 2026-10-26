from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.algorithms.forca_bruta_geodesica import forca_bruta_geodesica
from app.models.evento import Evento
from app.models.resultado import ParMaisProximo

StatusVerificacao = Literal["confirmado", "nao_verificado", "divergente"]

# 1 mm: abaixo disso a diferença é arredondamento, não efeito da projeção
TOLERANCIA_KM = 1e-6


@dataclass(frozen=True)
class VerificacaoGeodesica:
    status: StatusVerificacao
    par_geodesico: tuple[Evento, Evento] | None = None
    distancia_geodesica_minima_km: float | None = None
    # Geodésica do par do plano menos a mínima geodésica (>= 0)
    diferenca_km: float | None = None


def verificar_geodesica(
    eventos: Sequence[Evento],
    resultado: ParMaisProximo,
    limite_eventos: int | None = None,
    tolerancia_km: float = TOLERANCIA_KM,
) -> VerificacaoGeodesica:
    """Confere, com força bruta Haversine, se a projeção mudou o par mais próximo.

    Diverge quando o par escolhido no plano está mais longe, na esfera, do que o
    par geodesicamente mais próximo. Pares diferentes empatados contam como
    confirmados.
    """
    if limite_eventos is not None and len(eventos) > limite_eventos:
        return VerificacaoGeodesica("nao_verificado")

    geodesico = forca_bruta_geodesica(eventos)
    diferenca = resultado.distancia_geodesica_km - geodesico.distancia_geodesica_km
    status: StatusVerificacao = "divergente" if diferenca > tolerancia_km else "confirmado"
    return VerificacaoGeodesica(
        status,
        (geodesico.a, geodesico.b),
        geodesico.distancia_geodesica_km,
        diferenca,
    )
