import docx.shared
import streamlit as st
import sqlite3
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

db_path = "./pages/words.db"

def create_database():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE dict_words (
                word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name STRING UNIQUE,
                meaning TEXT
            );
        """)
        conn.commit()
        conn.close()

create_database()





st.write("# データベースに保存する用語集をアップロードしてください")
file = st.file_uploader("WORDをアップロードしてください", type="docx")


if file:
    document = docx.Document(file)
    lis = []
    for  paragraph in document.paragraphs:
        if len(paragraph.text) >= 2 and any(char in paragraph.text for char in ":;：；") :
            text = "".join(paragraph.text.split())
            lis.append(text)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for word in lis:
        name, meaning = re.split("[:;：；]",word, maxsplit=1)
        cur.execute("SELECT name FROM dict_words WHERE name=?", (name,))
        if not cur.fetchone():
            cur.execute("INSERT INTO dict_words (name, meaning) VALUES (?, ?)", (name, meaning))
    
    conn.commit()
    conn.close()

    st.success("データベースに登録しました")

