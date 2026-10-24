"""Valida catálogos em CSV: colunas, coordenadas, valores numéricos e ids duplicados.

Uso (a partir de backend/):
    uv run python scripts/validar_dados.py                 # todos os CSVs de app/data/
    uv run python scripts/validar_dados.py meu_catalogo.csv
"""

import argparse
import sys
from pathlib import Path

from app.services.catalogo import DIRETORIO_DADOS, ler_csv, validar_catalogo
from app.services.regioes import REGIOES

MAX_ERROS_EXIBIDOS = 10


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("arquivos", nargs="*", type=Path)
    args = parser.parse_args()

    arquivos = args.arquivos or sorted(DIRETORIO_DADOS.glob("*.csv"))
    if not arquivos:
        sys.exit(f"Nenhum CSV encontrado em {DIRETORIO_DADOS}")

    todos_validos = True
    for arquivo in arquivos:
        # Arquivos com nome de região (japao.csv) também têm a caixa conferida
        regiao = REGIOES.get(arquivo.stem)
        colunas, linhas = ler_csv(arquivo)
        relatorio = validar_catalogo(linhas, colunas, regiao)

        situacao = "válido" if relatorio.valido else f"{len(relatorio.erros)} erro(s)"
        print(f"{arquivo.name}: {relatorio.total} evento(s), {situacao}")
        for erro in relatorio.erros[:MAX_ERROS_EXIBIDOS]:
            print(f"  - {erro}")
        if len(relatorio.erros) > MAX_ERROS_EXIBIDOS:
            print(f"  ... e mais {len(relatorio.erros) - MAX_ERROS_EXIBIDOS}")
        todos_validos &= relatorio.valido

    sys.exit(0 if todos_validos else 1)


if __name__ == "__main__":
    main()
