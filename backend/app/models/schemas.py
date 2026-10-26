"""Schemas de entrada e saída da API."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.limites import (
    LIMITE_INSTANCIAS_VALIDACAO,
    LIMITE_N_VALIDACAO,
    LIMITE_PASSO_A_PASSO,
    TAMANHO_PADRAO_PASSO_A_PASSO,
)

EXEMPLO_FILTROS = {
    "inicio": "2023-01-01",
    "fim": "2023-12-31",
    "magnitude_min": 4.0,
    "profundidade_max": 700,
}

# ---------------------------------------------------------------- entrada


class Filtros(BaseModel):
    """Filtros opcionais sobre os eventos de uma região. Datas inclusivas."""

    inicio: date | None = Field(None, description="Data inicial (AAAA-MM-DD)")
    fim: date | None = Field(None, description="Data final, inclusiva (AAAA-MM-DD)")
    magnitude_min: float | None = Field(None, ge=0, le=10, description="Magnitude mínima")
    profundidade_max: float | None = Field(
        None, ge=0, description="Profundidade máxima em km"
    )

    @model_validator(mode="after")
    def _periodo_valido(self):
        if self.inicio and self.fim and self.fim < self.inicio:
            raise ValueError("a data final deve ser igual ou posterior à data inicial")
        return self


class RequisicaoCalculo(Filtros):
    regiao_id: str = Field(
        ..., min_length=1, description="Id de uma região ou de um catálogo importado"
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"regiao_id": "turquia", **EXEMPLO_FILTROS}]}
    )


class RequisicaoPassoAPasso(RequisicaoCalculo):
    tamanho_amostra: int = Field(
        TAMANHO_PADRAO_PASSO_A_PASSO,
        ge=2,
        le=LIMITE_PASSO_A_PASSO,
        description="Quantos eventos sortear para a animação",
    )
    semente: int = Field(42, description="Semente do sorteio da amostra")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"regiao_id": "turquia", **EXEMPLO_FILTROS, "tamanho_amostra": 30, "semente": 42}
            ]
        }
    )


class RequisicaoValidar(BaseModel):
    instancias: int = Field(50, ge=1, le=LIMITE_INSTANCIAS_VALIDACAO)
    n_max: int = Field(200, ge=2, le=LIMITE_N_VALIDACAO, description="Maior n sorteado")
    semente: int = Field(0, description="Semente da primeira instância")

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"instancias": 50, "n_max": 200, "semente": 0}]}
    )


# ---------------------------------------------------------------- saída


class EventoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    data: datetime
    latitude: float
    longitude: float
    profundidade: float = Field(description="km")
    magnitude: float
    local: str
    x: float = Field(description="Coordenada projetada, km")
    y: float = Field(description="Coordenada projetada, km")


class Caixa(BaseModel):
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


class Coordenada(BaseModel):
    latitude: float
    longitude: float


class RegiaoSaida(BaseModel):
    id: str
    nome: str
    importado: bool
    caixa: Caixa
    centro: Coordenada
    total_eventos: int
    inicio: date | None
    fim: date | None
    magnitude_min: float | None
    magnitude_max: float | None
    profundidade_max: float | None


class ListaEventos(BaseModel):
    regiao_id: str
    total: int
    eventos: list[EventoSaida]


class VerificacaoSaida(BaseModel):
    status: Literal["confirmado", "nao_verificado", "divergente"]
    limite_eventos: int
    par_geodesico: list[str] | None
    distancia_geodesica_minima_km: float | None
    diferenca_km: float | None = Field(
        description="Geodésica do par do plano menos a mínima geodésica"
    )


class ParSaida(BaseModel):
    regiao_id: str
    algoritmo: str
    n: int
    a: EventoSaida
    b: EventoSaida
    distancia_projetada_km: float
    distancia_geodesica_km: float
    comparacoes: int
    tempo_ms: float
    verificacao_geodesica: VerificacaoSaida


class ResultadoResumo(BaseModel):
    par: list[str]
    distancia_projetada_km: float
    distancia_geodesica_km: float
    comparacoes: int


class ComparacaoFaixa(BaseModel):
    a: str
    b: str
    distancia: float


class PassoSaida(BaseModel):
    profundidade: int
    tipo: Literal["base", "combinacao"]
    ids: list[str] = Field(description="Eventos do subproblema, em ordem de x")
    reta_l: float | None
    delta_esquerdo: float | None
    delta_direito: float | None
    delta: float
    faixa: list[str] = Field(description="Eventos a menos de δ da reta L, em ordem de y")
    comparacoes_faixa: list[ComparacaoFaixa]
    par: list[str]
    distancia: float


class PassoAPassoSaida(BaseModel):
    regiao_id: str
    n_filtrados: int
    n_amostra: int
    semente: int
    eventos: list[EventoSaida]
    passos: list[PassoSaida] = Field(description="Um passo por chamada, em pós-ordem")
    resultado: ResultadoResumo


class ItemComparativo(BaseModel):
    algoritmo: str
    nome: str
    complexidade: str
    executado: bool
    motivo: str | None = None
    tempo_ms: float | None = None
    comparacoes: int | None = None
    distancia_projetada_km: float | None = None
    par: list[str] | None = None


class ComparativoSaida(BaseModel):
    regiao_id: str
    n: int
    itens: list[ItemComparativo]
    mesma_distancia: bool = Field(description="Todas as versões executadas acharam a mesma distância")


class FalhaValidacao(BaseModel):
    semente: int
    distribuicao: str
    n: int
    algoritmo: str
    esperado: float
    obtido: float


class ValidacaoSaida(BaseModel):
    instancias: int
    aprovadas: int
    falhas: list[FalhaValidacao]
    tempo_ms: float


class MedicaoBenchmark(BaseModel):
    n: int
    algoritmo: str
    repeticoes: int
    tempos_ms: list[float] = Field(description="Tempo de cada repetição")
    tempo_medio_ms: float
    comparacoes_medias: float


class BenchmarkSaida(BaseModel):
    repeticoes: int
    semente: int
    teto_forca_bruta: int
    medicoes: list[MedicaoBenchmark]


class ErroImportacao(BaseModel):
    linha: int
    coluna: str
    mensagem: str


class ImportacaoSaida(BaseModel):
    regiao: RegiaoSaida
    mensagem: str
