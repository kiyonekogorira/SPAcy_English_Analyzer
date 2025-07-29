import streamlit as st
import spacy
from spacy import displacy
from spacy import displacy
import logging
import re

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- spaCyモデルのロードとキャッシュ ---
@st.cache_resource
def load_spacy_model(model_name="en_core_web_sm"):
    """指定されたspaCyモデルをロードし、存在しない場合はダウンロードを試みる"""
    try:
        return spacy.load(model_name)
    except OSError:
        st.error(f"SpaCyモデル '{model_name}' が見つかりませんでした。ダウンロードします...")
        try:
            spacy.cli.download(model_name)
            return spacy.load(model_name)
        except Exception as e:
            st.exception(f"モデルのダウンロード中にエラーが発生しました: {e}")
            st.stop()

# --- Mappings for Phrase Structure ---
# These are defined globally to be accessible by the tree formatting function.
POS_MAP = {
    "NOUN": "名詞", "PRON": "代名詞", "VERB": "動詞", "AUX": "助動詞",
    "ADJ": "形容詞", "ADV": "副詞", "ADP": "前置詞", "DET": "限定詞",
    "PUNCT": "句読点", "PROPN": "固有名詞", "NUM": "数詞", "CCONJ": "等位接続詞",
    "SCONJ": "従属接続詞", "INTJ": "間投詞", "PART": "小詞", "SYM": "記号",
    "X": "その他",
}
DEP_MAP = {
    "nsubj": "名詞的主語", "ROOT": "文の主動詞 (根)", "attr": "補語 (名詞的)",
    "det": "限定詞", "relcl": "関係節", "dobj": "直接目的語",
    "npadvmod": "名詞句副詞修飾語", "punct": "句読点", "aux": "助動詞",
    "auxpass": "受動態助動詞", "acomp": "補語 (形容詞的)", "pobj": "前置詞の目的語",
    "prep": "前置詞句", "amod": "形容詞修飾語", "advmod": "副詞修飾語",
    "cc": "等位接続詞", "conj": "接続された要素", "compound": "複合語",
    "xcomp": "補語 (動詞的)", "csubj": "節主語",
    "appos": "同格", "acl": "形容詞句", "advcl": "副詞節", "agent": "動作主",
    "case": "格", "ccomp": "補文", "dative": "与格",
    "expl": "形式主語/目的語", "mark": "標識語", "nummod": "数詞修飾語",
    "oprd": "目的格補語", "parataxis": "並列関係", "poss": "所有格",
    "preconj": "前置接続詞", "predet": "前限定詞", "quantmod": "数量修飾語",
}
RELATION_TEMPLATES = {
    "nsubj": "{}は{}の主語です。",
    "dobj": "{}は{}の直接目的語です。",
    "iobj": "{}は{}の間接目的語です。",
    "attr": "{}は{}の補語です。",
    "acomp": "{}は{}の補語です。",
    "det": "{}は{}を限定しています。",
    "amod": "{}は{}を修飾しています。",
    "advmod": "{}は{}を修飾しています。",
    "prep": "{}は{}の前置詞句の始まりです。",
    "pobj": "{}は{}の前置詞の目的語です。",
    "aux": "{}は{}の助動詞です。",
    "auxpass": "{}は{}の受動態助動詞です。",
    "relcl": "{}は{}を説明する関係節です。",
    "compound": "{}は{}と複合語を形成しています。",
    "cc": "{}は{}と{}を接続しています。",
    "conj": "{}は{}と接続されています。",
    "default": "{}は{}に依存しています。",
}

def get_tree_style_css():
    """CSS for the phrase structure tree."""
    return """
    <style>
        .tree ul {
            position: relative;
            padding: 0 0 0 20px;
            margin: 0;
            list-style: none;
        }
        .tree li {
            position: relative;
            padding: 3px 0 3px 20px;
            line-height: 1.5;
        }
        .tree li::before, .tree li::after {
            content: '';
            position: absolute;
            left: 0;
        }
        .tree li::before {
            border-left: 1px solid #999;
            height: 100%;
            width: 1px;
            top: -12px;
        }
        .tree li:last-child::before {
            height: 28px;
        }
        .tree li::after {
            border-top: 1px solid #999;
            height: 1px;
            width: 20px;
            top: 16px;
        }
        .tree .token-info {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 5px;
            margin-bottom: 3px;
            border: 1px solid #ccc;
            background-color: #e8dff5; /* Light purple */
        }
        .tree .head {
            background-color: #e8dff5; /* Light purple */
        }
        .tree .modifier {
            background-color: #f5f5f5; /* Lighter grey */
        }
        .tree .pos-dep {
            font-size: 0.85em;
            color: #555;
        }
        .tree .relation {
            font-size: 0.9em;
            color: #007bff; /* Blue */
            margin-left: 15px;
        }
    </style>
    """

def generate_phrase_tree_html(token, elements, main_verb, level=0):
    """
    Generates an HTML tree structure for a token and its children.
    When rendering the verb phrase, the subject is omitted.
    """
    html_parts = []
    pos_jp = POS_MAP.get(token.pos_, token.pos_)
    dep_jp = DEP_MAP.get(token.dep_, token.dep_)
    token_class = "head" if level == 0 else "modifier"

    html_parts.append("<li>")
    html_parts.append(f"<div class='token-info {token_class}'>")
    html_parts.append(f"<strong>{token.text}</strong> <span class='pos-dep'>({pos_jp} / {dep_jp})</span>")

    # Add relationship explanation
    relation_explanation = ""
    if level == 0 and token != main_verb:
        template = RELATION_TEMPLATES.get(token.dep_, RELATION_TEMPLATES["default"])
        try:
            relation_explanation = template.format(token.text, main_verb.text)
        except IndexError:
            relation_explanation = f"{token.text}は{main_verb.text}に依存しています。"
    elif level > 0:
        template = RELATION_TEMPLATES.get(token.dep_, RELATION_TEMPLATES["default"])
        try:
            relation_explanation = template.format(token.text, token.head.text)
        except IndexError:
            relation_explanation = f"{token.text}は{token.head.text}に依存しています。"
    
    if relation_explanation:
        html_parts.append(f"<span class='relation'>&mdash; {relation_explanation}</span>")

    html_parts.append("</div>")

    # Process children
    children = list(token.children)
    if children:
        html_parts.append("<ul>")
        for child in children:
            # When rendering the main verb's tree (verb phrase), skip the subject.
            if token == main_verb and child == elements.get("subject"):
                continue
            
            html_parts.append(generate_phrase_tree_html(child, elements, main_verb, level + 1))
        html_parts.append("</ul>")

    html_parts.append("</li>")
    return "".join(html_parts)

# --- spaCyモデルのロードとキャッシュ ---
@st.cache_resource
def load_spacy_model(model_name="en_core_web_sm"):
    """指定されたspaCyモデルをロードし、存在しない場合はダウンロードを試みる"""
    try:
        return spacy.load(model_name)
    except OSError:
        st.error(f"SpaCyモデル '{model_name}' が見つかりませんでした。ダウンロードします...")
        try:
            spacy.cli.download(model_name)
            return spacy.load(model_name)
        except Exception as e:
            st.exception(f"モデルのダウンロード中にエラーが発生しました: {e}")
            st.stop()

nlp = load_spacy_model()
st.markdown(get_tree_style_css(), unsafe_allow_html=True)

# --- 解析関数 ---
def find_sentence_elements(doc):
    """
    spaCyのDocオブジェクトから文の主要な要素を特定し、文型と態を判定する（修正版）。
    """
    elements = {"subject": None, "verb": None, "dobj": None, "iobj": None, "complement": None, "agent": None, "voice": "能動態"}
    pattern = "不明"
    
    passive_verb = None
    passive_aux = None

    # 1. まず、文全体で受動態の構造（auxpass）が存在するかをスキャンする
    for token in doc:
        if token.dep_ == "auxpass":
            passive_aux = token
            passive_verb = token.head
            break # 受動態の核心部分を見つけたらループを抜ける

    if passive_verb and passive_aux:
        # --- 受動態の処理 ---
        elements["voice"] = "受動態"
        elements["verb"] = passive_verb
        
        # 受動態の主語 (nsubjpass) を探す
        for child in passive_verb.children:
            if child.dep_ == "nsubjpass":
                elements["subject"] = child
                break
        
        # 動作主 (agent) を探す
        for child in passive_verb.children:
            if child.dep_ == "agent":
                # agentの子から実際の動作主（名詞）を取得
                for grand_child in child.children:
                    if grand_child.dep_ == "pobj":
                        elements["agent"] = grand_child
                        break
                break
        
        # 受動態の文では、補語は存在しうる (例: The room was painted blue.)
        for child in passive_verb.children:
            if child.dep_ in ["attr", "acomp", "oprd"]:
                elements["complement"] = child
                break
        
        # 受動態の文型は通常、能動態の文型に基づいて判断されるため、ここでは特定の文型名は付けない
        pattern = "受動態の文"

    else:
        # --- 能動態の処理 ---
        elements["voice"] = "能動態"
        main_verb = None
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ in ["VERB", "AUX"]:
                main_verb = token
                break
        
        if main_verb:
            elements["verb"] = main_verb
            
            # 能動態の主語 (nsubj) を探す
            for child in main_verb.children:
                if child.dep_ == "nsubj":
                    elements["subject"] = child
                    break
            
            # 目的語と補語を探す
            for child in main_verb.children:
                if child.dep_ == "dobj":
                    elements["dobj"] = child
                if child.dep_ in ["iobj", "dative"]:
                    elements["iobj"] = child
                if child.dep_ in ["attr", "acomp", "oprd"]:
                    elements["complement"] = child

            # 文型判定ロジック
            s = elements["subject"]
            v = elements["verb"]
            o1 = elements["dobj"]
            o2 = elements["iobj"]
            c = elements["complement"]

            if s and v:
                if o1 and c and c.dep_ == "oprd": # SVOC (目的格補語)
                     pattern = "SVOC (第5文型)"
                elif o1 and o2:
                     pattern = "SVOO (第4文型)"
                elif o1:
                     pattern = "SVO (第3文型)"
                elif c:
                     pattern = "SVC (第2文型)"
                else:
                     pattern = "SV (第1文型)"

    elements["pattern_name"] = pattern
    return pattern, elements

def find_clause_elements(doc):
    """
    spaCyのDocオブジェクトから主節と従属節を特定し、それぞれの要素を抽出する。
    """
    clauses = []
    
    # 主節の動詞（ROOT）を見つける
    main_verbs = [token for token in doc if token.dep_ == "ROOT" and token.pos_ in ["VERB", "AUX"]]
    
    # 等位接続詞で結ばれた複数の主節動詞を処理
    for verb in main_verbs:
        # 主節の主語を見つける
        subject = next((child for child in verb.children if child.dep_ in ["nsubj", "nsubjpass"]), None)
        
        # 主節の範囲を決定（単純化のため、動詞のサブツリー全体を主節と見なす）
        main_clause_span = doc[min(t.i for t in verb.subtree) : max(t.i for t in verb.subtree) + 1]

        clauses.append({
            "type": "主節",
            "verb": verb,
            "subject": subject,
            "introducer": None,
            "span": main_clause_span
        })

        # 主節に接続された他の節（conj）も主節として扱う
        for conjunct_verb in verb.conjuncts:
             conjunct_subject = next((child for child in conjunct_verb.children if child.dep_ in ["nsubj", "nsubjpass"]), None)
             if conjunct_subject:
                    conjunct_clause_span = doc[min(t.i for t in conjunct_verb.subtree) : max(t.i for t in conjunct_verb.subtree) + 1]
                    clauses.append({
                        "type": "主節", # 等位接続詞で結ばれているため主節
                        "verb": conjunct_verb,
                        "subject": conjunct_subject,
                        "introducer": next((child for child in conjunct_verb.children if child.dep_ == "cc"), None),
                        "span": conjunct_clause_span
                    })


    # 従属節を見つける (advcl, relcl, ccomp)
    for token in doc:
        # 副詞節 (advcl)
        if token.dep_ == "advcl":
            sub_verb = token
            sub_subject = next((child for child in sub_verb.children if child.dep_ in ["nsubj", "nsubjpass"]), None)
            introducer = next((child for child in sub_verb.children if child.dep_ == "mark"), None)
            
            if sub_subject:
                sub_clause_span = doc[min(t.i for t in sub_verb.subtree) : max(t.i for t in sub_verb.subtree) + 1]
                clauses.append({
                    "type": "従属節",
                    "verb": sub_verb,
                    "subject": sub_subject,
                    "introducer": introducer,
                    "span": sub_clause_span
                })

        # 関係節 (relcl)
        elif token.dep_ == "relcl":
            rel_verb = token
            # 関係節の主語は、関係代名詞(who, which)か、先行詞に依存する
            rel_subject = next((child for child in rel_verb.children if child.dep_ in ["nsubj", "nsubjpass"]), None)
            # 関係代名詞が主語でない場合、先行詞が主語となることがある
            if not rel_subject:
                 rel_subject = rel_verb.head # 先行詞
            
            if rel_subject:
                rel_clause_span = doc[min(t.i for t in rel_verb.subtree) : max(t.i for t in rel_verb.subtree) + 1]

                # 関係代名詞が導入語
                # 節の開始トークンを導入語候補とする
                introducer = None
                if rel_clause_span and rel_clause_span[0].pos_ in ["SCONJ", "PRON", "ADP"]:
                    introducer = rel_clause_span[0]

                clauses.append({
                    "type": "従属節",
                    "verb": rel_verb,
                    "subject": rel_subject,
                    "introducer": introducer,
                    "span": rel_clause_span
                })
        
        # 補文節 (ccomp)
        elif token.dep_ == "ccomp":
            ccomp_verb = token
            ccomp_subject = next((child for child in ccomp_verb.children if child.dep_ in ["nsubj", "nsubjpass"]), None)
            introducer = next((child for child in ccomp_verb.children if child.dep_ == "mark"), None)

            if ccomp_subject:
                ccomp_clause_span = doc[min(t.i for t in ccomp_verb.subtree) : max(t.i for t in ccomp_verb.subtree) + 1]
                clauses.append({
                    "type": "従属節",
                    "verb": ccomp_verb,
                    "subject": ccomp_subject,
                    "introducer": introducer,
                    "span": ccomp_clause_span
                })


    # 節を文中の出現順にソート
    clauses.sort(key=lambda c: c["span"].start)
    
    return clauses

def render_highlighted_text(doc, elements):
    """
    文の各要素（主語、動詞、目的語、補語）をハイライトしてHTML文字列を生成する。
    凡例の色と一致させる。文型構成要素の表示も含む。
    """
    highlighted_parts = []
    element_map = {
        elements["subject"]: ("主語", "#ADD8E6", "S"),
        elements["verb"]: ("動詞", "#FFB6C1", "V"),
        elements["dobj"]: ("目的語", "#FFDAB9", "O"),
        elements["iobj"]: ("間接目的語", "#90EE90", "O"),
        elements["complement"]: ("補語", "#D8BFD8", "C"),
    }

    for token in doc:
        token_html = token.text
        for element, (label, color, abbr) in element_map.items():
            if element and token.idx == element.idx:
                token_html = f'<span style="background-color: {color}; font-weight: bold; padding: 2px 5px; border-radius: 5px;" title="{label}">{token.text}</span>'
                break
        
        highlighted_parts.append(token_html)
        if token.whitespace_:
            highlighted_parts.append(token.whitespace_)
        elif token.i < len(doc) - 1 and not doc[token.i+1].is_punct:
            highlighted_parts.append(" ")
            
    return "".join(highlighted_parts)

def render_clause_highlighted_text(doc, clauses):
    """
    文の各節を背景色とキー要素のアンダーラインでハイライトしてHTML文字列を生成する。
    """
    highlighted_html_parts = []
    clause_summaries = []

    token_highlight_info = {}

    for clause in clauses:
        clause_type = clause["type"]
        # Background colors for clauses
        bg_color = '#E0FFFF' if clause_type == '主節' else '#FFFACD' # Light Cyan for main, Lemon Chiffon for subordinate
        # Underline colors for key elements
        underline_color = "blue" if clause_type == "主節" else "#DC143C" # Blue for main, Crimson for subordinate
        
        # Generate summary for each clause
        clause_summaries.append(f"<span style=\"background-color: {bg_color}; padding: 2px 5px; border-radius: 3px; font-size: 1.2em;\">{clause_type}</span>")
        
        # Populate token_highlight_info for background colors
        for token_in_span in clause["span"]:
            # If a token belongs to multiple clauses, the last one processed (which should be the most specific/inner clause) will set its background.
            token_highlight_info[token_in_span] = token_highlight_info.get(token_in_span, {})
            token_highlight_info[token_in_span]['bg_color'] = bg_color

        # Populate token_highlight_info for key elements (subject, verb, introducer)
        key_elements_map = {
            clause["subject"]: "主語",
            clause["verb"]: "動詞",
        }
        if clause["introducer"]:
            key_elements_map[clause["introducer"]] = "導入語"

        for key_elem, role in key_elements_map.items():
            if key_elem:
                token_highlight_info[key_elem] = token_highlight_info.get(key_elem, {})
                token_highlight_info[key_elem]['underline'] = True
                token_highlight_info[key_elem]['underline_color'] = underline_color
                token_highlight_info[key_elem]['roles'] = token_highlight_info[key_elem].get('roles', [])
                if role not in token_highlight_info[key_elem]['roles']:
                    token_highlight_info[key_elem]['roles'].append(role)

    # Now, iterate through the doc and build the HTML
    for token in doc:
        styles = []
        title_attr = ""
        
        info = token_highlight_info.get(token, {})

        if 'bg_color' in info:
            styles.append(f"background-color: {info['bg_color']}")
        
        if info.get('underline'):
            styles.append(f"text-decoration: underline; text-decoration-color: {info['underline_color']};")
            if info.get('roles'):
                title_attr = f'title="{", ".join(info['roles'])}"'
        
        if styles or title_attr:
            token_html = f'<span {title_attr} style="{"; ".join(styles)}">{token.text}</span>'
        else:
            token_html = token.text
        
        highlighted_html_parts.append(token_html)
        
        # Handle whitespace
        if token.whitespace_:
            highlighted_html_parts.append(token.whitespace_)
        elif token.i < len(doc) - 1 and not doc[token.i+1].is_punct:
            highlighted_html_parts.append(" ")
            
    return "".join(highlighted_html_parts), clause_summaries

# --- アプリケーション本体 ---
st.title("英文構造解析アプリ")

# --- 状態管理とコールバック ---
# セッションステートを初期化
if "user_input" not in st.session_state:
    st.session_state.user_input = "She is a very famous singer."

# selectboxの値が変更されたときに呼び出されるコールバック関数
def update_text_from_sample():
    st.session_state.user_input = st.session_state.sample_select

# --- サイドバー ---
st.sidebar.header("例文")
sample_sentences = [
    "The birds are flying in the sky.", # SV (第1文型)
    "She is a very famous singer.", # SVC (第2文型)
    "The man sitting by the window is my father.", # SVC (第2文型)
    "My friend plays the piano.", # SVO (第3文型)
    "He gave me a beautiful present.", # SVOO (第4文型)
    "I like apples and he loves oranges.",
    "This is the book that I bought yesterday.",
    "The ball was kicked by the boy.",
    "English is spoken all over the world.",
    "The window was broken.",
]
st.sidebar.selectbox(
    "試したい例文を選んでください:",
    [""] + sample_sentences,
    key="sample_select",
    on_change=update_text_from_sample
)

st.sidebar.markdown("### 文型判別の色分け")
st.sidebar.markdown("<span style=\"background-color: #ADD8E6; padding: 2px 5px; border-radius: 3px;\">主語 (S)</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style=\"background-color: #FFB6C1; padding: 2px 5px; border-radius: 3px;\">動詞 (V)</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style=\"background-color: #FFDAB9; padding: 2px 5px; border-radius: 3px;\">目的語 (O)</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style=\"background-color: #90EE90; padding: 2px 5px; border-radius: 3px;\">間接目的語 (O)</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style=\"background-color: #D8BFD8; padding: 2px 5px; border-radius: 3px;\">補語 (C)</span>", unsafe_allow_html=True)

st.sidebar.markdown("### 文節の色分け")
st.sidebar.markdown("<span style=\"background-color: #E0FFFF; padding: 2px 5px; border-radius: 3px;\">主節</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style=\"background-color: #FFFACD; padding: 2px 5px; border-radius: 3px;\">従属節</span>", unsafe_allow_html=True)

# --- メイン画面 ---
user_input = st.text_area("解析したい英文を入力してください。", key="user_input")

if st.button("解析する"):
    
    if user_input:
        doc = nlp(user_input)
        pattern, elements = find_sentence_elements(doc)
        
        st.header("解析結果")
        
        if elements["subject"] and elements["verb"]:
            st.success(f"文型を特定しました！")

            # --- タブ形式のレイアウト ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "文の骨格（文型）", 
                "句の分解", 
                "節の構造", 
                "単語の関係（詳細）",
                "実践と応用（態）"
            ])

            with tab1:
                st.header("文型と主要素のハイライト")
                st.markdown("文の骨格を掴むために、文の主要な要素（主語、動詞、目的語、補語）と、それが構成する「文型」を確認します。")
                st.info(f"例文: {doc.text}")
                st.markdown(f"### <span style=\"font-size: 1.2em;\">文型の判別: **{elements['pattern_name']}**</span>", unsafe_allow_html=True)
                
                # --- 提案1: 一言サマリー解説の追加 ---
                pattern_summary = {
                    "SV (第1文型)": "💡 **これは「SがVする」という、基本的な動作を表す文の形です。**",
                    "SVC (第2文型)": "💡 **これは「SはCである」と、主語の状態や性質を説明する文の形です。**",
                    "SVO (第3文型)": "💡 **これは「SがOをVする」と、主語の動作が対象（目的語）に影響を与える文の形です。**",
                    "SVOO (第4文型)": "💡 **これは「SがO1にO2をVする」と、誰かに何かを与える・受け取る動作を表す文の形です。**",
                }.get(elements["pattern_name"], "")
                if pattern_summary:
                    st.markdown(f"<p>{pattern_summary}</p>", unsafe_allow_html=True)

                # --- 提案3: 文型構成要素の文字列を色付きで生成 ---
                display_elements = []
                if elements["subject"]: display_elements.append((elements["subject"].i, f"<span style=\"background-color: #ADD8E6; padding: 2px 5px; border-radius: 3px;\">主語 (S)</span>"))
                if elements["verb"]: display_elements.append((elements["verb"].i, f"<span style=\"background-color: #FFB6C1; padding: 2px 5px; border-radius: 3px;\">動詞 (V)</span>"))
                if elements["dobj"]: display_elements.append((elements["dobj"].i, f"<span style=\"background-color: #FFDAB9; padding: 2px 5px; border-radius: 3px;\">目的語 (O)</span>"))
                if elements["iobj"]: display_elements.append((elements["iobj"].i, f"<span style=\"background-color: #90EE90; padding: 2px 5px; border-radius: 3px;\">間接目的語 (O)</span>"))
                if elements["complement"]: display_elements.append((elements["complement"].i, f"<span style=\"background-color: #D8BFD8; padding: 2px 5px; border-radius: 3px;\">補語 (C)</span>"))

                # token.i (インデックス) でソート
                display_elements.sort(key=lambda x: x[0])

                # ソートされたHTML文字列を結合
                pattern_elements_html_list = [item[1] for item in display_elements]
                pattern_info_html = f"<p><b>{elements['pattern_name']}</b>: {' '.join(pattern_elements_html_list)}</p>"
                st.markdown(pattern_info_html, unsafe_allow_html=True)

                highlighted_sentence_html = render_highlighted_text(doc, elements)
                st.markdown(highlighted_sentence_html, unsafe_allow_html=True)

            with tab2:
                st.header("句の構造分解")
                st.markdown("主語や動詞がどのような単語の集まりでできているか、その内部構造を詳しく見てみましょう。")
                st.info(f"例文: {doc.text}")
                if elements["subject"]:
                    st.markdown("#### 主語の構造:")
                    subject_root = elements["subject"]
                    subject_tree_html = generate_phrase_tree_html(subject_root, elements, elements["verb"])
                    st.markdown(f"<ul>{subject_tree_html}</ul>", unsafe_allow_html=True)
                else:
                    st.info("主語の構造を解析できませんでした。")

                if elements["verb"]:
                    st.markdown("#### 動詞句の構造:")
                    verb_root = elements["verb"]
                    verb_tree_html = generate_phrase_tree_html(verb_root, elements, elements["verb"])
                    st.markdown(f"<ul>{verb_tree_html}</ul>", unsafe_allow_html=True)

            with tab3:
                st.header("節の構造")
                clauses = find_clause_elements(doc)
                if clauses:
                    st.markdown("この文が接続詞などでどう区切られ、複数の「ミニ文」で構成されているかを見てみましょう。")
                    st.info(f"例文: {doc.text}")
                    st.markdown("**文節の色分け（背景色とアンダーライン）:** すべての節（主節・従属節）の範囲を背景色で区別し、各節の主語・動詞・導入語にアンダーラインを引きます。")
                    highlighted_html, clause_summaries = render_clause_highlighted_text(doc, clauses)
                    if clause_summaries:
                        st.markdown(" ".join(clause_summaries), unsafe_allow_html=True)
                    st.markdown(highlighted_html, unsafe_allow_html=True)
                    st.markdown("--- 各節の詳細 ---")
                    for i, clause in enumerate(clauses):
                        st.markdown(f"**節 {i+1} ({clause['type']}):**")
                        if clause.get('subject'):
                            st.markdown(f"- 主語: {clause['subject'].text}")
                        if clause.get('verb'):
                            st.markdown(f"- 動詞: {clause['verb'].text}")
                        if clause.get('introducer'):
                            st.markdown(f"- 導入語: {clause['introducer'].text}")
                else:
                    st.info("この文には解析対象となる節が1つ、または見つかりませんでした。")

            with tab4:
                st.header("単語の依存関係（詳細）")
                st.markdown("文中のすべての単語間の文法的な関係を視覚的に表示します。矢印は単語間の依存関係を示します。")
                
                # --- 提案：図の読み方ガイドの追加 ---
                st.markdown("""
                **この図の読み方ガイド**
                - **矢印:** 単語と単語の文法的な繋がりを表します。矢印の根元が、矢印の先の単語を修飾・説明しています。
                - **ラベル:** 矢印の下にあるラベル（`nsubj`など）は、その繋がりがどのような「文法的な役割」を持つかを示しています。
                - **ROOT:** すべての矢印を辿っていくと、文の中心である**ROOT**（根）に行き着きます。
                """)
                st.markdown("---")

                svg = displacy.render(doc, style="dep", options={"compact": True, "distance": 90, "word_spacing": 15, "arrow_spacing": 18})
                
                # --- 日本語化ロジック ---
                # 依存関係ラベルの日本語化
                for dep, label_jp in DEP_MAP.items():
                    svg = svg.replace(f'>{dep}</textPath>', f'>{label_jp}</textPath>')
                # 品詞タグの日本語化
                for pos, label_jp in POS_MAP.items():
                    svg = re.sub(rf'<tspan class="displacy-tag" dy="2em" fill="currentColor" x="[0-9.]+">{pos}</tspan>', 
                                 rf'<tspan class="displacy-tag" dy="2em" fill="currentColor" x="[0-9.]+">{label_jp}</tspan>', 
                                 svg)

                # Remove width, height, and style attributes from SVG for responsiveness
                svg = re.sub(r'\s(width|height|style)="[^"]*"', '', svg)
                
                # Wrap the SVG in a scrollable container with fixed height
                st.markdown(f'<div style="max-height: 400px; overflow: auto; border: 1px solid #eee; border-radius: 5px; padding: 10px;">{svg}</div>', unsafe_allow_html=True)

                # --- 提案：凡例の追加 ---
                st.markdown("---")
                st.markdown("**凡例：主な依存関係ラベルの意味**")
                legend_html = "<ul>"
                main_deps = [
                    "nsubj", "ROOT", "dobj", "iobj", "attr", "acomp", 
                    "det", "amod", "advmod", "prep", "pobj", "aux", "relcl", "conj"
                ]
                for dep in main_deps:
                    if dep in DEP_MAP:
                        legend_html += f"<li><b>{dep}:</b> {DEP_MAP[dep]}</li>"
                legend_html += "</ul>"
                st.markdown(legend_html, unsafe_allow_html=True)

            with tab5:
                st.header("実践と応用 - 文法と表現の『使いこなし』へ")
                st.markdown("文の態（能動態・受動態）を理解することは、表現の幅を広げる第一歩です。")
                st.info(f"例文: {doc.text}")
                st.markdown(f"### <span style=\"font-size: 1.2em;\">文の態: **{elements['voice']}**</span>", unsafe_allow_html=True)
                if elements['voice'] == "受動態":
                    st.markdown("💡 **解説:** この文は受動態です。主語が動作の『受け手』になっています。")
                    if elements.get('agent'):
                        st.markdown(f"**動作主:** {elements['agent'].text} (by句) - この動作を行ったのは {elements['agent'].text} ですね。")
                    else:
                        st.markdown("**動作主:** この文では動作主（by句）が明示されていません。")
                    st.markdown("**能動態への変換ヒント:**")
                    st.markdown("1. 動作主（by句）があれば、それを新しい主語にします。（例: `by the boy` → `The boy`）")
                    st.markdown("2. 元の主語を動詞の後に移動させます。（例: `The ball` → `... the ball`）")
                    st.markdown("3. 動詞を能動態の形に戻します。（例: `was kicked` → `kicked`）")
                    st.markdown("**例:** `The ball was kicked by the boy.` → `The boy kicked the ball.`")
                else:
                    st.markdown("💡 **解説:** この文は能動態です。主語が動作を『行う側』になっています。")
                    st.markdown("**受動態への変換ヒント:**")
                    st.markdown("1. 能動態の目的語を新しい主語にします。（例: `kicked the ball` → `The ball`）")
                    st.markdown("2. 動詞を `be動詞 + 過去分詞` の形にします。（例: `kicked` → `was kicked`）")
                    st.markdown("3. 元の主語を `by + 動作主` の形で動詞の後に移動させます。（例: `The boy` → `by the boy`）")
                    st.markdown("**例:** `The boy kicked the ball.` → `The boy kicked the ball.`")
            
        else:
            st.warning("この文の主語と動詞を特定できませんでした。よりシンプルな文でお試しください。")
            
    else:
        st.warning("英文を入力してください。")