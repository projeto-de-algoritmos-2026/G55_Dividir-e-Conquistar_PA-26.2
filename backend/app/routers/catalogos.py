from fastapi import APIRouter, File, UploadFile

from app.limites import LIMITE_IMPORTACAO_BYTES
from app.models.schemas import ImportacaoSaida
from app.routers.conversao import regiao_saida
from app.services import repositorio

router = APIRouter(tags=["catálogos"])


@router.post("/catalogos/importar", response_model=ImportacaoSaida)
def importar_catalogo(
    arquivo: UploadFile = File(..., description="CSV no formato do USGS (id, time, latitude, longitude, depth, mag, place)"),
):
    """Importa um catálogo próprio. Fica só em memória; o id devolvido vale como `regiao_id`."""
    # Lê um byte além do limite para detectar arquivo grande sem carregar tudo
    conteudo = arquivo.file.read(LIMITE_IMPORTACAO_BYTES + 1)
    catalogo = repositorio.importar_csv(conteudo, arquivo.filename)
    return ImportacaoSaida(
        regiao=regiao_saida(catalogo),
        mensagem=f"{len(catalogo.eventos)} evento(s) importado(s); use '{catalogo.id}' como regiao_id",
    )
