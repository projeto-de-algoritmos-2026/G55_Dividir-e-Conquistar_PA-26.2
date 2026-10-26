from collections.abc import Iterable
from datetime import datetime, timezone

import pytest

from app.algorithms.closest_pair_nlog2n import closest_pair_nlog2n
from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.models.evento import Evento

DATA_FIXA = datetime(2024, 1, 1, tzinfo=timezone.utc)

# Roda o teste nas duas versões de divisão e conquista
VERSOES = pytest.mark.parametrize(
    "closest_pair", [closest_pair_nlog2n, closest_pair_nlogn], ids=["nlog2n", "nlogn"]
)


def evento(id: str, x: float = 0.0, y: float = 0.0, lat: float = 0.0, lon: float = 0.0) -> Evento:
    """Evento mínimo para testes, com coordenadas planas e geográficas à escolha."""
    return Evento(
        id=id,
        data=DATA_FIXA,
        latitude=lat,
        longitude=lon,
        profundidade=10.0,
        magnitude=3.0,
        local="teste",
        x=x,
        y=y,
    )


def pontos(coordenadas: Iterable[tuple[float, float]]) -> list[Evento]:
    """Eventos p0, p1, ... nas coordenadas planas dadas."""
    return [evento(f"p{i}", x, y) for i, (x, y) in enumerate(coordenadas)]
