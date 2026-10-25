from app.geo.projecao import projetar_eventos
from app.models.evento import Evento
from app.services.catalogo import DIRETORIO_DADOS, ler_csv
from app.services.regioes import REGIOES


def carregar_eventos(id_regiao: str) -> list[Evento]:
    """Lê o catálogo versionado da região e devolve os eventos já projetados."""
    regiao = REGIOES[id_regiao]
    _, linhas = ler_csv(DIRETORIO_DADOS / f"{id_regiao}.csv")
    return projetar_eventos([Evento.de_linha(linha) for linha in linhas], regiao)
