"""Mede quantas vezes a projeção plana muda o par mais próximo, e grava em docs/dados/.

Para cada região roda o catálogo completo, subamostras do catálogo real e
instâncias sintéticas uniformes na caixa (pontos esparsos, onde a distorção
da projeção pesa mais). Sementes fixas: rodar de novo gera o mesmo CSV.

Uso (a partir de backend/):
    uv run python scripts/validar_geodesica.py
"""

import argparse
import csv
import random
from collections import defaultdict
from datetime import date
from pathlib import Path

from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.geo.projecao import projetar_eventos
from app.models.evento import Evento
from app.services.eventos import carregar_eventos
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos
from app.services.verificacao import verificar_geodesica

DIRETORIO_SAIDA = Path(__file__).resolve().parents[2] / "docs" / "dados"
COLUNAS = (
    "regiao",
    "tipo",
    "semente",
    "n",
    "par_plano",
    "distancia_projetada_km",
    "distancia_geodesica_par_plano_km",
    "distancia_geodesica_minima_km",
    "par_geodesico",
    "diferenca_km",
    "status",
)
ROTULOS = {"completo": "Catálogo completo", "subamostra": "Subamostras do real", "sintetico": "Sintético uniforme"}


def _instancias(id_regiao: str, quantidade: int, n_min: int, n_max: int):
    """Gera (tipo, semente, eventos projetados) para uma região."""
    regiao = REGIOES[id_regiao]
    catalogo = carregar_eventos(id_regiao)
    yield "completo", "", catalogo
    for semente in range(quantidade):
        gerador = random.Random(semente)
        yield "subamostra", semente, gerador.sample(catalogo, gerador.randint(n_min, n_max))
    for semente in range(quantidade):
        n = random.Random(semente).randint(n_min, n_max)
        linhas = gerar_eventos(n, semente, regiao)
        yield "sintetico", semente, projetar_eventos([Evento.de_linha(l) for l in linhas], regiao)


def _linha(id_regiao, tipo, semente, eventos) -> dict:
    resultado = closest_pair_nlogn(eventos)
    verificacao = verificar_geodesica(eventos, resultado)
    a, b = verificacao.par_geodesico
    return {
        "regiao": id_regiao,
        "tipo": tipo,
        "semente": semente,
        "n": len(eventos),
        "par_plano": f"{resultado.a.id}|{resultado.b.id}",
        "distancia_projetada_km": f"{resultado.distancia_projetada_km:.6f}",
        "distancia_geodesica_par_plano_km": f"{resultado.distancia_geodesica_km:.6f}",
        "distancia_geodesica_minima_km": f"{verificacao.distancia_geodesica_minima_km:.6f}",
        "par_geodesico": f"{a.id}|{b.id}",
        "diferenca_km": f"{verificacao.diferenca_km:.6f}",
        "status": verificacao.status,
    }


def _resumo(linhas: list[dict], comando: str) -> str:
    grupos = defaultdict(list)
    for linha in linhas:
        grupos[(linha["regiao"], linha["tipo"])].append(linha)

    total_div = sum(linha["status"] == "divergente" for linha in linhas)
    saida = [
        "# Validação geodésica",
        "",
        f"Gerado em {date.today().isoformat()} com `{comando}` (a partir de `backend/`).",
        "",
        "Cada instância roda o Sort_and_Closest-Pair no plano projetado e a força bruta",
        "com Haversine na esfera. A verificação **diverge** quando o par escolhido no plano",
        "está, na esfera, mais de 1 mm mais longe do que o par geodesicamente mais próximo.",
        "Pares diferentes empatados contam como confirmados.",
        "",
        f"**Total: {total_div} divergência(s) em {len(linhas)} instâncias.**",
        "",
        "| Região | Tipo | Instâncias | n (mín–máx) | Divergências | Maior diferença (km) |",
        "|---|---|--:|--:|--:|--:|",
    ]
    for (id_regiao, tipo), grupo in grupos.items():
        ns = [int(linha["n"]) for linha in grupo]
        divergencias = sum(linha["status"] == "divergente" for linha in grupo)
        maior = max(float(linha["diferenca_km"]) for linha in grupo)
        saida.append(
            f"| {REGIOES[id_regiao].nome} | {ROTULOS[tipo]} | {len(grupo)} | "
            f"{min(ns)}–{max(ns)} | {divergencias} | {max(maior, 0.0):.6f} |"
        )
    saida += ["", "Dados por instância: [`validacao_geodesica.csv`](./validacao_geodesica.csv).", ""]
    return "\n".join(saida)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--instancias", type=int, default=50, help="subamostras e sintéticos por região")
    parser.add_argument("--n-min", type=int, default=100)
    parser.add_argument("--n-max", type=int, default=1000)
    parser.add_argument("--saida", type=Path, default=DIRETORIO_SAIDA)
    args = parser.parse_args()

    linhas = []
    for id_regiao in REGIOES:
        for tipo, semente, eventos in _instancias(id_regiao, args.instancias, args.n_min, args.n_max):
            linhas.append(_linha(id_regiao, tipo, semente, eventos))
        divergencias = sum(l["status"] == "divergente" for l in linhas if l["regiao"] == id_regiao)
        print(f"{REGIOES[id_regiao].nome}: {divergencias} divergência(s)")

    args.saida.mkdir(parents=True, exist_ok=True)
    with (args.saida / "validacao_geodesica.csv").open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)

    comando = "uv run python scripts/validar_geodesica.py"
    padrao = (args.instancias, args.n_min, args.n_max) == (50, 100, 1000)
    if not padrao:
        comando += f" --instancias {args.instancias} --n-min {args.n_min} --n-max {args.n_max}"
    (args.saida / "validacao_geodesica.md").write_text(_resumo(linhas, comando), encoding="utf-8")
    print(f"{len(linhas)} instâncias gravadas em {args.saida}")


if __name__ == "__main__":
    main()
