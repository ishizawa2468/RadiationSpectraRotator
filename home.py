import streamlit as st

import app_utils.util as util

st.set_option('client.showSidebarNavigation', False) # デフォルトのサイドバー表示を一旦無効にする。自分でlabelをつけるため。
util.common_setting()

# 共通の表示
st.title("Welcome to SPE Rotator!")
st.markdown(
    """
    ### 【概要】
    - 露光データを持った`.spe`ファイルを複製して、露光データを回転させます。
    - 以下のようにページが分かれています。←から選択してください。
        1. Set folder **(必須)**: `.spe`があるフォルダを選ぶページ
        2. Search angle: 適切な回転角度を調べるページ
        3. Rotate SPE: 回転させるページ
    """
)

