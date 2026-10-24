from app.services.catalogo import COLUNAS, validar_catalogo
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos


def test_mesma_semente_gera_mesmos_eventos():
    assert gerar_eventos(200, 42, REGIOES["chile"]) == gerar_eventos(200, 42, REGIOES["chile"])


def test_sementes_diferentes_geram_eventos_diferentes():
    assert gerar_eventos(200, 42, REGIOES["chile"]) != gerar_eventos(200, 7, REGIOES["chile"])


def test_eventos_sinteticos_sao_validos_e_dentro_da_regiao():
    regiao = REGIOES["turquia"]
    eventos = gerar_eventos(500, 1, regiao)
    relatorio = validar_catalogo(eventos, COLUNAS, regiao)

    assert relatorio.valido
    assert relatorio.total == 500
