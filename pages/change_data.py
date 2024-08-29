import docx.shared
import streamlit as st
import pandas as pd
import os
import docx
import re
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

# CSVファイルのパス
csv_path = "./pages/dict_words.csv"

def create_csv():
    if not os.path.exists(csv_path):
        # 初期データを持つ空のDataFrameを作成
        df = pd.DataFrame(columns=["name", "meaning"])
        df.to_csv(csv_path, index=False)

create_csv()

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
        if name not in st.session_state.word_list:
            st.session_state.word_list.append(name)

st.write("現在の用語リスト:", st.session_state.word_list)

# 3. 登録された単語でCSVに存在しないものを抽出する
complete_button = st.button("完了")
if complete_button:
    df = pd.read_csv(csv_path)
    st.session_state.new_words = []
    st.session_state.change_words = []

    for word in st.session_state.word_list:
        if word not in df['name'].values:
            st.session_state.new_words.append(word)
        else:
            st.session_state.change_words.append(word)

# 4. 存在しない単語の意味を手動で入力し、CSVに登録する
if st.session_state.new_words:
    st.write("### 1.5 以下の単語はデータベースに存在しません。意味を入力してください。")

    with st.form("meaning_form"):
        new_meaning = {}
        for word in st.session_state.new_words:
            meaning = st.text_area(f"{word} の意味を入力してください")
            new_meaning[word] = meaning
        
        submit_meaning = st.form_submit_button("登録")

        if submit_meaning:
            df = pd.read_csv(csv_path)  # ここでもdfを読み込む
            new_entries = []

            for word, meaning in new_meaning.items():
                if meaning.strip():  # 空の意味が入力されていないか確認
                    # 新しい行を追加
                    new_entries.append({"name": word, "meaning": meaning})
            
            if new_entries:
                new_df = pd.DataFrame(new_entries)
                df = pd.concat([df, new_df], ignore_index=True)  # concatを使用
                df.to_csv(csv_path, index=False)
                st.success("意味がデータベースに保存されました")

            # リセットする
            st.session_state.new_words = []

# 意味を変更する
if st.session_state.change_words:
    st.write("### 1.5 変更する用語の意味を入力してください。")
    df = pd.read_csv(csv_path)  # ここでもdfを読み込む
    with st.form("update_form"):
        new_meaning = {}
        for word in st.session_state.change_words:
            # 現在の意味を取得
            result = df[df['name'] == word]
            if not result.empty:
                meaning = st.text_area(f"{word} の意味を入力してください", value=result['meaning'].values[0])
            else:
                meaning = st.text_area(f"{word} の意味を入力してください")
            new_meaning[word] = meaning
        
        submit_meaning = st.form_submit_button("登録")

        if submit_meaning:
            for word, meaning in new_meaning.items():
                if meaning.strip():  # 空の意味が入力されていないか確認
                    # 更新処理
                    df.loc[df['name'] == word, 'meaning'] = meaning
            
            df.to_csv(csv_path, index=False)
            st.success("意味がデータベースに保存されました")

            # リセットする
            st.session_state.new_words = []
            st.session_state.change_words = []
