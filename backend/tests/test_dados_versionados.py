import pytest

from app.services.catalogo import DIRETORIO_DADOS, ler_csv, validar_catalogo
from app.services.regioes import REGIOES


@pytest.mark.parametrize("id_regiao", list(REGIOES))
def test_catalogo_versionado_existe_e_e_valido(id_regiao):
    caminho = DIRETORIO_DADOS / f"{id_regiao}.csv"
    assert caminho.exists(), f"rode scripts/baixar_catalogo.py --regiao {id_regiao}"

    colunas, linhas = ler_csv(caminho)
    relatorio = validar_catalogo(linhas, colunas, REGIOES[id_regiao])

    assert relatorio.valido, relatorio.erros[:5]
    assert relatorio.total > 0
