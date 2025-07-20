# GPT_2 日本語ガイド

このドキュメントは、ChatGPT デスクトップアプリケーションの日本語向け説明書です。GUI は [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) を利用しており、Word や PDF、画像、Excel ファイルをアップロードしてモデルへ渡すことができます。

## 1. 環境構築

1. Python の仮想環境を作成します。
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows の場合: .\venv\Scripts\activate
   ```
2. 依存ライブラリをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
3. `.env.example` をコピーして OpenAI API キーを設定します。
   ```bash
   cp .env.example .env
   echo "OPENAI_API_KEY=your_key_here" >> .env
   ```
  必要に応じて `OPENAI_MODEL` や `OPENAI_TIMEOUT`、`OPENAI_BASE_URL`、`PREFERRED_FONT` などの環境変数も指定できます。`PREFERRED_FONT` はカンマ区切りで複数の候補を指定できます。

## 2. アプリケーションの起動

以下のコマンドで GUI を起動します。
```bash
python -m src.ui.main
```
Windows では `run_gui.bat` を利用することもできます。

左の設定パネルではモデル選択や温度の調整、新規会話の開始、過去会話の読み込みなどが行えます。"会話を保存" ボタンで手動保存も可能です。
このアップデートからレイアウトは `grid` ジオメトリマネージャを使用し、
ウィンドウサイズに合わせて各パネルが自動的にリサイズされます。最小ウィンドウサイズは `800x600` です。

## 3. ダイアグラム生成

`create_graphviz_diagram` と `create_mermaid_diagram` を使うと、DOT や Mermaid コードから PNG 画像を生成できます。図を描いてほしい旨をアシスタントに伝えるだけで、内部的にこれらのツールが呼び出され、一時ディレクトリに画像ファイルが作成されます。GUI に「図の作成」ボタンなどはなく、生成されたファイルパスがチャットに表示されると同時に右側のサイドバーへ自動的にプレビューが表示されます。"保存" ボタンで任意の場所へ保存でき、"コピー" ボタンでファイルパスをクリップボードにコピーできます。
`create_mermaid_diagram` は ```mermaid フェンスや HTML タグを除去したコードを送信します。生成に失敗するとプレビューに「図の生成に失敗しました」が表示され、"修正" ボタンから再生成を試せます。

## 4. コマンドラインツール

`python -m src.main` を実行すると、CLI からエージェント機能を試せます。`--list-tools` で利用可能なツール一覧を表示し、`--model gpt-4o` のようにモデル指定も可能です。実験的な Tree-of-Thoughts エージェントは `--agent tot` オプションで起動できます。

ToT エージェントの探索設定は次の環境変数で変更できます:

- `TOT_DEPTH` – `--depth` を省略した場合のデフォルト探索深さ
- `TOT_BREADTH` – `--breadth` を省略した場合の各階層の分岐数
- `TOT_LEVEL` – 深さと分岐数のプリセット (`LOW`, `MIDDLE`, `HIGH`, `EXTREME`)
  を選択できます

これらが無効な値でも、`--agent tot` を使用しない限り無視されます。

GUI では探索レベルを **LOW**, **MIDDLE**, **HIGH**, **EXTREME** から選択できます。
それぞれ `(2,2)`, `(3,3)`, `(4,4)`, `(5,5)` の深さと分岐数に対応し、
環境変数が設定されていればそちらが優先されます。
CLI でも `--tot-level` オプションで同じプリセットを指定できます。
例えば `--tot-level HIGH` は `(4,4)` を意味します。

GUI で ToT エージェントを実行すると、探索中の思考過程が `__TOT__`
で始まる行として一時的に表示されます。`__TOT_END__` という行が到達
すると、それまでの `__TOT__` 行は自動的に最終回答に置き換えられます。

## 5. テスト実行

開発用依存関係を含めてインストール後、`pytest` を実行してテストがすべて成功するか確認します。
```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## 6. ファイル配置

- 会話履歴はカレントディレクトリの `conversations` フォルダに保存されます。
- ダイアグラム画像は一時ディレクトリに出力されます。環境変数 `TMPDIR` などで変更可能です。

### CONVERSATION_DIR 環境変数

`CONVERSATION_DIR` を設定すると、デフォルトの `conversations` フォルダの代わりに指定したディレクトリへ会話履歴を保存できます。ディレクトリが存在しない場合は自動作成されます。

## 7. ロギング設定

`setup_logging` を使うとコンソールに加えて任意のファイルへログを書き出せます。
`AGENT_LOG_FILE` 環境変数を指定すると、デフォルトで使用するログファイルを設定できます。
`AGENT_LOG_LEVEL` を設定すると `--verbose` を使わない場合の既定ログレベルを変更できます。

```python
from src import setup_logging
setup_logging(level=logging.DEBUG)  # AGENT_LOG_FILE があれば使用
```

## 8. トークン使用量の記録

`create_llm` を `log_usage=True` で呼び出すと、OpenAI API のトークン数と概算コストをログに記録します。`OPENAI_TOKEN_PRICE` にトークン単価を設定してください。リクエストのタイムアウトは `OPENAI_TIMEOUT` で調整できます。

## 9. 参考

詳細な仕様や追加設定項目については英語版 README (`README.md`) を参照してください。
