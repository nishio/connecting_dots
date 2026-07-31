#!/usr/bin/env python3
"""Build story JSON files from dot tags and curated pick lists."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
DOTS_DIR = ROOT / "data" / "dots"
STORIES_DIR = ROOT / "data" / "stories"

TAG_STORIES = [
    {
        "id": "nishio-involved-all-ja",
        "lang": "ja",
        "title": "西尾関与 dots 全件（詳細）",
        "intro": "`nishio-involved` タグが付いたdotを時系列で並べた詳細ページ。プロフィール・活動・関連イベントを一望するための『全部入り』。",
        "include_tags": ["nishio-involved"],
    },
    {
        "id": "plurality-all-ja",
        "lang": "ja",
        "title": "Plurality関連 dots 全件（詳細）",
        "intro": "`plurality` タグが付いたdotを時系列で並べた詳細ページ。日本におけるPlurality史と周辺実践をまとめて追うための『全部入り』。",
        "include_tags": ["plurality"],
    },
]

PICK_STORIES = [
    {
        "id": "nishio-involved-picks-ja",
        "lang": "ja",
        "title": "西尾関与 dots ピックアップ",
        "intro": "`nishio-involved-all-ja` を母集団として、現時点で優先して見せるカードを選んだ版。状況に応じて差し替える運用を想定。",
        "dot_ids": [
            "plurality-ja-localization-lead-2025",
            "shin-tokyo-2050-broad-listening-2024-2025",
            "tokyo-gov-anno-broad-listening-2024",
            "digital-democracy-2030-kouchou-ai-idobata-2025",
            "japan-choice-yoron-chizu-2024",
            "nishio-cybozu-labs-principal-researcher-2018-04",
            "nishio-langbook-published-2013-04",
            "nishio-word2vec-book-published-2014-05",
        ],
    },
    {
        "id": "plurality-picks-ja",
        "lang": "ja",
        "title": "Plurality関連 dots ピックアップ",
        "intro": "`plurality-all-ja` を母集団として、節目を短く把握するためのピックアップ版。今後の進展に合わせて更新する。",
        "dot_ids": [
            "glen-collab-book-launch-2022-09-16",
            "plurality-jp-glen-translator-call-2022-09-08",
            "plurality-tokyo-2023-04-14",
            "autotrans-start-2023-10-17",
            "plurality-jp-glen-in-japan-2024-01-03",
            "plurality-jp-shin-tokyo-2050-project-start-2024-11-22",
            "plurality-jp-dd2030-oss-release-2025-03-16",
            "plurality-jp-book-release-2025-05-02",
        ],
    },
]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_sort_key(dot: Dict[str, Any]) -> tuple[int, int, int, str]:
    when = str(dot.get("when", ""))
    years = [int(y) for y in re.findall(r"\d{4}", when)]
    major_year = max(years) if years else 0

    m = re.search(r"(\d{4})[-/](\d{1,2})(?:[-/](\d{1,2}))?", when)
    month = 0
    day = 0
    if m:
        month = int(m.group(2))
        day = int(m.group(3) or 0)

    dot_id = str(dot.get("id", ""))
    return (major_year, month, day, dot_id)


def make_blocks(dot_ids: Iterable[str], section_title: str) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = [{"type": "section", "title": section_title}]
    for dot_id in dot_ids:
        blocks.append({"type": "dot", "dot": dot_id})
    return blocks


def main() -> int:
    STORIES_DIR.mkdir(parents=True, exist_ok=True)

    dots_by_id: Dict[str, Dict[str, Any]] = {}
    for dot_path in sorted(DOTS_DIR.glob("*.json")):
        dot = load_json(dot_path)
        dot_id = str(dot.get("id") or dot_path.stem)
        dots_by_id[dot_id] = dot

    for spec in TAG_STORIES:
        include_tags = set(spec["include_tags"])
        matched = [
            dot for dot in dots_by_id.values() if include_tags.intersection(set(dot.get("tags", [])))
        ]
        matched.sort(key=get_sort_key, reverse=True)
        dot_ids = [str(dot["id"]) for dot in matched]

        story = {
            "id": spec["id"],
            "lang": spec["lang"],
            "title": spec["title"],
            "blocks": [
                {
                    "type": "markdown",
                    "text": spec["intro"],
                },
                {
                    "type": "markdown",
                    "text": f"対象タグ: {', '.join(spec['include_tags'])} / 件数: {len(dot_ids)}",
                },
                *make_blocks(dot_ids, "カード一覧"),
            ],
        }
        out_path = STORIES_DIR / f"{spec['id']}.json"
        dump_json(out_path, story)
        print(f"Wrote: {out_path}")

    for spec in PICK_STORIES:
        for dot_id in spec["dot_ids"]:
            if dot_id not in dots_by_id:
                raise FileNotFoundError(f"Pick story references unknown dot id: {dot_id}")

        story = {
            "id": spec["id"],
            "lang": spec["lang"],
            "title": spec["title"],
            "blocks": [
                {
                    "type": "markdown",
                    "text": spec["intro"],
                },
                {
                    "type": "markdown",
                    "text": f"件数: {len(spec['dot_ids'])}",
                },
                *make_blocks(spec["dot_ids"], "ピックアップ"),
            ],
        }
        out_path = STORIES_DIR / f"{spec['id']}.json"
        dump_json(out_path, story)
        print(f"Wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
