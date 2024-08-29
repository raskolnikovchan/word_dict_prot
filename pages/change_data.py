import streamlit as st
import sqlite3
import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# ユーザー設定読み込み
current_dir = os.getcwd()
yaml_path = os.path.join(current_dir, "config.yaml")

with open(yaml_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days'],
)

# 認証チェック
if not st.session_state.get("authentication_status"):
    st.warning('Please log in to access this page.')
    st.stop()

# ログイン成功
st.write("Profile Page Content")

# データベースのパス

db_path = "D:/UDEMYPython/用語集アプリ/word/words.db" 
# セッションステートの初期化

if "word_list" not in st.session_state:
    st.session_state.word_list = []

if "new_words" not in st.session_state:
    st.session_state.new_words = []

if "change_words" not in st.session_state:
    st.session_state.change_words = []



st.write("最初にリストを削除してください")
delete_button = st.button("削除")

if delete_button:
    st.session_state.word_list = []
    st.session_state.new_words = []
    st.session_state.change_words = []

# 2. 単語を次々と登録していく
st.title("単語の意味を変更する")
st.write("## 1 単語を入力してください")

with st.form("word_form", clear_on_submit=True):
    name = st.text_input("用語名")
    add_button = st.form_submit_button("追加")

    if add_button and name:
        if name in st.session_state.word_list:
            pass
        else:
            st.session_state.word_list.append(name)

st.write("現在の用語リスト:", st.session_state.word_list)

# 3. 登録された単語でデータベースに存在しないものを抽出する
complete_button = st.button("完了")
if complete_button:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    st.session_state.new_words = []
    st.session_state.change_words = []

    for word in st.session_state.word_list:
        cur.execute("SELECT name FROM dict_words WHERE name=?", (word,))
        if not cur.fetchone():
            st.session_state.new_words.append(word)
        else:
            st.session_state.change_words.append(word)

    conn.close()

# 4. 存在しない単語の意味を手動で入力し、データベースに登録する
if st.session_state.new_words:
    st.write("### 1.5 以下の単語はデータベースに存在しません。意味を入力してください。")

    with st.form("meaning_form"):
        new_meaning = {}
        for word in st.session_state.new_words:
            meaning = st.text_area(f"{word} の意味を入力してください")
            new_meaning[word] = meaning
        
        submit_meaning = st.form_submit_button("登録")

        if submit_meaning:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            for word, meaning in new_meaning.items():
                if meaning.strip():  # 空の意味が入力されていないか確認
                    cur.execute("INSERT INTO dict_words (name, meaning) VALUES (?, ?)", (word, meaning))
            
            conn.commit()
            conn.close()
            st.success("意味がデータベースに保存されました")

            # リセットする
            st.session_state.new_words = []


#意味を変更する。
if st.session_state.change_words:
    st.write("### 1.5 変更する用語の意味を入力してください。")
    with st.form("update_form"):
        new_meaning = {}
        for word in st.session_state.change_words:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT meaning FROM dict_words WHERE name = ?", (word,))
            result = cur.fetchone()
            conn.close()
            if result is not None:
                meaning = st.text_area(f"{word} の意味を入力してください", value=result[0])
            else:
                meaning = st.text_area(f"{word} の意味を入力してください")
            new_meaning[word] = meaning
        
        submit_meaning = st.form_submit_button("登録")

        if submit_meaning:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            for word, meaning in new_meaning.items():
                if meaning.strip():  # 空の意味が入力されていないか確認
                    cur.execute("UPDATE dict_words SET meaning = ? WHERE name = ?",(meaning, word))
            
            conn.commit()
            conn.close()
            st.success("意味がデータベースに保存されました")

            # リセットする
            st.session_state.new_words = []
            st.session_state.change_words = []













# from pathlib import Path

# # 現在のスクリプトが存在するディレクトリのパスを取得
# base_dir = Path(__file__).resolve().parent

# # データベースへの相対パスを解決
# db_path = base_dir.parent / 'word' / 'words.db'

# # デバッグ: 解決されたパスを出力
# print(f"Resolved database path: {db_path}")

# # データベースにアクセス
# import sqlite3
# conn = sqlite3.connect(db_path)

