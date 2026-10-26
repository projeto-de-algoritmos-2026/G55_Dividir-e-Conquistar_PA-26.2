from collections.abc import Iterable
from datetime import datetime, time, timedelta, timezone

from app.erros import ErroNegocio
from app.models.evento import Evento
from app.models.schemas import Filtros


def filtrar(eventos: Iterable[Evento], filtros: Filtros) -> list[Evento]:
    """Aplica período (datas inclusivas, em UTC), magnitude mínima e profundidade máxima."""
    inicio = (
        datetime.combine(filtros.inicio, time.min, tzinfo=timezone.utc) if filtros.inicio else None
    )
    fim = (
        datetime.combine(filtros.fim + timedelta(days=1), time.min, tzinfo=timezone.utc)
        if filtros.fim
        else None
    )
    return [
        evento
        for evento in eventos
        if (inicio is None or evento.data >= inicio)
        and (fim is None or evento.data < fim)
        and (filtros.magnitude_min is None or evento.magnitude >= filtros.magnitude_min)
        and (filtros.profundidade_max is None or evento.profundidade <= filtros.profundidade_max)
    ]


def exigir_dois(eventos: list[Evento]) -> list[Evento]:
    if len(eventos) < 2:
        raise ErroNegocio(
            422,
            f"São necessários pelo menos 2 eventos após os filtros; encontrado(s): {len(eventos)}",
        )
    return eventos
