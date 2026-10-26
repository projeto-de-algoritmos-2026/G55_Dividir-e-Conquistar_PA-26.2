"""500 instâncias aleatórias reprodutíveis: Closest Pair contra força bruta."""

import pytest

from app.services.aleatorios import validar_aleatorio

INSTANCIAS = 500


def test_500_instancias_aleatorias():
    relatorio = validar_aleatorio(INSTANCIAS, n_max=300)

    assert relatorio.instancias == INSTANCIAS
    if relatorio.falhas:
        linhas = [
            f"semente={f.semente} {f.distribuicao} n={f.n} {f.algoritmo}: {f.obtido} != {f.esperado}"
            for f in relatorio.falhas[:20]
        ]
        pytest.fail(f"{len(relatorio.falhas)} divergência(s):\n" + "\n".join(linhas))
    assert relatorio.aprovadas == INSTANCIAS
