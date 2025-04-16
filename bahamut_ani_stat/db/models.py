from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, declarative_base, relationship

Base = declarative_base()

anime_studio_association = Table(
    "anime_studio_association",
    Base.metadata,
    Column("anime_sn", Integer, ForeignKey("anime.sn")),
    Column("studio_id", Integer, ForeignKey("studio.id_")),
)

anime_director_association = Table(
    "anime_director_association",
    Base.metadata,
    Column("anime_sn", Integer, ForeignKey("anime.sn")),
    Column("director_id", Integer, ForeignKey("director.id_")),
)


class Anime(Base):
    __tablename__ = "anime"

    sn = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    release_time = Column(DateTime, nullable=True)
    upload_hour = Column(String, nullable=True)
    is_new = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)

    genre = Column(String, nullable=True)
    target_audience = Column(String, nullable=True)

    agent_id = Column(Integer, ForeignKey("agent.id_"))
    agent: Mapped[Agent] = relationship("Agent", back_populates="animes")
    directors: list[Director] = relationship(
        "Director", back_populates="animes", secondary=anime_director_association
    )
    studios: list[Studio] = relationship(
        "Studio", back_populates="animes", secondary=anime_studio_association
    )

    anime_view_counts: list[AnimeViewCount] = relationship(
        "AnimeViewCount", back_populates="anime", uselist=True
    )
    anime_scores: list[AnimeScore] = relationship("AnimeScore", back_populates="anime", uselist=True)
    episodes: list[Episode] = relationship("Episode", back_populates="anime", uselist=True)
    danmus: list[Danmu] = relationship("Danmu", back_populates="anime", uselist=True)


class Director(Base):
    __tablename__ = "director"

    id_ = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)

    animes: Anime = relationship("Anime", back_populates="directors", secondary=anime_director_association)


class Agent(Base):
    __tablename__ = "agent"

    id_ = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)

    animes: Anime = relationship("Anime", back_populates="agent", uselist=True)


class Studio(Base):
    __tablename__ = "studio"

    id_ = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)

    animes: Anime = relationship("Anime", back_populates="studios", secondary=anime_studio_association)


class AnimeViewCount(Base):
    __tablename__ = "anime_view_count"

    id_ = Column(Integer, primary_key=True)
    view_count = Column(Integer)
    insert_time = Column(DateTime, default=datetime.now())

    anime_sn = Column(String, ForeignKey("anime.sn"))
    anime: Anime = relationship("Anime", back_populates="anime_view_counts")


class AnimeScore(Base):
    __tablename__ = "anime_score"

    id_ = Column(Integer, primary_key=True)
    score = Column(Float)
    reviewer_count = Column(Integer)

    five_star_percentage = Column(Float)
    four_star_percentage = Column(Float)
    three_star_percentage = Column(Float)
    two_star_percentage = Column(Float)
    one_star_percentage = Column(Float)

    insert_time = Column(DateTime, default=datetime.now())

    anime_sn = Column(String, ForeignKey("anime.sn"))
    anime: Anime = relationship("Anime", back_populates="anime_scores")


class Danmu(Base):
    __tablename__ = "danmu"

    sn = Column(Integer, primary_key=True)
    text = Column(String)
    color = Column(String(10))
    size = Column(Integer)
    position = Column(Integer)
    time = Column(DateTime)
    userid = Column(String)

    anime_sn = Column(String, ForeignKey("anime.sn"))
    anime: Anime = relationship("Anime", back_populates="danmus")


class Episode(Base):
    __tablename__ = "episode"

    sn = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    season_title = Column(String, nullable=True)
    upload_date = Column(DateTime, nullable=True)

    anime_sn = Column(String, ForeignKey("anime.sn"))
    anime: Anime = relationship("Anime", back_populates="episodes")

    episode_view_counts: EpisodeViewCount = relationship(
        "EpisodeViewCount", back_populates="episode", uselist=True
    )


class EpisodeViewCount(Base):
    __tablename__ = "episode_view_count"

    id_ = Column(Integer, primary_key=True)
    view_count = Column(Integer)
    insert_time = Column(DateTime, default=datetime.now())

    episode_sn = Column(String, ForeignKey("episode.sn"))
    episode: Episode = relationship("Episode", back_populates="episode_view_counts")


class PremiumRate(Base):
    __tablename__ = "premium_rate"

    id_ = Column(Integer, primary_key=True)
    premium_rate = Column(Float)
    insert_time = Column(DateTime, default=datetime.now())
