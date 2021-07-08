import click
import sqlalchemy
from sqlalchemy.orm import Session

from bahamut_ani_stat.parser import parser
from bahamut_ani_stat.db import models


@click.group(name="db")
def db_command_group():
    pass


def init_db(db_uri: str):
    engine = sqlalchemy.create_engine(db_uri)
    with engine.connect():
        models.Base.metadata.create_all(engine)


@db_command_group.command(name="init-db")
@click.argument("db-uri")
def init_db_command(db_uri: str):
    init_db(db_uri)


@db_command_group.command()
@click.argument("db-uri")
def add_premium_rate(db_uri: str):
    premium_rate = parser.get_premium_rate()

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session:
        premium_rate_obj = models.PremiumRate(premium_rate=premium_rate)

        session.add(premium_rate_obj)
        session.commit()


@db_command_group.command()
@click.argument("db-uri")
def update_new_animes(db_uri: str):
    new_animes = parser.get_new_animes()

    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session:
        for anime in new_animes:
            anime_obj = models.Anime(
                name=anime.name, sn=anime.sn, upload_hour=anime.upload_hour
            )
            session.add(anime_obj)
            session.flush()
            anime_view_count_obj = models.AnimeViewCount(
                view_count=anime.view_count, anime_sn=anime_obj.sn
            )
            episode_obj = models.Episode(sn=anime.episodes[0].sn, anime_sn=anime_obj.sn)
            session.add(anime_view_count_obj)
            session.add(episode_obj)

        session.commit()
