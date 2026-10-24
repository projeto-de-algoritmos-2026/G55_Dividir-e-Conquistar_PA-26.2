from fastapi import FastAPI

from app.routers import saude

app = FastAPI(
    title="SismoPar API",
    description="Par de terremotos mais próximo por divisão e conquista.",
    version="0.1.0",
)

app.include_router(saude.router, prefix="/api")
