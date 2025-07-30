spaCy-workflow-start_00ファイルから、特に教育用アプリケーションとしての側面を強く意識しています。

VS Code / GitHub / Streamlit / spaCy を活用した英文構造解析アプリ開発の基本ワークフロー
このワークフローは、迅速なプロトタイピングから安定した本番運用までを見据え、特に教育分野向けのインタラクティブな英文解析アプリケーション開発に特化しています。各フェーズにおいて、効率性、堅牢性、そして拡張性を重視した具体的な手順を詳述します。

1. 企画・要件定義フェーズ：アプリの目的とスコープの明確化
この段階は、開発の方向性を定め、手戻りを最小限に抑える上で最も重要です。

1.1. アプリケーションの目的とターゲットユーザーの特定:

目的: 英文構造解析を通じて、ユーザー（特に小中高生）の英文読解力と文法理解を向上させる。

具体的な機能目標:

英文の入力と即時解析。

主語と動詞の特定とハイライト表示。

品詞（名詞、動詞、形容詞など）の表示。

構文構造（句、節、依存関係）の可視化。

一般的な文法エラー（例: 主語と動詞の不一致、冠詞の誤用）の検出と指摘。

動詞の意味分類や類語の提示（オプション）。

解析結果に基づいた簡単な解説やヒント。

ターゲットユーザー: 小学生高学年〜高校生。彼らの学習レベル、集中力持続時間、デジタルデバイスへの慣れを考慮したUI/UX設計が必須となります。

1.2. 主要技術スタックの選定と確認:

フロントエンド/バックエンド: Streamlit (Python)。迅速なプロトタイピングとPythonのみでの完結が強み。

自然言語処理 (NLP): spaCy。高性能な構文解析、品詞タグ付け、固有表現認識機能を提供。モデルサイズと性能のトレードオフを考慮し、まずはen_core_web_smまたはen_core_web_mdから開始。

開発環境: VS Code。統合された開発体験を提供。

バージョン管理: Git/GitHub。共同開発とCI/CDの基盤。

デプロイ: Streamlit Cloud。手軽なWebアプリ公開。

1.3. MVP (Minimum Viable Product) の定義:

最初のリリースで提供する最小限かつ中核的な機能を決定します。例えば、「英文入力」「主語・動詞ハイライト」「品詞表示」など。これにより、早期にフィードバックを得て、次のイテレーションに活かします。

1.4. プロジェクト計画とタイムライン:

フェーズごとのタスク、担当者、おおよその期間を設定します。アジャイル開発手法を取り入れ、短いスプリントで開発とレビューを繰り返すことを推奨します。

2. 環境構築フェーズ：開発基盤の確立
スムーズな開発を行うための土台を構築します。

2.1. プロジェクトリポジトリの作成 (GitHub):

GitHub上で新規リポジトリを作成します（例: english-parser-app）。

README.mdファイルにプロジェクトの概要、目的、技術スタック、セットアップ手順などを記述します。

2.2. ローカル開発環境のセットアップ (VS Code):

2.2.1. プロジェクトフォルダの作成: ローカルPCにリポジトリをクローンまたは新規作成します。

Bash

git clone https://github.com/your-username/english-parser-app.git
cd english-parser-app
2.2.2. VS Codeでプロジェクトを開く:

Bash

code .
2.2.3. Python仮想環境の構築とアクティベート:

VS Codeの統合ターミナルを開き、プロジェクトルートで以下のコマンドを実行します。

Bash

python -m venv .venv
VS Codeが自動的に仮想環境を検出・設定しない場合は、Ctrl + Shift + P -> "Python: Select Interpreter" -> .venv/bin/python を選択します。これにより、Linterやデバッガーなどがこの仮想環境で動作するようになります。

（オプション）ターミナルを再起動し、プロンプトの先頭に(.venv)が表示されていることを確認します。

2.2.4. .gitignore ファイルの作成:

プロジェクトルートに.gitignoreファイルを作成し、以下の内容を記述します。

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/ # 仮想環境フォルダ
pip-log.txt
pip-delete-this-file.txt
.tox/
.coverage
.pytest_cache/
htmlcov/
.ipynb_checkpoints
.mypy_cache/
.ruff_cache/
.vscode/ # VS Codeのユーザー固有設定は除外 (launch.jsonは含めても良い場合がある)
*.sqlite3
*.db

# Streamlit
.streamlit/local/
.streamlit/secret.toml # 機密情報を含む可能性があるため
# Streamlit CloudのシークレットはGitに含めない

# Environment variables
.env
2.3. 依存関係の管理:

2.3.1. pip-tools の導入 (推奨):

仮想環境内でpip install pip-toolsを実行します。

requirements.inファイルを作成し、直接的な依存関係を記述します。バージョンを固定することで、再現性を高めます。

# requirements.in
streamlit>=1.28,<1.29
spacy>=3.5,<3.6
python-dotenv>=1.0,<1.1
pytest>=8.0,<8.1
2.3.2. requirements.txt の生成:

pip-compile requirements.inを実行し、全ての推移的な依存関係を含むrequirements.txtを生成します。

2.3.3. ライブラリのインストール:

pip-sync requirements.txtを実行し、requirements.txtに記述されたライブラリを仮想環境にインストールします。

2.4. spaCyモデルの準備:

2.4.1. ローカルでのモデルダウンロード: 仮想環境がアクティブな状態で、必要なspaCyモデルをダウンロードします。

Bash

python -m spacy download en_core_web_sm
# または
python -m spacy download en_core_web_md
2.4.2. Streamlit Cloud向け packages.txt の作成: Streamlit Cloudにデプロイする際、モデルをプリインストールさせるためにルートディレクトリにpackages.txtを作成し、モデル名を記述します。

# packages.txt
en_core_web_sm
2.5. Streamlit Cloud 設定ファイル (config.toml) の作成:

.streamlit/ディレクトリを作成し、その中にconfig.tomlファイルを作成します。

Ini, TOML

# .streamlit/config.toml
[general]
python_version = "3.9" # 使用するPythonバージョンに合わせる
2.6. Git初期コミット:

ここまでで作成したファイル (.gitignore, requirements.in, requirements.txt, packages.txt, .streamlit/config.toml) をGitに追加し、最初のコミットを行います。

Bash

git add .
git commit -m "feat: Initial project setup and environment configuration"
git push -u origin main
3. 開発フェーズ：アプリ機能の実装
企画で定義したMVP機能を実装し、テストを繰り返します。

3.1. Streamlitアプリケーションの骨格作成 (app.py):

プロジェクトルートにapp.pyファイルを作成し、Streamlitアプリの基本的な構造を記述します。

Python

import streamlit as st
import spacy

# --- spaCyモデルのロードとキャッシュ ---
@st.cache_resource
def load_spacy_model(model_name="en_core_web_sm"):
    try:
        nlp = spacy.load(model_name)
    except OSError:
        st.error(f"spaCy model '{model_name}' not found. Attempting to download...")
        try:
            # Streamlit Cloudではpackages.txtでモデルがプリインストールされるため、
            # 通常はここでspacy.cli.download()を呼ぶ必要はないが、ローカルでの
            # 初回実行やデバッグのために含めておくのも良い。
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)
        except Exception as e:
            st.exception(f"Failed to download spaCy model: {e}")
            st.stop() # アプリの実行を停止
    return nlp

nlp = load_spacy_model("en_core_web_sm") # または en_core_web_md

# --- 解析結果のキャッシュ (入力文が変わらなければ再計算しない) ---
@st.cache_data
def analyze_sentence_with_spacy(sentence: str):
    if not sentence.strip():
        return None
    doc = nlp(sentence)
    return doc

st.set_page_config(layout="wide", page_title="英文構造解析アプリ")
st.title("英語の文を解析しよう！")
st.markdown("文を入力すると、主語や動詞、品詞などが表示されます。")

# --- UI要素 ---
user_input_sentence = st.text_area(
    "ここに英文を入力してください:",
    "The quick brown fox jumps over the lazy dog.",
    height=150,
    help="解析したい英文を入力してください。"
)

if user_input_sentence:
    doc = analyze_sentence_with_spacy(user_input_sentence)

    if doc:
        st.subheader("解析結果")

        # --- 構文解析結果の表示 (詳細化) ---
        st.markdown("#### 文の構造")
        # 主語と動詞の特定とハイライト
        subject_token = None
        verb_token = None
        for token in doc:
            if "nsubj" in token.dep_ and token.head == token.sent.root:
                subject_token = token
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                verb_token = token

        display_text = []
        for token in doc:
            if subject_token and token.i == subject_token.i:
                display_text.append(f"**<span style='color:blue;'>{token.text}</span>**") # 主語を青色太字
            elif verb_token and token.i == verb_token.i:
                display_text.append(f"**<span style='color:red;'>{token.text}</span>**") # 動詞を赤色太字
            else:
                display_text.append(token.text)
        st.markdown(" ".join(display_text), unsafe_allow_html=True)
        if subject_token:
            st.info(f"主語: **{subject_token.text}**")
        if verb_token:
            st.info(f"動詞: **{verb_token.text}**")


        st.markdown("#### 品詞と依存関係")
        # 品詞と依存関係の表形式表示
        data = []
        for token in doc:
            data.append({
                "単語": token.text,
                "品詞": token.pos_,
                "詳細品詞": token.tag_,
                "依存関係": token.dep_,
                "親単語": token.head.text if token.head != token else "-",
                "説明": spacy.explain(token.dep_)
            })
        st.dataframe(data)

        # --- 構文エラー検出 (教育的要素) ---
        st.markdown("#### 文法チェック (簡易版)")
        errors = []
        # 例: 単数形主語と動詞のSなし
        if subject_token and verb_token and subject_token.tag_ == "NN" and verb_token.tag_ == "VB":
            errors.append(f"'{subject_token.text}' は単数形名詞ですが、動詞 '{verb_token.text}' は複数形（または原形）のようです。3人称単数現在形では動詞に 's' が必要かもしれません。例: '{verb_token.text}s'")

        # 例: 冠詞の欠落 (簡易的)
        if any(token.pos_ == "NOUN" and token.dep_ == "dobj" and not any(t.pos_ == "DET" for t in token.children) for token in doc):
            # 完全なロジックではないが、教育的なヒントとして
            errors.append("可算名詞に冠詞（a/an/the）が付いていない可能性があります。")

        if errors:
            for error in errors:
                st.warning(error)
        else:
            st.success("今のところ、大きな文法エラーは見つかりません。")

        # --- 動詞の意味分類と類語提示 (オプション) ---
        with st.expander("動詞の詳細情報と類語 (実験的機能)"):
            if verb_token:
                st.write(f"選択された動詞: **{verb_token.text}**")
                # ここにWordNetなどのAPI連携ロジックを実装
                st.info("動詞の意味分類や類語表示の機能は現在開発中です。")
            else:
                st.info("動詞が見つかりませんでした。")
    else:
        st.info("解析する英文を入力してください。")

# --- UIの整理整頓 (st.expander / st.tabs / st.sidebar) ---
with st.sidebar:
    st.header("設定")
    # モデル選択など、ユーザーが設定を変更できるオプションをここに追加
    # model_selection = st.selectbox("spaCyモデルを選択", ["en_core_web_sm", "en_core_web_md"])
    # st.info(f"現在選択中のモデル: {nlp.meta['name']}")

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 英文構造解析アプリ")
3.2. ローカルでの動作確認:

VS Codeターミナルで streamlit run app.py を実行し、ブラウザでアプリが正しく表示され、機能が動作するかを確認します。

3.3. 環境変数（APIキー）の管理:

外部API（例: 類語辞書API）を使用する場合、プロジェクトルートに.envファイルを作成し、APIキーを記述します。

# .env
DICTIONARY_API_KEY="your_secret_api_key_here"
python-dotenvを使用してapp.pyでロードします。

Python

import os
from dotenv import load_dotenv

load_dotenv() # .envファイルから環境変数をロード

api_key = os.getenv("DICTIONARY_API_KEY")
if api_key:
    # APIキーを使用するロジック
    pass
else:
    st.warning("DICTIONARY_API_KEY が設定されていません。")
重要な注意点: .envファイルは絶対にGitHubにプッシュしてはいけません（.gitignoreで除外されていることを再確認）。Streamlit Cloudでは、ダッシュボードのSecrets機能で安全に管理します。

3.4. 継続的なコミット:

小さな機能追加やバグ修正ごとに頻繁にコミットを行います。

Bash

git add .
git commit -m "feat: Add basic sentence parsing and display subject/verb"
4. テストフェーズ：品質保証
アプリケーションの品質を確保し、バグを早期に発見します。

4.1. 単体テストの作成 (testsディレクトリ):

testsディレクトリを作成し、test_app.pyなどのテストファイルを作成します。

pytestを使用して、spaCyの解析ロジック（主語・動詞の特定、エラー検出など）の単体テストを記述します。

様々な入力文（正しい文、誤った文、複雑な文）に対するテストケースを作成し、エッジケースも考慮に入れます。

Python

# tests/test_parsing.py
import pytest
import spacy
from app import analyze_sentence_with_spacy, load_spacy_model

@pytest.fixture(scope="module")
def nlp_model():
    return load_spacy_model("en_core_web_sm")

def test_subject_verb_identification(nlp_model):
    doc = analyze_sentence_with_spacy("The cat sat on the mat.")
    subject = None
    verb = None
    for token in doc:
        if "nsubj" in token.dep_ and token.head == token.sent.root:
            subject = token.text
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            verb = token.text
    assert subject == "cat"
    assert verb == "sat"

def test_simple_grammar_error_detection(nlp_model):
    doc = analyze_sentence_with_spacy("She go to school.")
    # 簡易的なテストのため、より複雑なロジックはapp.pyに
    errors = []
    subject_token = None
    verb_token = None
    for token in doc:
        if "nsubj" in token.dep_ and token.head == token.sent.root:
            subject_token = token
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            verb_token = token

    if subject_token and verb_token and subject_token.tag_ == "PRP" and subject_token.text.lower() == "she" and verb_token.tag_ == "VB":
        errors.append("動詞の形が適切ではない可能性があります（例: 'goes'）。")
    assert len(errors) > 0 # エラーが検出されたことを確認
4.2. VS Codeデバッガーの活用:

app.pyにブレークポイントを設定し、VS Codeのデバッガー (Run and Debug) を使用してステップ実行、変数の検査などを行います。

launch.jsonを設定すると、Streamlitアプリをデバッグモードで起動できます。

JSON

// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Streamlit Debug",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}",
            "module": "streamlit.web.cli",
            "args": [
                "run",
                "${workspaceFolder}/app.py",
                "--server.port", "8501",
                "--server.headless", "true"
            ],
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}" // 必要に応じてプロジェクトルートをPythonパスに追加
            }
        }
    ]
}
4.3. UI/UXのレビューと改善:

定期的にアプリをテスト実行し、ユーザー視点でUI/UXを確認します。特に教育対象である小中高生に実際に触ってもらい、フィードバックを収集します。

st.expander、st.tabs、st.sidebarなどを活用し、機能が増えてもUIが煩雑にならないように整理します。

教育的デザインの原則の適用:

視覚的なヒント: 主語と動詞のハイライト（色分け）、構文ツリーの簡易表示などを検討します。

簡潔な説明: ポップアップやサイドバーで、文法用語を避けた平易な言葉で解説を提供します。

インタラクティブ性: ユーザーが自分で例文を入力するだけでなく、あらかじめ用意された例文を選択したり、解析結果の特定の単語をクリックすると詳細情報が表示されたりするなどのインタラクティブな要素を盛り込みます。

5. CI/CDフェーズ：自動化されたデプロイメント
GitHub Actionsを活用し、コード変更が自動的にテストされ、デプロイされるパイプラインを構築します。

5.1. GitHub Actionsワークフローの設定:

.github/workflowsディレクトリを作成し、deploy.ymlなどのYAMLファイルを作成します。

このワークフローは、mainブランチへのプッシュをトリガーとし、テストの実行、必要なspaCyモデルのインストール、そしてStreamlit Cloudへのデプロイを自動で行います。

YAML

# .github/workflows/deploy.yml
name: Streamlit CI/CD

on:
  push:
    branches:
      - main # mainブランチへのプッシュでトリガー

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest # 実行環境

    steps:
    - name: Checkout code
      uses: actions/checkout@v4 # リポジトリのコードをチェックアウト

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.9' # .streamlit/config.tomlと一致させる

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt # requirements.txtから依存関係をインストール
        # spaCyモデルのダウンロードはpackages.txtがStreamlit Cloudで処理するため、
        # GitHub Actionsのビルドステップで改めて行う必要は少ないが、
        # テスト実行のために必要であればここで実行
        python -m spacy download en_core_web_sm --quiet

    - name: Run tests
      run: |
        pytest # テストの実行

    - name: Deploy to Streamlit Cloud
      if: success() # 前のステップが成功した場合のみデプロイ
      uses: streamlit/actions/deploy@v0.0.3 # Streamlit公式のデプロイアクション
      with:
        streamlit_app_path: app.py # アプリのエントリポイントファイル
        streamlit_api_key: ${{ secrets.STREAMLIT_API_KEY }} # GitHub SecretsからAPIキーを取得
        repository: ${{ github.repository }} # 現在のリポジトリ名
        branch: ${{ github.ref_name }} # 現在のブランチ名
        title: 英文構造解析アプリ # Streamlit Cloudでのアプリタイトル
5.2. Streamlit CloudでのAPIキー設定:

Streamlit Cloudダッシュボードにログインし、デプロイするアプリのリポジトリを選択します。

"Advanced settings" -> "Secrets" でSTREAMLIT_API_KEYという名前でGitHubのAPIキー（ダッシュボードで発行される）を設定します。これにより、GitHub Actionsから安全にStreamlit Cloudへデプロイできるようになります。

5.3. 自動デプロイの確認:

mainブランチにプッシュするたびに、GitHub Actionsがトリガーされ、テストが実行され、成功すればStreamlit Cloudに自動的にデプロイされることを確認します。

6. 運用・改善フェーズ：リリース後の継続的な発展
アプリは公開されて終わりではなく、ユーザーフィードバックに基づいて継続的に改善していきます。

6.1. ユーザーフィードバックの収集:

アプリ内にフィードバックフォームへのリンクを設置したり、アンケートを実施したりして、ユーザー（小中高生やその保護者、教師）からの意見を積極的に収集します。

「どの機能が役立ったか？」「もっとこうだったらいいのに、と思うことはあるか？」「分かりにくい点はあったか？」など、具体的な質問を投げかけます。

6.2. ログとエラー監視:

Streamlit Cloudダッシュボードのログ機能を定期的に確認し、アプリのエラーやパフォーマンスの問題を監視します。

Pythonのloggingモジュールを活用し、より詳細なログを出力するようにコードを改善します。

6.3. パフォーマンス最適化:

ユーザーが増えるにつれて、アプリの応答速度が重要になります。@st.cache_resourceや@st.cache_dataの適切な利用に加え、必要に応じてspaCyモデルの軽量化（例: nlp.disable_pipes()で不要なパイプラインコンポーネントを無効化）や、より強力なStreamlit Cloudインスタンスへのアップグレードを検討します。

大規模な辞書データや外部APIへのアクセスは、非同期処理を導入したり、バックエンドサービスとして分離したりすることも視野に入れます。

6.4. 機能改善と追加:

フィードバックや市場のニーズに基づいて、新たな機能（例: 練習問題、ゲーム化要素、進捗トラッキング、多言語対応）を追加します。

この際も、企画・要件定義からデプロイまでのワークフローを繰り返します（アジャイル開発のスプリント）。

6.5. ドキュメントの更新:

アプリの機能や使い方が変更された場合、READMEやアプリ内のヘルプテキストを常に最新の状態に保ちます。

この詳細なワークフローは、単なる技術的な手順に留まらず、アプリケーションの企画、ユーザー体験、そして継続的な改善というソフトウェア開発の全体像を網羅しています。特に教育用アプリケーションにおいては、技術的な正確性だけでなく、**「ユーザーが楽しく、効果的に学べるか」**という視点が成功の鍵となります。各フェーズでこの視点を忘れずに開発を進めることで、高品質な英文構造解析アプリを構築できるでしょう。



