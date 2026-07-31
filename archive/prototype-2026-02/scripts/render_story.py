#!/usr/bin/env python3
"""Render story JSON + dot JSON files into static HTML."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOTS_DIR = DATA_DIR / "dots"
STORIES_DIR = DATA_DIR / "stories"
DIST_DIR = ROOT / "dist"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a story into static HTML")
    parser.add_argument(
        "story",
        help="Story ID (e.g. nishio-profile-ja) or path to a story JSON file",
    )
    parser.add_argument(
        "--outdir",
        default=str(DIST_DIR),
        help="Output directory for generated HTML (default: dist)",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_story_path(story_arg: str) -> Path:
    arg_path = Path(story_arg)
    if arg_path.exists():
        return arg_path

    story_path = STORIES_DIR / f"{story_arg}.json"
    if story_path.exists():
        return story_path

    raise FileNotFoundError(f"Story not found: {story_arg}")


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def render_markdown_block(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n".join(
        f"<p>{escape(paragraph).replace(chr(10), '<br>')}</p>" for paragraph in paragraphs
    )


def render_sources(sources: List[Dict[str, Any]]) -> str:
    if not sources:
        return ""

    items: List[str] = []
    for source in sources:
        url = source.get("url")
        if not url:
            continue
        label = source.get("label") or url
        items.append(
            f'<li><a href="{escape(url)}" target="_blank" rel="noopener noreferrer">'
            f"{escape(label)}</a></li>"
        )

    if not items:
        return ""

    return "\n".join(
        [
            '<div class="dot-sources">',
            "<strong>Sources</strong>",
            "<ul>",
            *items,
            "</ul>",
            "</div>",
        ]
    )


def render_dot_block(block: Dict[str, Any], dot: Dict[str, Any]) -> str:
    caption_html = ""
    if block.get("caption"):
        caption_html = f'<p class="dot-caption">{escape(block["caption"])}</p>'

    note_html = ""
    if block.get("note"):
        note_html = f'<p class="dot-note">{escape(block["note"])}</p>'

    summary_html = ""
    if dot.get("summary"):
        summary_html = f'<p class="dot-summary">{escape(str(dot["summary"]))}</p>'

    sources_html = render_sources(dot.get("sources", []))

    return "\n".join(
        [
            '<article class="dot-card">',
            f'<div class="dot-when">{escape(str(dot.get("when", "")))}</div>',
            f'<h3 class="dot-title">{escape(str(dot.get("title", "")))}</h3>',
            caption_html,
            note_html,
            summary_html,
            sources_html,
            "</article>",
        ]
    )


def load_dot(dot_id: str, cache: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if dot_id in cache:
        return cache[dot_id]

    dot_path = DOTS_DIR / f"{dot_id}.json"
    if not dot_path.exists():
        raise FileNotFoundError(f"Dot not found: {dot_id} ({dot_path})")

    dot = load_json(dot_path)
    cache[dot_id] = dot
    return dot


def render_story(story: Dict[str, Any]) -> str:
    title = str(story.get("title", "Untitled Story"))
    lang = str(story.get("lang", "ja"))
    blocks = story.get("blocks", [])

    dot_cache: Dict[str, Dict[str, Any]] = {}
    body_parts: List[str] = []

    for idx, block in enumerate(blocks):
        if not isinstance(block, dict):
            raise ValueError(f"Invalid block at index {idx}: expected object")

        block_type = block.get("type")
        if block_type == "markdown":
            text = str(block.get("text", ""))
            body_parts.append(f'<section class="markdown-block">{render_markdown_block(text)}</section>')
        elif block_type == "section":
            section_title = str(block.get("title", ""))
            body_parts.append(f"<h2>{escape(section_title)}</h2>")
        elif block_type == "dot":
            dot_id = block.get("dot")
            if not dot_id or not isinstance(dot_id, str):
                raise ValueError(f"Invalid dot block at index {idx}: missing 'dot' id")
            dot = load_dot(dot_id, dot_cache)
            body_parts.append(render_dot_block(block, dot))
        else:
            raise ValueError(f"Unsupported block type at index {idx}: {block_type}")

    body_html = "\n".join(body_parts)

    return f"""<!doctype html>
<html lang=\"{escape(lang)}\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #faf9f6;
      --text: #1f2937;
      --muted: #6b7280;
      --card-bg: #ffffff;
      --border: #d1d5db;
      --accent: #0f766e;
      --shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
      line-height: 1.6;
      color: var(--text);
      background: radial-gradient(circle at top, #e6fffb 0%, var(--bg) 45%);
    }}
    main {{
      max-width: 860px;
      margin: 0 auto;
      padding: 40px 16px 64px;
    }}
    h1 {{
      margin: 0 0 20px;
      font-size: 2rem;
      line-height: 1.25;
    }}
    h2 {{
      margin: 36px 0 16px;
      padding-bottom: 6px;
      border-bottom: 2px solid var(--accent);
      font-size: 1.35rem;
    }}
    p {{
      margin: 0 0 12px;
    }}
    .dot-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 14px 16px;
      margin: 0 0 14px;
    }}
    .dot-when {{
      color: var(--muted);
      font-size: 0.92rem;
      margin-bottom: 2px;
    }}
    .dot-title {{
      margin: 0 0 8px;
      font-size: 1.1rem;
      line-height: 1.4;
    }}
    .dot-caption,
    .dot-note,
    .dot-summary {{
      margin: 0 0 8px;
    }}
    .dot-caption {{
      font-weight: 600;
    }}
    .dot-note {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .dot-sources strong {{
      display: block;
      margin-bottom: 4px;
      font-size: 0.92rem;
    }}
    .dot-sources ul {{
      margin: 0;
      padding-left: 20px;
    }}
    a {{
      color: #0c4a6e;
      word-break: break-word;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{escape(title)}</h1>
    {body_html}
  </main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    story_path = resolve_story_path(args.story)
    story = load_json(story_path)

    story_id = str(story.get("id") or story_path.stem)
    output_dir = Path(args.outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{story_id}.html"

    html_text = render_story(story)
    output_path.write_text(html_text, encoding="utf-8")

    print(f"Rendered: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
