import docx.shared
import streamlit as st
import os
import docx
import re
import yaml
import pandas as pd
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



if "concat_list" not in st.session_state:  
    st.session_state.concat_list = []


concat_remove= st.button("結合リストを初期化する")
if concat_remove:
    st.session_state.concat_list = []




def create_csv():
    if not os.path.exists(csv_path):
        # 初期データを持つ空のDataFrameを作成
        df = pd.DataFrame(columns=["name", "meaning"])
        df.to_csv(csv_path, index=False)

create_csv()

st.write("# データベースに保存する用語集をアップロードしてください")
file = st.file_uploader("WORDをアップロードしてください", type="docx")

if file:
    document = docx.Document(file)
    lis = []
    for paragraph in document.paragraphs:
        if len(paragraph.text) >= 2 and any(char in paragraph.text for char in ":;：；"):
            text = "".join(paragraph.text.split())
            lis.append(text)

    # CSVファイルを読み込み
    df = pd.read_csv(csv_path)

    new_entries = []  # 新しいエントリを保持するリスト

    for word in lis:
        word = re.sub(r'^\d+ ', '', word)
        name, meaning = re.split("[:;：；]", word, maxsplit=1)
        st.session_state.concat_list.append(name)
        # 既存の単語を確認
        if name not in df['name'].values:
            # 新しいエントリをリストに追加
            new_entries.append({"name": name, "meaning": meaning})

    # 新しいエントリがある場合、DataFrameに追加
    if new_entries:
        new_df = pd.DataFrame(new_entries)
        df = pd.concat([df, new_df], ignore_index=True)

    # CSVファイルに保存
    df.to_csv(csv_path, index=False)
    st.success("データベースに登録しました")



