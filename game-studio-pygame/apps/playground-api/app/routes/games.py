from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import GameCreate, GameResponse, RatingRequest
from app.services import game_service

router = APIRouter(prefix="/api/games", tags=["games"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[GameResponse])
def list_games(
    genre: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = Query("created_at", pattern=r"^(play_count|avg_rating|created_at|name)$"),
    order: str = Query("desc", pattern=r"^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return game_service.list_games(
        db, genre=genre, search=search, sort=sort, order=order, limit=limit, offset=offset
    )


@router.post("", response_model=GameResponse, status_code=201)
def create_game(data: GameCreate, db: Session = Depends(get_db)):
    existing = game_service.get_game(db, data.name)
    if existing:
        raise HTTPException(status_code=409, detail=f"Game '{data.name}' already exists")
    return game_service.create_game(db, data)


@router.get("/{name}", response_model=GameResponse)
def get_game(name: str, db: Session = Depends(get_db)):
    game = game_service.get_game(db, name)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.delete("/{name}", status_code=204)
def delete_game(name: str, db: Session = Depends(get_db)):
    ok = game_service.delete_game(db, name)
    if not ok:
        raise HTTPException(status_code=404, detail="Game not found")


@router.post("/{name}/rate", response_model=GameResponse)
def rate_game(name: str, data: RatingRequest, db: Session = Depends(get_db)):
    result = game_service.rate_game(db, name, data.session_id, data.rating)
    if not result:
        raise HTTPException(status_code=404, detail="Game not found")
    return result


@router.post("/{name}/play", response_model=GameResponse)
def increment_play(name: str, db: Session = Depends(get_db)):
    ok = game_service.increment_play_count(db, name)
    if not ok:
        raise HTTPException(status_code=404, detail="Game not found")
    game = game_service.get_game(db, name)
    return game


@router.get("/{name}/download")
def download_game(name: str, db: Session = Depends(get_db)):
    """Download a game as a ZIP file."""
    game = game_service.get_game(db, name)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game_dir = Path(settings.GAMES_DIR) / name
    if not game_dir.exists():
        raise HTTPException(status_code=404, detail="Game files not found on disk")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(game_dir.rglob("*")):
            if file_path.is_file() and file_path.suffix not in {".pyc", ".pyo"}:
                arcname = f"{name}/{file_path.relative_to(game_dir)}"
                zf.write(file_path, arcname)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name}.zip"'},
    )
