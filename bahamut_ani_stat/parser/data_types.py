from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

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
    upload_date: Optional[
        Union[datetime, str]
    ] = None  # TODO: Fix tests and type conflict (str and datetime)
    view_count: Optional[int] = None


class AnimeScore(BaseModel):
    score: float
    reviewer_count: int
    features: List[Tuple[str, str]]  # TODO: Tuple[str, float]


class Anime(BaseModel):
    sn: str
    name: Optional[str] = None
    view_count: Optional[int] = None
    release_time: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None
    upload_hour: Optional[str] = None
    labels: Optional[List[str]] = None

    anime_score: Optional[AnimeScore] = None
    episodes: Optional[List[Episode]] = None
    dammus: Optional[List[Danmu]] = None
