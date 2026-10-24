from dataclasses import dataclass
from datetime import date

# Recorte padrão dos catálogos versionados (datas inclusivas)
INICIO_PADRAO = date(2020, 1, 1)
FIM_PADRAO = date(2024, 12, 31)
MAGNITUDE_MIN_PADRAO = 2.5


@dataclass(frozen=True)
class Regiao:
    """Região pré-configurada, delimitada por uma caixa de coordenadas."""

    id: str
    nome: str
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float

    @property
    def centro(self) -> tuple[float, float]:
        """Centro da caixa (latitude, longitude), usado como origem da projeção."""
        return (self.lat_min + self.lat_max) / 2, (self.lon_min + self.lon_max) / 2

    def contem(self, latitude: float, longitude: float) -> bool:
        return (
            self.lat_min <= latitude <= self.lat_max
            and self.lon_min <= longitude <= self.lon_max
        )


# Todas longe do antimeridiano (longitude 180°)
REGIOES: dict[str, Regiao] = {
    regiao.id: regiao
    for regiao in (
        Regiao("japao", "Japão", 30.0, 46.0, 128.0, 146.0),
        Regiao("chile", "Chile", -45.0, -17.0, -76.0, -66.0),
        Regiao("california", "Califórnia", 32.0, 42.0, -125.0, -114.0),
        Regiao("turquia", "Turquia", 35.0, 43.0, 25.0, 45.0),
    )
}
