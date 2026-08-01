#!/usr/bin/env python3
"""ConnectingDots build v0 (pilot).

pilot/dots.json（受理済み Dot の単一フラットプール）と pilot/story-*.json（Story 定義）を読み、
build/ に「人間向け静的HTML」と「AIクロール面」を吐く。

設計対応:
- 単一フラットプール（ドメイン非分割）… dots.json をそのまま corpus とする
- 孤児 Dot は一級市民 … どの Story にも属さない Dot も URL・dots.json・all-dots に必ず出す
- 逆引き(Dot→Stories)は派生・非ゲート … in_stories を生成するが Dot の掲載条件にはしない
- クロール面 = Web 配信成果物 … build/dots.json + per-Dot URL + all-dots + sitemap.xml + llms.txt(ルート)
- status フィールドなし … 受理済みは dots.json にいる、で足りる
- 検証状態の随伴 … verifiability + refs をそのまま各 Dot に載せる

stdlib のみ。使い方: python3 build.py
"""
import glob
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build")
# 本番の canonical は nhiro.org（deploy-topology 決定）。プロトタイプでは sitemap/llms 用に使う。
BASE_URL = "https://nhiro.org"

CSS = """
body{font-family:system-ui,-apple-system,'Hiragino Kaku Gothic ProN',sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;line-height:1.7;color:#1a1a1a}
a{color:#0645ad}h1{font-size:1.5rem}h2{font-size:1.15rem;margin-top:2rem;border-bottom:1px solid #ddd;padding-bottom:.2rem}
.meta{color:#666;font-size:.85rem}.dot{margin:.6rem 0;padding:.5rem .8rem;border-left:3px solid #cbd5e1;background:#f8fafc}
.date{color:#475569;font-variant-numeric:tabular-nums;font-size:.85rem}.tags span{background:#e2e8f0;border-radius:3px;padding:0 .4rem;font-size:.75rem;margin-right:.3rem}
.orphan{border-left-color:#f59e0b}.caption{color:#334155;font-size:.9rem;margin-top:.2rem}
.refs a{font-size:.8rem;margin-right:.5rem}nav{font-size:.85rem;margin-bottom:1rem}code{background:#eee;padding:0 .3rem;border-radius:3px}
"""


def esc(s):
    return html.escape(str(s))


def page(title, body):
    return (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(title)}</title><style>{CSS}</style></head><body>"
            f"<nav><a href='../index.html'>&larr; index</a></nav>{body}</body></html>")


def load():
    dots_doc = json.load(open(os.path.join(HERE, "dots.json")))
    dots = {d["id"]: d for d in dots_doc["dots"]}
    stories = []
    for p in sorted(glob.glob(os.path.join(HERE, "story-*.json"))):
        stories.append(json.load(open(p)))
    return dots, stories


def reverse_lookup(dots, stories):
    """Dot -> [story ids]。派生・非ゲート。"""
    rev = {did: [] for did in dots}
    for s in stories:
        for did in s["dots"]:
            if did in rev and s["id"] not in rev[did]:
                rev[did].append(s["id"])
    return rev


def dot_block(d, rev, orphan_note=True):
    tags = "".join(f"<span>{esc(t)}</span>" for t in d.get("tags", []))
    refs = "".join(f"<a href='{esc(r)}'>{esc(_short(r))}</a>" for r in d.get("refs", []))
    cref = "".join(f"<a href='https://scrapbox.io/nishio/{esc(c)}'>[{esc(c)}]</a> " for c in d.get("cosense_refs", []))
    is_orphan = not rev.get(d["id"])
    cls = "dot orphan" if (is_orphan and orphan_note) else "dot"
    onote = " <span class='meta'>（どの Story にも未収録＝孤児 Dot・発見可能）</span>" if (is_orphan and orphan_note) else ""
    verif = d.get("verifiability", "?")
    return (f"<div class='{cls}' id='{esc(d['id'])}'>"
            f"<span class='date'>{esc(d.get('date',''))}</span> "
            f"<a href='../dots/{esc(d['id'])}.html'>{esc(d.get('event',''))}</a>{onote}"
            f"<div class='meta'>kind: {esc(d.get('kind','?'))} / verifiability: {esc(verif)}"
            f"{' / entities: '+esc('、'.join(d.get('entities',[]))) if d.get('entities') else ''}</div>"
            f"<div class='tags'>{tags}</div>"
            f"<div class='refs'>{cref}{refs}</div></div>")


def _short(url):
    return url.replace("https://", "").replace("http://", "").split("/")[0]


def build():
    dots, stories = load()
    rev = reverse_lookup(dots, stories)
    os.makedirs(os.path.join(OUT, "dots"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "stories"), exist_ok=True)
    urls = []

    # 1) per-Dot ページ（孤児含む全 Dot に安定 URL）
    for did, d in dots.items():
        instories = rev[did]
        story_links = "、".join(
            f"<a href='../stories/{esc(sid)}.html'>{esc(_story_title(stories,sid))}</a>" for sid in instories
        ) or "（どの Story にも未収録＝孤児 Dot）"
        body = (f"<h1>{esc(d.get('event',''))}</h1>"
                f"<p class='date'>{esc(d.get('date',''))} ・ kind: {esc(d.get('kind','?'))} ・ "
                f"verifiability: {esc(d.get('verifiability','?'))}</p>"
                f"<p class='meta'>id: <code>{esc(did)}</code></p>"
                f"<p>entities: {esc('、'.join(d.get('entities',[])) or '—')}</p>"
                f"<p class='tags'>{''.join(f'<span>{esc(t)}</span>' for t in d.get('tags',[]))}</p>"
                f"<h2>出典</h2><p class='refs'>"
                + "".join(f"<a href='{esc(r)}'>{esc(r)}</a><br>" for r in d.get("refs", []))
                + "".join(f"<a href='https://scrapbox.io/nishio/{esc(c)}'>[{esc(c)}]</a><br>" for c in d.get("cosense_refs", []))
                + (f"" if (d.get("refs") or d.get("cosense_refs")) else "—")
                + f"</p><h2>含まれる Story（逆引き・派生）</h2><p>{story_links}</p>")
        open(os.path.join(OUT, "dots", did + ".html"), "w").write(page(d.get("event", did), body))
        urls.append(f"{BASE_URL}/dots/{did}.html")

    # 2) Story ページ
    for s in stories:
        body = _render_story(s, dots, rev)
        open(os.path.join(OUT, "stories", s["id"] + ".html"), "w").write(page(s["title"], body))
        urls.append(f"{BASE_URL}/stories/{s['id']}.html")

    # 3) all-dots（絞り込みなし・時系列・孤児明示）
    ordered = sorted(dots.values(), key=lambda d: (d.get("date", ""), d["id"]))
    n_orphan = sum(1 for did in dots if not rev[did])
    body = (f"<h1>All Dots</h1><p class='meta'>全 {len(dots)} Dot（絞り込みなし）。"
            f"うち孤児（どの Story にも未収録）{n_orphan} 件。これらも一級で発見可能。</p>"
            + "".join(dot_block(d, rev) for d in ordered))
    open(os.path.join(OUT, "all-dots.html"), "w").write(page("All Dots", body))
    urls.append(f"{BASE_URL}/all-dots.html")

    # 4) dots.json（★AIクロールの一次面：フラット全 Dot ＋ 派生 in_stories ＋ url）
    manifest = {
        "$comment": "AI crawl surface. 単一フラットプールの全受理Dot。in_stories は逆引き(派生・非ゲート)。status フィールドなし(dots.jsonにいる=accepted)。",
        "generated_from": "pilot",
        "canonical": f"{BASE_URL}/dots.json",
        "count": len(dots),
        "dots": [dict(d, url=f"{BASE_URL}/dots/{d['id']}.html", in_stories=rev[d["id"]]) for d in ordered],
        "stories": [{"id": s["id"], "title": s["title"], "audience": s.get("audience"),
                     "dots": s["dots"], "url": f"{BASE_URL}/stories/{s['id']}.html"} for s in stories],
    }
    open(os.path.join(OUT, "dots.json"), "w").write(json.dumps(manifest, ensure_ascii=False, indent=2))

    # 5) Connecting Dots System の index（ja / en）/ sitemap / llms.txt
    story_items = "".join(
        f"<li><a href='stories/{esc(s['id'])}.html'>{esc(s['title'])}</a> "
        f"<span class='meta'>({len(s['dots'])} dots / {esc('、'.join(s.get('audience', [])))})</span></li>"
        for s in stories)

    desc_ja = ("<strong>Connecting Dots System</strong> は、後から振り返るとストーリーになる出来事を、"
               "忘れて失う前に記録しておくための仕組みです。検証可能な事実を「点（Dot）」として貯め、"
               "そこから人が後で「線（Story）」を編みます。「点は後からしか繋がらない」（Steve Jobs）ため、"
               "事実は個別に記録し、意味づけ（どう繋ぐか）は後から与える。"
               "同じ点の集合から、読者や目的に応じて複数の Story が並立します。"
               "全 Dot は出典付きの機械可読データ <code>dots.json</code> として公開します。")
    desc_en = ("<strong>Connecting Dots System</strong> records the events that, in hindsight, become a story "
               "— before they are forgotten and lost. Verifiable facts are kept as “Dots”; a person later "
               "weaves them into “Stories.” Because you can only connect the dots looking backwards "
               "(Steve Jobs), the facts are recorded individually and the meaning — how they connect — is added "
               "afterward. The same set of dots supports multiple parallel stories, by audience and purpose. "
               "Every Dot is published as sourced, machine-readable data (<code>dots.json</code>).")

    ja_body = (
        f"<h1>Connecting Dots System</h1><p>{desc_ja}</p>"
        f"<h2>Stories</h2><ul>{story_items}</ul>"
        f"<p class='meta'>読み物として整えた版は<a href='{BASE_URL}/ja.html'>西尾のホームページ</a>（各テーマ）にあります。</p>"
        f"<h2>全 Dot</h2><ul>"
        f"<li><a href='all-dots.html'>All Dots</a>（{len(dots)} 件・孤児含む）</li>"
        f"<li><a href='dots.json'>dots.json</a>（出典付きの機械可読データ）</li></ul>"
        f"<h2>ソース</h2><ul><li><a href='https://github.com/nishio/connecting_dots'>github.com/nishio/connecting_dots</a></li></ul>"
        f"<h2>機械向け</h2><ul><li><a href='sitemap.xml'>sitemap.xml</a> / <a href='llms.txt'>llms.txt</a></li></ul>"
        f"<p class='meta'><a href='{BASE_URL}/ja.html'>&larr; 西尾泰和のホームページ</a></p>")
    en_body = (
        f"<h1>Connecting Dots System</h1><p>{desc_en}</p>"
        f"<h2>Stories</h2><ul>{story_items}</ul>"
        f"<p class='meta'>Story text is in Japanese. English write-ups are on <a href='{BASE_URL}/'>NISHIO's homepage</a>.</p>"
        f"<h2>All Dots</h2><ul>"
        f"<li><a href='all-dots.html'>All Dots</a> ({len(dots)} incl. orphans)</li>"
        f"<li><a href='dots.json'>dots.json</a> (sourced, machine-readable data)</li></ul>"
        f"<h2>Source</h2><ul><li><a href='https://github.com/nishio/connecting_dots'>github.com/nishio/connecting_dots</a></li></ul>"
        f"<h2>Machine-readable</h2><ul><li><a href='sitemap.xml'>sitemap.xml</a> / <a href='llms.txt'>llms.txt</a></li></ul>"
        f"<p class='meta'><a href='{BASE_URL}/'>&larr; NISHIO Hirokazu's homepage</a></p>")

    def _landing(lang, title, toggle_href, toggle_label, body):
        return (f"<!DOCTYPE html><html lang='{lang}'><head><meta charset='utf-8'>"
                f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
                f"<title>{esc(title)}</title><style>{CSS}</style></head><body>"
                f"<nav><a href='{toggle_href}'>{esc(toggle_label)}</a></nav>{body}</body></html>")

    open(os.path.join(OUT, "dots.html"), "w").write(
        _landing("ja", "Connecting Dots System — 西尾泰和", "dots.en.html", "English", ja_body))
    open(os.path.join(OUT, "dots.en.html"), "w").write(
        _landing("en", "Connecting Dots System — NISHIO Hirokazu", "dots.html", "日本語", en_body))
    urls.append(f"{BASE_URL}/dots.html")
    urls.append(f"{BASE_URL}/dots.en.html")

    sm = "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"
    sm += "".join(f"  <url><loc>{esc(u)}</loc></url>\n" for u in urls)
    sm += f"  <url><loc>{BASE_URL}/dots.json</loc></url>\n</urlset>\n"
    open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)

    llms = (f"# nishio ConnectingDots — machine-readable data (Dots & Stories)\n\n"
            f"AI/agents: 一次データは以下。取得してローカルで読む/検索する（サイト側に検索機能は無い）。\n\n"
            f"- 全 Dot データ（受理済み・全件フラット・孤児含む）: {BASE_URL}/dots.json\n"
            f"- 全 Dot の人間向け View: {BASE_URL}/all-dots.html\n"
            f"- Story 一覧: {BASE_URL}/dots.html\n"
            f"- sitemap: {BASE_URL}/sitemap.xml\n\n"
            f"補足: 候補（未受理）Dot は別ファイル candidates/*.jsonl に置かれる（pilot には未収録）。"
            f"検証状態は各 Dot の verifiability(external|internal-only) と refs に随伴。\n")
    open(os.path.join(OUT, "llms.txt"), "w").write(llms)

    # サマリ
    shared = sum(1 for did in dots if len(rev[did]) > 1)
    print(f"built -> {OUT}")
    print(f"  dots: {len(dots)}  (孤児={n_orphan}, 複数Story共有={shared})")
    print(f"  stories: {len(stories)}  ({', '.join(s['id'] for s in stories)})")
    print(f"  files: dots.json, all-dots.html, {len(dots)} dot pages, {len(stories)} story pages, sitemap.xml, llms.txt, index.html")


def _story_title(stories, sid):
    for s in stories:
        if s["id"] == sid:
            return s["title"]
    return sid


def _render_story(s, dots, rev):
    # section の from/to を dots[] のインデックス範囲に写す
    order = s["dots"]
    pos = {did: i for i, did in enumerate(order)}
    sec_of = [None] * len(order)
    for sec in s.get("sections", []):
        a, b = pos.get(sec["from"]), pos.get(sec["to"])
        if a is None or b is None:
            continue
        for i in range(a, b + 1):
            if sec_of[i] is None:
                sec_of[i] = sec["title"]
    caps = s.get("captions", {})
    out = [f"<h1>{esc(s['title'])}</h1>",
           f"<p class='meta'>audience: {esc('、'.join(s.get('audience',[])))} ／ purpose: {esc(s.get('purpose',''))} ／ author: {esc(s.get('author',''))}</p>",
           f"<p>{esc(s.get('intro',''))}</p>"]
    cur = object()
    for i, did in enumerate(order):
        if sec_of[i] != cur:
            cur = sec_of[i]
            if cur:
                out.append(f"<h2>{esc(cur)}</h2>")
        d = dots.get(did)
        if not d:
            out.append(f"<div class='dot'><span class='meta'>[未解決 Dot: {esc(did)}]</span></div>")
            continue
        out.append(dot_block(d, rev, orphan_note=False))
        if did in caps:
            out.append(f"<div class='caption'>▸ {esc(caps[did])}</div>")
    return "".join(out)


if __name__ == "__main__":
    build()
