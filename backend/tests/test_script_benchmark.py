import csv

from scripts.benchmark import gerar_grafico, salvar_csv


def test_salvar_csv_preserva_repeticoes_e_comparacoes(tmp_path):
    caminho = tmp_path / "benchmark.csv"
    linhas = [
        {
            "n": 100,
            "algoritmo": "closest_pair_nlogn",
            "semente": 42,
            "repeticoes": 3,
            "tempo_1_ms": 1.0,
            "tempo_2_ms": 2.0,
            "tempo_3_ms": 3.0,
            "tempo_medio_ms": 2.0,
            "comparacoes": 40,
        }
    ]

    salvar_csv(linhas, caminho, 3)

    with caminho.open(newline="", encoding="utf-8") as arquivo:
        resultado = next(csv.DictReader(arquivo))
    assert resultado["tempo_1_ms"] == "1.0"
    assert resultado["tempo_medio_ms"] == "2.0"
    assert resultado["comparacoes"] == "40"


def test_gerar_grafico_produz_svg_com_series_e_legenda(tmp_path):
    linhas = [
        {
            "n": 100,
            "algoritmo": "closest_pair_nlogn",
            "tempo_medio_ms": 1.0,
            "comparacoes": 40,
        },
        {
            "n": 1000,
            "algoritmo": "closest_pair_nlogn",
            "tempo_medio_ms": 10.0,
            "comparacoes": 400,
        },
    ]
    caminho = tmp_path / "tempo.svg"

    gerar_grafico(linhas, caminho, "tempo", "Tempo de execução", "Tempo médio (ms)")

    conteudo = caminho.read_text(encoding="utf-8")
    assert '<svg' in conteudo
    assert "Tempo de execução" in conteudo
    assert "Sort_and_Closest-Pair" in conteudo
