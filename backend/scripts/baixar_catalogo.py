"""Baixa catálogos de terremotos do USGS para as regiões pré-configuradas.

Uso (a partir de backend/):
    uv run python scripts/baixar_catalogo.py --regiao todas
    uv run python scripts/baixar_catalogo.py --regiao japao --inicio 2024-01-01 --fim 2024-12-31 --mag-min 2.5
"""

import argparse
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from app.services.catalogo import DIRETORIO_DADOS, escrever_csv
from app.services.regioes import (
    FIM_PADRAO,
    INICIO_PADRAO,
    MAGNITUDE_MIN_PADRAO,
    REGIOES,
)
from app.services.usgs import baixar_catalogo


def _inicio_do_dia(dia: date) -> datetime:
    return datetime.combine(dia, time.min, tzinfo=timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--regiao", required=True, choices=[*REGIOES, "todas"])
    parser.add_argument("--inicio", type=date.fromisoformat, default=INICIO_PADRAO)
    parser.add_argument(
        "--fim", type=date.fromisoformat, default=FIM_PADRAO, help="data final, inclusiva"
    )
    parser.add_argument("--mag-min", type=float, default=MAGNITUDE_MIN_PADRAO)
    parser.add_argument(
        "--saida", type=Path, help="arquivo de saída (só com uma região; padrão app/data/<id>.csv)"
    )
    args = parser.parse_args()

    if args.fim < args.inicio:
        parser.error("--fim deve ser igual ou posterior a --inicio")
    ids = list(REGIOES) if args.regiao == "todas" else [args.regiao]
    if args.saida and len(ids) > 1:
        parser.error("--saida só pode ser usado com uma única região")

    inicio = _inicio_do_dia(args.inicio)
    fim = _inicio_do_dia(args.fim + timedelta(days=1))
    for id_regiao in ids:
        regiao = REGIOES[id_regiao]
        print(f"{regiao.nome}: {args.inicio} a {args.fim}, magnitude >= {args.mag_min}")
        resultado = baixar_catalogo(regiao, inicio, fim, args.mag_min)
        saida = args.saida or DIRETORIO_DADOS / f"{id_regiao}.csv"
        escrever_csv(saida, resultado.linhas)
        print(
            f"  {len(resultado.janelas)} janela(s), {resultado.descartadas} linha(s) "
            f"descartada(s), {len(resultado.linhas)} evento(s) salvos em {saida}"
        )


if __name__ == "__main__":
    main()
