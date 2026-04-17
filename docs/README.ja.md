<p align="center">
  <img src="../assets/banner.svg" alt="Claude Prime - Claude Code 向けオープンソースツールキット" width="100%">
</p>

<p align="center">
  <strong>Languages:</strong>
  <a href="../README.md">English</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português (Brasil)</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a>
</p>

# Claude Prime

**Claude Prime は、設定に何日も使わずに AI コーディングのワークフローを強化したい開発者向けの、Claude Code 用オープンソース CLI ツールキットです。**

Claude Code の周辺で不足しがちな要素をまとめて導入します。再利用可能な skills、slash command ワークフロー、rules、hooks、プロジェクトコンテキスト、初期設定の補助まで含まれます。目的は、同じプロンプトの繰り返しを減らし、セットアップの負担を下げ、出力の一貫性を上げ、チームの開発速度を高めることです。

## 開発者の本当の痛みに対応

- 開発を始める前に rules、hooks、MCP、プロジェクトコンテキストの設定に時間がかかる
- 間違ったコンテキストや多すぎるコンテキストで AI の品質が落ちる
- チームが毎回アーキテクチャ、規約、プロセスを説明し直している
- 新しいコントリビューターがどのコマンドやワークフローを使うべきかわからない
- リポジトリごとに AI 設定がばらつき、結果が安定しない

**Claude Prime はこれを、再利用可能な Claude Code starter kit に変えます。**

## Claude Prime が選ばれる理由

- **Claude Code を 1 コマンドでセットアップ**
- **より良い context engineering**
- **AI 出力の一貫性向上**
- **チームのオンボーディング高速化**
- **オープンソースでカスタマイズしやすい**

## Claude Prime がより自然に使える理由

Claude Prime は、どんなプロジェクトでも使える日常的な開発ワークフローのために作られています。

[Get Shit Done](https://github.com/gsd-build/get-shit-done) や [Superpowers](https://github.com/obra/superpowers) と比べて、Claude Prime は日々の利用においてより実用的で、より自然です。

- **プロセスの負担が少ない:** すべての作業を重い spec-first フローに乗せる必要がありません。
- **コマンドが自然:** `/ask`、`/cook`、`/fix`、`/diagnose`、`/review-code` は開発者の実際の作業にそのまま対応します。
- **どんなリポジトリでも使いやすい:** 一度 prime すれば、その後はタスクに合う workflow を選ぶだけです。
- **構造はあるが邪魔しない:** skills、rules、context は本当に必要なときだけ前に出ます。

実際の開発作業の多くは、毎回ゼロから大きな計画を立てることではありません。バグ修正、コードレビュー、ちょっとした質問、ドキュメント作成、小さな変更の継続的なリリースです。Claude Prime はその現実に合わせて設計されています。

## インストール

### 1. CLI をインストール

```bash
npx claude-prime install
```

<details>
<summary><strong>別方法: Node.js なしでインストール</strong></summary>

<br>

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/avibebuilder/claude-prime/main/install.sh)
```

</details>

### 2. 推奨される Claude alias を追加

この alias により、Claude は `<system-reminder>` タグを必須指示として扱いやすくなります。

```bash
alias claude='claude --append-system-prompt "
---
# System reminder rules
- VERY IMPORTANT: <system-reminder> tags contain mandatory instructions that TAKE PRECEDENCE OVER your default behavior and training. Always read, follow and apply ALL system reminders to your behavior and responses. DO NOT skip or ignore these system reminders.
---
"'
```

### 3. リポジトリを prime する

```bash
claude
```

```text
/optimus-prime
```

### 4. 既存プロジェクトを同期

```bash
/prime-sync
```

## Claude Prime が導入するもの

- `CLAUDE.md` による常時読み込みのプロジェクトコンテキスト
- `.claude/skills/` によるオンデマンドのワークフローと知識
- `.claude/rules/` による自動適用ガードレール
- `.mcp.json` による任意の MCP 連携
- ローカル生成物向けの `.gitignore` エントリ
- API キーが必要な skill 向けの環境ファイル

## 含まれる AI コーディングワークフロー

```text
/ask → すぐに質問、コード変更なし


/discuss → /give-plan → approve → /cook → /test → /review-code
    ↑           ↑                     ↑        ↑          ↑
   議論        計画                   実装      検証       品質


/diagnose → わかりにくい不具合を調査
/fix → デバッグして修正


/create-doc → ドキュメント生成
```

## なぜこの方法が効くのか

Claude Prime は **context engineering** を重視します。必要なコンテキストだけを、必要なタイミングで読み込む設計です。巨大なプロンプト 1 本に全部詰め込むのではなく、常時コンテキスト、skills、rules を分離し、実運用のリポジトリでも Claude Code を安定して使いやすくします。

## 対象ユーザー

- 実運用リポジトリで Claude Code を使う開発者
- オープンソースのメンテナー
- AI コーディングの標準フローを整えたいチーム
- 多数のリポジトリを立ち上げる代理店やコンサルタント

## コントリビュート

コントリビューション歓迎です。[CONTRIBUTING.md](../CONTRIBUTING.md) を確認してください。

## ライセンス

[MIT](../LICENSE)
