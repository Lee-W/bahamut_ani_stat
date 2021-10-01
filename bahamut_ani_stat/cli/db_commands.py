from typing import Optional

import click
import sqlalchemy

# from dataclasses import todict
from sqlalchemy import select
from sqlalchemy.orm import Session

from bahamut_ani_stat.db import models
from bahamut_ani_stat.db.utils import (
    clean_up_old_animes,
    create_tables,
    is_score_or_reviewer_changed_since_latest_update,
    is_view_count_changed_since_latest_update,
    upsert_anime,
    upsert_episode,
)
from bahamut_ani_stat.parser import parser


@click.group(name="db")
def db_command_group():
    pass


@db_command_group.command(name="create-tables")
@click.argument("db-uri")
def create_tables_command(db_uri: str):
    """Create tables if not yet exists"""
    create_tables(db_uri)


@db_command_group.command(name="add-animes-base-data")
@click.argument("db-uri")
@click.option("--page", default=None, type=int)
def add_animes_base_data_command(db_uri: str, page: Optional[int]):
    """Parse 所有動畫 page and add animes data to database"""
    animes = parser.get_all_animes_base_data(page)

    click.echo(f"Adding {len(animes)} animes base data to {db_uri}")

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        with click.progressbar(animes) as animes_bar:
            for anime in animes_bar:
                upsert_anime(
                    session,
                    {
                        "sn": anime.sn,
                        "name": anime.name,
                        "release_time": anime.release_time,
                    },
                )
                if is_view_count_changed_since_latest_update(
                    session, anime.view_count, anime.sn
                ):
                    anime_view_count_obj = models.AnimeViewCount(
                        view_count=anime.view_count, anime_sn=anime.sn
                    )
                    session.add(anime_view_count_obj)

    click.echo("Fininsh adding animes")


@db_command_group.command(name="add-premium-rate")
@click.argument("db-uri")
def add_premium_rate_command(db_uri: str):
    """Add latest premium rate to database"""

    premium_rate = parser.get_premium_rate()
    click.echo(f"Premium rate: {premium_rate}")

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.PremiumRate.premium_rate).order_by(
            models.PremiumRate.insert_time.desc()
        )
        latest_premium_rate = session.execute(stmt).scalars().first()

        if premium_rate != latest_premium_rate:
            premium_rate_obj = models.PremiumRate(premium_rate=premium_rate)
            session.add(premium_rate_obj)
            click.echo("Finish adding premium rate")
        else:
            click.echo("Skip. Premium rate has not changed since last update.")


@db_command_group.command(name="add-new-animes")
@click.argument("db-uri")
def add_new_animes_command(db_uri: str):
    """Parse new anime data from 本季新番 table and add them to database"""

    new_animes = parser.get_new_animes()
    new_animes_sn = {anime.sn for anime in new_animes}

    click.echo(f"Adding {len(new_animes)} new animes to {db_uri}")

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        clean_up_old_animes(session, new_animes_sn)

        with click.progressbar(new_animes) as animes_bar:
            for anime in animes_bar:
                upsert_anime(
                    session,
                    {
                        "sn": anime.sn,
                        "name": anime.name,
                        "upload_hour": anime.upload_hour,
                        "is_new": True if "電影" not in anime.labels else False,
                    },
                )

                if is_view_count_changed_since_latest_update(
                    session, anime.view_count, anime.sn
                ):
                    anime_view_count_obj = models.AnimeViewCount(
                        view_count=anime.view_count, anime_sn=anime.sn
                    )
                    session.add(anime_view_count_obj)

                upsert_episode(
                    session, {"sn": anime.episodes[0].sn, "anime_sn": anime.sn}
                )
    click.echo("Fininsh adding new animes")


@db_command_group.command(name="add-animes-detail")
@click.argument("db-uri")
@click.option("--only-new-anime/--no-only-new-anime", is_flag=True, default=True)
def add_animes_detail(db_uri: str, only_new_anime: bool):
    """Parse anime data from first episode and add data to database"""

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.Anime.sn).where(models.Anime.is_available.is_(True))
        if only_new_anime:
            stmt = stmt.where(models.Anime.is_new.is_(True))
        animes_sn = session.execute(stmt).scalars().all()
        click.echo(f"Adding detail data for {len(animes_sn)} animes to {db_uri}")

        with click.progressbar(animes_sn) as animes_bar:
            for anime_sn in animes_bar:
                try:
                    anime = parser.get_anime_detail_data(anime_sn)
                except Exception:
                    click.echo(f"Failed to parser anime {anime_sn}")

                if not anime:
                    stmt = select(models.Anime).where(models.Anime.sn == anime_sn)
                    anime_obj = session.execute(stmt).fetchone()[0]  # type: ignore
                    anime_obj.is_available = False
                    click.echo(f"\nanime {anime_sn} is unaviable for now")
                    continue

                if is_score_or_reviewer_changed_since_latest_update(
                    session,
                    anime.anime_score.score,
                    anime.anime_score.reviewer_count,
                    anime.sn,
                ):
                    anime_score_obj = models.AnimeScore(
                        score=anime.anime_score.score,
                        reviewer_count=anime.anime_score.reviewer_count,
                        anime_sn=anime.sn,
                    )
                    session.add(anime_score_obj)

                for episode in anime.episodes:
                    epi_attrs = {
                        "sn": episode.sn,
                        "name": episode.name,
                        "anime_sn": anime.sn,
                    }
                    upsert_episode(session, epi_attrs)
    click.echo("Finish adding anime details")
