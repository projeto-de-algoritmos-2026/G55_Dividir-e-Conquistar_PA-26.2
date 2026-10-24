"""Cliente do FDSN Event Web Service do USGS (catálogo ComCat)."""

import csv
import io
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.services.catalogo import reduzir_linha
from app.services.regioes import Regiao

URL_BASE = "https://earthquake.usgs.gov/fdsnws/event/1"
LIMITE = 20_000

Janela = tuple[datetime, datetime]


def _parametros(regiao: Regiao, inicio: datetime, fim: datetime, mag_min: float) -> dict:
    return {
        "eventtype": "earthquake",
        "starttime": inicio.isoformat(),
        "endtime": fim.isoformat(),
        "minmagnitude": mag_min,
        "minlatitude": regiao.lat_min,
        "maxlatitude": regiao.lat_max,
        "minlongitude": regiao.lon_min,
        "maxlongitude": regiao.lon_max,
    }


def contar(
    cliente: httpx.Client, regiao: Regiao, inicio: datetime, fim: datetime, mag_min: float
) -> int:
    resposta = cliente.get(
        f"{URL_BASE}/count",
        params={**_parametros(regiao, inicio, fim, mag_min), "format": "geojson"},
    )
    resposta.raise_for_status()
    return int(resposta.json()["count"])


def planejar_janelas(
    inicio: datetime, fim: datetime, contar_fn: Callable[[datetime, datetime], int]
) -> list[Janela]:
    """Divide [inicio, fim) ao meio até cada janela ter no máximo LIMITE eventos."""
    if contar_fn(inicio, fim) <= LIMITE:
        return [(inicio, fim)]
    meio = inicio + (fim - inicio) / 2
    if meio <= inicio:
        raise ValueError(f"Mais de {LIMITE} eventos em um intervalo indivisível: {inicio}")
    return planejar_janelas(inicio, meio, contar_fn) + planejar_janelas(meio, fim, contar_fn)


def baixar_janela(
    cliente: httpx.Client, regiao: Regiao, inicio: datetime, fim: datetime, mag_min: float
) -> list[dict[str, str]]:
    """Linhas brutas do CSV do USGS para uma janela."""
    resposta = cliente.get(
        f"{URL_BASE}/query",
        params={
            **_parametros(regiao, inicio, fim, mag_min),
            "format": "csv",
            "orderby": "time-asc",
        },
    )
    resposta.raise_for_status()
    return list(csv.DictReader(io.StringIO(resposta.text)))


@dataclass
class ResultadoDownload:
    janelas: list[Janela]
    linhas: list[dict[str, str]]
    descartadas: int


def baixar_catalogo(
    regiao: Regiao, inicio: datetime, fim: datetime, mag_min: float
) -> ResultadoDownload:
    """Baixa o catálogo da região, já reduzido às colunas usadas e ordenado por data."""
    with httpx.Client(timeout=60, headers={"User-Agent": "SismoPar/0.1"}) as cliente:
        janelas = planejar_janelas(
            inicio, fim, lambda a, b: contar(cliente, regiao, a, b, mag_min)
        )
        por_id: dict[str, dict[str, str]] = {}
        descartadas = 0
        for inicio_janela, fim_janela in janelas:
            for bruta in baixar_janela(cliente, regiao, inicio_janela, fim_janela, mag_min):
                linha = reduzir_linha(bruta)
                if linha is None:
                    descartadas += 1
                # Eventos na fronteira entre janelas aparecem nas duas
                elif linha["id"] not in por_id:
                    por_id[linha["id"]] = linha

    linhas = sorted(por_id.values(), key=lambda linha: linha["time"])
    return ResultadoDownload(janelas, linhas, descartadas)
