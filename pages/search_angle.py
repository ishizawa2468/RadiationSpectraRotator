import sys
import time

import streamlit as st

import numpy as np
from scipy.ndimage import rotate

import os
from datetime import datetime

from app_utils import setting_handler
from modules.file_format.spe_wrapper import SpeWrapper
from modules.data_model.raw_spectrum_data import RawSpectrumData
from modules.radiation_fitter import RadiationFitter
from modules.figure_maker import FigureMaker

# 共通の設定
setting_handler.set_common_setting()
# まず設定インスタンスを作成しておく。これを通してフォルダパスを読み込んだり保存したりする
setting = setting_handler.Setting()

st.title("📐Search angle")
st.divider()

# 調査するファイルを選択
st.subheader("1. 調べるファイルを選択")
path_to_files = setting.setting_json['read_path'] # 別ページで設定した読み込みpathを取得
# ファイルが得られるpathかどうか確認
try:
    files = os.listdir(path_to_files)
    if not any(file.endswith('.spe') and not file.startswith('.') for file in files):
        st.write(f'有効なファイルが {path_to_files} にありません。')
        st.stop()
except Exception as e:
    st.subheader('Error: pathが正しく設定されていません。ファイルが存在するフォルダを指定してください。')
    st.subheader('現在の設定されているpath: {}'.format(path_to_files))
    st.stop() # 以降の処理をしない

# ファイルが見つかった場合
files.sort() # 見やすいようにソートしておく
if st.checkbox('.spe拡張子のみを選択肢にする', value=True):
    filtered_files = [] # .speで終わるもののみを入れるリスト
    for file in files:
        if file.endswith('.spe') and not file.startswith('.'):
            filtered_files.append(file)
    # 一通り終わったら、filesを置き換える
    files = filtered_files
file_name = st.selectbox("ファイルを選択", files)

# もしspeファイルが選択されたらファイル情報を表示し、そうでなければ描画を終了する
if file_name.endswith('.spe'):
    # speファイルオブジェクトを作成する
    path_to_spe = os.path.join(path_to_files, file_name)
    spe = SpeWrapper(path_to_spe)
    # radiationにもしておく
    original_radiation = RawSpectrumData(spe)
    try:
        # おそらくspe ver.3 以上でないとできない。あと設定されていないと取得できない。
        spe.get_params_from_xml()
        # メタ情報を表示
        # FIXME: 辞書にして表示で揃える
        st.write(f'フィルター: {spe.OD}')
        st.write(f'Framerate: {spe.framerate} fps')
        # HACK: chatgpt -> Pythonのdatetime.fromisoformatは標準のISO 8601形式に従い、ミリ秒部分は最大6桁までしか対応していません。
        date_obj = datetime.fromisoformat(spe.date[:26]+spe.date[-6:])
        calibration_date_obj = datetime.fromisoformat(spe.calibration_date[:26]+spe.calibration_date[-6:])
        st.write(f'取得日時: {date_obj.strftime("%Y年%m月%d日 %H時%M分%S秒")}')

        # あまり意味ないので表示してない
        # spe_settings = spe.retrieve_all_experiment_settings()
        # for spe_setting in spe_settings:
        #     st.write(spe_setting.setting_name, spe_setting.setting_value)

    except Exception as e:
        print(e)
else:
    st.stop()

st.divider()

st.subheader("2. Frameを選択")
if spe.num_frames == 1:
    frame = 0
    st.write('1 frameのみなのでskip')
else:
    # スライダーでframeを選択できるようにする
    frame = st.slider(
        "Frame数",
        0,  # スライダーの最小値
        spe.num_frames - 1,  # スライダーの最大値
    )
    # 最大強度の時間配列を取得する
    all_max_I = original_radiation.get_max_intensity_arr()
    up_max_I, down_max_I = original_radiation.get_separated_max_intensity_arr()
    # 図を作る
    fig, ax = FigureMaker.get_max_I_figure(
        file_name,
        all_max_I,
        up_max_I,
        down_max_I
    )
    st.pyplot(fig)

original_image = spe.get_frame_data(frame=frame) # スライダーframeの露光データを取得

# frameにおける露光データを描画
fig, ax = FigureMaker.get_exposure_image_figure(
    file_name,
    frame,
    original_image,
)
st.pyplot(fig)

st.divider()

st.subheader("3. 回転角度を試す")
# 回転中心をどこに置くかで分岐。これは選択できるようにする
st.write("ファイル、frameは上で調節してください。")
st.write("※元ファイルは変更されません。")

rotate_deg = st.slider(
    "回転角度 (0.05°刻み、-1.0〜1.0まで)",
    min_value=-1.0,
    max_value=1.0,
    value=0.0,
    step=0.05
)
rotate_option = st.selectbox(
    label='回転中心を選択',
    options=[
        'whole',
        'separate_half'
    ]
)
# 角度とoptionに基づいて回転させる
rotated_image = original_radiation.get_rotated_image(
    frame=frame,
    rotate_deg=rotate_deg,
    rotate_option=rotate_option
)

threshold = st.slider(
    "中心位置を調べる際の、スペクトルの最大強度の下限",
    0,  # スライダーの最小値
    round(all_max_I.max()),  # スライダーの最大値
)
# fittingするべきpositionを絞る
are_fitted_positions = rotated_image.max(axis=1) > threshold # boolean配列ができる
fitted_positions = np.where(are_fitted_positions)[0] # trueのframe数を格納した配列

st.divider()
st.subheader("最大値波長ピクセルを表示")
# 位置ピクセルごとの最大波長ピクセルを計算
max_wavelength_pixels = np.argmax(rotated_image, axis=1)  # 各行の最大値のインデックス
# まず露光イメージ作成
fig, ax = FigureMaker.get_exposure_image_figure(
    file_name,
    frame,
    original_image,
)
# 露光イメージの上に点を打つ
ax = FigureMaker.overlap_by_center_positions(
    ax=ax,
    wavelength_pixels=max_wavelength_pixels[fitted_positions],
    center_pixels=fitted_positions,
    color='red'
)
# titleも上書き
ax.set_title(f"Max pixel\nRotated = {rotate_deg} deg / Frame = {frame}")
st.pyplot(fig)

st.divider()
st.subheader("fitting中心波長ピクセルを表示")
# fittingして中心位置を取得
fitted_result = [] # デバッグのときとかに使う
fitted_center = [] # plotに使うのはこれだけ
x_data = np.arange(rotated_image.shape[1])
fitting_start = time.time()
for position in fitted_positions:
    y_data = rotated_image[position]
    result = RadiationFitter.fit_by_asymmetric_gaussian(x_data, y_data)
    fitted_result.append(result)
    try:
        fitted_center.append(result["parameters"]["mu"])
    except Exception as e:
        st.subheader(f"Fittingに失敗しました。\n{repr(e)}")
        st.stop()

# まず露光イメージ作成
fig, ax = FigureMaker.get_exposure_image_figure(
    file_name,
    frame,
    original_image,
)
# 露光イメージの上に点を打つ
ax = FigureMaker.overlap_by_center_positions(
    ax=ax,
    wavelength_pixels=fitted_center,
    center_pixels=fitted_positions,
    color='lightgreen'
)
# titleも上書き
ax.set_title(f"Fitted center by skew gaussian\nRotated = {rotate_deg} deg / Frame = {frame}")
st.pyplot(fig)
