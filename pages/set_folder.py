import streamlit as st

import app_utils.util as util

# 共通の設定
util.common_setting()

# ファイル選択をする画面
# まず設定インスタンスを作成しておく。これを通してフォルダパスを読み込んだり保存したりする
setting = util.Setting()

# ここから画面と操作
st.title("📂Set folder")

st.divider()

st.subheader("読み込むフォルダ")
st.write("※ここで設定したフォルダから`.spe`ファイルを選択できます。")
st.write("※オリジナルのファイルは読み込むのみで変更しません。回転後のファイルは新しく作られます。")
read_path = st.text_input(label='オリジナルの`.spe`があるフォルダまでのfull path', value=setting.json['read_path'])
if st.button('読み込み先を更新'):
    setting.update_read_spe_path(read_path)

st.divider()

st.subheader("保存先フォルダ")
st.write("※ここで設定したフォルダに、回転した`.spe`ファイルを作成します。")
save_path = st.text_input(label='保存フォルダまでのfull path', value=setting.json['save_path'])
if st.button('保存先を更新'):
    setting.update_save_spe_path(save_path)
