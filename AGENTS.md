# txhistory

<!-- このファイルは AI エージェント（Claude Code・Codex など）と人の両方に向けた、このリポジトリの作業規則。
     「プロジェクト固有」の節はプロジェクトごとに書き換え、「共通の規則」の節は sahokun の全リポジトリで共通に保つ。 -->

## プロジェクト固有

### 概要

Etherscan 系・Blockscout 系のエクスプローラーの API から、アドレスの取引履歴を集めて CSV にし、その CSV とレート表から取引履歴の xlsx を作る Python のツール。

### 技術スタックと構成

- Python。開発環境は `.devcontainer/development/` の Docker。
  - `run_get_scan_csv.py`: エクスプローラーから取引を取得し、`output/` に CSV を出す。対象のネットワーク・アドレス・期間（JST）はスクリプト内で調整する。
  - `run_make_history.py`: `data/` に置いた CSV と `data/rate.xlsx` から、`output/` に xlsx を出す。データ量によっては時間がかかる。
  - `scan_api/`: エクスプローラーごとの API（`etherscan/`・`blockscout/`）と、ネットワークの定義（`types.py`）。Etherscan 系の API キーは `scan_api/types` に設定する。
  - `util/`・`models.py`・`wopenpyxl.py`: 共通の処理・データの型・xlsx の書き出し。
- 依存は `requirements.txt`（固定は `requirements-district.txt`）。

### 確認の手順

```bash
pip install -r requirements-district.txt
python -m pytest tests
```

- `tests/test_api.py` は実際の API を呼ぶので、ネットワークと API キーが要る。
- API キーやアドレスの実データをコミットしない。

## 共通の規則

### ブランチと PR

<!-- branch-model:begin -->
- 既定のブランチは `main`。作業はブランチを切り、`main` への PR にする。
- PR は squash merge で取り込む。main の履歴には PR のタイトルだけが 1 コミットとして残る。
<!-- branch-model:end -->
- PR のタイトルは Conventional Commits（`feat: ...`・`fix: ...` など）で、変更の内容が 1 行で分かるように書く。
- PR がマージされたら、作業ブランチは自動で削除される。

### 履歴と公開物に書かないもの

- メールアドレス・トークン・パスワード・個人の環境の情報・AI エージェントのセッションへのリンクを、コミット・PR・Issue・コメントに書かない。
  - 作業ブランチのコミットと PR は、マージ後も GitHub に残り続け、所有者でも消せない。main の履歴も書き換えには強制 push とサポートへの依頼が要る。PR の本文だけは後から編集で直せる。
- コミットの作成者のメールアドレスは、GitHub の noreply アドレス（`<ID>+<ユーザー名>@users.noreply.github.com`）を使う。
- `.env`・鍵ファイル・ローカル設定（`.claude/settings.local.json` など）はコミットしない。

### 依存関係

- 追加・更新する依存は、公開から 7 日以上たったバージョンに限る。公開直後に乗っ取り・差し替えが見つかる事例が多いため。
  - Dependabot のバージョン更新は `cooldown` で 7 日待つ。npm は `.npmrc` の `min-release-age=7` で手作業の更新にも同じ制限を掛ける。
- GitHub Actions のアクションは、フル SHA（40 桁）で固定し、行末にバージョンをコメントで残す（例: `actions/checkout@<SHA> # v7.0.1`）。タグは差し替えられるため。
- Dependabot の PR は、更新を知らせる合図として扱う。CI が通ることと、メジャー更新では変更点を確かめてから取り込む。
