# ConnectingDots — implementation (central store)

西尾泰和の **Dots（検証可能な事実カード）/ Stories（並び＋語り）** を JSON で保持し、
静的HTML と **AI クロール面 `dots.json`** を生成する中央実装リポジトリ。

設計の正典は `connecting-dot-design` wiki（別リポジトリ）。主要決定:
- 単一フラットプール（ドメイン非分割、ドメインは tags/Story所属で回収）
- 孤児 Dot も一級市民（どの Story にも属さない Dot も dots.json / per-Dot URL に載る）
- クロール面は Web 配信成果物、canonical は nhiro.org、`llms.txt` はルート（サイト側に検索は持たない）
- `status` フィールドなし（候補=別ファイル `candidates/*.jsonl`、受理=`dots.json`、区別は location）
- deploy: ソースは中央（このrepo）、View は宛先別 federated（自己紹介→nhiro.org / Plurality史→dd2030）

## 使い方
```
python3 build.py   # dots.json + story-*.json → build/（HTML + dots.json/sitemap/llms.txt）
```

## 構成
- `dots.json` — 受理済み Dot の単一フラットプール（pilot: Plurality 35件、暫定で単一ファイル。per-Dot 分割は今後）
- `story-*.json` — Story 定義
- `build.py` — ビルド v0
- `build/` — 生成物（gitignore）
- `archive/prototype-2026-02/` — 2月の旧プロトタイプ（旧スキーマ when/title/sources・blocks）。自己紹介 Dot の**内容の移行元**として保存
