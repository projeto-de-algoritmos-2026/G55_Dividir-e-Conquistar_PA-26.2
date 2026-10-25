from datetime import datetime, timezone

from app.models.evento import Evento

DATA_FIXA = datetime(2024, 1, 1, tzinfo=timezone.utc)


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
