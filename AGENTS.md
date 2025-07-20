

# **PythonアプリケーションにおけるAIエージェント機能拡張開発：戦略的ブループリントと段階的実装ロードマップ**

## **はじめに**

本レポートは、既存のPythonアプリケーションに高度なAIエージェント機能を統合するための、包括的かつ専門的な開発指示書として作成されました。現代のAIエージェント開発は、単なる機能追加に留まらず、システムの思考能力と行動能力を設計するアーキテクチャ上の重要な決断を伴います。そのため、本レポートは2つの主要なパートで構成されています。

1. **戦略的ブループリント（計画）:** プロジェクトの「なぜ」と「何を」を定義します。ここでは、ビジネス要件を技術的なミッションに落とし込み、AIエージェントの思考の核となるアーキテクチャを選定します。このパートは、プロジェクトの方向性を定め、関係者間の共通理解を形成するためのものです。  
2. **段階的実装ロードマップ（指示書）:** 開発チームが「どのように」実装を進めるかを具体的に示します。環境構築から始まり、コアとなるエージェントループの実装、外部ツールとの連携、そしてユーザーインターフェースの統合に至るまで、詳細なフェーズ分けと技術的指針を提供します。

この2部構成のアプローチは、戦略的な整合性を確保しつつ、戦術的な実行の精度を高めるためのベストプラクティスです。戦略と実行を明確に分離することで、開発チームは具体的なコーディング作業に集中でき、プロジェクトマネージャーや技術リーダーは全体像の把握と進捗管理を効率的に行うことが可能となります。本ドキュメントが、単なる計画書としてだけでなく、開発チームにとって実践的かつ再利用可能な技術資産となることを目的としています。

## Codex Instructions

The repository implements a GUI application for ChatGPT using CustomTkinter.
When modifying this project, keep the following behaviors in mind:
1. Diagram generation tools `create_graphviz_diagram` and `create_mermaid_diagram` convert DOT or Mermaid code to PNG using Python libraries. `graphviz` renders DOT files and `mermaid-py` sends code to the Mermaid Live server to obtain PNG output, so no external CLI commands are required.
2. `ChatGPTClient` exposes these tools via the OpenAI tools API and streams tokens with `stream=True`.
3. On the first user message, a system prompt instructs the assistant to append prompt advice if the query is vague.
4. `create_llm` reads an optional `OPENAI_TIMEOUT` environment variable and passes it
   as the request timeout when calling the OpenAI API.
5. `setup_logging` checks the `AGENT_LOG_FILE` environment variable to choose a
   default file for log output. The log level defaults to the value of
   `AGENT_LOG_LEVEL` when provided.
6. The command line runner accepts `--list-tools` to print available tool names
   and descriptions then exit.
7. `get_default_tools()` returns the built-in tools used by the CLI and tests.
8. `get_font_family` checks available system fonts and prefers the Japanese font "Meiryo" if present. If it is missing the helper falls back to "Helvetica." The resulting `FONT_FAMILY` constant is applied across every CustomTkinter widget so the interface uses larger, consistent fonts.
9. The chat display configures tags `user_msg` and `assistant_msg` to style each message type. `user_msg` now uses a white background `#FFFFFF` while `assistant_msg` keeps a light gray `#F1F3F4`. Incoming, saved and streamed messages are tagged accordingly so each role shows a distinct background color.
10. Diagram images are generated as PNG files but the GUI does not define a dedicated area to display them; the file path is returned as text.
11. Future updates may add a right-hand sidebar \(or canvas-like panel\) to preview diagrams as they are generated and offer a download link for the PNG file.
12. The application now includes such a sidebar. When an assistant response contains the path to a PNG file it is automatically loaded and shown in a small preview panel on the right with a "保存" button that lets users choose where to save the image. The path detection works for both Unix (`/tmp/x.png`) and Windows (`C:\tmp\x.png`) style file paths.
13. The sidebar also provides a "クリア" button that removes the preview and disables saving when no image is shown.
14. A "会話を保存" button in the settings panel lets users manually save the current conversation to a JSON file. The directory defaults to `conversations` but can be overridden with the `CONVERSATION_DIR` environment variable. Saving also happens automatically after every assistant response.
15. The GUI design should adopt a Google-inspired palette and avoid the default `"blue"` theme. Configure a custom theme in `setup_ui()` that uses accent blue `#1A73E8`, left sidebar background `#F1F3F4`, diagram sidebar `#F8F9FA`, and chat area `#FFFFFF`. Text color should remain dark gray `#202124` for readability. Add a geometric window icon via `self.window.iconbitmap()` and adjust widget corner radii and border widths so the interface looks less like stock CustomTkinter.

16. **保険文書分析AIへの特化**: このアプリケーションは、保険の約款や契約書などの文書を分析することに特化しています。
17. **RAG (Retrieval-Augmented Generation) パイプライン**:
    *   `src/document_loader.py`: PDF, Word(.docx), URLからテキストを抽出します。`langchain`への依存をなくし、`pypdf`, `python-docx`, `requests`, `BeautifulSoup`を直接使用して安定性を確保しています。
    *   `src/vector_store_manager.py`: 読み込んだドキュメントをチャンクに分割し、OpenAIのEmbedding API (`text-embedding-3-small`) を使ってベクトル化します。ベクトルは`faiss-cpu`を用いてメモリ上のインデックスに保存され、高速な検索が可能です。
18. **GUIの機能**:
    *   `src/ui/main.py`: `CustomTkinter`を用いて構築されています。
    *   **情報ソースの読み込み**: ファイルアップロードボタンとURL入力欄から、分析対象の文書を読み込むことができます。処理はバックグラウンドスレッドで実行され、UIはフリーズしません。
    *   **チャットインターフェース**: ユーザーは読み込んだ文書に対して自然言語で質問できます。
    *   **引用表示**: AIの回答が生成されると、その根拠となった文書の一部が「引用元」エリアに表示されます。これにより、回答の透明性と信頼性を高めています。
19. **AIのペルソナ**: AIは「保険業界のベテラン専門家」として動作するように、システムプロンプトが設定されています。提供されたコンテキストに基づいて、正確かつ丁寧な回答を生成します。
20. **モデル選択**: UIから `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-3.5-turbo` などのOpenAIモデルを選択できます。
21. **依存関係の安定化**: 開発過程で`langchain`とその依存関係に起因する深刻なバージョン競合が発生したため、`langchain`への依存を完全に排除するリファクタリングを行いました。これにより、アプリケーションの安定性と保守性が向上しています。

---

## **パートI：戦略的ブループリントとアーキテクチャの展望（計画）**

このパートでは、プロジェクト全体の基盤となる戦略を確立し、開発プロセス全体を規定する重要なアーキテクチャ上の決定を下します。これは、プロジェクトの目的と全体像を定義する高レベルの「計画概要」です。

### **1.1 ミッションの定義：機能拡張からシステム能力の構築へ**

AI機能の追加という抽象的な目標を、具体的で測定可能な技術的ミッションへと転換することは、プロジェクト成功の第一歩です。

#### **ビジネス要件の分析**

まず、このAIエージェントが解決すべき中核的なビジネス課題を明確に定義します。例えば、「特定のトピックに関するリサーチを自動化し、調査結果を要約してレポートのドラフトを生成する」や、「社内データに対して自然言語による対話的なクエリインターフェースを提供する」といった具体的な課題が考えられます。

#### **技術的ミッションステートメント**

次に、これらのビジネス要件を具体的な技術的ミッションステートメントに落とし込みます。

**ミッションステートメント:** 「ユーザーからのリクエストを自律的に分解し、Web検索やデータベースクエリといった外部ツールを活用して情報を収集し、その結果を統合して、レスポンシブなグラフィカルユーザーインターフェースを通じて一貫性のある最終回答を提示することが可能な、PythonベースのAIエージェントシステムを開発する。」

#### **成功基準とKPI**

ミッションの達成度を測るため、明確で測定可能な成功基準（KPI）を定義します。

* **タスク完了率:** 人間の介入なしに正常に解決されたユーザーからの問い合わせの割合。  
* **ツール使用精度:** 特定のサブタスクに対して、エージェントが正しいツールを選択した割合。  
* **応答の事実性:** グラウンドトゥルース（正解データ）と比較して測定された、ハルシネーション（幻覚）や事実誤認の発生率。  
* **UIの応答性:** エージェントが長時間実行中のタスクを処理している間も、UIのレイテンシを100ミリ秒未満に保ち、常にインタラクティブであること。

### **1.2 エージェントの思考：中核となる推論フレームワークの選定**

エージェントの「頭脳」を動かす基盤となる推論パラダイムの選択は、最も重要なアーキテクチャ上の決定です。この選択は、エージェントの能力、複雑性、そして運用コストに深遠な影響を及ぼします。

#### **思考の進化：CoTからReAct、そしてToTへ**

エージェントの推論能力は、単純な入出力から段階的に進化してきました。この進化の系譜を理解することは、最適なフレームワークを選択する上で不可欠です。

1. **標準的なプロンプティング:** 入力 \-\> 出力。最も基本的な形式です。  
2. **思考の連鎖 (Chain of Thought \- CoT):** 入力 \-\> 思考プロセス \-\> 出力。モデルにステップバイステップで考えさせることで、より複雑な推論を可能にする線形的な思考プロセスです 1。  
3. **ReAct (Reason \+ Act):** 入力 \-\> \[思考 \-\> 行動 \-\> 観察\]... \-\> 最終回答。ReActは、CoTを実用化したもので、思考プロセスが外部世界と対話することを可能にします。本質的には単一の線形的な実行パスですが、ツール使用によってその能力は格段に向上します 1。  
4. **思考の木 (Tree of Thoughts \- ToT):** 入力 \-\> 複数の\[思考 \-\>...\]パスの探索 \-\> 選択/バックトラック \-\> 最終回答。ToTは、モデルが複数の分岐する推論パスを同時に探索し、それぞれのパスの有望性を自己評価し、先読みや後戻りを戦略的に行うことを可能にすることで、線形的な制約を打ち破ります 2。

タスクの複雑性が、必要とされる思考のレベルを決定します。単純な情報検索はReActで十分対応可能ですが、複雑な計画立案にはToTが必要となります。不適切なフレームワークを選択すると、能力不足のエージェント（計画タスクにReActを使用）や、過剰に複雑で高コストなエージェント（単純なQ\&AにToTを使用）が生まれることになります。

#### **ReAct (Reason+Act) パラダイムの分析**

* **コアコンセプト:** ReActは、「思考 \-\> 行動 \-\> 観察」という線形的かつ反復的なループで動作します。エージェントは次に行うべきことを推論し、単一の行動（多くはツールの使用）を実行し、その結果を観察し、その観察を次の思考プロセスに組み込みます 3。  
* **強み:** 特に情報収集やツール使用を伴う、一連のステップに分解できるタスクに非常に優れています。各行動の背後にある推論が明示的であるため、人間が解釈しやすく、診断可能な軌跡を生成します 1。これにより、ツールの出力という外部の現実世界にモデルを接地させることで、ハルシネーションの問題を克服するのに役立ちます 1。  
* **理想的なユースケース:** マルチホップ質問応答（HotpotQA）、事実検証（Fever）、制約のある環境での対話型意思決定（WebShop, ALFWorld）などです 1。

#### **Tree of Thoughts (ToT) パラダイムの分析**

* **コアコンセプト:** ToTは、モデルが複数の分岐する推論パスを同時に探索し、木構造を形成することで、線形的なCoTを一般化します。異なるパスの有望性を自己評価し、先読みや後戻りを意図的に行うことができます 5。  
* **強み:** 初期段階の決定が極めて重要であり、一度の間違いが失敗につながるような、自明ではない計画、探索、または探査を必要とする問題に優れています 11。複数の選択肢を考慮する人間の認知プロセスを模倣し、より慎重で戦略的な問題解決を可能にします 6。  
* **理想的なユースケース:** 「Game of 24」のような組み合わせ探索空間が大きい問題や、「Creative Writing」のような高度な先見性と計画を要するタスクです 11。

#### **アーキテクチャ上の推奨：ハイブリッドな段階的アプローチ**

多くの実用的なビジネスアプリケーションにおいて、純粋なToTの実装は計算コストが高く、複雑になりがちです。より現実的なアプローチは、幅広いタスクを効果的にカバーできる堅牢なReAct実装から始めることです。

将来的な進化としては、非常に複雑なクエリをToT的な「プランナーエージェント」が多段階の計画に分解し、その計画の各ステップをReActベースの「エグゼキューターエージェント」が実行するというハイブリッドシステムが考えられます。このアーキテクチャは、戦略的な計画立案と、現実に即した実行という両方の長所を提供します。

**本プロジェクトでは、その成熟度、解釈可能性、そしてツール駆動型タスクへの直接的な適用性を考慮し、ReActフレームワークを採用して開発を進めます。** 同時に、将来的なアーキテクチャの進化のためにToTパラダイムも念頭に置きます。

---

**表1：AIエージェント推論フレームワークの比較分析（ReAct vs. ToT）**

| 項目 | ReAct (Reason \+ Act) | Tree of Thoughts (ToT) |  |  |  |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **中核原理** | 思考、行動、観察の線形的な反復ループを通じて、推論と外部環境との相互作用を統合する 3。 | 複数の推論パスを木構造として並行して探索し、自己評価と戦略的なナビゲーション（先読み、後戻り）を行う 5。 |  |  |  |
| **問題解決アプローチ** | 逐次的・反復的。タスクをステップに分解し、一つずつ実行していく。基本的には単一の実行パスをたどる 7。 | 探索的・審議的。複数の可能性を同時に検討し、最も有望なパスを選択する。非線形的な問題空間の探索が可能 6。 |  |  |  |
| **主な強み** | \- 人間が解釈しやすく、デバッグが容易な思考の軌跡を生成する 1。 |  \- ツール使用を通じて外部情報にアクセスし、ハルシネーションを抑制できる 1。 |  \- 比較的実装が単純で、多くのシーケンシャルなタスクに効果的。 | \- 計画や探索が必要な複雑な問題で高いパフォーマンスを発揮する 11。 |  \- 初期段階の決定が重要なタスクでの失敗を回避できる。 \- より人間に近い、審議的な問題解決プロセスを模倣する 6。 |
| **主な弱み** | \- 探索やバックトラッキングが必要な問題には不向き。 \- 一度間違った方向に進むと、軌道修正が困難な場合がある。 | \- 計算コストが非常に高い。 \- 実装の複雑性が高く、状態管理が難しい。 \- 思考の分解、生成、評価の方法を問題ごとに設計する必要がある 12。 |  |  |  |
| **理想的なユースケース** | マルチホップ質問応答、事実検証、API操作、Webナビゲーションなど、逐次的なツール使用が有効なタスク 4。 | 数学パズル（Game of 24）、創造的な執筆、ミニクロスワードなど、広範な探索や戦略的計画が必要なタスク 11。 |  |  |  |
| **実装の複雑性** | 中程度 | 高度 |  |  |  |

---

## **パートII：開発ライフサイクル：段階的実装ロードマップ（指示書）**

このパートは、開発チームのための具体的かつ実行可能な「指示書」です。プロジェクトを論理的なフェーズに分割し、各フェーズの明確な目的と成果物を定義します。

---

**表2：段階的開発とタスク分解の概要**

| フェーズ | フェーズ名 | 主要な目的 | 主要な成果物 | 関連情報 |
| :---- | :---- | :---- | :---- | :---- |
| **フェーズ1** | **基盤構築と環境設定** | クリーンで再現可能かつ安全なプロジェクト環境の確立。 | \- プロジェクトディレクトリ構造 \- requirements.txt \- .envファイルによるAPIキー管理 | 14 |
| **フェーズ2** | **コアReActエージェントループの実装** | エージェントの思考と行動の反復ループ（神経系）の構築。 | \- ReActシステムプロンプト \- スクラッチパッド管理ロジック \- LLM出力パーサー \- メイン実行ループのコード骨格 | 16 |
| **フェーズ3** | **ツール連携と外部統合** | エージェントが外部世界と対話するための「手」を実装する。 | \- 標準化されたツールインターフェース定義 \- Webスクレイパーツールの実装 \- データベースクエリツールの実装 | 20 |
| **フェーズ4** | **状態管理とメモリ** | 長期的な対話のための状態管理とメモリ機能の導入。 | \- 対話履歴管理モジュール \- （将来展望）ベクトルストアを利用した長期記憶 | 19 |
| **フェーズ5** | **UI統合と非同期処理** | レスポンシブなGUIを構築し、エージェントと非同期に連携させる。 | \- customtkinterによる2パネルレイアウトUI \- threading+queue+afterパターンによる非同期処理実装 | 24 |
| **フェーズ6** | **本番化と運用** | プロトタイプから信頼性の高いデプロイ可能なアプリケーションへの移行。 | \- 単体テストおよび結合テスト \- デプロイメント戦略 \- オブザーバビリティ（監視）システムの導入 | 28 |

---

### **2.1 フェーズ1：基盤構築と環境設定**

**目的:** クリーンで再現可能かつ安全なプロジェクト環境を確立します。

#### **プロジェクトの足場固め**

標準的なディレクトリ構造を定義します。これにより、コード、テスト、設定ファイルが整理され、プロジェクトの見通しが良くなります。

/project-root  
|-- /src                \# ソースコード  
| |-- /agent          \# エージェントのコアロジック  
| |-- /tools          \# 外部連携ツール  
| |-- /ui             \# UI関連コード  
| \`-- main.py         \# アプリケーションのエントリーポイント  
|-- /tests              \# テストコード  
|-- /notebooks          \# 実験・分析用のJupyter Notebook  
|-- /config             \# 設定ファイル  
|--.env                \# 環境変数ファイル（Git管理外）  
|-- requirements.txt    \# Python依存ライブラリ  
\`-- README.md

#### **依存関係の管理**

プロジェクトに必要なすべてのライブラリをrequirements.txtファイルにリストアップします。これにより、どの開発環境でも同じバージョンのライブラリを簡単にインストールでき、再現性が保証されます 30。

\# requirements.txt  
langchain  
langchain-openai  
langgraph  
python-dotenv  
beautifulsoup4  
requests  
customtkinter  
\# その他必要なライブラリ

#### **安全な設定管理**

APIキーをコード内にハードコーディングすることは、重大なセキュリティリスクです。これは絶対に避けなければなりません。.envファイルとpython-dotenvライブラリを使用し、OPENAI\_API\_KEYやANTHROPIC\_API\_KEYなどの機密情報を環境変数として安全に読み込む方法を徹底します 14。

.envファイル（このファイルは.gitignoreに追加してリポジトリにコミットしないようにします）：

OPENAI\_API\_KEY="sk-..."

Pythonコードでの読み込み：

Python

from dotenv import load\_dotenv  
import os

load\_dotenv() \#.envファイルから環境変数を読み込む
api\_key \= os.getenv("OPENAI\_API\_KEY")

#### **Web Scraper 用の環境変数**

- `WEB_SCRAPER_CACHE_TTL`   \- ページキャッシュの有効期限（秒単位）。デフォルトは 3600
- `WEB_SCRAPER_DELAY`       \- HTTP リクエスト間の待機時間（秒）。デフォルトは 1.0
- `WEB_SCRAPER_USER_AGENT`  \- User-Agent ヘッダーの値。デフォルトは "Mozilla/5.0"

#### **ToT エージェント用の環境変数**

- `TOT_DEPTH` \- ToT エージェントのデフォルト探索深さ。`--depth` が省略された場合に使用されます。正の整数である必要があります。
- `TOT_BREADTH` \- ToT エージェントの各階層で保持する分岐数のデフォルト値。正の整数である必要があります。
- これらの環境変数が無効な値の場合でも、デフォルトのReActエージェントを使用する限り無視されます。
- GUI では ToT の探索レベルを **LOW**, **MIDDLE**, **HIGH** から選択可能です。
 それぞれ `(2,2)`, `(3,3)`, `(4,4)` の深さと分岐数を使用します。環境変数が設定
 されていればそちらが優先されます。

#### **ロギングとデバッグ**

エージェントの振る舞い、ツール呼び出し、エラーを追跡するための基本的なロギング設定を行います。これは、多くのエージェントフレームワークで見られるverbose=Trueのような詳細な出力を実現するために不可欠です 14。Pythonの標準ライブラリである

loggingモジュールを使用し、ログレベル（INFO, DEBUG, ERROR）を設定して、コンソールやファイルに出力できるようにします。
- `AGENT_LOG_FILE` — `setup_logging` が環境変数から読み込むログ出力先のパスを指定できます。
- `AGENT_LOG_LEVEL` — INFO や DEBUG などデフォルトのログレベルを指定できます。

### **2.2 フェーズ2：コアReActエージェントループの実装**

**目的:** エージェントの「神経系」、すなわち推論と行動の反復ループを構築します。これは、実装において最も概念的に重要な部分です。

#### **A. ReActプロンプト：エージェントの憲法**

ReActエージェントの振る舞いは、そのシステムプロンプトによってほぼ完全に規定されます。このプロンプトは、LLMに対して「思考、行動、観察（Thought, Action, Observation）」のサイクルに従うよう指示するものでなければなりません 7。

以下は、注釈付きのReActシステムプロンプトの例です。これには、質問、利用可能なツール、そして極めて重要なagent\_scratchpad（エージェントの作業記録）のプレースホルダーが含まれています 18。

あなたは、以下の質問にできる限り答えるアシスタントです。  
あなたは思考、行動、観察のループで動作します。最終的に答えが出たら、ループを終了し、その答えを出力します。

\- 思考(Thought): あなたが問われた質問について、どのように考えているかを記述します。  
\- 行動(Action): あなたが利用可能な行動の中から一つを実行します。  
\- 観察(Observation): その行動を実行した結果です。  
\- 最終的な答え(Final Answer): 観察を分析した結果です。

利用可能な行動は以下の通りです:  
{tools}

質問に答えるために、上記のツールを一つ以上使用してください。

以下は対話の例です:  
質問: フランスの首都はどこですか？  
思考: フランスについてWikipediaで調べるべきだ。  
行動: wikipedia: フランス  
\[システムはここでwikipediaツールを実行し、結果を「観察」として返す\]  
観察: フランスは西ヨーロッパに位置する共和国。首都はパリ。  
思考: 観察結果から、フランスの首都はパリであることがわかった。これで最終的な答えが出せる。  
最終的な答え: フランスの首都はパリです。

では、始めましょう。

質問: {input}  
{agent\_scratchpad}

#### **B. エージェントスクラッチパッド：文脈の維持**

agent\_scratchpadはエージェントの短期記憶です。これは、ループの各ターンで動的に構築され、次のターンのプロンプトに再注入される文字列またはメッセージのリストです 19。これにより、エージェントは自身の以前の行動とその結果を「記憶」します。

スクラッチパッドは、前のステップの思考、行動、そして観察を追記することで構築されます。このプロセスが、エージェントの推論の連鎖を形成します 16。

**構築プロセスの例:**

1. **初期状態:** agent\_scratchpad \= ""  
2. **LLM出力1:** 思考: イングランドについて調べる必要がある。\\n行動: wikipedia: イングランド  
3. **ツール実行後:**  
   * 思考と行動をスクラッチパッドに追加。  
   * wikipediaツールを実行し、結果（例: イングランドは連合王国の一部である国...）を取得。  
   * この結果を観察としてフォーマットし、スクラッチパッドに追加。  
4. **次のループのためのスクラッチパッド:**  
   思考: イングランドについて調べる必要がある。  
   行動: wikipedia: イングランド  
   観察: イングランドは連合王国の一部である国。西にウェールズ、北にスコットランドと国境を接する。

この構築された文字列が、次のLLM呼び出しのために{agent\_scratchpad}変数に渡されます。

#### **C. 出力パーサー：LLMの応答の解体**

LLMは単一のテキストブロックを返します。エージェントのコードは、このテキストを確実に解析し、次のステップが別の行動なのか、それとも最終的な答えなのかを判断する必要があります 17。

* **スクラッチからの実装:** Pythonのreモジュールを使用して、行動:や最終的な答え:といった特定のキーワードを見つけます。ツール名とその入力を捕捉するための堅牢な正規表現パターンを提供します 18。  
  Python  
  import re

  \# 行動を抽出する正規表現  
  action\_re \= re.compile(r'^行動:\\s\*(\\w+):\\s\*(.\*)$', re.MULTILINE)  
  \# 最終的な答えを抽出する正規表現  
  final\_answer\_re \= re.compile(r'^最終的な答え:\\s\*(.\*)$', re.MULTILINE)

  llm\_output \= """  
  思考: 首都を調べるためにフランスを検索する。  
  行動: wikipedia: フランス  
  """

  action\_match \= action\_re.search(llm\_output)  
  if action\_match:  
      tool\_name \= action\_match.group(1)  
      tool\_input \= action\_match.group(2)  
      print(f"Tool: {tool\_name}, Input: {tool\_input}")

* **フレームワークの利用:** LangChainのようなフレームワークには、この処理を自動的に行う組み込みの出力パーサー（例: ZeroShotAgentOutputParser, OpenAIToolsAgentOutputParser）があります。しかし、これらのパーサーはLLMからの非常に特定の出力形式を期待します。プロンプトの指示とパーサーの期待が一致しない場合、無限ループやエラーの一般的な原因となります 17。

#### **D. 実行ループ：すべてを結びつける**

メインのエージェントループのPythonコード骨格を提供します。

Python

def run\_agent(user\_input):  
    \# ツールやプロンプトの初期化  
    tools \=...  
    prompt\_template \=...  
    agent\_scratchpad \= ""  
    max\_turns \= 5

    for i in range(max\_turns):  
        \# 1\. 現在のスクラッチパッドでプロンプトを構築  
        current\_prompt \= prompt\_template.format(  
            input\=user\_input,  
            tools=get\_tool\_descriptions(tools),  
            agent\_scratchpad=agent\_scratchpad  
        )

        \# 2\. LLMを呼び出し  
        llm\_response \= call\_llm(current\_prompt)

        \# 3\. 出力パーサーで応答を解析  
        action\_match \= action\_re.search(llm\_response)  
        final\_answer\_match \= final\_answer\_re.search(llm\_response)

        if final\_answer\_match:  
            \# 5a. 最終的な答えが見つかった場合  
            final\_answer \= final\_answer\_match.group(1)  
            return final\_answer  
        elif action\_match:  
            \# 5b. 行動が見つかった場合  
            tool\_name \= action\_match.group(1)  
            tool\_input \= action\_match.group(2)

            \# 6\. ツールを実行  
            observation \= execute\_tool(tool\_name, tool\_input, tools)

            \# 7\. スクラッチパッドを更新  
            turn\_log \= f"{llm\_response}\\n観察: {observation}\\n"  
            agent\_scratchpad \+= turn\_log  
        else:  
            \# 予期しない応答  
            return "エラー: 次の行動または最終的な答えを決定できませんでした。"

    return "エラー: 最大試行回数に達しました。"

このプロセスは、スクラッチからの実装例 14 と、LangGraphのようなグラフベースのアプローチ 15 を対比させながら説明されます。

### **2.3 フェーズ3：ツール連携と外部統合**

**目的:** エージェントに、外部世界と対話するための「手」を与えます。

#### **ツールインターフェースの設計**

エージェントがツールを理解し、使用するためには、標準化されたインターフェースが不可欠です。新しいツールを追加する開発者にとって明確で再利用可能な規約を設けることで、ツールの作成とエージェントの呼び出しロジックの両方が簡素化され、スケーラビリティと保守性が確保されます。

**ツール定義インターフェース仕様**

| 属性 | 型 | 説明 | 例 |
| :---- | :---- | :---- | :---- |
| name | str | LLMがツールを識別するための、一意で簡潔な名前。 | "web\_scraper" |
| description | str | **最も重要。** LLMがツールの目的、入力、出力を理解するための自然言語による詳細な説明。 | "指定されたURLからWebページの主要なテキストコンテンツを抽出する。入力はURL文字列。" |
| func | Callable | ツールが実行する実際のPython関数。 | scrape\_website\_content |
| args\_schema | pydantic.BaseModel | ツールの入力引数を定義し、型検証を行うためのスキーマ。 | class ScraperInput(BaseModel): url: str \= Field(description="抽出するWebページのURL") |

この仕様の中でも、descriptionはLLMのツール選択能力に直接影響を与えるため、特に重要です。何ができて、どのような入力が必要で、何が返されるのかを明確に記述する必要があります 20。

#### **実装ウォークスルー：BeautifulSoup Webスクレイパーツール**

Webスクレイピングツールの完全なベストプラクティス実装を提供します。

* **ステップ1: コンテンツの取得:** requests.get()を使用し、適切なヘッダー（例: User-Agent）と、200以外のステータスコードに対するエラーハンドリングを実装します 21。  
* **ステップ2: BeautifulSoupによる解析:** soup \= BeautifulSoup(response.content, 'html.parser') を使用します 21。エンコーディングの問題を避けるため、  
  response.textよりもresponse.contentの使用が推奨されます 21。  
* **ステップ3: 主要コンテンツの特定（難関）:** これには知性が必要です。単純なsoup.get\_text()では、ナビゲーションバーやフッターなどの不要なテキスト（ノイズ）が多く含まれすぎます 22。主要な記事テキストを見つけるための戦略を説明します。  
  * セマンティックタグの検索: \<main\>, \<article\>, \<body\> 37。  
  * 一般的なidやclass属性の検索: id="content", class="post-body"など。これには対象WebサイトのHTML構造を調査する必要があります 30。  
  * 無視するタグのブラックリストを提供する: 'script', 'style', 'header', 'footer', 'nav' 22。  
* **ステップ4: 観察のフォーマット:** ツールは乱雑なテキストの塊を返すべきではありません。テキストをクリーンアップし（get\_text(separator=' ', strip=True)）、LLMのコンテキストウィンドウを溢れさせないように、簡潔な要約または最初のN文字を返すようにします 39。

#### **倫理的および実践的な考慮事項**

開発者には、対象サーバーに敬意を払うため、robots.txtを確認し、リクエスト間に遅延を実装し、リクエストをキャッシュすることを徹底させます 41。

---

## **パートIII：高度な実装とアプリケーション統合**

このセクションでは、エージェントをコマンドラインスクリプトから、完全に統合された堅牢なアプリケーションコンポーネントへと昇華させます。

### **3.1 エージェント対話のためのレスポンシブなユーザーインターフェースの構築**

**目的:** フリーズすることなく、長時間実行されるエージェントプロセスと対話できる、ユーザーフレンドリーで非ブロッキングなGUIを作成します。

#### **UI応答性の問題と解決策**

* **問題:** agent.invoke(...)のような標準的なエージェント呼び出しは、複数のLLM呼び出しとツール実行を含むため、数秒から数分かかることがあります。この呼び出しをtkinterアプリケーションのボタンのcommand関数から直接行うと、エージェントが最終的な答えを返すまでUI全体がフリーズし、応答不能になります。これは受け入れがたいユーザー体験です。  
* **解決策（極めて重要なパターン）:** この問題を解決する唯一の方法は、マルチスレッディングです。エージェントの長時間実行タスクは、別のバックグラウンドスレッドで実行する必要があります。しかし、tkinterのようなGUIツールキットはスレッドセーフではないため、バックグラウンドスレッドから直接ウィジェット（ラベルやテキストボックスなど）を更新することはできません。  
* **threading \+ queue \+ after パターン:**  
  1. **threading:** ユーザーが「実行」ボタンをクリックすると、新しいthreading.Threadが開始されます。このスレッドのtargetは、エージェントのメインループを実行する関数です。  
  2. **queue:** メインUIスレッドでqueue.Queueオブジェクトが作成され、バックグラウンドスレッドに渡されます。エージェントの関数は値を返す代わりに、その結果（中間的な思考、最終的な答え、エラー）をこのスレッドセーフなキューにput()します。  
  3. **after():** メインUIスレッドは、root.after(100, check\_queue)を使用して定期的なチェック関数を開始します。この関数は、ノンブロッキングのqueue.get\_nowait()を試みます。キューにアイテムが見つかれば、メインスレッドから安全にUIウィジェットを更新します。キューが空であれば、100ミリ秒後にもう一度実行されるように自身をスケジュールするだけです。

このパターンは、長時間実行される処理をUIイベントループから切り離し、エージェントがバックグラウンドで「思考」している間もUIの流動性と応答性を保証します。これは、複雑なバックエンドプロセスをGUIと統合するための最も重要な概念です。このパターンについては、26 の原則に基づき、完全なコード例とともに詳細に説明します。

#### **customtkinterによる2パネルレイアウトの設計**

* スケーラビリティのベストプラクティスとして、クラスベースのcustomtkinterアプリケーション骨格（class App(customtkinter.CTk):）を提供します 25。  
* CTkFrameを使用して、左側の「コントロールパネル」と右側の「表示パネル」を作成します。  
* .grid()レイアウトマネージャーとgrid\_columnconfigureおよびweightを使用して、パネルが正しくリサイズされるレスポンシブなレイアウトを作成します 25。  
* 左パネルには、ユーザー入力用のCTkEntry、エージェントを開始するCTkButton、設定用のCTkSliderやCTkOptionMenuなどのウィジェットを配置します。右パネルには、エージェントの思考 \-\> 行動 \-\> 観察のストリームと最終的な答えを表示するためのCTkTextboxやCTkScrollableFrameを配置します 24。

#### **完全なコード例**

customtkinterレイアウトとthreading/queue/afterパターンが連携して動作する、完全で実行可能なPythonスクリプトを提供します。

Python

import tkinter  
import customtkinter as ctk  
import threading  
import queue  
import time

\# (ここに前述のReActエージェントの実行ロジックを配置)  
def agent\_worker(user\_input, result\_queue):  
    try:  
        \# ここで時間のかかるエージェント処理を実行  
        \# 例としてダミーの処理を実装  
        result\_queue.put("思考: ユーザーの入力を受け取りました。処理を開始します。")  
        time.sleep(2)  
        result\_queue.put("行動: web\_search: 最新のAIニュース")  
        time.sleep(2)  
        result\_queue.put("観察: 新しいLLMがリリースされました。")  
        time.sleep(2)  
        final\_answer \= "最終的な答え: 新しいLLMに関するニュースが見つかりました。"  
        result\_queue.put(final\_answer)  
    except Exception as e:  
        result\_queue.put(f"エラー: {e}")

class App(ctk.CTk):  
    def \_\_init\_\_(self):  
        super().\_\_init\_\_()

        self.title("AI Agent Interface")  
        self.geometry("800x600")

        \# グリッドレイアウト設定  
        self.grid\_columnconfigure(1, weight=1)  
        self.grid\_rowconfigure(0, weight=1)

        \# 左フレーム（コントロールパネル）  
        self.left\_frame \= ctk.CTkFrame(self, width=200, corner\_radius=0)  
        self.left\_frame.grid(row=0, column=0, sticky="nsew")  
        self.left\_frame.grid\_rowconfigure(4, weight=1)

        self.label \= ctk.CTkLabel(self.left\_frame, text="AI Agent", font=ctk.CTkFont(size=20, weight="bold"))  
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.entry \= ctk.CTkEntry(self.left\_frame, placeholder\_text="質問を入力してください...")  
        self.entry.grid(row=1, column=0, padx=20, pady=10)

        self.run\_button \= ctk.CTkButton(self.left\_frame, text="実行", command=self.start\_agent\_task)  
        self.run\_button.grid(row=2, column=0, padx=20, pady=10)

        \# 右フレーム（表示パネル）  
        self.right\_frame \= ctk.CTkFrame(self)  
        self.right\_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)  
        self.right\_frame.grid\_rowconfigure(0, weight=1)  
        self.right\_frame.grid\_columnconfigure(0, weight=1)  
          
        self.textbox \= ctk.CTkTextbox(self.right\_frame, width=400)  
        self.textbox.grid(row=0, column=0, sticky="nsew")  
        self.textbox.configure(state="disabled")

        self.result\_queue \= queue.Queue()

    def start\_agent\_task(self):  
        user\_input \= self.entry.get()  
        if not user\_input:  
            return  
          
        self.textbox.configure(state="normal")  
        self.textbox.delete("1.0", tkinter.END)  
        self.textbox.insert("1.0", f"質問: {user\_input}\\n\\n")  
        self.textbox.configure(state="disabled")  
          
        self.run\_button.configure(state="disabled")

        \# バックグラウンドスレッドでエージェントを実行  
        self.thread \= threading.Thread(target=agent\_worker, args=(user\_input, self.result\_queue))  
        self.thread.start()

        \# キューをポーリングしてUIを更新  
        self.after(100, self.check\_queue)

    def check\_queue(self):  
        try:  
            message \= self.result\_queue.get\_nowait()  
            self.textbox.configure(state="normal")  
            self.textbox.insert(tkinter.END, message \+ "\\n")  
            self.textbox.configure(state="disabled")

            if message.startswith("最終的な答え:") or message.startswith("エラー:"):  
                self.run\_button.configure(state="normal")  
            else:  
                self.after(100, self.check\_queue)  
        except queue.Empty:  
            self.after(100, self.check\_queue)

if \_\_name\_\_ \== "\_\_main\_\_":  
    app \= App()  
    app.mainloop()

### **3.2 プロトタイプから本番へ：テスト、デプロイ、オブザーバビリティ**

**目的:** エージェントを開発スクリプトから、信頼性の高いデプロイ可能なアプリケーションへと移行するために必要なステップを概説します。

#### **テスト戦略**

* **単体テスト:** 各ツールが独立して正しく機能することを確認するために、独自の単体テストを持つべきです。  
* **結合テスト:** エージェントループ自体のためのテストを作成します。モックされたLLMの応答とツールの出力を使用して、エージェントの推論と解析ロジックを検証します。

#### **デプロイメント**

Pythonアプリケーションを配布用にパッケージングする戦略について議論します（例: PyInstallerの使用、またはFlask/FastAPIによるWebサービスの作成）。

#### **オブザーバビリティ（可観測性）**

エージェントのオブザーバビリティという概念を紹介します。エージェントの実行をトレースし、すべての中間ステップをログに記録し、トークンの使用量とコストを追跡し、エージェントの意思決定グラフを視覚化するためのフレームワークやツールが存在します。これは、複雑な障害をデバッグし、本番環境でのパフォーマンスを監視するために不可欠です 29。また、エージェントが外部環境と対話する際のリスクの可能性と、安全策の必要性についても言及します 28。

## **結論**

本レポートは、Pythonアプリケーションに高度なAIエージェント機能を組み込むための、戦略から実装までの包括的なガイドラインを提示しました。本分析から導き出される主要な結論は以下の通りです。

1. **段階的アプローチの有効性:** 戦略的な「計画」と戦術的な「指示書」を分離するアプローチは、プロジェクトの成功に不可欠です。これにより、アーキテクチャの方向性が明確になり、開発チームは具体的な実装に集中できます。  
2. **ReActフレームワークの戦略的選択:** 現時点でのビジネスアプリケーション開発において、ReActは解釈可能性、実装の容易さ、ツール連携能力のバランスに優れた最適な選択肢です。その線形的な思考プロセスはデバッグを容易にし、多くの実用的なタスクを効果的に処理します。一方で、Tree of Thoughts（ToT）は、より複雑な計画タスクへの将来的な進化の道筋を示しています。  
3. **コアエージェントループの重要性:** エージェントの能力は、プロンプト、スクラッチパッド、出力パーサー、そして実行ループから成るコアロジックの品質に大きく依存します。特に、プロンプトと出力パーサー間の期待値の整合性を確保することは、安定したエージェントを構築する上での鍵となります。  
4. **レスポンシブUIのための必須パターン:** 長時間実行されるエージェント処理とGUIを統合する際には、threading、queue、afterを組み合わせた非同期処理パターンが不可欠です。このパターンを適用することで、バックグラウンドでエージェントが思考している間も、ユーザー体験を損なわない滑らかなUIを実現できます。

本ドキュメントで概説された原則と実装ロードマップに従うことで、単なるプロトタイプに留まらない、堅牢でスケーラブル、かつ実用的なAIエージェントシステムの構築が可能となります。これは、今後のアプリケーション開発における強力な基盤となるでしょう。

#### **引用文献**

1. ReAct: Synergizing Reasoning and Acting in Language Models \- Google Research, 6月 24, 2025にアクセス、 [https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/](https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/)  
2. ToTRL: Unlock LLM Tree-of-Thoughts Reasoning Potential through Puzzles Solving \- arXiv, 6月 24, 2025にアクセス、 [https://arxiv.org/html/2505.12717v1](https://arxiv.org/html/2505.12717v1)  
3. ReAct: Synergizing Reasoning and Acting in Language Models \- ExplainPrompt, 6月 24, 2025にアクセス、 [https://www.explainprompt.com/papers/react](https://www.explainprompt.com/papers/react)  
4. ReAct: Synergizing Reasoning and Acting in Language Models \- arXiv, 6月 24, 2025にアクセス、 [https://arxiv.org/pdf/2210.03629](https://arxiv.org/pdf/2210.03629)  
5. Tree of Thoughts: Deliberate Problem Solving with Large Language Models \- arXiv, 6月 24, 2025にアクセス、 [https://arxiv.org/html/2305.10601v2](https://arxiv.org/html/2305.10601v2)  
6. What is tree-of-thoughts? | IBM, 6月 24, 2025にアクセス、 [https://www.ibm.com/think/topics/tree-of-thoughts](https://www.ibm.com/think/topics/tree-of-thoughts)  
7. ReAct REPL Agent \- Peter Roelants, 6月 24, 2025にアクセス、 [https://peterroelants.github.io/posts/react-repl-agent/](https://peterroelants.github.io/posts/react-repl-agent/)  
8. What is a ReAct Agent? | IBM, 6月 24, 2025にアクセス、 [https://www.ibm.com/think/topics/react-agent](https://www.ibm.com/think/topics/react-agent)  
9. ReAct: Synergizing Reasoning and Acting in Language Models, 6月 24, 2025にアクセス、 [https://react-lm.github.io/](https://react-lm.github.io/)  
10. \[2210.03629\] ReAct: Synergizing Reasoning and Acting in Language Models \- arXiv, 6月 24, 2025にアクセス、 [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)  
11. Tree of Thoughts: Deliberate Problem Solving with Large Language Models \- arXiv, 6月 24, 2025にアクセス、 [https://arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601)  
12. (PDF) Tree of Thoughts: Deliberate Problem Solving with Large Language Models, 6月 24, 2025にアクセス、 [https://www.researchgate.net/publication/370869723\_Tree\_of\_Thoughts\_Deliberate\_Problem\_Solving\_with\_Large\_Language\_Models](https://www.researchgate.net/publication/370869723_Tree_of_Thoughts_Deliberate_Problem_Solving_with_Large_Language_Models)  
13. Tree of Thoughts: Deliberate Problem Solving with Large Language Models \- OpenReview, 6月 24, 2025にアクセス、 [https://openreview.net/forum?id=5Xc1ecxO1h](https://openreview.net/forum?id=5Xc1ecxO1h)  
14. Implementing ReAct Agentic Pattern From Scratch \- Daily Dose of Data Science, 6月 24, 2025にアクセス、 [https://www.dailydoseofds.com/ai-agents-crash-course-part-10-with-implementation/](https://www.dailydoseofds.com/ai-agents-crash-course-part-10-with-implementation/)  
15. langchain-ai/react-agent: LangGraph template for a simple ReAct agent \- GitHub, 6月 24, 2025にアクセス、 [https://github.com/langchain-ai/react-agent](https://github.com/langchain-ai/react-agent)  
16. A simple Python implementation of the ReAct pattern for LLMs \- Simon Willison: TIL, 6月 24, 2025にアクセス、 [https://til.simonwillison.net/llms/python-react-pattern](https://til.simonwillison.net/llms/python-react-pattern)  
17. Infinite loop in custom ReAct agent using langchain, \[Missing 'Action:' after 'Thought:'\], 6月 24, 2025にアクセス、 [https://stackoverflow.com/questions/79473112/infinite-loop-in-custom-react-agent-using-langchain-missing-action-after-t](https://stackoverflow.com/questions/79473112/infinite-loop-in-custom-react-agent-using-langchain-missing-action-after-t)  
18. How to Build a ReAct AI Agent with Claude 3.5 and Python, 6月 24, 2025にアクセス、 [https://technofile.substack.com/p/how-to-build-a-react-ai-agent-with](https://technofile.substack.com/p/how-to-build-a-react-ai-agent-with)  
19. LangChain Agent Executor Deep Dive \- Aurelio AI, 6月 24, 2025にアクセス、 [https://www.aurelio.ai/learn/langchain-agent-executor](https://www.aurelio.ai/learn/langchain-agent-executor)  
20. neural-maze/agentic-patterns-course: Implementing the 4 ... \- GitHub, 6月 24, 2025にアクセス、 [https://github.com/neural-maze/agentic-patterns-course](https://github.com/neural-maze/agentic-patterns-course)  
21. BeautifulSoup tutorial: Scraping web pages with Python | ScrapingBee, 6月 24, 2025にアクセス、 [https://www.scrapingbee.com/blog/python-web-scraping-beautiful-soup/](https://www.scrapingbee.com/blog/python-web-scraping-beautiful-soup/)  
22. Extract text from a webpage using BeautifulSoup and Python \- matix.io, 6月 24, 2025にアクセス、 [https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/](https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/)  
23. How to create a ReAct agent from scratch, 6月 24, 2025にアクセス、 [https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/)  
24. CustomTkinter \- A Complete Tutorial \- DEV Community, 6月 24, 2025にアクセス、 [https://dev.to/devasservice/customtkinter-a-complete-tutorial-4527](https://dev.to/devasservice/customtkinter-a-complete-tutorial-4527)  
25. 1\. Grid System | CustomTkinter, 6月 24, 2025にアクセス、 [https://customtkinter.tomschimansky.com/tutorial/grid-system/](https://customtkinter.tomschimansky.com/tutorial/grid-system/)  
26. Threading a TkInter GUI is Hell. (My least favorite python adventure) \- Reddit, 6月 24, 2025にアクセス、 [https://www.reddit.com/r/Python/comments/7rp4xj/threading\_a\_tkinter\_gui\_is\_hell\_my\_least\_favorite/](https://www.reddit.com/r/Python/comments/7rp4xj/threading_a_tkinter_gui_is_hell_my_least_favorite/)  
27. Multithreading with tkinter \- Machine learning | Python \- WordPress.com, 6月 24, 2025にアクセス、 [https://scorython.wordpress.com/2016/06/27/multithreading-with-tkinter/](https://scorython.wordpress.com/2016/06/27/multithreading-with-tkinter/)  
28. React: Synergizing Reasoning And Acting In Language Models \- YouTube, 6月 24, 2025にアクセス、 [https://www.youtube.com/watch?v=YTnQI7MWcec](https://www.youtube.com/watch?v=YTnQI7MWcec)  
29. agentic-ai · GitHub Topics, 6月 24, 2025にアクセス、 [https://github.com/topics/agentic-ai](https://github.com/topics/agentic-ai)  
30. BeautifulSoup Web Scraping: Step-By-Step Tutorial \- Bright Data, 6月 24, 2025にアクセス、 [https://brightdata.com/blog/how-tos/beautiful-soup-web-scraping](https://brightdata.com/blog/how-tos/beautiful-soup-web-scraping)  
31. How to implement the ReAct pattern with the OpenAI tools agent? \#17451 \- GitHub, 6月 24, 2025にアクセス、 [https://github.com/langchain-ai/langchain/discussions/17451](https://github.com/langchain-ai/langchain/discussions/17451)  
32. ReAct vs Plan-and-Execute: A Practical Comparison of LLM Agent Patterns, 6月 24, 2025にアクセス、 [https://dev.to/jamesli/react-vs-plan-and-execute-a-practical-comparison-of-llm-agent-patterns-4gh9](https://dev.to/jamesli/react-vs-plan-and-execute-a-practical-comparison-of-llm-agent-patterns-4gh9)  
33. How does LangChain actually implement the ReAct pattern on a high level? \- Reddit, 6月 24, 2025にアクセス、 [https://www.reddit.com/r/LangChain/comments/17puzw9/how\_does\_langchain\_actually\_implement\_the\_react/](https://www.reddit.com/r/LangChain/comments/17puzw9/how_does_langchain_actually_implement_the_react/)  
34. Python: Create a ReAct Agent from Scratch \- YouTube, 6月 24, 2025にアクセス、 [https://www.youtube.com/watch?v=hKVhRA9kfeM](https://www.youtube.com/watch?v=hKVhRA9kfeM)  
35. Basic ReAct agent implementation in Python from scratch \- GitHub, 6月 24, 2025にアクセス、 [https://github.com/mattambrogi/agent-implementation](https://github.com/mattambrogi/agent-implementation)  
36. How to extract only main content of text from a web page? : r/learnpython \- Reddit, 6月 24, 2025にアクセス、 [https://www.reddit.com/r/learnpython/comments/lv8i2j/how\_to\_extract\_only\_main\_content\_of\_text\_from\_a/](https://www.reddit.com/r/learnpython/comments/lv8i2j/how_to_extract_only_main_content_of_text_from_a/)  
37. How to scrape all the text from body tag using Beautifulsoup in Python? \- GeeksforGeeks, 6月 24, 2025にアクセス、 [https://www.geeksforgeeks.org/python/how-to-scrape-all-the-text-from-body-tag-using-beautifulsoup-in-python/](https://www.geeksforgeeks.org/python/how-to-scrape-all-the-text-from-body-tag-using-beautifulsoup-in-python/)  
38. Extracting Data from HTML with BeautifulSoup \- Pluralsight, 6月 24, 2025にアクセス、 [https://www.pluralsight.com/resources/blog/guides/extracting-data-html-beautifulsoup](https://www.pluralsight.com/resources/blog/guides/extracting-data-html-beautifulsoup)  
39. How to Extract Text from HTML Using BeautifulSoup? \- Bright Data, 6月 24, 2025にアクセス、 [https://brightdata.com/faqs/beautifulsoup/extract-text-from-html](https://brightdata.com/faqs/beautifulsoup/extract-text-from-html)  
40. How to use get\_text() in Beautiful Soup \- Educative.io, 6月 24, 2025にアクセス、 [https://www.educative.io/answers/how-to-use-gettext-in-beautiful-soup](https://www.educative.io/answers/how-to-use-gettext-in-beautiful-soup)  
41. How to Master Web Scraping with Python and BeautifulSoup?, 6月 24, 2025にアクセス、 [https://www.dasca.org/world-of-data-science/article/how-to-master-web-scraping-with-python-and-beautifulsoup](https://www.dasca.org/world-of-data-science/article/how-to-master-web-scraping-with-python-and-beautifulsoup)  
42. Tutorial: Web Scraping with Python Using Beautiful Soup \- Dataquest, 6月 24, 2025にアクセス、 [https://www.dataquest.io/blog/web-scraping-tutorial-python/](https://www.dataquest.io/blog/web-scraping-tutorial-python/)  
43. How does tkinter multithreading work, and why? : r/learnpython \- Reddit, 6月 24, 2025にアクセス、 [https://www.reddit.com/r/learnpython/comments/10qzto6/how\_does\_tkinter\_multithreading\_work\_and\_why/](https://www.reddit.com/r/learnpython/comments/10qzto6/how_does_tkinter_multithreading_work_and_why/)  
44. Build a Basic Form GUI using CustomTkinter module in Python \- GeeksforGeeks, 6月 24, 2025にアクセス、 [https://www.geeksforgeeks.org/build-a-basic-form-gui-using-customtkinter-module-in-python/](https://www.geeksforgeeks.org/build-a-basic-form-gui-using-customtkinter-module-in-python/)  
45. Python \- CUSTOMTKINTER How can I make both these elements appear in the same row?, 6月 24, 2025にアクセス、 [https://stackoverflow.com/questions/75271870/python-customtkinter-how-can-i-make-both-these-elements-appear-in-the-same-row](https://stackoverflow.com/questions/75271870/python-customtkinter-how-can-i-make-both-these-elements-appear-in-the-same-row)