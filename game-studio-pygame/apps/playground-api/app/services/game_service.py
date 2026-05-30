from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import shutil

from sqlalchemy.orm import Session

from app.config import settings
from app.database import GameRecord, RatingRecord
from app.models import GameCreate, GameResponse


def _to_response(rec: GameRecord) -> GameResponse:
    preview = rec.preview_image_url
    if preview and not preview.startswith(("http://", "https://", "/")):
        preview = f"/static/screenshots/{preview}"
    return GameResponse(
        id=rec.id,
        name=rec.name,
        display_name=rec.display_name,
        description=rec.description or "",
        genre=rec.genre,
        author_name=rec.author_name or "",
        preview_image_url=preview,
        screen_width=rec.screen_width,
        screen_height=rec.screen_height,
        controls=rec.controls or "",
        is_template=rec.is_template,
        play_count=rec.play_count,
        avg_rating=rec.avg_rating,
        rating_count=rec.rating_count,
        created_at=rec.created_at,
    )


def list_games(
    db: Session,
    *,
    genre: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> list[GameResponse]:
    q = db.query(GameRecord)
    if genre:
        q = q.filter(GameRecord.genre == genre)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (GameRecord.display_name.ilike(like)) | (GameRecord.description.ilike(like))
        )
    col = getattr(GameRecord, sort, GameRecord.created_at)
    if order == "asc":
        q = q.order_by(col.asc())
    else:
        q = q.order_by(col.desc())
    rows = q.offset(offset).limit(limit).all()
    return [_to_response(r) for r in rows]


def get_game(db: Session, name: str) -> Optional[GameResponse]:
    rec = db.query(GameRecord).filter(GameRecord.name == name).first()
    if not rec:
        return None
    return _to_response(rec)


def create_game(db: Session, data: GameCreate) -> GameResponse:
    rec = GameRecord(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        genre=data.genre,
        author_name=data.author_name,
        config_yaml=data.config_yaml,
        screen_width=data.screen_width,
        screen_height=data.screen_height,
        controls=data.controls,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return _to_response(rec)


def delete_game(db: Session, name: str) -> bool:
    rec = db.query(GameRecord).filter(GameRecord.name == name).first()
    if not rec:
        return False
    game_dir = Path(settings.GAMES_DIR) / name
    if game_dir.exists():
        shutil.rmtree(game_dir, ignore_errors=True)
    db.delete(rec)
    db.commit()
    return True


def increment_play_count(db: Session, name: str) -> bool:
    rec = db.query(GameRecord).filter(GameRecord.name == name).first()
    if not rec:
        return False
    rec.play_count = (rec.play_count or 0) + 1
    db.commit()
    return True


def rate_game(db: Session, game_name: str, session_id: str, rating: int) -> Optional[GameResponse]:
    rec = db.query(GameRecord).filter(GameRecord.name == game_name).first()
    if not rec:
        return None
    existing = (
        db.query(RatingRecord)
        .filter(RatingRecord.game_name == game_name, RatingRecord.session_id == session_id)
        .first()
    )
    if existing:
        old_rating = existing.rating
        existing.rating = rating
        total = rec.avg_rating * rec.rating_count - old_rating + rating
        rec.avg_rating = total / rec.rating_count
    else:
        db.add(RatingRecord(game_name=game_name, session_id=session_id, rating=rating))
        total = rec.avg_rating * rec.rating_count + rating
        rec.rating_count += 1
        rec.avg_rating = total / rec.rating_count
    db.commit()
    db.refresh(rec)
    return _to_response(rec)


def update_preview(db: Session, name: str, image_path: str) -> None:
    rec = db.query(GameRecord).filter(GameRecord.name == name).first()
    if rec:
        rec.preview_image_url = image_path
        db.commit()
