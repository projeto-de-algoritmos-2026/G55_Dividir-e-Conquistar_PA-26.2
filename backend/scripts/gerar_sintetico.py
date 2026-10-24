"""Gera um catálogo sintético reprodutível (mesma semente, mesmo arquivo).

Uso (a partir de backend/):
    uv run python scripts/gerar_sintetico.py --n 1000 --semente 42 --regiao japao
"""

import argparse
from pathlib import Path

from app.services.catalogo import DIRETORIO_DADOS, escrever_csv
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, required=True, help="número de eventos")
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--regiao", choices=list(REGIOES), default="japao")
    parser.add_argument(
        "--saida", type=Path, help="padrão: app/data/sintetico/sintetico_<n>_<semente>.csv"
    )
    args = parser.parse_args()

    if args.n < 0:
        parser.error("--n deve ser não negativo")
    saida = args.saida or DIRETORIO_DADOS / "sintetico" / f"sintetico_{args.n}_{args.semente}.csv"
    escrever_csv(saida, gerar_eventos(args.n, args.semente, REGIOES[args.regiao]))
    print(f"{args.n} evento(s) sintético(s) salvos em {saida}")


if __name__ == "__main__":
    main()
