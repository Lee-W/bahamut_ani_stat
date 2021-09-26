import re
from datetime import datetime
from functools import wraps
from typing import Any, Callable, List, Optional

import httpx
from bs4 import BeautifulSoup
from tqdm import tqdm, trange

from bahamut_ani_stat import config
from bahamut_ani_stat.parser.data_types import Anime, AnimeScore, Danmu, Episode
from bahamut_ani_stat.parser.urls import (
    ANIME_DANMU_URL,
    ANIME_LIST_URL,
    ANIME_OUT_OF_SEASON_MORE_URL,
    ANIME_REF_URL,
    ANIME_VIDEO_URL,
    GAMMER_ANIME_BASE_URL,
)


def _model_to_dict(obj: Any, ignore_none: bool = True) -> Any:
    if isinstance(obj, (Anime, AnimeScore, Danmu, Episode)):
        return {
            key: _model_to_dict(value, ignore_none)
            for key, value in obj.dict().items()
            if ignore_none and value
        }
    elif isinstance(obj, list):
        return [_model_to_dict(obj_item, ignore_none) for obj_item in obj]
    elif isinstance(obj, dict):
        return {key: value for key, value in obj.items() if ignore_none and value}
    return obj


def check_anime_availability(soup: BeautifulSoup) -> bool:
    messages = ["此作品目前無影片可以播放" or "沒有此部作品"]

    for message in messages:
        if message in soup.text:
            return False
    return True


def to_dict_args(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        to_dict = kwargs.pop("to_dict", None)
        ignore_none = kwargs.pop("ignore_none", None)

        obj = func(*args, **kwargs)

        if to_dict:
            return _model_to_dict(obj, ignore_none)
        return obj

    return wrapper


def _santinize_view_count(view_count_str: str) -> int:
    pattern = re.compile(r"(\d+\.{0,1}\d*)(萬*)")
    match = pattern.match(view_count_str)

    if match:
        if match.group(2):
            return int(float(match.group(1)) * 10000)
        else:
            return int(match.group(1))
    else:
        tqdm.write(f'View count "{view_count_str}" can not be parsed as a number ')
        return -1


def _santinize_sn(url_suffix: str) -> str:
    pattern = re.compile(r".*\?sn=(\d+)")
    match = pattern.match(url_suffix)
    if match:
        return match.group(1)
    return ""


@to_dict_args
def get_danmu(episode_sn: str) -> List[Danmu]:
    req = httpx.post(ANIME_DANMU_URL, data={"sn": episode_sn})
    return [Danmu(**danmu) for danmu in req.json()]


def get_premium_rate(soup: Optional[BeautifulSoup] = None) -> float:
    if not soup:
        req = httpx.get(GAMMER_ANIME_BASE_URL)
        soup = BeautifulSoup(req.text, features=config.bs4_parser)
    return float(soup.select_one("div.premium-info__title > span.number").text)


def get_anime_list_page_count() -> int:
    req = httpx.get(ANIME_LIST_URL)
    soup = BeautifulSoup(req.text, features=config.bs4_parser)
    last_page_a = soup.select_one("div.page_number > a:nth-last-child(1)")
    return int(last_page_a.text)


@to_dict_args
def get_animes_base_data(page_number: int = 1) -> List[Anime]:
    req = httpx.get(ANIME_LIST_URL, params={"page": page_number, "sort": 1})
    soup = BeautifulSoup(req.text, features=config.bs4_parser)

    theme_list_main_a_s = soup.select("div.theme-list-block > a.theme-list-main")

    animes_data: List[Anime] = list()
    for theme_list_main_a in theme_list_main_a_s:
        view_number = theme_list_main_a.select_one("div.show-view-number > p").text
        theme_info_div = theme_list_main_a.select_one("div.theme-info-block")
        anime_labels = [
            s.text
            for s in theme_list_main_a.select_one("div.anime-label-block").select(
                "span"
            )
        ]

        anime = Anime(
            sn=_santinize_sn(theme_list_main_a.get("href")),
            view_count=_santinize_view_count(view_number),
            name=theme_info_div.select_one("p.theme-name").text,
            release_time=datetime.strptime(
                theme_info_div.select_one("p.theme-time").text, "年份：%Y/%m"
            ),
            labels=anime_labels,
        )
        animes_data.append(anime)
    return animes_data


@to_dict_args
def get_all_animes_base_data(page_count: Optional[int] = None) -> List[Anime]:
    if not page_count:
        page_count = get_anime_list_page_count()

    animes_data = list()
    for page_number in trange(1, page_count + 1, desc="Parsing all anime pages"):
        animes_data.extend(get_animes_base_data(page_number))
    return animes_data


@to_dict_args
def _get_anime_score(soup: BeautifulSoup) -> AnimeScore:
    acg_data_li_s = soup.select("div.ACG-data > ul:first-child > li")
    acg_persent_li_s = soup.select("div.ACG-data > ul.ACG-persent > li")

    acg_score_soup = soup.select_one("div.ACG-score")
    try:
        reviewer_count = int(acg_score_soup.span.extract().text[:-1])
    except ValueError:
        reviewer_count = -1
    acg_score = float(acg_score_soup.text) if acg_score_soup.text != "--" else -1

    return AnimeScore(
        score=acg_score,
        reviewer_count=reviewer_count,
        features=[
            (str(data.text), str(percent.text))
            for data, percent in zip(acg_data_li_s, acg_persent_li_s)
        ],
    )


@to_dict_args
def get_anime_detail_data(anime_sn: str) -> Optional[Anime]:
    req = httpx.get(ANIME_REF_URL, params={"sn": anime_sn})
    soup = BeautifulSoup(req.text, features=config.bs4_parser)

    if not check_anime_availability(soup):
        return None

    season_section = soup.select_one("section.season")
    episodes_data: List[Episode] = list()
    if not season_section:
        # new anime
        episodes_data.append(
            Episode(
                season_title=None,
                name="1",  # TODO: parse from class=anime_name
                sn=req.url.params.get("sn"),  # type: ignore
            )
        )
    else:
        season_section_titles = season_section.select("p") or [None]

        for sections_title, section_ul in zip(
            season_section_titles, soup.select("section.season > ul")
        ):
            li_a_s = section_ul.select("a")
            for li_a in li_a_s:
                episodes_data.append(
                    Episode(
                        season_title=sections_title.text if sections_title else None,
                        name=li_a.text,
                        sn=_santinize_sn(li_a.get("href")),
                    )
                )

    data_type_li_s = soup.select("ul.data_type > li")
    anime_metadata = dict()
    for data_type_content in data_type_li_s:
        key = data_type_content.span.extract().text
        value = data_type_content.text
        anime_metadata[key] = value

    anime_score = _get_anime_score(soup)

    return Anime(
        sn=anime_sn,
        metadata=anime_metadata,
        anime_score=anime_score,
        episodes=episodes_data,
    )


@to_dict_args
def get_anime_episode_data(episode_sn: str) -> Episode:
    req = httpx.get(ANIME_VIDEO_URL, params={"sn": episode_sn})
    soup = BeautifulSoup(req.text, features=config.bs4_parser)
    anime_info_detail = soup.select_one("div.anime_info_detail")
    upload_date = datetime.strptime(
        anime_info_detail.select_one("p").text, "上架時間：%Y/%m/%d %H:%M"
    )
    view_count = _santinize_view_count(anime_info_detail.select_one("span > span").text)

    return Episode(
        sn=episode_sn,
        upload_date=upload_date,
        view_count=view_count,
    )


@to_dict_args
def get_new_animes() -> List[Anime]:
    req = httpx.get(GAMMER_ANIME_BASE_URL)
    soup = BeautifulSoup(req.text, features=config.bs4_parser)
    new_anime_block = soup.select_one("div.newanime-wrap.timeline-ver")

    anime_sn_s = [
        s.get("data-animesn")
        for s in new_anime_block.select("div.newanime-date-area")[:-1]
    ]
    episode_sn_s = [
        _santinize_sn(s.get("href"))
        for s in new_anime_block.select("a.anime-card-block")
    ]
    anime_hours = [
        s.text
        for s in new_anime_block.select("div.anime-hours-block > span.anime-hours")
    ]
    anime_names = [
        s.text
        for s in new_anime_block.select("div.anime-name > p.anime-name_for-marquee")
    ]
    anime_view_counts = [
        _santinize_view_count(s.text)
        for s in new_anime_block.select("div.anime-watch-number > p")
    ]
    animes_labels = [
        [ss.text for ss in s.select("span.label-edition")]
        for s in new_anime_block.select("div.anime-label-block")
    ]

    return [
        Anime(
            sn=ani_sn,
            name=ani_name,
            upload_hour=ani_upload_hour,
            view_count=ani_view_count,
            episodes=[Episode(sn=epi_sn)],
            labels=ani_labels,
        )
        for ani_sn, epi_sn, ani_upload_hour, ani_name, ani_view_count, ani_labels in zip(
            anime_sn_s,
            episode_sn_s,
            anime_hours,
            anime_names,
            anime_view_counts,
            animes_labels,
        )
    ]


@to_dict_args
def get_out_of_season_animes(offset: int = 1, limit: int = 10) -> List[Anime]:
    req = httpx.get(
        ANIME_OUT_OF_SEASON_MORE_URL, params={"offset": offset, "limit": limit}
    )
    req_data = req.json()
    if req_data["msg"] == "success":
        soup = BeautifulSoup(req.json()["data"], features=config.bs4_parser)

        anime_sn_s = [
            _santinize_sn(s.get("href")) for s in soup.select("a.theme-list-main")
        ]
        anime_view_counts = [
            _santinize_view_count(s.text)
            for s in soup.select("div.show-view-number > p")
        ]
        anime_names = [s.text for s in soup.select("p.theme-name")]
        episode_upload_time_s = [s.text for s in soup.select("p.theme-time")]
        latest_episode_names = [
            s.text.strip() for s in soup.select("span.theme-number")
        ]

        return [
            Anime(
                sn=sn,
                view_count=view_count,
                name=name,
                episodes=[Episode(upload_date=upload_date, name=epi_name)],
            )
            for sn, view_count, name, upload_date, epi_name in zip(
                anime_sn_s,
                anime_view_counts,
                anime_names,
                episode_upload_time_s,
                latest_episode_names,
            )
        ]
    return []
