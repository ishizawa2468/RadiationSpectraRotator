import streamlit as st

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

import os
from datetime import datetime

import app_utils.util as util
# import Spe

# 共通の設定
util.common_setting()
# セッションに保存するもの（リロードでクリア、それ以外の画面操作で使い回される）

# まず設定インスタンスを作成しておく。これを通してフォルダパスを読み込んだり保存したりする
setting = util.Setting()

st.title("📐Search angle")

st.divider()

# 調査するファイルを選択
st.subheader("1. 調べるファイルを選択")
path_to_files = setting.json['read_path'] # 別ページで設定した読み込みpathを取得
files = os.listdir(path_to_files)
files.sort() # 見やすいようにソートしておく
if st.checkbox('.spe拡張子のみを選択肢にする', value=True):
    filtered_files = [] # .speで終わるもののみを入れるリスト
    for file in files:
        if file.endswith('.spe'):
            filtered_files.append(file)
    # 一通り終わったら、filesを置き換える
    files = filtered_files
file_name = st.selectbox("ファイルを選択", files)

# もしspeファイルが選択されたらファイル情報を表示し、そうでなければ描画を終了する
if file_name.endswith('.spe'):
    # speファイルオブジェクトを作成する
    path_to_spe = os.path.join(path_to_files, file_name)
    spe = SpeWrapper(path_to_spe)  # NOTE: 勝手に作ったラッパークラスを使ってる。人によって使いづらいかも
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
    except Exception as e:
        print(e)
else:
    st.stop()

st.divider()


st.subheader("2. Frameを選択")

# 目安として各フレームの露光強度最大値配列を取得して描画する
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(spe.get_max_intensity())
ax.grid(linestyle='--')
ax.set_title('Max Intensity')
ax.set_xlabel('Frame')
ax.set_ylabel('Intensity')
st.pyplot(fig)

# スライダーでframeを選択できるようにする
frame = st.slider(
    "Frame数",
    1,  # スライダーの最小値
    spe.num_frames,  # スライダーの最大値
) - 1 # GUIでは1始まりにして、処理では0始まりにしているため

original_image = spe.get_one_data_df(frame=frame) # スライダーframeの露光データを取得

# frameにおける露光データを描画
fig, ax = plt.subplots(dpi=300)
im = ax.imshow(original_image, cmap='jet') # colorbarを作るために返り値を保存しておく
fig.colorbar(im, ax=ax)
ax.set_title(f'Original / Frame = {frame+1}')
ax.set_xlabel('Wavelength (pixel)')
ax.set_ylabel('Position (pixel)')
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

rotated_image = rotate(original_image, rotate_deg, reshape=False)
# 位置ピクセルごとの最大波長ピクセルを計算
max_wavelength_pixels = np.argmax(rotated_image, axis=1)  # 各行の最大値のインデックス
position_pixels = np.arange(rotated_image.shape[0])      # 位置ピクセル
# TODO: fittingして中心位置を取得

fig, ax = plt.subplots(dpi=300)
im = ax.imshow( # colorbarを作るために返り値を保存しておく
    rotated_image,
    cmap='gray'
)
fig.colorbar(im, ax=ax)
ax.set_title(f'Rotated / Frame = {frame+1}')
ax.scatter(max_wavelength_pixels, position_pixels, color='red', s=2, marker='+')
ax.set_xlabel('Wavelength (pixel)')
ax.set_ylabel('Position (pixel)')
st.pyplot(fig)
