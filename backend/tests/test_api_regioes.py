from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_lista_as_quatro_regioes():
    resposta = cliente.get("/api/regioes")

    assert resposta.status_code == 200
    totais = {r["id"]: r["total_eventos"] for r in resposta.json() if not r["importado"]}
    assert totais == {"japao": 3695, "chile": 4557, "california": 7714, "turquia": 1509}


def test_regiao_traz_caixa_centro_e_periodo():
    turquia = next(r for r in cliente.get("/api/regioes").json() if r["id"] == "turquia")

    assert turquia["caixa"] == {"lat_min": 35.0, "lat_max": 43.0, "lon_min": 25.0, "lon_max": 45.0}
    assert turquia["centro"] == {"latitude": 39.0, "longitude": 35.0}
    assert turquia["inicio"] >= "2020-01-01" and turquia["fim"] <= "2024-12-31"


def test_eventos_sem_filtro():
    corpo = cliente.get("/api/regioes/turquia/eventos").json()

    assert corpo["total"] == 1509 == len(corpo["eventos"])
    assert {"id", "data", "latitude", "longitude", "profundidade", "magnitude", "local", "x", "y"} <= set(
        corpo["eventos"][0]
    )


def test_eventos_com_filtros():
    corpo = cliente.get(
        "/api/regioes/turquia/eventos",
        params={"inicio": "2023-02-06", "fim": "2023-02-06", "magnitude_min": 5, "profundidade_max": 15},
    ).json()

    assert corpo["total"] > 0
    for evento in corpo["eventos"]:
        assert evento["data"].startswith("2023-02-06")
        assert evento["magnitude"] >= 5 and evento["profundidade"] <= 15


def test_regiao_inexistente():
    resposta = cliente.get("/api/regioes/marte/eventos")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Região ou catálogo 'marte' não encontrado"


def test_periodo_invertido_em_portugues():
    resposta = cliente.get("/api/regioes/turquia/eventos", params={"inicio": "2024-01-01", "fim": "2023-01-01"})

    assert resposta.status_code == 422
    assert "data final deve ser igual ou posterior" in resposta.json()["detail"][0]["mensagem"]


def test_magnitude_e_data_invalidas_em_portugues():
    resposta = cliente.get("/api/regioes/turquia/eventos", params={"magnitude_min": 11, "inicio": "ontem"})

    mensagens = {erro["campo"]: erro["mensagem"] for erro in resposta.json()["detail"]}
    assert resposta.status_code == 422
    assert mensagens["consulta.magnitude_min"] == "deve ser menor ou igual a 10"
    assert mensagens["consulta.inicio"] == "data inválida, use o formato AAAA-MM-DD"
