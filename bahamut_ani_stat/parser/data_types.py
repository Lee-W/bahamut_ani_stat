from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Danmu:
    text: str
    color: str
    size: int
    position: int
    time: int
    sn: int
    userid: str


@dataclass_json
@dataclass
class Episode:
    sn: Optional[str] = None
    name: Optional[str] = None
    season_title: Optional[str] = None
    upload_date: Optional[datetime] = None
    view_count: Optional[int] = None


@dataclass_json
@dataclass
class AnimeScore:
    score: float
    reviewer_count: int
    features: List[Tuple[str, str]]  # TODO: Tuple[str, float]


@dataclass_json
@dataclass
class Anime:
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
