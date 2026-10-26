"""Catálogos disponíveis para a API: as regiões versionadas e os importados em memória."""

import csv
import io
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from app.erros import ErroNegocio
from app.geo.projecao import projetar_eventos
from app.limites import (
    LIMITE_CATALOGOS_IMPORTADOS,
    LIMITE_ERROS_EXIBIDOS,
    LIMITE_EXTENSAO_GRAUS,
    LIMITE_IMPORTACAO_BYTES,
)
from app.models.evento import Evento
from app.services.catalogo import reduzir_linha, validar_catalogo
from app.services.eventos import carregar_eventos
from app.services.regioes import REGIOES, Regiao


@dataclass(frozen=True)
class Catalogo:
    id: str
    nome: str
    regiao: Regiao
    eventos: tuple[Evento, ...]  # já projetados no plano da região
    importado: bool


_importados: OrderedDict[str, Catalogo] = OrderedDict()


@cache
def _predefinido(id_regiao: str) -> Catalogo:
    regiao = REGIOES[id_regiao]
    return Catalogo(regiao.id, regiao.nome, regiao, tuple(carregar_eventos(id_regiao)), False)


def listar() -> list[Catalogo]:
    return [_predefinido(id_regiao) for id_regiao in REGIOES] + list(_importados.values())


def obter(id_catalogo: str) -> Catalogo:
    if id_catalogo in REGIOES:
        return _predefinido(id_catalogo)
    if id_catalogo in _importados:
        return _importados[id_catalogo]
    raise ErroNegocio(404, f"Região ou catálogo '{id_catalogo}' não encontrado")


def limpar_importados() -> None:
    _importados.clear()


def importar_csv(conteudo: bytes, nome_arquivo: str | None) -> Catalogo:
    """Valida um CSV no formato USGS e guarda o catálogo em memória."""
    if len(conteudo) > LIMITE_IMPORTACAO_BYTES:
        raise ErroNegocio(
            413, f"Arquivo maior que o limite de {LIMITE_IMPORTACAO_BYTES // (1024 * 1024)} MB"
        )
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ErroNegocio(422, "O arquivo precisa estar codificado em UTF-8") from None

    leitor = csv.DictReader(io.StringIO(texto))
    linhas = list(leitor)
    relatorio = validar_catalogo(linhas, leitor.fieldnames or [])
    if not relatorio.valido:
        erros = [
            {"linha": e.linha, "coluna": e.coluna, "mensagem": e.mensagem}
            for e in relatorio.erros[:LIMITE_ERROS_EXIBIDOS]
        ]
        raise ErroNegocio(
            422, f"Catálogo inválido: {len(relatorio.erros)} erro(s) encontrado(s)", erros
        )
    if relatorio.total < 2:
        raise ErroNegocio(422, "O catálogo precisa ter pelo menos 2 eventos")

    eventos = [Evento.de_linha(reduzir_linha(linha)) for linha in linhas]
    regiao = _regiao_dos_eventos(eventos, nome_arquivo)
    catalogo = Catalogo(
        regiao.id, regiao.nome, regiao, tuple(projetar_eventos(eventos, regiao)), True
    )

    _importados[catalogo.id] = catalogo
    while len(_importados) > LIMITE_CATALOGOS_IMPORTADOS:
        _importados.popitem(last=False)
    return catalogo


def _regiao_dos_eventos(eventos: list[Evento], nome_arquivo: str | None) -> Regiao:
    """Caixa mínima que contém os eventos; o centro dela vira o centro da projeção."""
    latitudes = [evento.latitude for evento in eventos]
    longitudes = [evento.longitude for evento in eventos]
    regiao = Regiao(
        id=f"importado-{uuid.uuid4().hex[:8]}",
        nome=Path(nome_arquivo).stem if nome_arquivo else "Catálogo importado",
        lat_min=min(latitudes),
        lat_max=max(latitudes),
        lon_min=min(longitudes),
        lon_max=max(longitudes),
    )
    extensao = max(regiao.lat_max - regiao.lat_min, regiao.lon_max - regiao.lon_min)
    if extensao > LIMITE_EXTENSAO_GRAUS:
        raise ErroNegocio(
            422,
            f"Os eventos cobrem {extensao:.1f}°, acima do limite regional de "
            f"{LIMITE_EXTENSAO_GRAUS:.0f}° (a projeção plana deixa de valer)",
        )
    return regiao
