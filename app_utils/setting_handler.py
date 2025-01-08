import streamlit as st

import os
import json

# それぞれのページで共通レイアウト・設定を作る
def set_common_setting():
    # 共通の設定
    st.set_page_config(
        page_title="SPE Rotater",
        layout="wide",
    )

    # 共通のサイドバー(ページリンク)
    st.set_option('client.showSidebarNavigation', False) # デフォルトのサイドバー表示を一旦無効にする。自分でlabelをつけるため。
    with st.sidebar:
        st.page_link("home.py", label="About app", icon="🏠")
        st.page_link("pages/set_folder.py", label="Set folder", icon="📂")
        st.page_link("pages/search_angle.py", label="Search angle", icon="📐")
        st.page_link("pages/rotate_spe.py", label="Rotate SPE", icon="↪️")

#
class Setting:
    # クラス固有の変数
    PATH_TO_JSON = 'app_utils/spe_rotator_setting.json'

    def __init__(self):
        self.setting_json = self._get_setting()

    # 設定jsonを読み込むメソッド
    def _get_setting(self) -> dict:
        try:
            with open(self.PATH_TO_JSON, 'r') as f:
                setting_json = json.load(f)
        except FileNotFoundError:
            print(f'File {self.PATH_TO_JSON} not found.')
            st.write(f"ファイル {self.PATH_TO_JSON}が見つかりません")
        return setting_json

    # 設定jsonを更新するメソッド
    def _update_setting(self, *, key, value):
        setting_json = self._get_setting() # 読み込み。エラー処理を書いてるのでこれを使う
        setting_json[key] = value  # 追加
        with open(self.PATH_TO_JSON, 'w') as f:  # 追加したものを書き込み
            json.dump(setting_json, f, ensure_ascii=False)
            print(f"{self.PATH_TO_JSON} の {key} に {value} が追加されました。")

    def update_read_spe_path(self, read_path):
        self._update_setting(key='read_path', value=read_path)

    def update_save_spe_path(self, save_path):
        self._update_setting(key='save_path', value=save_path)
