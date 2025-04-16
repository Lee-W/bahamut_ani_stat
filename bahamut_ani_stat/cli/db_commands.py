from __future__ import annotations

from random import randint
from time import sleep

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
def db_command_group() -> None:
    pass


@db_command_group.command(name="create-tables")
@click.argument("db-uri")
def create_tables_command(db_uri: str) -> None:
    """Create tables if not yet exists"""
    create_tables(db_uri)


@db_command_group.command(name="add-animes-base-data")
@click.argument("db-uri")
@click.option("--page", default=None, type=int)
@click.option("--random-sleep", default=False, is_flag=True)
def add_animes_base_data_command(db_uri: str, page: int | None, random_sleep: bool) -> None:
    """Parse 所有動畫 page and add animes data to database"""
    animes = parser.get_all_animes_base_data(page)

    click.echo(f"Adding {len(animes)} animes base data to {db_uri}")

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        with click.progressbar(animes) as animes_bar:  # type: ignore
            for anime in animes_bar:
                upsert_anime(
                    session,
                    {
                        "sn": anime.sn,
                        "name": anime.name,
                        "release_time": anime.release_time,
                    },
                )
                if is_view_count_changed_since_latest_update(session, anime.view_count, anime.sn):
                    anime_view_count_obj = models.AnimeViewCount(
                        view_count=anime.view_count, anime_sn=anime.sn
                    )
                    session.add(anime_view_count_obj)
                if random_sleep:
                    sec = randint(0, 10)
                    click.echo(f"\nSleep for {sec} seconds")
                    sleep(sec)

    click.echo("Fininsh adding animes")


@db_command_group.command(name="add-premium-rate")
@click.argument("db-uri")
def add_premium_rate_command(db_uri: str) -> None:
    """Add latest premium rate to database"""

    premium_rate = parser.get_premium_rate()
    click.echo(f"Premium rate: {premium_rate}")

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.PremiumRate.premium_rate).order_by(models.PremiumRate.insert_time.desc())
        latest_premium_rate = session.execute(stmt).scalars().first()

        if premium_rate != latest_premium_rate:
            premium_rate_obj = models.PremiumRate(premium_rate=premium_rate)
            session.add(premium_rate_obj)
            click.echo("Finish adding premium rate")
        else:
            click.echo("Skip. Premium rate has not changed since last update.")


@db_command_group.command(name="add-new-animes")
@click.argument("db-uri")
@click.option("--random-sleep", is_flag=True, default=False)
def add_new_animes_command(db_uri: str, random_sleep: bool) -> None:
    """Parse new anime data from 本季新番 table and add them to database"""

    new_animes = parser.get_new_animes()
    new_animes_sn = {anime.sn for anime in new_animes}

    click.echo(f"Adding {len(new_animes)} new animes to {db_uri}")

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        clean_up_old_animes(session, new_animes_sn)

        with click.progressbar(new_animes) as animes_bar:  # type: ignore
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

                if is_view_count_changed_since_latest_update(session, anime.view_count, anime.sn):
                    anime_view_count_obj = models.AnimeViewCount(
                        view_count=anime.view_count, anime_sn=anime.sn
                    )
                    session.add(anime_view_count_obj)

                upsert_episode(session, {"sn": anime.episodes[0].sn, "anime_sn": anime.sn})
                if random_sleep:
                    sec = randint(0, 10)
                    click.echo(f"\nSleep for {sec} seconds")
                    sleep(sec)
    click.echo("Fininsh adding new animes")


@db_command_group.command(name="add-animes-detail")
@click.argument("db-uri")
@click.option("--only-new-anime/--no-only-new-anime", is_flag=True, default=True)
@click.option("--only-old-anime/--no-only-old-anime", is_flag=True, default=False)
@click.option("--random-sleep", is_flag=True, default=False)
@click.option("--retry-limit", default=3, type=int)
def add_animes_detail_command(
    db_uri: str,
    only_new_anime: bool,
    only_old_anime: bool,
    random_sleep: bool,
    retry_limit: int,
) -> None:
    """Parse anime data from first episode and add data to database"""

    if only_new_anime and only_old_anime:
        click.echo(
            click.style(
                "Error: only_new_anime {only_new_anime} and "
                "only_old_anime {only_old_anime} are mutually exclusive"
            )
        )
        return

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.Anime.sn).where(models.Anime.is_available.isnot(False))

        if only_new_anime:
            stmt = stmt.where(models.Anime.is_new.is_(True))
        elif only_old_anime:
            stmt = stmt.where(models.Anime.is_new.is_(False))

        animes_sn = session.execute(stmt).scalars().all()
        click.echo(f"Adding detail data for {len(animes_sn)} animes to {db_uri}")

        with click.progressbar(animes_sn) as animes_bar:
            for anime_sn in animes_bar:
                stmt = select(models.Anime).where(models.Anime.sn == anime_sn)
                anime_obj = session.execute(stmt).fetchone()[0]  # type: ignore

                click.echo(f"\nParsing anime '{anime_obj.name}' ({anime_sn})")

                retry_count = 0
                while retry_count <= retry_limit:
                    try:
                        anime = parser.get_anime_detail_data(anime_sn)
                        break
                    except AttributeError as e:
                        click.echo(
                            click.style(
                                f"Failed to parser {anime_obj.name} ({anime_sn}) due to {str(e)} "
                                "(most likely due to parsing too frequently)",
                                fg="red",
                            )
                        )
                        if "'NoneType' object has no attribute 'text'" == str(e):
                            sec = randint(0, 10)
                            click.echo(f"\nSleep for {sec} seconds")
                            sleep(sec)
                        retry_count += 1
                        click.echo(click.style(f"{retry_count} time retry", fg="yellow"))
                    except Exception as e:
                        click.echo(
                            click.style(
                                f"Failed to parser {anime_obj.name} ({anime_sn}) due to {str(e)} "
                                "(most likely due to parsing too frequently)",
                                fg="red",
                            )
                        )

                if not anime:
                    anime_obj.is_available = False
                    click.echo(
                        click.style(
                            f"\nanime '{anime_obj.name}' ({anime_sn}) is unaviable for now",
                            fg="yellow",
                        )
                    )
                    continue

                if is_score_or_reviewer_changed_since_latest_update(
                    session,
                    anime.anime_score.score,
                    anime.anime_score.reviewer_count,
                    anime.sn,
                ):
                    anime_score = anime.anime_score
                    anime_score_obj = models.AnimeScore(
                        score=anime_score.score,
                        reviewer_count=anime_score.reviewer_count,
                        anime_sn=anime.sn,
                        five_star_percentage=anime_score.five_star_percentage,
                        four_star_percentage=anime_score.four_star_percentage,
                        three_star_percentage=anime_score.three_star_percentage,
                        two_star_percentage=anime_score.two_star_percentage,
                        one_star_percentage=anime_score.one_star_percentage,
                    )
                    session.add(anime_score_obj)

                for episode in anime.episodes:
                    epi_attrs = {
                        "sn": episode.sn,
                        "name": episode.name,
                        "anime_sn": anime.sn,
                    }
                    upsert_episode(session, epi_attrs)

                if random_sleep:
                    sec = randint(0, 10)
                    click.echo(f"\nSleep for {sec} seconds")
                    sleep(sec)

    click.echo("Finish adding anime details")
