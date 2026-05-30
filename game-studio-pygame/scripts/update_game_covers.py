#!/usr/bin/env python3
"""Update game cover preview_image_url in the playground database.

Scans data/screenshots/ for preview PNGs and sets each game's
preview_image_url accordingly.

Usage:
    python update_game_covers.py [--db path/to/games.db] [--screenshots-dir data/screenshots]
    python update_game_covers.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_DATA_DIR = PROJECT_ROOT / "apps" / "playground-api" / "data"


def main():
    parser = argparse.ArgumentParser(description="Update game cover preview URLs")
    parser.add_argument("--db", default=None, help="Path to SQLite database")
    parser.add_argument("--screenshots-dir", default=None, help="Path to screenshots directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without applying")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else API_DATA_DIR / "games.db"
    screenshots_dir = Path(args.screenshots_dir) if args.screenshots_dir else API_DATA_DIR / "screenshots"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    # Use SQLite directly (avoids importing FastAPI/SQLAlchemy)
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get all games
    cursor.execute("SELECT id, name, display_name, preview_image_url FROM games")
    rows = cursor.fetchall()

    updated = 0
    skipped = 0

    for row in rows:
        game_id, name, display_name, current_url = row
        preview_png = screenshots_dir / name / "preview.png"

        target_url = f"/static/screenshots/{name}/preview.png" if preview_png.exists() else None

        if target_url and target_url == current_url:
            print(f"  [OK] {name}: already set to {target_url}")
            skipped += 1
            continue

        if target_url:
            if args.dry_run:
                print(f"  [DRY-RUN] {name}: would set preview_image_url -> {target_url}")
            else:
                cursor.execute(
                    "UPDATE games SET preview_image_url = ? WHERE id = ?",
                    (target_url, game_id),
                )
                print(f"  [UPDATED] {name}: {current_url or '(none)'} -> {target_url}")
            updated += 1
        else:
            print(f"  [SKIP] {name}: no preview.png found in {screenshots_dir / name}")
            skipped += 1

    if not args.dry_run and updated > 0:
        conn.commit()
        print(f"\nCommitted {updated} updates to database")

    conn.close()
    print(f"\nSummary: {updated} updated, {skipped} skipped, {len(rows)} total games")
    sys.exit(0)


if __name__ == "__main__":
    main()
