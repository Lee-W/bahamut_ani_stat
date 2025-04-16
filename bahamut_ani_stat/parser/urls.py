from __future__ import annotations

from urllib.parse import urljoin

GAMMER_ANIME_BASE_URL = "https://ani.gamer.com.tw/"
ANIME_LIST_URL = urljoin(GAMMER_ANIME_BASE_URL, "animeList.php")
ANIME_REF_URL = urljoin(GAMMER_ANIME_BASE_URL, "animeRef.php")
ANIME_VIDEO_URL = urljoin(GAMMER_ANIME_BASE_URL, "animeVideo.php")
ANIME_DANMU_URL = urljoin(GAMMER_ANIME_BASE_URL, "ajax/danmuGet.php")
ANIME_OUT_OF_SEASON_MORE_URL = urljoin(GAMMER_ANIME_BASE_URL, "ajax/animeOutOfSeasonMore.php")
