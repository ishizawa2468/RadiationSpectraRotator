import os

import streamlit as st

import app_utils.setting_handler as setting_handler
from app_utils.file_handler import FileHander
from log_util import logger

# 共通の設定
setting_handler.set_common_setting()

# ファイル選択をする画面
# まず設定インスタンスを作成しておく。これを通してフォルダパスを読み込んだり保存したりする
setting = setting_handler.Setting()

# ここから画面と操作
st.title("📂Set folder")
logger.info('Set Folder画面')

st.divider()

st.subheader("読み込み先フォルダの設定")
st.markdown(
    """
    - ここで設定した **フォルダ** から`.spe`ファイルを取得できます
    - オリジナルのファイルは読み込むのみで変更されません。回転後のファイルは新しく作られます
    """
)
read_path = st.text_input(label='`.spe`があるフォルダまでのfull path', value=setting.setting_json['read_path'])
if st.button('読み込み先を更新', type='primary'):
    setting.update_read_spe_path(read_path)
    logger.info(f'読み込み先を更新: {read_path}')

st.subheader("見つかったFiles")
setting = setting_handler.Setting() # オブジェクトを作り直して読み込み直す
path_to_files = setting.setting_json['read_path'] # 別ページで設定した読み込みpathを取得
# ファイルが得られるpathかどうか確認
try:
    files = os.listdir(path_to_files)
    if not any(file.endswith('.spe') and not file.startswith('.') for file in files):
        st.write(f'有効なファイルが {path_to_files} にありません。')
        logger.info('ファイルが無いパスが設定された')
        st.stop()
except Exception as e:
    st.subheader('Error: pathが正しく設定されていません。ファイルが存在するフォルダを指定してください。')
    st.subheader('現在の設定されているpath: {}'.format(path_to_files))
    logger.info('存在しないパスが設定された')
    st.stop() # 以降の処理をしない

# ファイルが見つかった場合
logger.info('ファイルが見つかった')
files.sort() # 見やすいようにソートしておく
filtered_files = [] # .speで終わるもののみを入れるリスト
for file in files:
    if file.endswith('.spe') and not file.startswith('.'):
        filtered_files.append(file)
# 一通り終わったら、filesを置き換える
files = filtered_files
# ODごとに表示
spe_display_data = FileHander.get_file_list_with_OD(path_to_files, files)
for od in (set(spe_display_data['OD'])):
    st.table(spe_display_data[spe_display_data['OD'] == od])


st.divider()

st.subheader("保存先フォルダの設定")
st.write("- ここで設定したフォルダに回転された`.spe`ファイルが保存されます。")
save_path = st.text_input(label='保存フォルダまでのfull path', value=setting.setting_json['save_path'])
if st.button('保存先を更新', type='primary'):
    setting.update_save_spe_path(save_path)
