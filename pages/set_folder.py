import streamlit as st

import app_utils.setting_handler as setting_handler

# 共通の設定
setting_handler.set_common_setting()

# ファイル選択をする画面
# まず設定インスタンスを作成しておく。これを通してフォルダパスを読み込んだり保存したりする
setting = setting_handler.Setting()

# ここから画面と操作
st.title("📂Set folder")

st.divider()

st.subheader("読み込むフォルダ")
st.markdown(
    """
    - ここで設定したフォルダから`.spe`ファイルを選択できます。
        - Macの場合、Finderでフォルダを選択して `option + command + c`
        - Windowsの場合、エクスプローラーでフォルダを選択して `shift + control + c`
    - オリジナルのファイルは読み込むのみで変更されません。回転後のファイルは新しく作られます。
    """
)
read_path = st.text_input(label='オリジナルの`.spe`があるフォルダまでのfull path', value=setting.setting_json['read_path'])
if st.button('読み込み先を更新'):
    setting.update_read_spe_path(read_path)

st.divider()

st.subheader("保存先フォルダ")
st.write("- ここで設定したフォルダに回転された`.spe`ファイルが保存されます。")
save_path = st.text_input(label='保存フォルダまでのfull path', value=setting.setting_json['save_path'])
if st.button('保存先を更新'):
    setting.update_save_spe_path(save_path)
