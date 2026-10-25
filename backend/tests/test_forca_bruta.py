import pytest

from app.algorithms.forca_bruta import forca_bruta
from app.algorithms.forca_bruta_geodesica import forca_bruta_geodesica
from app.geo.haversine import haversine_km
from app.geo.projecao import projetar_eventos
from app.models.evento import Evento
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos
from tests.fabricas import evento


def _ids(resultado):
    return {resultado.a.id, resultado.b.id}


def test_par_conhecido():
    pontos = [
        evento("a", 0, 0),
        evento("b", 10, 10),
        evento("c", 10.5, 11),
        evento("d", -5, 3),
        evento("e", 20, -4),
    ]
    resultado = forca_bruta(pontos)

    assert _ids(resultado) == {"b", "c"}
    assert resultado.distancia_projetada_km == pytest.approx(5**0.5 / 2)


@pytest.mark.parametrize("n", [2, 3, 7, 50])
def test_conta_todas_as_comparacoes(n):
    pontos = [evento(str(i), x=i * 1.5, y=i % 3) for i in range(n)]

    assert forca_bruta(pontos).comparacoes == n * (n - 1) // 2
    assert forca_bruta_geodesica(pontos).comparacoes == n * (n - 1) // 2


def test_pontos_coincidentes_tem_distancia_zero():
    pontos = [evento("a", 1, 1), evento("b", 5, 5), evento("c", 1, 1)]
    resultado = forca_bruta(pontos)

    assert _ids(resultado) == {"a", "c"}
    assert resultado.distancia_projetada_km == 0.0


def test_dois_pontos():
    resultado = forca_bruta([evento("a", 0, 0), evento("b", 3, 4)])

    assert resultado.distancia_projetada_km == 5.0
    assert resultado.comparacoes == 1


@pytest.mark.parametrize("pontos", [[], [evento("a")]])
def test_menos_de_dois_eventos_levanta_erro(pontos):
    with pytest.raises(ValueError, match="pelo menos 2"):
        forca_bruta(pontos)
    with pytest.raises(ValueError, match="pelo menos 2"):
        forca_bruta_geodesica(pontos)


def test_geodesica_par_conhecido():
    eventos = [
        evento("a", lat=35.0, lon=139.0),
        evento("b", lat=35.1, lon=139.1),
        evento("c", lat=36.0, lon=141.0),
        evento("d", lat=33.0, lon=135.0),
    ]
    resultado = forca_bruta_geodesica(eventos)

    assert _ids(resultado) == {"a", "b"}
    assert resultado.distancia_geodesica_km == pytest.approx(haversine_km(35.0, 139.0, 35.1, 139.1))


def test_resultado_traz_as_duas_distancias():
    regiao = REGIOES["japao"]
    eventos = projetar_eventos(
        [Evento.de_linha(linha) for linha in gerar_eventos(50, 1, regiao)], regiao
    )
    resultado = forca_bruta(eventos)

    assert resultado.distancia_geodesica_km == pytest.approx(
        haversine_km(resultado.a.latitude, resultado.a.longitude, resultado.b.latitude, resultado.b.longitude)
    )


def test_plano_e_geodesica_concordam_em_regiao_pequena():
    regiao = REGIOES["turquia"]
    eventos = projetar_eventos(
        [Evento.de_linha(linha) for linha in gerar_eventos(300, 11, regiao)], regiao
    )

    assert _ids(forca_bruta(eventos)) == _ids(forca_bruta_geodesica(eventos))
