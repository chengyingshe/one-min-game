from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone

from app.config import settings


class Base(DeclarativeBase):
    pass


class GameRecord(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    genre = Column(String(32), default="arcade", index=True)
    author_name = Column(String(64), default="")
    config_yaml = Column(Text, default="")
    screen_width = Column(Integer, default=800)
    screen_height = Column(Integer, default=600)
    controls = Column(Text, default="")
    preview_image_url = Column(String(256), nullable=True)
    is_template = Column(Boolean, default=False)
    play_count = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class RatingRecord(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_name = Column(String(64), nullable=False, index=True)
    session_id = Column(String(128), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
