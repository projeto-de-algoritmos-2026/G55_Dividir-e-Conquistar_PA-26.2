import math

from app.models.evento import Evento

# Raio médio da Terra (IUGG). A projeção usa a mesma esfera.
RAIO_TERRA_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância de grande círculo entre dois pontos dados em graus."""
    fi1, fi2 = math.radians(lat1), math.radians(lat2)
    delta_fi = fi2 - fi1
    delta_lambda = math.radians(lon2 - lon1)
    h = (
        math.sin(delta_fi / 2) ** 2
        + math.cos(fi1) * math.cos(fi2) * math.sin(delta_lambda / 2) ** 2
    )
    # min() protege contra h levemente acima de 1 por arredondamento (antípodas)
    return 2 * RAIO_TERRA_KM * math.asin(math.sqrt(min(1.0, h)))


def distancia_geodesica(a: Evento, b: Evento) -> float:
    return haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)
