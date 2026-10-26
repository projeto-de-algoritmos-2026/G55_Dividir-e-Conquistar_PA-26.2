import pytest
from fastapi.testclient import TestClient

from app.limites import LIMITE_FORCA_BRUTA_BENCHMARK, LIMITE_VERIFICACAO_GEODESICA
from app.main import app

cliente = TestClient(app)


def test_par_mais_proximo_turquia():
    corpo = cliente.post("/api/par-mais-proximo", json={"regiao_id": "turquia"}).json()

    assert {corpo["a"]["id"], corpo["b"]["id"]} == {"us6000jpkt", "us6000jpff"}
    assert corpo["distancia_projetada_km"] == pytest.approx(0.0925, abs=1e-4)
    assert corpo["n"] == 1509 and corpo["comparacoes"] > 0
    verificacao = corpo["verificacao_geodesica"]
    assert verificacao["status"] == "confirmado"
    assert verificacao["limite_eventos"] == LIMITE_VERIFICACAO_GEODESICA


def test_par_mais_proximo_grande_nao_verificado():
    corpo = cliente.post("/api/par-mais-proximo", json={"regiao_id": "california"}).json()

    assert corpo["n"] > LIMITE_VERIFICACAO_GEODESICA
    assert corpo["verificacao_geodesica"]["status"] == "nao_verificado"
    assert corpo["verificacao_geodesica"]["par_geodesico"] is None


def test_filtros_que_deixam_menos_de_dois_eventos():
    resposta = cliente.post("/api/par-mais-proximo", json={"regiao_id": "turquia", "magnitude_min": 9.9})

    assert resposta.status_code == 422
    assert resposta.json()["detail"].startswith("São necessários pelo menos 2 eventos")


def test_regiao_id_obrigatorio():
    resposta = cliente.post("/api/par-mais-proximo", json={})

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == [{"campo": "corpo.regiao_id", "mensagem": "campo obrigatório"}]


def test_passo_a_passo():
    corpo = cliente.post(
        "/api/passo-a-passo", json={"regiao_id": "japao", "tamanho_amostra": 30, "semente": 7}
    ).json()

    assert corpo["n_amostra"] == 30 == len(corpo["eventos"]) and corpo["n_filtrados"] == 3695
    raiz = corpo["passos"][-1]
    assert raiz["profundidade"] == 0 and len(raiz["ids"]) == 30
    assert raiz["par"] == corpo["resultado"]["par"]
    assert raiz["distancia"] == corpo["resultado"]["distancia_projetada_km"]


def test_passo_a_passo_amostra_reprodutivel():
    requisicao = {"regiao_id": "chile", "tamanho_amostra": 20, "semente": 3}
    primeira = cliente.post("/api/passo-a-passo", json=requisicao).json()
    segunda = cliente.post("/api/passo-a-passo", json=requisicao).json()

    assert primeira == segunda


def test_passo_a_passo_acima_do_limite():
    resposta = cliente.post("/api/passo-a-passo", json={"regiao_id": "japao", "tamanho_amostra": 201})

    assert resposta.status_code == 422
    assert resposta.json()["detail"][0]["mensagem"] == "deve ser menor ou igual a 200"


def test_comparativo():
    corpo = cliente.post("/api/comparativo", json={"regiao_id": "turquia"}).json()

    assert [item["algoritmo"] for item in corpo["itens"]] == [
        "forca_bruta",
        "closest_pair_nlog2n",
        "closest_pair_nlogn",
    ]
    assert all(item["executado"] for item in corpo["itens"])
    assert corpo["mesma_distancia"]
    forca_bruta = corpo["itens"][0]
    assert forca_bruta["comparacoes"] == 1509 * 1508 // 2


def test_validar():
    corpo = cliente.post("/api/validar", json={"instancias": 20, "n_max": 100}).json()

    assert corpo["instancias"] == corpo["aprovadas"] == 20
    assert corpo["falhas"] == []


def test_benchmark():
    corpo = cliente.get("/api/benchmark", params={"tamanhos": [100, 3000], "repeticoes": 1}).json()

    medidos = {(m["n"], m["algoritmo"]) for m in corpo["medicoes"]}
    assert (100, "forca_bruta") in medidos and (3000, "closest_pair_nlogn") in medidos
    # Força bruta respeita o teto
    assert (3000, "forca_bruta") not in medidos and 3000 > LIMITE_FORCA_BRUTA_BENCHMARK
    assert all(len(m["tempos_ms"]) == 1 for m in corpo["medicoes"])


def test_benchmark_fora_dos_limites():
    assert cliente.get("/api/benchmark", params={"tamanhos": [50000]}).status_code == 422
    assert cliente.get("/api/benchmark", params={"repeticoes": 9}).status_code == 422
