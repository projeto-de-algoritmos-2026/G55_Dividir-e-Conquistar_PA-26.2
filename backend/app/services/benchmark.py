"""Medição de tempo e comparações das três versões para n crescente."""

from collections.abc import Iterable
from dataclasses import dataclass
from statistics import mean

from app.geo.projecao import projetar_eventos
from app.models.evento import Evento
from app.services.execucao import ALGORITMOS, cronometrar
from app.services.regioes import REGIOES
from app.services.sintetico import gerar_eventos

REGIAO_BENCHMARK = "japao"


@dataclass(frozen=True)
class Medicao:
    n: int
    algoritmo: str
    tempos_ms: tuple[float, ...]
    comparacoes: int

    @property
    def repeticoes(self) -> int:
        return len(self.tempos_ms)

    @property
    def tempo_medio_ms(self) -> float:
        return mean(self.tempos_ms)


def instancia_sintetica(n: int, semente: int) -> list[Evento]:
    """Eventos uniformes na caixa da região de referência, já projetados."""
    regiao = REGIOES[REGIAO_BENCHMARK]
    return projetar_eventos([Evento.de_linha(l) for l in gerar_eventos(n, semente, regiao)], regiao)


def medir(
    tamanhos: Iterable[int], repeticoes: int, teto_forca_bruta: int, semente: int = 42
) -> list[Medicao]:
    """Mesma instância para as três versões em cada n; força bruta só até o teto."""
    medicoes = []
    for n in tamanhos:
        eventos = instancia_sintetica(n, semente)
        for algoritmo in ALGORITMOS.values():
            if algoritmo.id == "forca_bruta" and n > teto_forca_bruta:
                continue
            tempos = []
            for _ in range(repeticoes):
                resultado, tempo_ms = cronometrar(algoritmo.funcao, eventos)
                tempos.append(tempo_ms)
            # Comparações não variam entre repetições: o algoritmo é determinístico
            medicoes.append(Medicao(n, algoritmo.id, tuple(tempos), resultado.comparacoes))
    return medicoes
