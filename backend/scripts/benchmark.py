"""Mede os três algoritmos em instâncias sintéticas e gera CSVs e gráficos SVG.

Uso (a partir de backend/):
    uv run python scripts/benchmark.py
    uv run python scripts/benchmark.py --tamanhos 100 1000 10000 --semente 7
"""

import argparse
import csv
import json
import math
import os
import platform
import sys
import time
from pathlib import Path

from app.services.benchmark import REGIAO_BENCHMARK, instancia_sintetica
from app.services.execucao import ALGORITMOS, cronometrar

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
DIRETORIO_DADOS = RAIZ_PROJETO / "docs" / "dados"
DIRETORIO_GRAFICOS = RAIZ_PROJETO / "docs" / "img"
TAMANHOS_PADRAO = (100, 250, 500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000)
REPETICOES_PADRAO = 3
LIMITE_FORCA_BRUTA = 2_000
ARQUIVO_CSV = DIRETORIO_DADOS / "benchmark.csv"
ARQUIVO_METADADOS = DIRETORIO_DADOS / "benchmark_metadados.json"

CORES = {
    "forca_bruta": "#c1272d",
    "closest_pair_nlog2n": "#d19a22",
    "closest_pair_nlogn": "#2e7d4f",
}


def coletar(tamanhos: list[int], repeticoes: int, semente: int) -> list[dict[str, object]]:
    resultados = []
    algoritmos = list(ALGORITMOS.values())

    for n in tamanhos:
        eventos = instancia_sintetica(n, semente)
        resultados_n = []
        for algoritmo in algoritmos:
            if algoritmo.id == "forca_bruta" and n > LIMITE_FORCA_BRUTA:
                continue

            tempos = []
            comparacoes = None
            distancia = None
            for _ in range(repeticoes):
                resultado, tempo_ms = cronometrar(algoritmo.funcao, eventos)
                tempos.append(tempo_ms)
                if comparacoes is not None and resultado.comparacoes != comparacoes:
                    raise RuntimeError(f"Número de comparações não determinístico em {algoritmo.id}, n={n}")
                if distancia is not None and not math.isclose(
                    resultado.distancia_projetada_km, distancia, rel_tol=1e-12, abs_tol=1e-12
                ):
                    raise RuntimeError(f"Resultado não determinístico em {algoritmo.id}, n={n}")
                comparacoes = resultado.comparacoes
                distancia = resultado.distancia_projetada_km

            resultados_n.append((algoritmo.id, distancia))
            linha: dict[str, object] = {
                "n": n,
                "algoritmo": algoritmo.id,
                "semente": semente,
                "repeticoes": repeticoes,
                "comparacoes": comparacoes,
                "tempo_medio_ms": sum(tempos) / len(tempos),
            }
            linha.update({f"tempo_{indice}_ms": tempo for indice, tempo in enumerate(tempos, start=1)})
            resultados.append(linha)
            print(
                f"n={n:>6} | {algoritmo.nome:<25} | "
                f"média={sum(tempos) / len(tempos):>10.3f} ms | comparações={comparacoes}"
            )

        distancias = [distancia for _, distancia in resultados_n]
        if distancias and not all(
            math.isclose(distancias[0], valor, rel_tol=1e-12, abs_tol=1e-12)
            for valor in distancias[1:]
        ):
            raise RuntimeError(f"Algoritmos discordaram sobre a distância mínima para n={n}")

    return resultados


def salvar_csv(linhas: list[dict[str, object]], caminho: Path, repeticoes: int) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    colunas = [
        "n",
        "algoritmo",
        "semente",
        "repeticoes",
        *(f"tempo_{indice}_ms" for indice in range(1, repeticoes + 1)),
        "tempo_medio_ms",
        "comparacoes",
    ]
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)


def valor_grafico(linha: dict[str, object], metrica: str) -> float:
    return float(linha["tempo_medio_ms"] if metrica == "tempo" else linha["comparacoes"])


def rotulo_algoritmo(identificador: str) -> str:
    return ALGORITMOS[identificador].nome


def gerar_grafico(
    linhas: list[dict[str, object]], caminho: Path, metrica: str, titulo: str, eixo_y: str
) -> None:
    largura, altura = 960, 560
    margem_esquerda, margem_direita, margem_superior, margem_inferior = 92, 250, 76, 100
    area_largura = largura - margem_esquerda - margem_direita
    area_altura = altura - margem_superior - margem_inferior
    tamanhos = sorted({int(linha["n"]) for linha in linhas})
    xs = [math.log10(n) for n in tamanhos]
    menor_x, maior_x = min(xs), max(xs)
    if menor_x == maior_x:
        menor_x -= 0.5
        maior_x += 0.5

    valores = [valor_grafico(linha, metrica) for linha in linhas if valor_grafico(linha, metrica) > 0]
    menor_y, maior_y = min(math.log10(v) for v in valores), max(math.log10(v) for v in valores)
    if menor_y == maior_y:
        menor_y -= 0.5
        maior_y += 0.5
    margem_y = max((maior_y - menor_y) * 0.08, 0.08)
    menor_y -= margem_y
    maior_y += margem_y

    def px(n: int) -> float:
        return margem_esquerda + (math.log10(n) - menor_x) / (maior_x - menor_x) * area_largura

    def py(valor: float) -> float:
        return margem_superior + (maior_y - math.log10(valor)) / (maior_y - menor_y) * area_altura

    algoritmo_ids = [algoritmo.id for algoritmo in ALGORITMOS.values()]
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}" role="img" aria-labelledby="titulo descricao">',
        "<title id=\"titulo\">" + titulo + "</title>",
        "<desc id=\"descricao\">Gráfico log-log dos resultados medidos pelo script benchmark.py.</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{largura / 2}" y="34" text-anchor="middle" font-family="sans-serif" '
        f'font-size="20" font-weight="700" fill="#1c2a35">{titulo}</text>',
    ]

    tick_logs = range(math.floor(menor_y), math.ceil(maior_y) + 1)
    for expoente in tick_logs:
        valor = 10.0**expoente
        if not menor_y <= math.log10(valor) <= maior_y:
            continue
        y = py(valor)
        partes.extend(
            [
                f'<line x1="{margem_esquerda}" y1="{y:.2f}" x2="{margem_esquerda + area_largura}" '
                f'y2="{y:.2f}" stroke="#dfe6e2" stroke-width="1"/>',
                f'<text x="{margem_esquerda - 12}" y="{y + 4:.2f}" text-anchor="end" '
                f'font-family="sans-serif" font-size="12" fill="#4f5f6a">{valor:g}</text>',
            ]
        )

    for n in tamanhos:
        x = px(n)
        partes.extend(
            [
                f'<line x1="{x:.2f}" y1="{margem_superior}" x2="{x:.2f}" '
                f'y2="{margem_superior + area_altura}" stroke="#eef2f0" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{margem_superior + area_altura + 22}" text-anchor="middle" '
                f'font-family="sans-serif" font-size="11" fill="#4f5f6a">{n:,}</text>',
            ]
        )

    partes.extend(
        [
            f'<line x1="{margem_esquerda}" y1="{margem_superior + area_altura}" '
            f'x2="{margem_esquerda + area_largura}" y2="{margem_superior + area_altura}" '
            'stroke="#52616b" stroke-width="1.5"/>',
            f'<line x1="{margem_esquerda}" y1="{margem_superior}" '
            f'x2="{margem_esquerda}" y2="{margem_superior + area_altura}" '
            'stroke="#52616b" stroke-width="1.5"/>',
            f'<text x="{margem_esquerda + area_largura / 2}" y="{altura - 25}" text-anchor="middle" '
            'font-family="sans-serif" font-size="14" fill="#1c2a35">Quantidade de pontos n (escala log)</text>',
            f'<text x="22" y="{margem_superior + area_altura / 2}" text-anchor="middle" '
            f'transform="rotate(-90 22 {margem_superior + area_altura / 2})" '
            f'font-family="sans-serif" font-size="14" fill="#1c2a35">{eixo_y} (escala log)</text>',
        ]
    )

    for indice, algoritmo_id in enumerate(algoritmo_ids):
        serie = sorted(
            (linha for linha in linhas if linha["algoritmo"] == algoritmo_id),
            key=lambda linha: int(linha["n"]),
        )
        if not serie:
            continue
        pontos = [
            (px(int(linha["n"])), py(valor_grafico(linha, metrica)))
            for linha in serie
            if valor_grafico(linha, metrica) > 0
        ]
        caminho_svg = " ".join(
            f"{'M' if indice_ponto == 0 else 'L'} {x:.2f} {y:.2f}"
            for indice_ponto, (x, y) in enumerate(pontos)
        )
        cor = CORES[algoritmo_id]
        partes.append(
            f'<path d="{caminho_svg}" fill="none" stroke="{cor}" stroke-width="3" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        partes.extend(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{cor}"/>' for x, y in pontos
        )
        legenda_y = margem_superior + 22 + indice * 28
        partes.extend(
            [
                f'<line x1="{margem_esquerda + area_largura + 20}" y1="{legenda_y}" '
                f'x2="{margem_esquerda + area_largura + 48}" y2="{legenda_y}" '
                f'stroke="{cor}" stroke-width="3"/>',
                f'<text x="{margem_esquerda + area_largura + 56}" y="{legenda_y + 4}" '
                f'font-family="sans-serif" font-size="12" fill="#1c2a35">{rotulo_algoritmo(algoritmo_id)}</text>',
            ]
        )

    partes.append("</svg>")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(partes) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--tamanhos",
        type=int,
        nargs="+",
        default=list(TAMANHOS_PADRAO),
        help="quantidades de pontos; padrão: 100 a 100.000",
    )
    parser.add_argument("--repeticoes", type=int, default=REPETICOES_PADRAO)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=ARQUIVO_CSV)
    parser.add_argument(
        "--diretorio-graficos", type=Path, default=DIRETORIO_GRAFICOS
    )
    args = parser.parse_args()

    if args.repeticoes < 1:
        parser.error("--repeticoes deve ser pelo menos 1")
    if not args.tamanhos or any(n < 2 for n in args.tamanhos):
        parser.error("todos os tamanhos devem ser pelo menos 2")
    tamanhos = sorted(set(args.tamanhos))
    if any(n > 100_000 for n in tamanhos):
        parser.error("o script aceita no máximo 100.000 pontos")

    inicio = time.perf_counter()
    resultados = coletar(tamanhos, args.repeticoes, args.semente)
    salvar_csv(resultados, args.saida, args.repeticoes)
    gerar_grafico(
        resultados,
        args.diretorio_graficos / "benchmark_tempo.svg",
        "tempo",
        "Tempo médio dos algoritmos",
        "Tempo médio (ms)",
    )
    gerar_grafico(
        resultados,
        args.diretorio_graficos / "benchmark_comparacoes.svg",
        "comparacoes",
        "Comparações realizadas",
        "Número de comparações",
    )

    metadados = {
        "regiao": REGIAO_BENCHMARK,
        "tamanhos": tamanhos,
        "repeticoes": args.repeticoes,
        "semente": args.semente,
        "limite_forca_bruta": LIMITE_FORCA_BRUTA,
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "processador": platform.processor() or "não informado",
        "cpus_logicas": os.cpu_count(),
        "tempo_script_s": round(time.perf_counter() - inicio, 3),
        "csv": str(args.saida.relative_to(RAIZ_PROJETO))
        if args.saida.is_relative_to(RAIZ_PROJETO)
        else str(args.saida),
    }
    ARQUIVO_METADADOS.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_METADADOS.write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nResultados brutos: {args.saida}")
    print(f"Gráficos: {args.diretorio_graficos}")
    print(f"Metadados: {ARQUIVO_METADADOS}")


if __name__ == "__main__":
    main()
