import math
from collections.abc import Sequence
from dataclasses import replace

from pyproj import Proj

from app.geo.haversine import RAIO_TERRA_KM
from app.models.evento import Evento
from app.services.regioes import Regiao


def criar_projecao(centro: tuple[float, float]) -> Proj:
    """Azimutal equidistante centrada em (latitude, longitude), saída em km.

    Usa a mesma esfera do Haversine, então a distância projetada a partir do
    centro coincide com a geodésica.
    """
    latitude, longitude = centro
    # No PROJ o raio R é sempre em metros; units="km" vale só para a saída
    return Proj(
        proj="aeqd", lat_0=latitude, lon_0=longitude, R=RAIO_TERRA_KM * 1000, units="km"
    )


def projetar_eventos(eventos: Sequence[Evento], regiao: Regiao) -> list[Evento]:
    """Devolve cópias dos eventos com x e y preenchidos no plano da região."""
    if not eventos:
        return []
    projecao = criar_projecao(regiao.centro)
    xs, ys = projecao(
        [evento.longitude for evento in eventos], [evento.latitude for evento in eventos]
    )
    return [
        replace(evento, x=float(x), y=float(y)) for evento, x, y in zip(eventos, xs, ys)
    ]


def distancia_projetada(a: Evento, b: Evento) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)
