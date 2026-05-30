from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import RunRequest, RunResponse
from app.services import game_service, runner_service

router = APIRouter(prefix="/api/runner", tags=["runner"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/run", response_model=RunResponse)
def run_game(req: RunRequest, db: Session = Depends(get_db)):
    game = game_service.get_game(db, req.game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    try:
        result = runner_service.run_game(
            game_name=req.game_name,
            duration_seconds=req.duration_seconds,
            capture_frames=req.capture_frames,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Runner error: {e}")

    if result["screenshots"] and result["screenshots"][0]:
        game_service.update_preview(db, req.game_name, result["screenshots"][0])

    return RunResponse(
        screenshots=result["screenshots"],
        gif_url=result.get("gif_url"),
        exit_code=result["exit_code"],
        duration_ms=result["duration_ms"],
    )


@router.get("/status/{task_id}")
def get_status(task_id: str):
    return {"task_id": task_id, "status": "completed"}
