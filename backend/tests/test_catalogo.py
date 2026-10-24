from app.services.catalogo import COLUNAS, reduzir_linha, validar_catalogo
from app.services.regioes import REGIOES


def _evento(**alteracoes):
    evento = {
        "id": "us1",
        "time": "2024-01-01T07:10:09.476Z",
        "latitude": "37.4874",
        "longitude": "137.2710",
        "depth": "10",
        "mag": "7.5",
        "place": "Noto Peninsula, Japan",
    }
    return {**evento, **alteracoes}


def _colunas_com_erro(relatorio):
    return [erro.coluna for erro in relatorio.erros]


def test_catalogo_valido():
    linhas = [_evento(), _evento(id="us2")]
    relatorio = validar_catalogo(linhas, COLUNAS, REGIOES["japao"])

    assert relatorio.valido
    assert relatorio.total == 2


def test_coluna_obrigatoria_ausente():
    colunas = [coluna for coluna in COLUNAS if coluna != "mag"]
    relatorio = validar_catalogo([], colunas)

    assert not relatorio.valido
    assert relatorio.erros[0].coluna == "mag"


def test_coordenadas_fora_do_intervalo():
    relatorio = validar_catalogo(
        [_evento(latitude="91"), _evento(id="us2", longitude="-181")], COLUNAS
    )

    assert _colunas_com_erro(relatorio) == ["latitude", "longitude"]
    assert [erro.linha for erro in relatorio.erros] == [2, 3]


def test_valores_nao_numericos_e_data_invalida():
    relatorio = validar_catalogo([_evento(mag="forte", depth="", time="ontem")], COLUNAS)

    assert sorted(_colunas_com_erro(relatorio)) == ["depth", "mag", "time"]


def test_id_duplicado():
    relatorio = validar_catalogo([_evento(), _evento()], COLUNAS)

    assert _colunas_com_erro(relatorio) == ["id"]
    assert "linha 2" in relatorio.erros[0].mensagem


def test_ponto_fora_da_regiao():
    relatorio = validar_catalogo([_evento(latitude="-33.4", longitude="-70.6")], COLUNAS, REGIOES["japao"])

    assert _colunas_com_erro(relatorio) == ["latitude/longitude"]


def test_reduzir_linha_mantem_so_colunas_usadas():
    bruta = {**_evento(), "magType": "mww", "net": "us"}

    assert reduzir_linha(bruta) == _evento()


def test_reduzir_linha_descarta_sem_magnitude():
    assert reduzir_linha(_evento(mag="")) is None
