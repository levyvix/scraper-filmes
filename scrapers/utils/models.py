from pydantic import BaseModel, Field


class Movie(BaseModel):
    """Movie data model with validation."""

    titulo_dublado: str | None = None
    titulo_original: str | None = None
    imdb: float | None = Field(None, ge=0, le=10)
    ano: int | None = Field(None, ge=1888)
    genero: str | None = None
    tamanho: str | None = None
    duracao: str | None = Field(None, description="Duration in minutes")
    qualidade_video: float | None = Field(None, ge=0, description="Video quality score (0-10)")
    qualidade: str | None = Field(None, description="Quality description (e.g., '1080p', '720p BluRay')")
    dublado: bool | None = None
    sinopse: str | None = None
    link: str | None = None
    poster_url: str | None = None
