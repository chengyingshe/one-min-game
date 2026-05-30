from __future__ import annotations

import base64
import os
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import GameCreate, GameResponse
from app.services import game_service

router = APIRouter(prefix="/api/upload", tags=["upload"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=GameResponse, status_code=201)
async def upload_game(
    file: UploadFile = File(...),
    name: str = Form(...),
    display_name: str = Form(...),
    description: str = Form(""),
    genre: str = Form("arcade"),
    author_name: str = Form(""),
    config_yaml: str = Form(""),
    screen_width: int = Form(800),
    screen_height: int = Form(600),
    controls: str = Form(""),
    screenshot_base64: str = Form(""),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")

    existing = game_service.get_game(db, name)
    if existing:
        raise HTTPException(status_code=409, detail=f"Game '{name}' already exists")

    game_dir = Path(settings.GAMES_DIR) / name
    game_dir.mkdir(parents=True, exist_ok=True)

    zip_path = game_dir / "upload.zip"
    content = await file.read()
    zip_path.write_bytes(content)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            entries = zf.namelist()
            top_dirs = {n.split("/")[0] for n in entries if "/" in n}
            has_root_file = any("/" not in n for n in entries)
            if len(top_dirs) == 1 and not has_root_file:
                prefix = list(top_dirs)[0] + "/"
                for entry in entries:
                    if entry == prefix:
                        continue
                    target = game_dir / entry[len(prefix):]
                    if entry.endswith("/"):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(zf.read(entry))
            else:
                zf.extractall(game_dir)
    except zipfile.BadZipFile:
        zip_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    finally:
        zip_path.unlink(missing_ok=True)

    # Save preview screenshot if provided
    preview_url = None
    if screenshot_base64:
        try:
            screenshots_dir = Path(settings.SCREENSHOTS_DIR) / name
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            preview_path = screenshots_dir / "preview.png"
            preview_path.write_bytes(base64.b64decode(screenshot_base64))
            preview_url = f"/static/screenshots/{name}/preview.png"
        except Exception:
            pass

    game_data = GameCreate(
        name=name,
        display_name=display_name,
        description=description,
        genre=genre,
        author_name=author_name,
        config_yaml=config_yaml,
        screen_width=screen_width,
        screen_height=screen_height,
        controls=controls,
    )
    result = game_service.create_game(db, game_data)
    if preview_url:
        game_service.update_preview(db, name, preview_url)
    return result
