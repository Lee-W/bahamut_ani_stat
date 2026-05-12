from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


anime_studio_association = Table(
    "anime_studio_association",
    Base.metadata,
    Column("anime_sn", String, ForeignKey("anime.sn")),
    Column("studio_id", Integer, ForeignKey("studio.id_")),
)

anime_director_association = Table(
    "anime_director_association",
    Base.metadata,
    Column("anime_sn", String, ForeignKey("anime.sn")),
    Column("director_id", Integer, ForeignKey("director.id_")),
)


class Anime(Base):
    __tablename__ = "anime"

    sn: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None]
    release_time: Mapped[datetime | None]
    upload_hour: Mapped[str | None]
    is_new: Mapped[bool] = mapped_column(default=False)
    is_available: Mapped[bool] = mapped_column(default=True)

    genre: Mapped[str | None]
    target_audience: Mapped[str | None]

    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent.id_"))
    agent: Mapped[Agent | None] = relationship("Agent", back_populates="animes")
    directors: Mapped[list[Director]] = relationship(
        "Director", back_populates="animes", secondary=anime_director_association
    )
    studios: Mapped[list[Studio]] = relationship(
        "Studio", back_populates="animes", secondary=anime_studio_association
    )

    anime_view_counts: Mapped[list[AnimeViewCount]] = relationship(
        "AnimeViewCount", back_populates="anime"
    )
    anime_scores: Mapped[list[AnimeScore]] = relationship("AnimeScore", back_populates="anime")
    episodes: Mapped[list[Episode]] = relationship("Episode", back_populates="anime")
    danmus: Mapped[list[Danmu]] = relationship("Danmu", back_populates="anime")


class Director(Base):
    __tablename__ = "director"

    id_: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String, unique=True)

    animes: Mapped[list[Anime]] = relationship(
        "Anime", back_populates="directors", secondary=anime_director_association
    )


class Agent(Base):
    __tablename__ = "agent"

    id_: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String, unique=True)

    animes: Mapped[list[Anime]] = relationship("Anime", back_populates="agent")


class Studio(Base):
    __tablename__ = "studio"

    id_: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String, unique=True)

    animes: Mapped[list[Anime]] = relationship(
        "Anime", back_populates="studios", secondary=anime_studio_association
    )


class AnimeViewCount(Base):
    __tablename__ = "anime_view_count"

    id_: Mapped[int] = mapped_column(primary_key=True)
    view_count: Mapped[int | None]
    insert_time: Mapped[datetime] = mapped_column(default=datetime.now)

    anime_sn: Mapped[str | None] = mapped_column(ForeignKey("anime.sn"))
    anime: Mapped[Anime] = relationship("Anime", back_populates="anime_view_counts")


class AnimeScore(Base):
    __tablename__ = "anime_score"

    id_: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[float]
    reviewer_count: Mapped[int]

    five_star_percentage: Mapped[float | None]
    four_star_percentage: Mapped[float | None]
    three_star_percentage: Mapped[float | None]
    two_star_percentage: Mapped[float | None]
    one_star_percentage: Mapped[float | None]

    insert_time: Mapped[datetime] = mapped_column(default=datetime.now)

    anime_sn: Mapped[str | None] = mapped_column(ForeignKey("anime.sn"))
    anime: Mapped[Anime] = relationship("Anime", back_populates="anime_scores")


class Danmu(Base):
    __tablename__ = "danmu"

    sn: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str | None]
    color: Mapped[str | None] = mapped_column(String(10))
    size: Mapped[int | None]
    position: Mapped[int | None]
    time: Mapped[datetime | None]
    userid: Mapped[str | None]

    anime_sn: Mapped[str | None] = mapped_column(ForeignKey("anime.sn"))
    anime: Mapped[Anime] = relationship("Anime", back_populates="danmus")


class Episode(Base):
    __tablename__ = "episode"

    sn: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None]
    season_title: Mapped[str | None]
    upload_date: Mapped[datetime | None]

    anime_sn: Mapped[str | None] = mapped_column(ForeignKey("anime.sn"))
    anime: Mapped[Anime] = relationship("Anime", back_populates="episodes")

    episode_view_counts: Mapped[list[EpisodeViewCount]] = relationship(
        "EpisodeViewCount", back_populates="episode"
    )


class EpisodeViewCount(Base):
    __tablename__ = "episode_view_count"

    id_: Mapped[int] = mapped_column(primary_key=True)
    view_count: Mapped[int | None]
    insert_time: Mapped[datetime] = mapped_column(default=datetime.now)

    episode_sn: Mapped[str | None] = mapped_column(ForeignKey("episode.sn"))
    episode: Mapped[Episode] = relationship("Episode", back_populates="episode_view_counts")


class PremiumRate(Base):
    __tablename__ = "premium_rate"

    id_: Mapped[int] = mapped_column(primary_key=True)
    premium_rate: Mapped[float | None]
    insert_time: Mapped[datetime] = mapped_column(default=datetime.now)
