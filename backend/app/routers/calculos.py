import time
from typing import Annotated

from fastapi import APIRouter, Query

from app.algorithms.closest_pair_nlogn import closest_pair_nlogn
from app.erros import ErroNegocio
from app.limites import (
    LIMITE_FORCA_BRUTA_BENCHMARK,
    LIMITE_FORCA_BRUTA_COMPARATIVO,
    LIMITE_N_BENCHMARK,
    LIMITE_REPETICOES_BENCHMARK,
    LIMITE_VERIFICACAO_GEODESICA,
)
from app.models.passo import PassoRecursao
from app.models.schemas import (
    BenchmarkSaida,
    ComparativoSaida,
    FalhaValidacao,
    ItemComparativo,
    MedicaoBenchmark,
    ParSaida,
    PassoAPassoSaida,
    RequisicaoCalculo,
    RequisicaoPassoAPasso,
    RequisicaoValidar,
    ValidacaoSaida,
    VerificacaoSaida,
)
from app.routers.conversao import evento_saida, passo_saida, resumo
from app.services import repositorio
from app.services.aleatorios import validar_aleatorio
from app.services.benchmark import medir
from app.services.execucao import ALGORITMOS, amostrar, comparar, cronometrar
from app.services.filtros import exigir_dois, filtrar
from app.services.verificacao import verificar_geodesica

router = APIRouter(tags=["cálculos"])

TAMANHOS_PADRAO_BENCHMARK = [100, 250, 500, 1000, 2000, 5000]


def _eventos(requisicao: RequisicaoCalculo):
    return exigir_dois(filtrar(repositorio.obter(requisicao.regiao_id).eventos, requisicao))


@router.post("/par-mais-proximo", response_model=ParSaida)
def par_mais_proximo(requisicao: RequisicaoCalculo):
    """Sort_and_Closest-Pair O(n log n) com distâncias projetada e geodésica e verificação."""
    eventos = _eventos(requisicao)
    resultado, tempo_ms = cronometrar(closest_pair_nlogn, eventos)
    verificacao = verificar_geodesica(
        eventos, resultado, limite_eventos=LIMITE_VERIFICACAO_GEODESICA
    )
    return ParSaida(
        regiao_id=requisicao.regiao_id,
        algoritmo=ALGORITMOS["closest_pair_nlogn"].nome,
        n=len(eventos),
        a=evento_saida(resultado.a),
        b=evento_saida(resultado.b),
        distancia_projetada_km=resultado.distancia_projetada_km,
        distancia_geodesica_km=resultado.distancia_geodesica_km,
        comparacoes=resultado.comparacoes,
        tempo_ms=tempo_ms,
        verificacao_geodesica=VerificacaoSaida(
            status=verificacao.status,
            limite_eventos=LIMITE_VERIFICACAO_GEODESICA,
            par_geodesico=(
                [evento.id for evento in verificacao.par_geodesico]
                if verificacao.par_geodesico
                else None
            ),
            distancia_geodesica_minima_km=verificacao.distancia_geodesica_minima_km,
            diferenca_km=verificacao.diferenca_km,
        ),
    )


@router.post("/passo-a-passo", response_model=PassoAPassoSaida)
def passo_a_passo(requisicao: RequisicaoPassoAPasso):
    """Registro da recursão sobre uma amostra dos eventos, para o modo didático."""
    filtrados = _eventos(requisicao)
    amostra = amostrar(filtrados, requisicao.tamanho_amostra, requisicao.semente)
    registro: list[PassoRecursao] = []
    resultado = closest_pair_nlogn(amostra, registro=registro)
    return PassoAPassoSaida(
        regiao_id=requisicao.regiao_id,
        n_filtrados=len(filtrados),
        n_amostra=len(amostra),
        semente=requisicao.semente,
        eventos=[evento_saida(e) for e in amostra],
        passos=[passo_saida(p) for p in registro],
        resultado=resumo(resultado),
    )


@router.post("/comparativo", response_model=ComparativoSaida)
def comparativo(requisicao: RequisicaoCalculo):
    """As três versões sobre os mesmos eventos, com tempo e número de comparações."""
    eventos = _eventos(requisicao)
    itens = []
    for execucao in comparar(eventos, LIMITE_FORCA_BRUTA_COMPARATIVO):
        algoritmo, resultado = execucao.algoritmo, execucao.resultado
        itens.append(
            ItemComparativo(
                algoritmo=algoritmo.id,
                nome=algoritmo.nome,
                complexidade=algoritmo.complexidade,
                executado=resultado is not None,
                motivo=execucao.motivo,
                tempo_ms=execucao.tempo_ms,
                comparacoes=resultado.comparacoes if resultado else None,
                distancia_projetada_km=resultado.distancia_projetada_km if resultado else None,
                par=[resultado.a.id, resultado.b.id] if resultado else None,
            )
        )
    distancias = {item.distancia_projetada_km for item in itens if item.executado}
    return ComparativoSaida(
        regiao_id=requisicao.regiao_id, n=len(eventos), itens=itens, mesma_distancia=len(distancias) == 1
    )


@router.post("/validar", response_model=ValidacaoSaida)
def validar(requisicao: RequisicaoValidar):
    """As duas versões de divisão e conquista contra a força bruta em instâncias aleatórias."""
    inicio = time.perf_counter()
    relatorio = validar_aleatorio(requisicao.instancias, requisicao.n_max, requisicao.semente)
    tempo_ms = (time.perf_counter() - inicio) * 1000
    return ValidacaoSaida(
        instancias=relatorio.instancias,
        aprovadas=relatorio.aprovadas,
        falhas=[FalhaValidacao(**vars(falha)) for falha in relatorio.falhas],
        tempo_ms=tempo_ms,
    )


@router.get("/benchmark", response_model=BenchmarkSaida)
def benchmark(
    tamanhos: Annotated[
        list[int], Query(description=f"Valores de n, cada um entre 2 e {LIMITE_N_BENCHMARK}")
    ] = TAMANHOS_PADRAO_BENCHMARK,
    repeticoes: Annotated[int, Query(ge=1, le=LIMITE_REPETICOES_BENCHMARK)] = 3,
    semente: int = 42,
):
    """Tempo médio e comparações das três versões para n crescente (instâncias sintéticas).

    A força bruta só roda até n = 2.000; os n grandes ficam para `scripts/benchmark.py`.
    """
    if not 1 <= len(tamanhos) <= 10:
        raise ErroNegocio(422, "Informe de 1 a 10 tamanhos")
    fora = [n for n in tamanhos if not 2 <= n <= LIMITE_N_BENCHMARK]
    if fora:
        raise ErroNegocio(422, f"Tamanhos fora do intervalo [2, {LIMITE_N_BENCHMARK}]: {fora}")

    medicoes = medir(sorted(set(tamanhos)), repeticoes, LIMITE_FORCA_BRUTA_BENCHMARK, semente)
    return BenchmarkSaida(
        repeticoes=repeticoes,
        semente=semente,
        teto_forca_bruta=LIMITE_FORCA_BRUTA_BENCHMARK,
        medicoes=[
            MedicaoBenchmark(
                n=m.n,
                algoritmo=m.algoritmo,
                repeticoes=m.repeticoes,
                tempos_ms=list(m.tempos_ms),
                tempo_medio_ms=m.tempo_medio_ms,
                comparacoes_medias=m.comparacoes,
            )
            for m in medicoes
        ],
    )
