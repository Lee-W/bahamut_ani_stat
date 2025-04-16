from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx
import pytest
import yaml

from bahamut_ani_stat.parser import parser

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

yaml.SafeDumper.yaml_representers[None] = (  # type: ignore
    lambda self, data: yaml.representer.SafeRepresenter.represent_str(
        self,  # type: ignore
        str(data),
    )
)


@pytest.fixture
def datadir_text(request, shared_datadir) -> str:
    return (shared_datadir / request.param).read_text()


@pytest.fixture
def anime_list_data(shared_datadir) -> str:
    return (shared_datadir / "animeList.html").read_text()


@pytest.fixture
def home_page_data(shared_datadir) -> str:
    return (shared_datadir / "homePage.html").read_text()


@pytest.fixture
def out_of_season_data(shared_datadir) -> list:
    return json.loads((shared_datadir / "animeOutOfSeasonMore.html").read_text())


@pytest.mark.parametrize(
    ("view_count_str", "expected"),
    [("101.1萬", 1011000), ("10萬", 100000), ("1213", 1213), ("統計中", -1)],
)
def test_santinize_view_count(view_count_str: str, expected: int):
    assert parser._santinize_view_count(view_count_str) == expected


def test_get_danmu(httpx_mock: HTTPXMock, data_regression, shared_datadir):
    danmu_data = json.loads((shared_datadir / "danmu.json").read_text())
    httpx_mock.add_response(json=danmu_data)

    with httpx.Client():
        danmus = parser.get_danmu("23289", to_dict=True, ignore_none=True)
        data_regression.check(danmus)


def test_get_anime_list_page_count(httpx_mock: HTTPXMock, data_regression, anime_list_data):
    httpx_mock.add_response(text=anime_list_data)
    with httpx.Client():
        page_count = parser.get_anime_list_page_count()
        data_regression.check(page_count)


def test_get_animes_base_data(httpx_mock: HTTPXMock, data_regression, anime_list_data):
    httpx_mock.add_response(text=anime_list_data)
    with httpx.Client():
        animes = parser.get_animes_base_data(to_dict=True, ignore_none=True)
        data_regression.check(animes)


@pytest.mark.slow
def test_get_all_animes_base_data(httpx_mock: HTTPXMock, data_regression, anime_list_data):
    httpx_mock.add_response(text=anime_list_data)
    with httpx.Client():
        animes = parser.get_all_animes_base_data(to_dict=True, ignore_none=True)
        data_regression.check(animes)


@pytest.mark.parametrize(
    "datadir_text",
    [
        "animeVideo.html",
        "animeVideo_new_anime.html",
        "animeVideo_with_season_section.html",
    ],
    ids=("standard", "new_anime", "with_season_section"),
    indirect=True,
)
def test_get_anime_detail_data(httpx_mock: HTTPXMock, data_regression, datadir_text):
    httpx_mock.add_response(text=datadir_text)
    with httpx.Client():
        anime = parser.get_anime_detail_data("23373", to_dict=True, ignore_none=True)
        data_regression.check(anime)


@pytest.mark.parametrize(
    "datadir_text",
    [
        "animeVideo.html",
        "animeVideo_new_anime.html",
        "animeVideo_with_season_section.html",
    ],
    ids=("standard", "new_anime", "with_season_section"),
    indirect=True,
)
def test_get_anime_episode_data(httpx_mock: HTTPXMock, data_regression, datadir_text):
    httpx_mock.add_response(text=datadir_text)
    with httpx.Client():
        ep_data = parser.get_anime_episode_data("23373", to_dict=True, ignore_none=True)
        data_regression.check(ep_data)


def test_get_premium_rate(httpx_mock: HTTPXMock, data_regression, home_page_data):
    httpx_mock.add_response(text=home_page_data)
    with httpx.Client():
        data_regression.check(parser.get_premium_rate())


def test_get_out_of_season_animes(httpx_mock: HTTPXMock, data_regression, out_of_season_data):
    httpx_mock.add_response(json=out_of_season_data)
    with httpx.Client():
        animes = parser.get_out_of_season_animes(to_dict=True, ignore_none=True)
        data_regression.check(animes)


def test_get_new_animes(httpx_mock: HTTPXMock, data_regression, home_page_data):
    httpx_mock.add_response(text=home_page_data)
    with httpx.Client():
        new_animes = parser.get_new_animes(to_dict=True, ignore_none=True)
        data_regression.check(new_animes)
