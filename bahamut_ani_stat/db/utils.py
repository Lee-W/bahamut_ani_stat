from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sqlalchemy
from sqlalchemy import func, select, update
from sqlalchemy.dialects.sqlite import insert

from bahamut_ani_stat.db import models

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# pre-defined CTE

latest_score_cte = (
    select(
        models.AnimeScore.anime_sn,
        func.first_value(models.AnimeScore.score)
        .over(
            partition_by=models.AnimeScore.anime_sn,
            order_by=models.AnimeScore.insert_time.desc(),
        )
        .label("score"),
    )
    .distinct()
    .cte("latest_score")
)
latest_view_count_cte = (
    select(
        models.AnimeViewCount.anime_sn,
        func.first_value(models.AnimeViewCount.view_count)
        .over(
            partition_by=models.AnimeViewCount.anime_sn,
            order_by=models.AnimeViewCount.insert_time.desc(),
        )
        .label("view_count"),
    )
    .distinct()
    .cte("latest_view_count")
)


def create_tables(db_uri: str) -> None:
    engine = sqlalchemy.create_engine(db_uri)
    with engine.connect():
        models.Base.metadata.create_all(engine)


def upsert_anime(session: Session, attrs: dict[str, Any]) -> None:
    insert_stmt = insert(models.Anime).values(attrs)
    upsert_stmt = insert_stmt.on_conflict_do_update(index_elements=[models.Anime.sn], set_=attrs)
    session.execute(upsert_stmt)


def upsert_episode(session: Session, attrs: dict[str, Any]) -> None:
    insert_stmt = insert(models.Episode).values(attrs)
    upsert_stmt = insert_stmt.on_conflict_do_update(index_elements=[models.Episode.sn], set_=attrs)
    session.execute(upsert_stmt)


def clean_up_old_animes(session: Session, new_animes_sn: set[str]) -> None:
    # Set is_new to False for old animes
    select_stmt = select(models.Anime.sn).where(models.Anime.is_new.is_(True))
    result = session.execute(select_stmt)
    original_new_animes_sn = result.scalars().all()
    old_anime_sn = set(original_new_animes_sn) - set(new_animes_sn)

    update_stmt = update(models.Anime).where(models.Anime.sn.in_(old_anime_sn)).values(is_new=False)
    session.execute(update_stmt)


def is_view_count_changed_since_latest_update(session: Session, view_count: float, anime_sn: str) -> bool:
    stmt = (
        select(models.AnimeViewCount.view_count)
        .filter_by(anime_sn=anime_sn)
        .order_by(models.AnimeViewCount.insert_time.desc())
    )
    latest_view_count = session.execute(stmt).scalars().first()

    return view_count != latest_view_count


def is_score_or_reviewer_changed_since_latest_update(
    session: Session, score: float, reviewer_count: int, anime_sn: str
) -> bool:
    stmt = (
        select(models.AnimeScore.score, models.AnimeScore.reviewer_count)
        .filter_by(anime_sn=anime_sn)
        .order_by(models.AnimeScore.insert_time.desc())
    )
    result = session.execute(stmt).first()
    if result:
        latest_score, latest_reviewer_count = result
        return bool((score != latest_score) or (reviewer_count != latest_reviewer_count))
    return True
