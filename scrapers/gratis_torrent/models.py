"""Data models for movie information."""

from datetime import datetime, timezone

from pydantic import Field


from scrapers.utils.models import Movie as BaseMovie


class Movie(BaseMovie):
    """Movie data model with validation."""

    duracao: str | None = Field(None, exclude=True)
    duracao_minutos: int | None = Field(None, ge=1)
    date_updated: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
