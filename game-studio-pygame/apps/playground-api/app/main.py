from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings, ensure_dirs
from app.database import init_db
from app.routes import games, upload, runner, ws_play, ws_multiplayer, rooms, llm, ws_mystery


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_dirs()
    init_db()
    yield


app = FastAPI(title="PyGame Playground API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(upload.router)
app.include_router(runner.router)
app.include_router(ws_play.router)
app.include_router(ws_multiplayer.router)
app.include_router(rooms.router)
app.include_router(llm.router)
app.include_router(ws_mystery.router)

screenshots_dir = Path(settings.SCREENSHOTS_DIR)
screenshots_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")
