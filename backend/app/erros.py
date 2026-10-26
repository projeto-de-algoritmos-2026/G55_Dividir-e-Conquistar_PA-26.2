"""Erros da API em português."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

LOCAIS = {"body": "corpo", "query": "consulta", "path": "caminho"}

MENSAGENS = {
    "missing": "campo obrigatório",
    "greater_than": "deve ser maior que {gt}",
    "greater_than_equal": "deve ser maior ou igual a {ge}",
    "less_than": "deve ser menor que {lt}",
    "less_than_equal": "deve ser menor ou igual a {le}",
    "date_parsing": "data inválida, use o formato AAAA-MM-DD",
    "date_from_datetime_parsing": "data inválida, use o formato AAAA-MM-DD",
    "date_type": "data inválida, use o formato AAAA-MM-DD",
    "float_parsing": "deve ser um número",
    "float_type": "deve ser um número",
    "int_parsing": "deve ser um número inteiro",
    "int_type": "deve ser um número inteiro",
    "int_from_float": "deve ser um número inteiro",
    "string_type": "deve ser um texto",
    "string_too_short": "deve ter pelo menos {min_length} caractere(s)",
    "too_short": "deve ter pelo menos {min_length} item(ns)",
    "too_long": "deve ter no máximo {max_length} item(ns)",
    "list_type": "deve ser uma lista",
    "json_invalid": "JSON inválido",
    "model_attributes_type": "corpo da requisição inválido",
    "dict_type": "corpo da requisição inválido",
    "extra_forbidden": "campo não reconhecido",
}


class ErroNegocio(Exception):
    """Erro previsto da aplicação, devolvido como {"detail": mensagem}."""

    def __init__(self, status: int, mensagem: str, detalhes: object | None = None):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem
        self.detalhes = detalhes


def _formatar(valor: object) -> object:
    # 10.0 vira 10; 2.5 continua 2.5
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    return valor


def _traduzir(erro: dict) -> dict[str, str]:
    local = [LOCAIS.get(str(parte), str(parte)) for parte in erro.get("loc", ())]
    tipo = erro.get("type", "")
    if tipo == "value_error":
        # Validadores próprios já escrevem em português
        mensagem = str(erro.get("msg", "")).removeprefix("Value error, ")
    elif tipo in MENSAGENS:
        contexto = {chave: _formatar(valor) for chave, valor in erro.get("ctx", {}).items()}
        mensagem = MENSAGENS[tipo].format(**contexto)
    else:
        mensagem = str(erro.get("msg", "valor inválido"))
    return {"campo": ".".join(local), "mensagem": mensagem}


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, erro: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422, content={"detail": [_traduzir(e) for e in erro.errors()]}
        )

    @app.exception_handler(ErroNegocio)
    async def _negocio(_: Request, erro: ErroNegocio) -> JSONResponse:
        conteudo: dict[str, object] = {"detail": erro.mensagem}
        if erro.detalhes is not None:
            conteudo["erros"] = erro.detalhes
        return JSONResponse(status_code=erro.status, content=conteudo)
