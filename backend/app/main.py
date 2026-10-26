from fastapi import FastAPI

from app.erros import registrar_tratadores
from app.routers import calculos, catalogos, regioes, saude

app = FastAPI(
    title="SismoPar API",
    description=(
        "Par de terremotos mais próximo por divisão e conquista. Os eventos são projetados "
        "no plano da região (azimutal equidistante, km) e todo resultado traz a distância "
        "projetada, a geodésica (Haversine) e o status da verificação geodésica."
    ),
    version="0.1.0",
)

registrar_tratadores(app)
for modulo in (saude, regioes, catalogos, calculos):
    app.include_router(modulo.router, prefix="/api")
