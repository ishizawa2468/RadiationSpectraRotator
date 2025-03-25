import streamlit as st

import app_utils.setting_handler as setting_handler

from log_util import logger

# サイドバーを隠す処理
def hide_sidebar():
    # 初回実行を判定するためのフラグを session_state に用意
    if "sidebar_navigation_disabled" not in st.session_state:
        st.session_state.sidebar_navigation_disabled = False  # まだ無効化していない状態

    # もし無効化していないなら、オプションを False に書き換えて rerun する
    if st.session_state.sidebar_navigation_disabled is False:
        st.set_option('client.showSidebarNavigation', False) # デフォルトのサイドバー表示を一旦無効にする。自分でlabelをつけるため。
        st.session_state.sidebar_navigation_disabled = True  # これ以上変更しないようフラグを更新
        st.rerun()

hide_sidebar()
setting_handler.set_common_setting()

logger.info('Homeを表示')

# 共通の表示
st.title("Welcome to SPE Rotator!")
st.markdown(
    """
    ### 【概要】
    - 露光データを持った`.spe`ファイルを複製して、露光データを回転させます。
        - 説明・使い方はこちら → [README](https://github.com/ishizawa2468/RadiationSpectraRotator?tab=readme-ov-file#radiation-spectra-rotator)
    - 以下のようにページが分かれています。←から選択してください。
        1. **(必須)** Set folder: `.spe`があるフォルダを選ぶページ
        2. Search angle: 適切な回転角度を調べるページ
        3. Rotate SPE: 回転させるページ
    """
)

