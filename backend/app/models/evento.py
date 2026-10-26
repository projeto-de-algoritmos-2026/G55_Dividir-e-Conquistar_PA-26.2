from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class Evento:
    """Terremoto do catálogo. x e y são as coordenadas projetadas, em km."""

    id: str
    data: datetime
    latitude: float
    longitude: float
    profundidade: float
    magnitude: float
    local: str
    x: float = 0.0
    y: float = 0.0

    @classmethod
    def de_linha(cls, linha: Mapping[str, str]) -> "Evento":
        """Converte uma linha do catálogo reduzido (colunas do formato USGS)."""
        data = datetime.fromisoformat(linha["time"])
        if data.tzinfo is None:
            # Catálogos importados sem fuso: o USGS publica em UTC
            data = data.replace(tzinfo=timezone.utc)
        return cls(
            id=linha["id"],
            data=data,
            latitude=float(linha["latitude"]),
            longitude=float(linha["longitude"]),
            profundidade=float(linha["depth"]),
            magnitude=float(linha["mag"]),
            local=linha.get("place") or "",
        )
