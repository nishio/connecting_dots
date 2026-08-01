# ConnectingDots — 引き継ぎ文書（2026-08-01 更新）

新しいコンテキストで作業を再開するための現在地メモ。設計の正典は別リポジトリ
`/Users/nishio/connecting-dot-design`（LLM Wiki、非git）。本 repo は実装（git）。

## 現在地（TL;DR）
- 設計は closed。`build.py` v0 が end-to-end で動作。
- **本移行 進行中**。完了テーマ: **highdim**（7 Dot）／**mentoring**（14 Dot）／**intellectual-production**（9 Dot）。現在 **65 Dot / 5 Story**（story-highdim / story-mentoring / story-intellectual-production ＋ 既存 Plurality 2本）、build 動作確認済み。**やり方（3工程）は下記「移行プレイブック」で確立**。
- **フラットプールの実効**: テーマ間で Dot を共有（共有5件）。`2003-super-creator-certification`＝highdim/mentoring、`2014-05-word2vec-book`＝highdim/IP、`2013-04-langbook`・`2018-08-engineers-way-book`＝mentoring/IP。書籍 Dot は IP 移行で作り、mentoring Story にも後付けリンク済み（deferral 解消）。
- **Story の dots[] 配列順が描画順＝セクション境界**（build の `_render_story` は from/to を配列 index に写す）。共有 Dot を挿入したら**時系列を崩さない位置に**置くこと（崩すとセクション間で無所属 Dot が浮く）。
- **次の作業 = 残りテーマの本移行**：broadlistening / plurality-facet。確立した3工程を繰り返す。一次年表は `entrypoint/docs/history-ja.html` が全テーマ共通で使える。都知事選2024など broadlistening の一次は `history-ja.html` line 93 と Scrapbox。

## 移行プレイブック（highdim で確立、以降のテーマもこれで）
1. **atomize** — facet Story の `<li>` と旧プロトタイプ Dot（`archive/prototype-2026-02/data/dots/`）を atomic fact に分解。判定「同じ atomic イベントか別の事実か」。**credential（学位・認定）は研究とは別 fact に分割**（cf. 24歳博士）。
2. **fact-check** — 一次ソースは西尾自身の `/Users/nishio/entrypoint/docs/history-ja.html`（年表＋発表歴の一次リスト）。facet Story の文言を鵜呑みにしない（繋ぎ目の焼き込み誤りを探す）。
3. **Dot化** — 新スキーマ（0.1-pilot）で dots.json の単一フラットプールへ追記。共有 Dot は1 Dot＋Story別 caption に畳む。`story-<theme>.json` を作り `python3 build.py` で確認。
- **属性の注意**: 過剰帰属を避ける（例: Talk to the City は nishio 作でなく「用いた実験」、kouchou-ai は dd2030 の一員として開発参加）。cf. IGF京都の教訓。
- **孤児 OK**: どの Story にも属さない Dot（例: スーパークリエータ認定）はフラットプールに置いたままで一級市民（orphan-dot-discovery）。

## リポジトリ / 置き場所
- **`/Users/nishio/connecting_dots/`（本 repo, git）** = 実装＝中央ストア。`build.py` / `dots.json`（Plurality pilot 35件）/ `story-*.json` 2本 / `archive/prototype-2026-02/`（2月の旧プロトタイプ＝自己紹介 Dot の移行元）。`build/` は生成物（gitignore）。
- **`/Users/nishio/connecting-dot-design/`（非git）** = 設計 wiki。`wiki/{concepts,decisions,architecture,use-cases}/` ＋ `open-questions.md` ＋ `overview.md` ＋ `log.md`。全ての設計決定はここに file back 済み。
- **`/Users/nishio/entrypoint/`（git, nhiro.org / GitHub Pages）** = deploy 先。`docs/{broadlistening,plurality,intellectual-production,mentoring,highdim}/` に手書き facet Story 5本（＝最初の自己紹介 Story、移行の見本）。

## 確定した設計決定（connecting-dot-design/wiki/ 参照）
- **flatness-is-view-resolution** — ストアは AI 向けで忠実・自由・フラットでよい。人間が要求する「平坦で理解可能な形」は render 時に View が一つの高度にコミットして与える。**Dot と Story は固定層でなく相対的な役**、Dot粒度は出力の高度が決める。
- **単一フラットプール** — 自己紹介 Dot と Plurality 史 Dot をドメインで分けず1プール。ドメインは `tags`／Story 所属で回収。可視性（public/private）だけは分ける。
- **orphan-dot-discovery** — どの Story にも属さない孤児 Dot も一級市民で AI 発見可能に。発見インデックスは Story でなく **Dot コーパス `dots.json`** に張る。クロール面＝**Web 配信された静的成果物**（`dots.json`＋per-Dot URL＋`all-dots.html`＋`sitemap.xml`＋`llms.txt`ルート）。**canonical は nhiro.org**。クライアント検索は作らない（AI が dots.json を取得してローカルで読む）。
- **status フィールドは持たない** — 候補=別ファイル `candidates/*.jsonl`（Q18 分離スタイル）、受理=`dots.json`。区別は location。昇格＝ファイル間移動。
- **deploy-topology** — ソースは中央（本 repo）、View は宛先別 federated（自己紹介→nhiro.org / Plurality 史→dd2030）。entrypoint(nhiro.org) は自己紹介 View の配信先＋クロール面ホスト。
- **story-joints-hide-claims** — Story の繋ぎ目（命名・因果・帰属）は解釈に見えて検証可能な事実主張を紛れ込ませる。全 Dot が真でも繋ぎ目が偽なら Story は偽。→ 繋ぎ目は一次ソースで検証。
- **relationships-as-edits** — Dot 間の関係はデータ化せず Story の編集（並び＋caption）で表す。

## スキーマ（pilot 0.1、新フィールド不要で確定）
**Dot**: `id(YYYY-MM-DD-slug) / date(ISO8601, interval "from/to"可, open "2016/.."可) / event(自己完結の1行=事実) / kind(meeting|act|release|decision|publication|education|research) / entities[] / tags[] / refs[] / cosense_refs[] / verifiability(external|internal-only)`。任意: `notes`, `parent_id`(container索引, Q14)。**status は持たない**。
**Story**: `id / title / language / audience[] / purpose / author / intro / dots[](id配列) / captions{id:文} / sections[{title,from,to}]`。

## build.py v0（動作確認済み）
`python3 build.py` で `dots.json`+`story-*.json` → `build/` に人間向けHTML（Story/all-dots/per-Dot）＋クロール面（dots.json/sitemap.xml/llms.txt）。孤児・共有 Dot を検出し逆引き（派生・非ゲート）を生成。canonical=nhiro.org。**次の拡張候補**: `dots/*.json` per-Dot ファイル分割（git 差分性）、タグ絞り込みView。

## 次の作業：自己紹介 Dot の本移行（atomize + fact-check）
**作業定義**（この順で）:
1. **atomize** — facet Story の `<li>` や旧 Dot を atomic fact に分解。`<li>` はしばしば複数 fact の束（例「未踏ジュニア コファウンダー・メンター」＝設立＋継続メンターの2 fact）。
2. **fact-check** — 各 fact と**順序・因果**を一次ソース（or 西尾）で検証。**Set B（facet Story）の文言を鵜呑みにしない**（下記の通り誤りが焼き込まれている）。
3. **Dot 化** — 新スキーマで `dots/` へ。共有イベントは1 Dot＋Story 別 caption。

**畳む vs 分割の判定基準（検証で確立）**:
> 1 Dot＋caption に畳めるのは、全 Story の角度が**同じ atomic イベント**を指すときだけ。角度が**別の事実**を指すなら分割（Q14, container＋sub-dot, `parent_id` は任意索引）。
> 診断: 「その枠の違いは同じ事実の解釈・強調か、別の事実か」。別事実を caption に入れ始めたら分割のサイン。

**検証済みの例**:
- word2vec本(2014) → 畳める（profile / intellectual-production / highdim が同じ刊行を指す）
- 未踏理事 → **3分割**（一般社団法人未踏 理事2015-2025 / 未踏ジュニア設立2016 / 未踏ジュニア メンター2016-継続）
- 24歳博士 → **分割**（学位 credential 2006 vs 球面SOM研究2004-2006 は別事実。mentoring の「後輩指導」も別 fact）

**移行元データ**:
- Set A: `archive/prototype-2026-02/data/dots/`（25 Dot、うち profile タグ約15、旧スキーマ `when/title/summary/sources`）
- Set B: nhiro.org の5 facet Story（`/Users/nishio/entrypoint/docs/<theme>/ja.html` の実践の記録リスト、約40件、内容は豊富だが**文言に誤り有り**）
- Set B ⊋ Set A（B が30件ほど多い＝人材育成の縦糸・道具・高次元スレッド等を発見）。移行は B を主軸に A 固有の素経歴を足す。

## 今セッションで見つけ潰した誤り（story-joints-hide-claims の実証3件）
Set B の文言には**繋ぎ目の捏造**が焼き込まれている。移行時に必ず再検証すること:
1. **ReGroup 命名**＝「grouping プロジェクトの再始動」(iPad+Pencil契機)。「分類への批判」ではない（私の推測誤り）。
2. **国連IGF京都(2023)**＝Audrey Tang が Talk to the City を紹介した場。西尾の実践ではない（過剰帰属、修正済み）。
3. **highdim の博士期**＝正しくは 未踏ユース(ゲノム配列可視化,2002)→スーパークリエータ認定(2003)→修士進学(2003)→球面SOM(遺伝子発現)可視化研究(2004-2006)。ゲノム配列可視化と SOM遺伝子発現可視化は**別の研究**。逆因果と混同を nhiro.org highdim Story で修正・デプロイ済み（2026-08-01, commit あり）。

## 副産物（このセッションで完了・出荷済み、移行の素材になる）
- nhiro.org の facet Story 5本（broadlistening/plurality/intellectual-production/mentoring/highdim）＝自己紹介 Story の手書き版。相互リンク済み。
- Scrapbox `考えを整理するツールの系譜`（Grouping→ReGroup→Movidea→Kozaneba）Story。`Grouping`/`Movidea` ページ新設、`Regroup` に系譜行。
- Claude メモリ: `thought-tool-lineage.md`（系譜）。

## 未決（connecting-dot-design/wiki/open-questions.md）
- 解決済: Q3(Inbox=candidates/*.jsonl) / Q5(all-dots) / Q11(deploy federated) / Q13+Q14(畳む vs 分割ルール) / Q18(分離スタイル・status不要)。
- 未決: Q6(ビルドツール選定・現状 Python stdlib で足りている) / Q7(AI候補抽出フロー) / Q15(Story の entry_points/call_to_action) / Q16(prototype-first の重み付け)。

## 外向きステップ（自己紹介移行が一段落してから）
- `dots/*.json` per-Dot 分割 / GitHub remote 作成 + push / `build/` を nhiro.org(entrypoint) へ配信して `https://nhiro.org/dots.json` を実公開。
