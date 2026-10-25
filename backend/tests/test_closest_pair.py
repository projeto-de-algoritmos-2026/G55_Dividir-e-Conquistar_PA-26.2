import pytest

from app.algorithms.closest_pair_comum import VIZINHOS_NA_FAIXA
from app.algorithms.closest_pair_nlog2n import closest_pair_nlog2n
from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.algorithms.forca_bruta import forca_bruta
from app.geo.projecao import projetar_eventos
from app.models.evento import Evento
from app.services.eventos import carregar_eventos
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos
from tests.fabricas import evento

VERSOES = pytest.mark.parametrize(
    "closest_pair", [closest_pair_nlog2n, closest_pair_nlogn], ids=["nlog2n", "nlogn"]
)


def _sinteticos(n, semente, id_regiao="japao"):
    regiao = REGIOES[id_regiao]
    return projetar_eventos([Evento.de_linha(linha) for linha in gerar_eventos(n, semente, regiao)], regiao)


def _ids(resultado):
    return {resultado.a.id, resultado.b.id}


@VERSOES
def test_par_conhecido(closest_pair):
    pontos = [
        evento("a", 0, 0),
        evento("b", 10, 10),
        evento("c", 10.5, 11),
        evento("d", -5, 3),
        evento("e", 20, -4),
        evento("f", 30, 30),
        evento("g", -20, 15),
    ]
    resultado = closest_pair(pontos)

    assert _ids(resultado) == {"b", "c"}
    assert resultado.distancia_projetada_km == pytest.approx(5**0.5 / 2)


@VERSOES
def test_par_que_cruza_a_reta_l(closest_pair):
    # Metades bem espalhadas; o par mais próximo fica um de cada lado de x = 0
    esquerda = [evento(f"e{i}", x=-10 - 10 * i, y=10 * i) for i in range(4)]
    direita = [evento(f"d{i}", x=10 + 10 * i, y=10 * i) for i in range(4)]
    cruzando = [evento("p", x=-0.4, y=50), evento("q", x=0.4, y=50.3)]
    resultado = closest_pair(esquerda + direita + cruzando)

    assert _ids(resultado) == {"p", "q"}


@VERSOES
@pytest.mark.parametrize("n", [2, 3])
def test_apenas_caso_base(closest_pair, n):
    pontos = [evento(str(i), x=i * 2.0, y=i * i) for i in range(n)]
    resultado = closest_pair(pontos)

    assert resultado.distancia_projetada_km == forca_bruta(pontos).distancia_projetada_km
    assert resultado.comparacoes == n * (n - 1) // 2


@VERSOES
@pytest.mark.parametrize("pontos", [[], [evento("a")]])
def test_menos_de_dois_eventos_levanta_erro(closest_pair, pontos):
    with pytest.raises(ValueError, match="pelo menos 2"):
        closest_pair(pontos)


@VERSOES
@pytest.mark.parametrize("semente", [1, 2, 3])
def test_mesma_distancia_que_a_forca_bruta(closest_pair, semente):
    eventos = _sinteticos(200, semente)

    assert closest_pair(eventos).distancia_projetada_km == forca_bruta(eventos).distancia_projetada_km


@VERSOES
def test_faz_bem_menos_comparacoes_que_a_forca_bruta(closest_pair):
    n = 2000
    resultado = closest_pair(_sinteticos(n, 5))

    assert resultado.comparacoes < (n * (n - 1) // 2) / 50


@VERSOES
def test_resultado_traz_distancia_geodesica(closest_pair):
    eventos = _sinteticos(300, 9)

    assert closest_pair(eventos).distancia_geodesica_km == forca_bruta(eventos).distancia_geodesica_km


@VERSOES
def test_registro_da_recursao(closest_pair):
    eventos = _sinteticos(40, 4)
    registro = []
    resultado = closest_pair(eventos, registro=registro)

    raiz = registro[-1]
    assert raiz.profundidade == 0 and raiz.tipo == "combinacao"
    assert set(raiz.ids) == {e.id for e in eventos}
    assert set(raiz.par) == _ids(resultado)
    assert raiz.distancia == resultado.distancia_projetada_km

    for passo in registro:
        if passo.tipo == "base":
            assert 2 <= len(passo.ids) <= 3 and passo.reta_l is None
        else:
            assert passo.delta == min(passo.delta_esquerdo, passo.delta_direito)
            assert passo.distancia <= passo.delta
            posicao = {id_evento: i for i, id_evento in enumerate(passo.faixa)}
            for id_p, id_q, distancia in passo.comparacoes_faixa:
                assert 0 < posicao[id_q] - posicao[id_p] <= VIZINHOS_NA_FAIXA

    # Folhas somam todos os eventos, sem repetição
    folhas = [id_evento for passo in registro if passo.tipo == "base" for id_evento in passo.ids]
    assert sorted(folhas) == sorted(e.id for e in eventos)


@VERSOES
def test_registro_e_opcional(closest_pair):
    eventos = _sinteticos(40, 4)

    sem = closest_pair(eventos)
    com = closest_pair(eventos, registro=[])

    assert sem == com


def test_as_duas_versoes_concordam():
    eventos = _sinteticos(1000, 8, "chile")

    assert closest_pair_nlogn(eventos) == closest_pair_nlog2n(eventos)


@pytest.mark.parametrize("id_regiao", list(REGIOES))
def test_catalogos_reais(id_regiao):
    """Critério de pronto da Fase 3: mesma distância que a força bruta nos catálogos reais."""
    eventos = carregar_eventos(id_regiao)
    esperado = forca_bruta(eventos).distancia_projetada_km

    assert closest_pair_nlogn(eventos).distancia_projetada_km == esperado
    assert closest_pair_nlog2n(eventos).distancia_projetada_km == esperado
