from typing import Annotated

from fastapi import APIRouter, Query

from app.models.schemas import Filtros, ListaEventos, RegiaoSaida
from app.routers.conversao import evento_saida, regiao_saida
from app.services import repositorio
from app.services.filtros import filtrar

router = APIRouter(tags=["regiões"])


@router.get("/regioes", response_model=list[RegiaoSaida])
def listar_regioes():
    """Regiões pré-configuradas e catálogos importados, com período e número de eventos."""
    return [regiao_saida(catalogo) for catalogo in repositorio.listar()]


@router.get("/regioes/{regiao_id}/eventos", response_model=ListaEventos)
def listar_eventos(regiao_id: str, filtros: Annotated[Filtros, Query()]):
    """Eventos da região com filtros opcionais de período, magnitude e profundidade."""
    eventos = filtrar(repositorio.obter(regiao_id).eventos, filtros)
    return ListaEventos(
        regiao_id=regiao_id, total=len(eventos), eventos=[evento_saida(e) for e in eventos]
    )
