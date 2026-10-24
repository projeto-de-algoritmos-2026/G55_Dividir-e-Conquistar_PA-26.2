import random
from datetime import datetime, timedelta, timezone

from app.services.regioes import Regiao

INICIO_SINTETICO = datetime(2024, 1, 1, tzinfo=timezone.utc)


def gerar_eventos(n: int, semente: int, regiao: Regiao) -> list[dict[str, str]]:
    """Eventos aleatórios uniformes na caixa da região, no mesmo formato do catálogo real."""
    if n < 0:
        raise ValueError("n deve ser não negativo")
    gerador = random.Random(semente)
    eventos = []
    for i in range(1, n + 1):
        instante = INICIO_SINTETICO + timedelta(minutes=i)
        eventos.append(
            {
                "id": f"sint-{i:06d}",
                "time": instante.isoformat().replace("+00:00", "Z"),
                "latitude": f"{gerador.uniform(regiao.lat_min, regiao.lat_max):.4f}",
                "longitude": f"{gerador.uniform(regiao.lon_min, regiao.lon_max):.4f}",
                "depth": f"{gerador.uniform(0, 100):.3f}",
                "mag": f"{gerador.uniform(2.5, 7.0):.1f}",
                "place": f"Evento sintético {i} ({regiao.nome})",
            }
        )
    return eventos
