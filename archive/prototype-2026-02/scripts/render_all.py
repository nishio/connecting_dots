#!/usr/bin/env python3
"""Render all stories in data/stories to dist/*.html."""

from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = ROOT / "data" / "stories"
RENDER_SCRIPT = ROOT / "scripts" / "render_story.py"
DIST_DIR = ROOT / "dist"


def render_index(stories: list[dict[str, str]]) -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    items = "\n".join(
        f'<li><a href="{html.escape(story["id"])}.html">{html.escape(story["title"])}</a></li>'
        for story in stories
    )
    content = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Stories Index</title>
  <style>
    body {{
      margin: 0;
      padding: 32px 16px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
      background: #f8fafc;
      color: #1f2937;
    }}
    main {{
      max-width: 860px;
      margin: 0 auto;
      background: #fff;
      border: 1px solid #d1d5db;
      border-radius: 10px;
      padding: 24px;
    }}
    h1 {{
      margin-top: 0;
    }}
    li {{
      margin: 0 0 10px;
    }}
    a {{
      color: #0c4a6e;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Story Index</h1>
    <ul>
      {items}
    </ul>
  </main>
</body>
</html>
"""
    (DIST_DIR / "index.html").write_text(content, encoding="utf-8")


def main() -> int:
    story_paths = sorted(STORIES_DIR.glob("*.json"))
    if not story_paths:
        print("No stories found.")
        return 0

    stories: list[dict[str, str]] = []
    for story_path in story_paths:
        story = json.loads(story_path.read_text(encoding="utf-8"))
        stories.append(
            {
                "id": str(story.get("id") or story_path.stem),
                "title": str(story.get("title") or story_path.stem),
            }
        )
        subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), str(story_path)],
            check=True,
        )
    render_index(stories)
    print(f"Rendered: {DIST_DIR / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
