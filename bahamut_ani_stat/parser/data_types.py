from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from datetime import datetime


class Danmu(BaseModel):
    text: str
    color: str
    size: int
    position: int
    time: int
    sn: int
    userid: str


class Episode(BaseModel):
    sn: str | None = None
    name: str | None = None
    season_title: str | None = None
    upload_date: datetime | str | None = (
        None  # TODO: Fix tests and type conflict (str and datetime)
    )
    view_count: int | None = None


class AnimeScore(BaseModel):
    score: float
    reviewer_count: int

    five_star_percentage: float | None = None
    four_star_percentage: float | None = None
    three_star_percentage: float | None = None
    two_star_percentage: float | None = None
    one_star_percentage: float | None = None


class Anime(BaseModel):
    sn: str
    name: str | None = None
    view_count: int | None = None
    release_time: datetime | None = None
    metadata: dict[str, str] | None = None
    upload_hour: str | None = None
    labels: list[str] | None = None

    anime_score: AnimeScore | None = None
    episodes: list[Episode] | None = None
    dammus: list[Danmu] | None = None
