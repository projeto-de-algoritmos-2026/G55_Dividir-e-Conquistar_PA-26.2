from app.algorithms.forca_bruta import forca_bruta
from tests.fabricas import VERSOES, pontos


def _confere(closest_pair, eventos):
    """Mesma distância mínima que a força bruta."""
    resultado = closest_pair(eventos)
    assert resultado.distancia_projetada_km == forca_bruta(eventos).distancia_projetada_km
    return resultado


@VERSOES
def test_dois_pontos(closest_pair):
    _confere(closest_pair, pontos([(0, 0), (3, 4)]))


@VERSOES
def test_tres_pontos(closest_pair):
    _confere(closest_pair, pontos([(0, 0), (10, 0), (4, 1)]))


@VERSOES
def test_n_impar(closest_pair):
    for n in (5, 7, 101):
        _confere(closest_pair, pontos((i * 7.3 % 11, i * 3.1 % 13) for i in range(n)))


@VERSOES
def test_todos_com_o_mesmo_x(closest_pair):
    # A reta L passa por todos os pontos em toda divisão
    _confere(closest_pair, pontos((5, y) for y in (40, 3, 17, 9, 25, 1, 33, 12, 50, 8.5)))


@VERSOES
def test_todos_com_o_mesmo_y(closest_pair):
    _confere(closest_pair, pontos((x, -2) for x in (40, 3, 17, 9, 25, 1, 33, 12, 50, 8.5)))


@VERSOES
def test_pares_coincidentes_espalhados(closest_pair):
    coordenadas = [(0, 0), (100, 100), (50, 20), (50, 20), (-30, 70), (90, -10), (-30, 70)]
    resultado = _confere(closest_pair, pontos(coordenadas))

    assert resultado.distancia_projetada_km == 0.0


@VERSOES
def test_todos_os_pontos_identicos(closest_pair):
    resultado = _confere(closest_pair, pontos([(7, 7)] * 20))

    assert resultado.distancia_projetada_km == 0.0


@VERSOES
def test_grade_com_muitos_empates(closest_pair):
    resultado = _confere(closest_pair, pontos((x, y) for x in range(8) for y in range(8)))

    assert resultado.distancia_projetada_km == 1.0


@VERSOES
def test_varios_pontos_sobre_a_reta_l(closest_pair):
    # 8 pontos: os 4 do meio da ordem por x têm x = 0 e caem dos dois lados da divisão
    coordenadas = [(-50, 0), (-40, 30), (0, 0), (0, 10), (0, 20), (0, 30), (40, 5), (50, 25)]
    resultado = _confere(closest_pair, pontos(coordenadas))

    assert resultado.distancia_projetada_km == 10.0


@VERSOES
def test_par_vencedor_cruza_l_com_empate_em_x(closest_pair):
    # p3 e p4 têm o mesmo x e ficam em lados opostos da divisão por posição
    coordenadas = [(-30, 0), (-20, 40), (-10, 80), (0, 50), (0, 50.5), (10, 0), (20, 40), (30, 80)]
    resultado = _confere(closest_pair, pontos(coordenadas))

    assert {resultado.a.id, resultado.b.id} == {"p3", "p4"}


@VERSOES
def test_coordenadas_negativas_e_muito_proximas(closest_pair):
    coordenadas = [(-1000.0, -1000.0), (-1000.0 + 1e-9, -1000.0), (-500.0, -999.0), (-1e-9, -1e-9), (0.0, 0.0)]
    resultado = _confere(closest_pair, pontos(coordenadas))

    assert resultado.distancia_projetada_km < 1e-8
