import pytest

from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.geo.projecao import projetar_eventos
from app.models.evento import Evento
from app.services.eventos import carregar_eventos
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos
from app.services.verificacao import verificar_geodesica


def _projetados(n, semente, id_regiao):
    regiao = REGIOES[id_regiao]
    return projetar_eventos([Evento.de_linha(linha) for linha in gerar_eventos(n, semente, regiao)], regiao)


def test_confirmado_em_conjunto_pequeno():
    eventos = _projetados(50, 1, "turquia")
    verificacao = verificar_geodesica(eventos, closest_pair_nlogn(eventos))

    assert verificacao.status == "confirmado"
    assert verificacao.diferenca_km == pytest.approx(0.0, abs=1e-6)


def test_nao_verificado_acima_do_limite():
    eventos = _projetados(50, 1, "turquia")
    verificacao = verificar_geodesica(eventos, closest_pair_nlogn(eventos), limite_eventos=49)

    assert verificacao.status == "nao_verificado"
    assert verificacao.par_geodesico is None


def test_divergente_quando_a_projecao_troca_o_par():
    # 8 pontos esparsos no Chile (caixa de 28° de latitude), achados varrendo sementes:
    # no plano vence um par; na esfera, outro, 0,33 km mais perto.
    eventos = _projetados(8, 246, "chile")
    resultado = closest_pair_nlogn(eventos)
    verificacao = verificar_geodesica(eventos, resultado)

    assert verificacao.status == "divergente"
    assert verificacao.diferenca_km == pytest.approx(0.33, abs=0.01)
    assert {e.id for e in verificacao.par_geodesico} != {resultado.a.id, resultado.b.id}


@pytest.mark.lento
@pytest.mark.parametrize("id_regiao", list(REGIOES))
def test_catalogos_reais(id_regiao):
    eventos = carregar_eventos(id_regiao)
    verificacao = verificar_geodesica(eventos, closest_pair_nlogn(eventos))

    assert verificacao.status in {"confirmado", "divergente"}
    # O mínimo geodésico nunca é maior que a geodésica do par do plano
    assert verificacao.diferenca_km >= -1e-6
