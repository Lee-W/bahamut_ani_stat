from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Anime(Base):
    __tablename__ = "anime"

    sn = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    release_time = Column(DateTime, nullable=True)
    upload_hour = Column(String, nullable=True)
    # TODO: metadata: Optional[Dict[str, str]] = None

    anime_view_counts: List["AnimeViewCount"] = relationship(
        "AnimeViewCount", back_populates="anime", uselist=True
    )
    anime_scores: List["AnimeScore"] = relationship(
        "AnimeScore", back_populates="anime", uselist=True
    )
    episodes: List["Episode"] = relationship(
        "Episode", back_populates="anime", uselist=True
    )
    danmus: List["Danmu"] = relationship("Danmu", back_populates="anime", uselist=True)


class AnimeViewCount(Base):
    __tablename__ = "anime_view_count"

    vc_id = Column(Integer, primary_key=True)
    view_count = Column(Integer)
    insert_time = Column(DateTime, default=datetime.now())

    anime_sn = Column(String, ForeignKey("anime.sn"))
    anime: "Anime" = relationship("Anime", back_populates="anime_view_counts")


class AnimeScore(Base):
    __tablename__ = "anime_score"

    score_id = Column(Integer, primary_key=True)
    average_score = Column(Float)
    insert_time = Column(DateTime, default=datetime.now())

    anime_sn = Column(String, ForeignKey("anime.sn"))

    anime: "Anime" = relationship("Anime", back_populates="anime_scores")
    # TODO: features = Column


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

    anime: "Anime" = relationship("Anime", back_populates="danmus")


class Episode(Base):
    __tablename__ = "episode"

    sn = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    season_title = Column(String, nullable=True)
    upload_date = Column(DateTime, nullable=True)

    anime_sn = Column(String, ForeignKey("anime.sn"))
    anime: "Anime" = relationship("Anime", back_populates="episodes")

    episode_view_counts: "EpisodeViewCount" = relationship(
        "EpisodeViewCount", back_populates="episode", uselist=True
    )


class EpisodeViewCount(Base):
    __tablename__ = "episode_view_count"

    vc_id = Column(Integer, primary_key=True)
    view_count = Column(Integer)
    insert_time = Column(DateTime, default=datetime.now())

    episode_sn = Column(String, ForeignKey("episode.sn"))
    episode: "Episode" = relationship("Episode", back_populates="episode_view_counts")


class PremiumRate(Base):
    __tablename__ = "premium_rate"

    prem_id = Column(Integer, primary_key=True)
    premium_rate = Column(Float)
    insert_time = Column(DateTime, default=datetime.now())
