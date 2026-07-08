from __future__ import annotations

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.orm import Session

from bahamut_ani_stat.db import models
from bahamut_ani_stat.db.utils import (
    apply_anime_metadata,
    clean_up_old_animes,
    is_score_or_reviewer_changed_since_latest_update,
    is_view_count_changed_since_latest_update,
    upsert_anime,
    upsert_episode,
)


def _session() -> Session:
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    return Session(engine)


def test_upsert_anime_inserts_and_updates_existing_row() -> None:
    with _session() as session, session.begin():
        upsert_anime(session, {"sn": "1", "name": "old name"})
        upsert_anime(session, {"sn": "1", "name": "new name"})

        anime = session.execute(select(models.Anime).where(models.Anime.sn == "1")).scalar_one()

        assert anime.name == "new name"


def test_upsert_episode_inserts_and_updates_existing_row() -> None:
    with _session() as session, session.begin():
        upsert_anime(session, {"sn": "1", "name": "anime"})
        upsert_episode(session, {"sn": "10", "anime_sn": "1", "name": "episode 1"})
        upsert_episode(session, {"sn": "10", "anime_sn": "1", "name": "episode 1 revised"})

        episode = session.execute(select(models.Episode).where(models.Episode.sn == "10")).scalar_one()

        assert episode.name == "episode 1 revised"


def test_clean_up_old_animes_keeps_current_new_animes() -> None:
    with _session() as session, session.begin():
        session.add_all(
            [
                models.Anime(sn="1", name="still new", is_new=True),
                models.Anime(sn="2", name="old now", is_new=True),
            ]
        )

        clean_up_old_animes(session, {"1"})

        still_new = session.execute(select(models.Anime).where(models.Anime.sn == "1")).scalar_one()
        old_now = session.execute(select(models.Anime).where(models.Anime.sn == "2")).scalar_one()

        assert still_new.is_new is True
        assert old_now.is_new is False


def test_is_view_count_changed_since_latest_update() -> None:
    with _session() as session, session.begin():
        session.add(models.Anime(sn="1", name="anime"))

        assert is_view_count_changed_since_latest_update(session, 100, "1") is True

        session.add(models.AnimeViewCount(anime_sn="1", view_count=100))
        session.flush()

        assert is_view_count_changed_since_latest_update(session, 100, "1") is False
        assert is_view_count_changed_since_latest_update(session, 101, "1") is True


def test_is_score_or_reviewer_changed_since_latest_update() -> None:
    with _session() as session, session.begin():
        session.add(models.Anime(sn="1", name="anime"))

        assert is_score_or_reviewer_changed_since_latest_update(session, 4.8, 100, "1") is True

        session.add(models.AnimeScore(anime_sn="1", score=4.8, reviewer_count=100))
        session.flush()

        assert is_score_or_reviewer_changed_since_latest_update(session, 4.8, 100, "1") is False
        assert is_score_or_reviewer_changed_since_latest_update(session, 4.9, 100, "1") is True
        assert is_score_or_reviewer_changed_since_latest_update(session, 4.8, 101, "1") is True


def test_apply_anime_metadata_updates_columns_and_relationships() -> None:
    with _session() as session, session.begin():
        anime = models.Anime(sn="1", name="anime")
        session.add(anime)

        apply_anime_metadata(
            session,
            anime,
            {
                "作品類型": "推理懸疑",
                "對象族群": "青年",
                "台灣代理": "曼迪",
                "導演監督": "木下麥、另一位導演",
                "製作廠商": "P.I.C.S. × OLM",
            },
        )

        assert anime.genre == "推理懸疑"
        assert anime.target_audience == "青年"
        assert anime.agent is not None
        assert anime.agent.name == "曼迪"
        assert {director.name for director in anime.directors} == {"木下麥", "另一位導演"}
        assert {studio.name for studio in anime.studios} == {"P.I.C.S.", "OLM"}
