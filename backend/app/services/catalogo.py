import csv
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from app.services.regioes import Regiao

DIRETORIO_DADOS = Path(__file__).resolve().parents[1] / "data"

COLUNAS = ("id", "time", "latitude", "longitude", "depth", "mag", "place")
COLUNAS_NUMERICAS = ("latitude", "longitude", "depth", "mag")


@dataclass
class ErroLinha:
    linha: int
    coluna: str
    mensagem: str

    def __str__(self) -> str:
        return f"linha {self.linha}, coluna '{self.coluna}': {self.mensagem}"


@dataclass
class RelatorioValidacao:
    total: int = 0
    erros: list[ErroLinha] = field(default_factory=list)

    @property
    def valido(self) -> bool:
        return not self.erros


def reduzir_linha(linha: Mapping[str, str]) -> dict[str, str] | None:
    """Mantém só as colunas usadas; descarta a linha se faltar algum valor numérico."""
    reduzida = {coluna: (linha.get(coluna) or "").strip() for coluna in COLUNAS}
    if any(not reduzida[coluna] for coluna in COLUNAS_NUMERICAS):
        return None
    return reduzida


def _ler_numero(valor: str) -> float | None:
    try:
        numero = float(valor)
    except ValueError:
        return None
    return numero if math.isfinite(numero) else None


def _ler_data(valor: str) -> datetime | None:
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None


def validar_catalogo(
    linhas: Iterable[Mapping[str, str]],
    colunas: Iterable[str],
    regiao: Regiao | None = None,
) -> RelatorioValidacao:
    """Valida um catálogo no formato reduzido. A linha 1 é o cabeçalho."""
    relatorio = RelatorioValidacao()

    faltando = [coluna for coluna in COLUNAS if coluna not in set(colunas)]
    if faltando:
        relatorio.erros.append(
            ErroLinha(1, ", ".join(faltando), "coluna obrigatória ausente")
        )
        return relatorio

    ids_vistos: dict[str, int] = {}
    for numero, linha in enumerate(linhas, start=2):
        relatorio.total += 1
        erros = relatorio.erros

        id_evento = (linha.get("id") or "").strip()
        if not id_evento:
            erros.append(ErroLinha(numero, "id", "identificador vazio"))
        elif id_evento in ids_vistos:
            erros.append(
                ErroLinha(numero, "id", f"'{id_evento}' repetido da linha {ids_vistos[id_evento]}")
            )
        else:
            ids_vistos[id_evento] = numero

        if _ler_data(linha.get("time") or "") is None:
            erros.append(ErroLinha(numero, "time", "data fora do formato ISO 8601"))

        valores = {}
        for coluna in COLUNAS_NUMERICAS:
            valor = _ler_numero(linha.get(coluna) or "")
            if valor is None:
                erros.append(ErroLinha(numero, coluna, "valor ausente ou não numérico"))
            valores[coluna] = valor

        latitude, longitude = valores["latitude"], valores["longitude"]
        if latitude is not None and not -90 <= latitude <= 90:
            erros.append(ErroLinha(numero, "latitude", f"{latitude} fora de [-90, 90]"))
        if longitude is not None and not -180 <= longitude <= 180:
            erros.append(ErroLinha(numero, "longitude", f"{longitude} fora de [-180, 180]"))
        if (
            regiao is not None
            and latitude is not None
            and longitude is not None
            and not regiao.contem(latitude, longitude)
        ):
            erros.append(
                ErroLinha(numero, "latitude/longitude", f"ponto fora da região {regiao.nome}")
            )

    return relatorio


def ler_csv(caminho: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Devolve as colunas do cabeçalho e as linhas do arquivo."""
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)
        return list(leitor.fieldnames or []), linhas


def escrever_csv(caminho: Path, linhas: Iterable[Mapping[str, str]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)
