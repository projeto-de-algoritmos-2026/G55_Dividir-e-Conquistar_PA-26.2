import math

import pytest

from app.geo.haversine import haversine_km
from app.geo.projecao import distancia_projetada, projetar_eventos
from app.models.evento import Evento
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos
from tests.fabricas import evento


def test_centro_da_regiao_vai_para_a_origem():
    regiao = REGIOES["japao"]
    lat, lon = regiao.centro
    (projetado,) = projetar_eventos([evento("c", lat=lat, lon=lon)], regiao)

    assert projetado.x == pytest.approx(0.0, abs=1e-9)
    assert projetado.y == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("id_regiao", list(REGIOES))
def test_distancia_a_partir_do_centro_igual_a_geodesica(id_regiao):
    regiao = REGIOES[id_regiao]
    lat_c, lon_c = regiao.centro
    eventos = [Evento.de_linha(linha) for linha in gerar_eventos(500, 7, regiao)]

    for projetado in projetar_eventos(eventos, regiao):
        geodesica = haversine_km(lat_c, lon_c, projetado.latitude, projetado.longitude)
        assert math.hypot(projetado.x, projetado.y) == pytest.approx(geodesica, abs=1e-6)


def test_orientacao_dos_eixos():
    regiao = REGIOES["chile"]
    lat, lon = regiao.centro
    norte, leste = projetar_eventos(
        [evento("n", lat=lat + 1, lon=lon), evento("l", lat=lat, lon=lon + 1)], regiao
    )

    assert norte.x == pytest.approx(0.0, abs=1e-9) and norte.y > 0
    assert leste.x > 0 and leste.y == pytest.approx(0.0, abs=1.0)


def test_projecao_preserva_os_demais_campos():
    regiao = REGIOES["turquia"]
    original = Evento.de_linha(gerar_eventos(1, 3, regiao)[0])
    (projetado,) = projetar_eventos([original], regiao)

    assert (projetado.id, projetado.data, projetado.latitude, projetado.longitude) == (
        original.id,
        original.data,
        original.latitude,
        original.longitude,
    )
    assert (original.x, original.y) == (0.0, 0.0)


def test_lista_vazia():
    assert projetar_eventos([], REGIOES["japao"]) == []


def test_distancia_projetada():
    assert distancia_projetada(evento("a", x=0, y=0), evento("b", x=3, y=4)) == 5.0
