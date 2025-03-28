import os
import streamlit as st

import app_utils.setting_handler as setting_handler
from app_utils.file_handler import FileHander
from log_util import logger


def display_read_path_setting(setting: setting_handler.Setting):
    """
    読み込みフォルダ設定の入力画面を表示し、ユーザー操作を受け付ける。
    """
    st.title("📂Set folder")
    logger.info('Set Folder画面のロード開始')

    st.divider()

    st.subheader("読み込み先フォルダの設定")
    st.markdown(
        """
        - ここで設定した **フォルダ** から `.spe` ファイルを取得できます
        - オリジナルのファイルは読み込むのみで変更されません。回転後のファイルは新しく作られます
        """
    )

    read_path = st.text_input(
        label='`.spe`があるフォルダまでのfull path',
        value=setting.setting_json['read_path']
    )

    if st.button('読み込み先を更新', type='primary'):
        setting.update_read_spe_path(read_path)
        logger.info(f'読み込み先を更新: {read_path}')


def get_spe_files(setting: setting_handler.Setting):
    """
    Setting オブジェクトから読み込み先フォルダを取得し、
    該当フォルダ内の .spe ファイルリストを返す。
    """
    # オブジェクトを作り直して最新設定を読み込む
    setting = setting_handler.Setting()
    path_to_files = setting.setting_json['read_path']

    try:
        files = os.listdir(path_to_files)
        # 拡張子が .spe のもののみ抽出
        filtered_files = [
            f for f in files
            if f.endswith('.spe') and not f.startswith('.')
        ]

        if not filtered_files:
            st.write(f'有効なファイルが {path_to_files} にありません。')
            logger.info('ファイルが無いパスが設定された')
            st.stop()  # 以降の処理を中断

        # ファイルを整形して返す
        filtered_files.sort()
        return filtered_files, path_to_files

    except Exception:
        st.subheader('Error: pathが正しく設定されていません。ファイルが存在するフォルダを指定してください。')
        st.subheader(f'現在の設定されているpath: {path_to_files}')
        logger.info('存在しないパスが設定された')
        st.stop()  # 以降の処理を中断


def display_spe_files_table(files, path_to_files):
    """
    speファイルのリストをテーブル表示する。
    ODごとに仕分けし、テーブルを出力。
    """
    logger.info('ファイルが見つかった')

    # ODごとに分けるため、先にDataFrame状に整形
    spe_display_data = FileHander.get_file_list_with_OD(path_to_files, files)

    # ODごとに表示
    for od in set(spe_display_data['OD']):
        st.table(spe_display_data[spe_display_data['OD'] == od])


def display_save_path_setting(setting):
    """
    保存先フォルダ設定の入力画面を表示し、ユーザー操作を受け付ける。
    """
    st.divider()

    st.subheader("保存先フォルダの設定")
    st.write("- ここで設定したフォルダに回転された`.spe`ファイルが保存されます。")

    save_path = st.text_input(
        label='保存フォルダまでのfull path',
        value=setting.setting_json['save_path']
    )

    if st.button('保存先を更新', type='primary'):
        # 保存先パスの存在確認
        if not os.path.isdir(save_path):
            st.error(f"このパスはフォルダとして有効ではありません: {save_path}")
            logger.error(f"このパスはフォルダとして有効ではありません: {save_path}")
            st.stop()
        # 有効なので保存
        setting.update_save_spe_path(save_path)
        st.success('')
        logger.info(f'保存先を更新: {save_path}')


# メイン処理
# 1. 共通設定
setting_handler.set_common_setting()

# 2. 読み込み先フォルダ設定の入力・更新
setting = setting_handler.Setting() # settingの読み込み
display_read_path_setting(setting)

# 3. speファイルリスト取得
setting = setting_handler.Setting()
files, path_to_files = get_spe_files(setting)

# 4. speファイルテーブル表示
display_spe_files_table(files, path_to_files)

# 5. 保存先フォルダ設定の入力・更新
setting = setting_handler.Setting()
display_save_path_setting(setting)
