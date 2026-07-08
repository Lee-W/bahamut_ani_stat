from __future__ import annotations

import sqlalchemy
from click.testing import CliRunner
from sqlalchemy import select
from sqlalchemy.orm import Session

from bahamut_ani_stat.cli.db_commands import db_command_group
from bahamut_ani_stat.db import models
from bahamut_ani_stat.parser.data_types import Anime, AnimeScore, Episode


def _db_uri(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'anime.db'}"


def _create_tables(db_uri: str) -> None:
    engine = sqlalchemy.create_engine(db_uri)
    models.Base.metadata.create_all(engine)


def test_add_new_animes_aborts_without_clearing_existing_new_flags(monkeypatch, tmp_path) -> None:
    db_uri = _db_uri(tmp_path)
    _create_tables(db_uri)
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        session.add(models.Anime(sn="1", name="existing", is_new=True))

    monkeypatch.setattr("bahamut_ani_stat.cli.db_commands.parser.get_new_animes", lambda: [])

    result = CliRunner().invoke(db_command_group, ["add-new-animes", db_uri])

    assert result.exit_code != 0
    assert "Got 0 new animes" in result.output
    with Session(engine) as session:
        anime = session.execute(select(models.Anime).where(models.Anime.sn == "1")).scalar_one()
        assert anime.is_new is True


def test_add_animes_detail_writes_metadata_score_and_episodes(monkeypatch, tmp_path) -> None:
    db_uri = _db_uri(tmp_path)
    _create_tables(db_uri)
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        session.add(models.Anime(sn="1", name="anime", is_new=True))

    def fake_get_anime_detail_data(anime_sn: str) -> Anime:
        return Anime(
            sn=anime_sn,
            metadata={
                "作品類型": "推理懸疑",
                "對象族群": "青年",
                "台灣代理": "曼迪",
                "導演監督": "木下麥",
                "製作廠商": "P.I.C.S. × OLM",
            },
            anime_score=AnimeScore(score=4.8, reviewer_count=100),
            episodes=[Episode(sn="10", name="第 1 集")],
        )

    monkeypatch.setattr(
        "bahamut_ani_stat.cli.db_commands.parser.get_anime_detail_data",
        fake_get_anime_detail_data,
    )

    result = CliRunner().invoke(db_command_group, ["add-animes-detail", db_uri, "--retry-limit", "0"])

    assert result.exit_code == 0
    with Session(engine) as session:
        anime = session.execute(select(models.Anime).where(models.Anime.sn == "1")).scalar_one()
        assert anime.genre == "推理懸疑"
        assert anime.target_audience == "青年"
        assert anime.agent is not None
        assert anime.agent.name == "曼迪"
        assert {studio.name for studio in anime.studios} == {"P.I.C.S.", "OLM"}

        score = session.execute(
            select(models.AnimeScore).where(models.AnimeScore.anime_sn == "1")
        ).scalar_one()
        assert score.score == 4.8
        assert score.reviewer_count == 100

        episode = session.execute(select(models.Episode).where(models.Episode.sn == "10")).scalar_one()
        assert episode.name == "第 1 集"


def test_add_animes_detail_parse_error_does_not_mark_anime_unavailable(monkeypatch, tmp_path) -> None:
    db_uri = _db_uri(tmp_path)
    _create_tables(db_uri)
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        session.add(models.Anime(sn="1", name="anime", is_new=True, is_available=True))

    def fake_get_anime_detail_data(anime_sn: str) -> Anime:
        raise AttributeError("'NoneType' object has no attribute 'text'")

    monkeypatch.setattr(
        "bahamut_ani_stat.cli.db_commands.parser.get_anime_detail_data",
        fake_get_anime_detail_data,
    )
    monkeypatch.setattr("bahamut_ani_stat.cli.db_commands.sleep", lambda sec: None)

    result = CliRunner().invoke(db_command_group, ["add-animes-detail", db_uri, "--retry-limit", "0"])

    assert result.exit_code != 0
    assert "Failed to parse anime (1) after 1 attempts" in result.output
    with Session(engine) as session:
        anime = session.execute(select(models.Anime).where(models.Anime.sn == "1")).scalar_one()
        assert anime.is_available is True
