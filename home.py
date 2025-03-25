import streamlit as st

import app_utils.setting_handler as setting_handler

st.set_option('client.showSidebarNavigation', False) # デフォルトのサイドバー表示を一旦無効にする。自分でlabelをつけるため。
setting_handler.set_common_setting()

print('log: Homeを表示')

# 共通の表示
st.title("Welcome to SPE Rotator!")
st.markdown(
    """
    ### 【概要】
    - 露光データを持った`.spe`ファイルを複製して、露光データを回転させます。
        - 詳細はこちら → [Github]()
    - 以下のようにページが分かれています。←から選択してください。
        1. **(必須)** Set folder: `.spe`があるフォルダを選ぶページ
        2. Search angle: 適切な回転角度を調べるページ
        3. Rotate SPE: 回転させるページ
    """
)

