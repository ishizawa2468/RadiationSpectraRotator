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
    - ソフトウェアの前提
        - 最初の開発者はBL10XU(2022後期-2024前期)での実験データだけを取り扱ったことがあります。
        - ROIは設定したことがありません。
    - 以下のことも前提にしています。
        - 回転はフィルターのtiltによるもので、それを回転によって補正している。色収差は考えない。
        - 光学系は半年に一回調整される。またフィルターによってtiltが異なる。
            - そのため、回転角度は基本的に(半期, ODの種類)が異なるものを調べればよい。
            - ex. (2023A, OD5)では適切な角度は1つで、(2023A, OD6)や(2023B, OD5)とは異なる可能性がある。
    - 以下のようにページが分かれています。←から選択してください。
        1. **(必須)** Set folder: `.spe`があるフォルダを選ぶページ
        2. Search angle: 適切な回転角度を調べるページ
        3. Rotate SPE: 回転させるページ
    """
)

