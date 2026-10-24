from fastapi import APIRouter

router = APIRouter(tags=["saude"])


@router.get("/saude")
def saude() -> dict[str, str]:
    """Confirma que a API está no ar."""
    return {"status": "ok", "servico": "sismopar"}
