from typing import Optional

import click
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from bahamut_ani_stat.db import models
from bahamut_ani_stat.db.utils import (
    clean_up_old_animes,
    create_tables,
    is_view_count_changed_since_latest_update,
    upsert_anime,
)
from bahamut_ani_stat.parser import parser


@click.group(name="db")
def db_command_group():
    pass


@db_command_group.command(name="create-tables")
@click.argument("db-uri")
def create_tables_command(db_uri: str):
    create_tables(db_uri)


@db_command_group.command(name="add-animes-base-data")
@click.argument("db-uri")
@click.option("--page", default=None, type=int)
def add_animes_base_data_command(db_uri: str, page: Optional[int]):
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
                        "is_new": True,
                    },
                )

                if is_view_count_changed_since_latest_update(
                    session, anime.view_count, anime.sn
                ):
                    anime_view_count_obj = models.AnimeViewCount(
                        view_count=anime.view_count, anime_sn=anime.sn
                    )
                    session.add(anime_view_count_obj)

                episode_attrs = {"sn": anime.episodes[0].sn, "anime_sn": anime.sn}
                insert_stmt = insert(models.Episode).values(**episode_attrs)
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=[models.Episode.sn], set_=episode_attrs
                )
                session.execute(upsert_stmt)
    click.echo("Fininsh adding new animes")
