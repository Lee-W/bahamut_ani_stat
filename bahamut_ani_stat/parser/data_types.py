from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Optional, Union

from pydantic import BaseModel


class Danmu(BaseModel):
    text: str
    color: str
    size: int
    position: int
    time: int
    sn: int
    userid: str


class Episode(BaseModel):
    sn: Optional[str] = None
    name: Optional[str] = None
    season_title: Optional[str] = None
    upload_date: Union[datetime, Optional[str]] = None  # TODO: Fix tests and type conflict (str and datetime)
    view_count: Optional[int] = None


class AnimeScore(BaseModel):
    score: float
    reviewer_count: int

    five_star_percentage: Optional[float] = None
    four_star_percentage: Optional[float] = None
    three_star_percentage: Optional[float] = None
    two_star_percentage: Optional[float] = None
    one_star_percentage: Optional[float] = None


class Anime(BaseModel):
    sn: str
    name: Optional[str] = None
    view_count: Optional[int] = None
    release_time: Optional[datetime] = None
    metadata: Optional[dict[str, str]] = None
    upload_hour: Optional[str] = None
    labels: Optional[list[str]] = None

    anime_score: Optional[AnimeScore] = None
    episodes: Optional[list[Episode]] = None
    dammus: Optional[list[Danmu]] = None


Anime.model_rebuild()
Episode.model_rebuild()
