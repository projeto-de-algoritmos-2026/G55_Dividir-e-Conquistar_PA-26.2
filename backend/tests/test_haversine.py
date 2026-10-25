import math

import pytest

from app.geo.haversine import RAIO_TERRA_KM, distancia_geodesica, haversine_km
from tests.fabricas import evento


def test_mesmo_ponto_tem_distancia_zero():
    assert haversine_km(35.0, 139.0, 35.0, 139.0) == 0.0


def test_um_grau_de_latitude():
    assert haversine_km(0.0, 0.0, 1.0, 0.0) == pytest.approx(RAIO_TERRA_KM * math.pi / 180)


def test_um_grau_de_longitude_encolhe_com_a_latitude():
    no_equador = haversine_km(0.0, 0.0, 0.0, 1.0)
    a_60_graus = haversine_km(60.0, 0.0, 60.0, 1.0)

    assert a_60_graus == pytest.approx(no_equador / 2, rel=1e-4)


def test_antipodas():
    assert haversine_km(10.0, 20.0, -10.0, -160.0) == pytest.approx(math.pi * RAIO_TERRA_KM)


def test_simetria():
    assert haversine_km(35.68, 139.69, -33.45, -70.67) == haversine_km(-33.45, -70.67, 35.68, 139.69)


def test_toquio_osaka():
    # Distância de grande círculo de referência ≈ 397 km
    assert haversine_km(35.6895, 139.6917, 34.6937, 135.5023) == pytest.approx(397, abs=5)


def test_distancia_geodesica_entre_eventos():
    a = evento("a", lat=0.0, lon=0.0)
    b = evento("b", lat=1.0, lon=0.0)

    assert distancia_geodesica(a, b) == pytest.approx(haversine_km(0.0, 0.0, 1.0, 0.0))
