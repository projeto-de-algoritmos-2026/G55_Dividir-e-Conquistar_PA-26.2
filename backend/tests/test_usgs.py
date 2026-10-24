from datetime import datetime, timedelta, timezone

from app.services.usgs import LIMITE, planejar_janelas

INICIO = datetime(2020, 1, 1, tzinfo=timezone.utc)
FIM = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _contador_uniforme(total):
    """Simula `total` eventos distribuídos uniformemente em [INICIO, FIM)."""
    duracao = FIM - INICIO

    def contar(inicio, fim):
        return round(total * ((fim - inicio) / duracao))

    return contar


def test_janela_unica_quando_abaixo_do_limite():
    assert planejar_janelas(INICIO, FIM, _contador_uniforme(LIMITE)) == [(INICIO, FIM)]


def test_divide_quando_acima_do_limite():
    contar = _contador_uniforme(50_000)
    janelas = planejar_janelas(INICIO, FIM, contar)

    assert len(janelas) == 4
    assert all(contar(inicio, fim) <= LIMITE for inicio, fim in janelas)
    assert janelas[0][0] == INICIO and janelas[-1][1] == FIM
    assert all(anterior[1] == atual[0] for anterior, atual in zip(janelas, janelas[1:]))


def test_divide_so_onde_ha_concentracao():
    # 30.000 eventos no primeiro dia (sequência de réplicas) e quase nada depois
    fim_pico = INICIO + timedelta(days=1)

    def contar(inicio, fim):
        sobreposicao = max(timedelta(0), min(fim, fim_pico) - max(inicio, INICIO))
        return round(30_000 * (sobreposicao / timedelta(days=1)))

    janelas = planejar_janelas(INICIO, FIM, contar)

    assert all(contar(inicio, fim) <= LIMITE for inicio, fim in janelas)
    assert janelas[0][0] == INICIO and janelas[-1][1] == FIM
    # A divisão se aprofunda só no começo: a última janela continua longa
    assert janelas[-1][1] - janelas[-1][0] > timedelta(days=365)
