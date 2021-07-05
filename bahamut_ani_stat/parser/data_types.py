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
class AnimeEpisode:
    episode_sn: str
    episode_name: str
    season_title: Optional[str]
    upload_date: Optional[datetime] = None
    episode_view_count: Optional[int] = None


@dataclass_json
@dataclass
class AnimeScore:
    features: List[Tuple[str, str]]  # TODO: Tuple[str, float]
    score: float
    reviewer_count: int


@dataclass_json
@dataclass
class Anime:
    anime_sn: str
    anime_name: str
    anime_release_time: datetime
    anime_view_count: int
    anime_metadata: Optional[Dict[str, str]] = None

    anime_score: Optional[AnimeScore] = None
    episodes: Optional[List[AnimeEpisode]] = None
    dammus: Optional[List[Danmu]] = None
