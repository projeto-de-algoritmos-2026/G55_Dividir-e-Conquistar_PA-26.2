import pytest
from fastapi.testclient import TestClient

from app.limites import LIMITE_CATALOGOS_IMPORTADOS
from app.main import app
from app.services import repositorio

cliente = TestClient(app)

CABECALHO_USGS = "time,latitude,longitude,depth,mag,magType,id,place,type\n"
CSV_VALIDO = CABECALHO_USGS + (
    "2024-01-01T07:10:09.476Z,37.4874,137.2710,10,7.5,mww,a1,\"Noto, Japan\",earthquake\n"
    "2024-01-01T07:18:00.000Z,37.5000,137.3000,12,5.1,mb,a2,\"Noto, Japan\",earthquake\n"
    "2024-01-02T10:00:00.000Z,36.9000,136.8000,8,4.2,mb,a3,\"Noto, Japan\",earthquake\n"
)


@pytest.fixture(autouse=True)
def _sem_importados():
    repositorio.limpar_importados()
    yield
    repositorio.limpar_importados()


def _importar(conteudo: str, nome="meu_catalogo.csv"):
    return cliente.post("/api/catalogos/importar", files={"arquivo": (nome, conteudo.encode(), "text/csv")})


def test_importa_e_usa_como_regiao():
    resposta = _importar(CSV_VALIDO)

    assert resposta.status_code == 200
    regiao = resposta.json()["regiao"]
    assert regiao["importado"] and regiao["nome"] == "meu_catalogo" and regiao["total_eventos"] == 3
    assert regiao["id"].startswith("importado-")

    par = cliente.post("/api/par-mais-proximo", json={"regiao_id": regiao["id"]}).json()
    assert {par["a"]["id"], par["b"]["id"]} == {"a1", "a2"}
    assert par["verificacao_geodesica"]["status"] == "confirmado"
    assert any(r["id"] == regiao["id"] for r in cliente.get("/api/regioes").json())


def test_csv_com_erros_aponta_linha_e_coluna():
    conteudo = CABECALHO_USGS + (
        "2024-01-01T00:00:00Z,95,137,10,5,mb,b1,x,earthquake\n"
        "ontem,37,137,10,,mb,b1,x,earthquake\n"
    )
    resposta = _importar(conteudo)

    corpo = resposta.json()
    assert resposta.status_code == 422
    assert corpo["detail"] == "Catálogo inválido: 4 erro(s) encontrado(s)"
    assert {(e["linha"], e["coluna"]) for e in corpo["erros"]} == {
        (2, "latitude"),
        (3, "id"),
        (3, "time"),
        (3, "mag"),
    }


def test_sem_colunas_obrigatorias():
    resposta = _importar("latitude,longitude\n1,2\n")

    assert resposta.status_code == 422
    assert resposta.json()["erros"][0]["mensagem"] == "coluna obrigatória ausente"


def test_caixa_grande_demais():
    conteudo = CABECALHO_USGS + (
        "2024-01-01T00:00:00Z,0,0,10,5,mb,c1,x,earthquake\n"
        "2024-01-01T00:00:00Z,60,10,10,5,mb,c2,x,earthquake\n"
    )
    resposta = _importar(conteudo)

    assert resposta.status_code == 422
    assert "limite regional" in resposta.json()["detail"]


def test_arquivo_que_nao_e_utf8():
    resposta = cliente.post(
        "/api/catalogos/importar", files={"arquivo": ("x.csv", "café".encode("latin-1"), "text/csv")}
    )

    assert resposta.status_code == 422
    assert "UTF-8" in resposta.json()["detail"]


def test_descarta_o_mais_antigo_acima_do_limite():
    ids = [_importar(CSV_VALIDO).json()["regiao"]["id"] for _ in range(LIMITE_CATALOGOS_IMPORTADOS + 1)]

    assert cliente.get(f"/api/regioes/{ids[0]}/eventos").status_code == 404
    assert cliente.get(f"/api/regioes/{ids[-1]}/eventos").status_code == 200
