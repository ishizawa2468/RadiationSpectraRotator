import os
import shutil

import pandas as pd
import streamlit as st
from tqdm import tqdm

from app_utils import setting_handler
from app_utils.file_handler import FileHander
from modules.data_model.raw_spectrum_data import RawSpectrumData
from modules.file_format.spe_wrapper import SpeWrapper

# 共通の設定
setting_handler.set_common_setting()

# まず設定インスタンスを作成しておく。これを通してフォルダパスを読み込んだり保存したりする
setting = setting_handler.Setting()

st.title("Rotate SPE")

file_ext = '.spe'

# 回転させるファイルを選択
st.subheader("1. 調べるファイルを選択")
# FIXME: 関数化
path_to_original_files = setting.setting_json['read_path'] # 別ページで設定した読み込みpathを取得
# ファイルが得られるpathかどうか確認
try:
    files = os.listdir(path_to_original_files)
    if not any(file.endswith(file_ext) and not file.startswith('.') for file in files):
        st.write(f'有効なファイルが {path_to_original_files} にありません。')
        st.stop()
except Exception as e:
    st.subheader('Error: pathが正しく設定されていません。ファイルが存在するフォルダを指定してください。')
    st.subheader('現在の設定されているpath: {}'.format(path_to_original_files))
    st.stop() # 以降の処理をしない

# ファイルが見つかった場合
files.sort() # 見やすいようにソートしておく
filtered_files = [] # .speで終わるもののみを入れるリスト
for file in files:
    if file.endswith(file_ext) and not file.startswith('.'):
        filtered_files.append(file)
# 一通り終わったら、filesを置き換える
files = filtered_files
# 表示
st.table(FileHander.get_file_list_with_OD(path_to_original_files, files))
# 回転させるものを選択させる
selected_files = st.multiselect(
    label='回転させるファイルを選択',
    options=files,
    placeholder='Choose files',
)
st.write(selected_files)

st.subheader("2. 回転角度などを選択")

st.divider()
# sliderでdeg
rotate_deg = st.slider(
    "回転角度 (0.05°刻み、-1.0〜1.0まで)",
    min_value=-1.0,
    max_value=1.0,
    value=0.0,
    step=0.05
)
st.divider()

# 回転中心
rotate_option = st.selectbox(
    label='回転中心を選択',
    options=[
        'whole',
        'separate_half'
    ]
)

st.divider()
# さちったフレームを0にするかどうか
will_set_zero_with_saturation = st.checkbox(
    label='強度が飽和したフレームを0にする',
    value=True
)
if will_set_zero_with_saturation:
    saturation_threshold = st.slider(
        "飽和したと判断するしきい値 (これ以上の値があるframeを0にする)",
        min_value=60_000,
        max_value=65_535,
        value=65_000,
        step=1
    )
else:
    saturation_threshold = None

st.divider()
# すでに回転したことのあるファイルがある場合に上書きするかどうか
is_overwrite = st.checkbox(
    label='すでに同じ回転ファイルがある場合に、上書きする'
)
st.divider()


st.subheader('3. 確認して実行')
if len(selected_files) == 0:
    st.write('ファイルが選択されていません。')
    st.stop()

# オプションを確認
option_dict = {
    '回転角度': rotate_deg,
    '回転中心': rotate_option,
    '飽和しきい値': saturation_threshold,
    '上書き': is_overwrite
}
st.write(option_dict)

# 保存先を確認
path_to_save_files = setting.setting_json['save_path']
st.markdown(
    f"""
    ##### `{path_to_save_files}` に以下のファイルが生成されます。
    """
)
# 拡張子付きの新しいファイル名を生成
new_files_with_ext = FileHander.get_rotated_file_names(
    selected_files,
    rotate_deg,
    rotate_option,
    file_ext
)
# 表示
st.write(new_files_with_ext)

conduct_rotation = st.button(
    label='回転を実行する',
    icon='↪️',
    type='primary'
)
if conduct_rotation:
    for i, selected_file in tqdm(enumerate(selected_files)):
        path_to_original_file = os.path.join(path_to_original_files, selected_file)
        path_to_save_file = os.path.join(path_to_save_files, new_files_with_ext[i])
        st.write(f'{selected_file} -> {new_files_with_ext[i]}')
        print(f"{path_to_original_file}\n -> {path_to_save_file}") # log

        # コピー処理
        st.write(f'複製中...')
        print('コピー開始') # log
        shutil.copyfile(
            src=path_to_original_file,
            dst=path_to_save_file
        )
        print('コピー終了') # log

        # 回転処理
        st.write(f'回転中...')
        print('回転開始') # log
        RawSpectrumData.overwrite_spe_image(
            before_spe_path=path_to_original_file,
            after_spe_path=path_to_save_file,
            rotate_deg=rotate_deg,
            rotate_option=rotate_option
        )
        st.write('回転終了')
        print('回転終了') # log
    st.subheader('すべて完了!')
