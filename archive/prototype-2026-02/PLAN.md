# Codex引き継ぎメモ：Dots / Stories MVP（自己紹介 → Plurality史）

## ゴール（MVP）
- Git管理できるJSONデータとして **dots（事実カード）** を実データで作る
- dotsを参照して **story（並び＋語り）** を1本以上作る
- storyを **静的HTMLとしてレンダリング** できる最小実装を作る（ローカルで生成→プレビュー）
- まず「西尾個人の自己紹介ページ」のMVPを優先。次に「日本におけるPluralityの歴史」。

## スコープ / 非スコープ
- 優先度1：西尾個人の自己紹介（最近の活動ハイライトをdots化→storyで提示）
- 優先度2：「日本におけるPluralityの歴史」（Scrapboxの年表からdots化→storyで提示）
- 非スコープ：
  - Sonar（他者に質問して思考整理するツール）は今回の半径外
  - dd2030週次レポートは今回の対象外
  - verifiable credentials / オンチェーンなど「社会的証明」機構は今回やらない
  - 閲覧者が自由に並べ替えるようなインタラクティブ編集はやらない（キュレーターが作ったstoryを読む）

## 設計方針（重要）
- Dot = 検証可能な「最小の事実」。出典URLを必ず持つ。内容は後から再利用される部品。
- Story = 人間がキュレーションした「作品」（dotの順序＋短い語り）。同じdotを複数storyで再利用できる。
- 「関係性(edge)をデータ化しない」は強い禁則ではない。必要が見えたら後で足す（MVPでは不要）。
- 多言語：dotは再利用できる前提。storyは言語・文脈ごとに別物として並立してよい（翻訳に固定しない）。

## MVPでやること（タスク）
1) data/dots に、まず5〜15件くらい実データのdotを置く
   - まずは自己紹介ページの「最近の活動」5項目をdot化（後で精密化する）
   - 余力があれば Plurality史の代表イベントも数件dot化
2) data/stories に story を1〜2本置く
   - story: nishio-profile-ja（自己紹介ハイライト）
   - story: plurality-history-ja（日本におけるPlurality史の短い導入版）
3) scripts/ などにレンダラーを実装
   - 入力：story_id（or storyファイルパス）
   - 処理：story → 参照dotを読み込み → HTML出力
   - 出力：dist/<story_id>.html（or docs/ 配下など、サイト構成に合わせる）
4) ローカルでHTMLを開く/簡易サーバで確認できるようにする
   - 例：python -m http.server / npx serve dist

## ディレクトリ案（例）
- data/
  - dots/
    - <dot_id>.json
  - stories/
    - <story_id>.json
- scripts/
  - render_story.(ts|js|py)
- templates/（任意）
  - story.html（任意。なくてもコード内文字列でOK）
- dist/（生成物）
  - <story_id>.html

## スキーマ（MVP版：厳密な型は後で強化）
### Dot（data/dots/*.json）
必須：
- id: string（ファイル名と一致推奨）
- when: string（表示用。YYYY / YYYY-MM / YYYY-MM-DD / "2024–2025" など許容。MVPはソートしない）
- title: string
- sources: [{ url: string, label?: string }]

任意：
- summary: string（短い補足。事実寄り）
- tags: string[]
- people/orgs/projects: string[]（必要になったら）

例：
{
  "id": "plurality-ja-localization-lead-2025",
  "when": "2025",
  "title": "『PLURALITY』日本語版の企画・編集リーダー",
  "sources": [{"url":"...","label":"..."}],
  "summary": "（任意）",
  "tags": ["profile","plurality"]
}

### Story（data/stories/*.json）
必須：
- id: string
- lang: string（"ja"など）
- title: string
- blocks: Block[]

Block（MVP）：
- { "type": "markdown", "text": string }
- { "type": "section", "title": string }
- { "type": "dot", "dot": "<dot_id>", "caption"?: string, "note"?: string }

例：
{
  "id":"nishio-profile-ja",
  "lang":"ja",
  "title":"西尾泰和：最近の活動（MVP）",
  "blocks":[
    {"type":"markdown","text":"ここは固定プロフィールではなく、活動（dots）から組み立てたstoryを見せる実験。"},
    {"type":"dot","dot":"plurality-ja-localization-lead-2025","caption":"翻訳を統括した、という主張の根拠リンクを集める"},
    {"type":"dot","dot":"shin-tokyo-2050-broad-listening-2024-2025"},
    {"type":"dot","dot":"tokyo-gov-anno-broad-listening-2024"},
    {"type":"dot","dot":"digital-democracy-2030-kouchou-ai-idobata-2025"},
    {"type":"dot","dot":"japan-choice-yoron-chizu-2024"}
  ]
}

## レンダリング要件（MVP）
- story.blocks を上から順に描画（ストーリー順が正）
- dotブロック描画：
  - when / title
  - caption（あれば）
  - summary（あれば）
  - sources（リンク一覧：labelがあればlabel、なければurl）
- 参照dotが見つからない場合はエラーで落とす or placeholder表示（どちらでも良いがMVPは落としてOK）
- まずはCSSは最小（読みやすさ優先）
- MarkdownはMVPでは「改行を<p>にする」程度でもOK（後で拡張）

## “実データ”から作る最初のdots案（暫定。後で出典を増やして精密化）
### 自己紹介（最近の活動 5 dots）
- plurality-ja-localization-lead-2025
  when: "2025"
  title: "『PLURALITY』日本語版の企画・編集リーダー"
  sources:
    - https://nishio.github.io/entrypoint/ja.html
    - https://cybozushiki.cybozu.co.jp/articles/m006211.html （該当するなら）
- shin-tokyo-2050-broad-listening-2024-2025
  when: "2024–2025"
  title: "シン東京2050 でのブロードリスニング"
  sources:
    - https://nishio.github.io/entrypoint/ja.html
- tokyo-gov-anno-broad-listening-2024
  when: "2024"
  title: "都知事選2024（安野貴博氏）でブロードリスニングに関与"
  sources:
    - https://nishio.github.io/entrypoint/ja.html
- digital-democracy-2030-kouchou-ai-idobata-2025
  when: "2025"
  title: "デジタル民主主義2030（広聴AI / いどばた）"
  sources:
    - https://nishio.github.io/entrypoint/ja.html
- japan-choice-yoron-chizu-2024
  when: "2024"
  title: "JAPAN CHOICE『世論地図（ヨロンチズ）』の実装協力"
  sources:
    - https://nishio.github.io/entrypoint/ja.html

### Plurality史（まずは3〜5 dotsだけ切り出し）
（元ネタ：Scrapbox「日本におけるPluralityの歴史」）
- glen-collab-book-launch-2022-09-16
  when: "2022-09-16"
  title: "Glen Weylが collaborative book project を発表（Plurality本の立ち上げ）"
  sources:
    - https://scrapbox.io/plurality-japanese/日本におけるPluralityの歴史
    - https://x.com/glenweyl/status/1570427940621402113
- plurality-tokyo-2023-04-14
  when: "2023-04-14"
  title: "Plurality Tokyo 開催"
  sources:
    - https://scrapbox.io/plurality-japanese/日本におけるPluralityの歴史
- autotrans-start-2023-10-17
  when: "2023-10-17"
  title: "本家GitHub原稿を毎日自動翻訳する autotrans が稼働"
  sources:
    - https://scrapbox.io/plurality-japanese/日本におけるPluralityの歴史
- social-hack-day-57-2024-01-20
  when: "2024-01-20"
  title: "Social Hack Day #57（初の読書会イベント）／Trinity Merge"
  sources:
    - https://scrapbox.io/plurality-japanese/日本におけるPluralityの歴史

## 受け入れ条件（Doneの定義）
- `data/dots/*.json` が最低5件ある（自己紹介の5件）
- `data/stories/nishio-profile-ja.json` があり、それを `render_story` でHTMLにできる
- 生成HTMLをブラウザで開くと、storyの順でカードが表示され、各カードに出典リンクが出る
- （余力）plurality-history-ja も同様にレンダリングできる
