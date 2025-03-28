import os
import time
import numpy as np
import streamlit as st
from datetime import datetime

from app_utils import setting_handler
from modules.file_format.spe_wrapper import SpeWrapper
from modules.data_model.raw_spectrum_data import RawSpectrumData
from modules.radiation_fitter import RadiationFitter
from modules.figure_maker import FigureMaker
from log_util import logger


def configure_common_settings():
    """
    アプリ全体で必要となる共通設定を行う。
    """
    setting_handler.set_common_setting()


def get_setting_instance():
    """
    Settingインスタンスを生成して返す。
    """
    return setting_handler.Setting()


def display_title():
    """
    ページタイトルや最初の区切り線を表示する。
    """
    st.title("📐Search angle")
    logger.info("Search angle画面のロード開始")
    st.divider()


def retrieve_files_from_path(path_to_files):
    """
    指定パスからファイルリストを取得する。
    `.spe`ファイルが存在しない・またはパスが異常な場合は処理を停止する。
    """
    logger.debug(f'from setting json: path_to_files = {path_to_files}')
    try:
        files = os.listdir(path_to_files)
        # 有効なファイルがなければストップ
        if not any(file.endswith('.spe') and not file.startswith('.') for file in files):
            st.write(f'有効なファイルが {path_to_files} にありません。')
            logger.debug(f'有効なファイルが {path_to_files} にありません。')
            st.stop()
        files.sort()
        logger.debug('ファイル一覧の取得に成功')
        return files
    except Exception:
        st.subheader('Error: pathが正しく設定されていません。ファイルが存在するフォルダパスを指定してください。')
        st.subheader(f'現在の設定されているpath: {path_to_files}')
        logger.debug('ファイルが存在しないpathを読み込んだ')
        st.stop()


def display_file_selector(files):
    """
    ファイル選択UIを表示する。
    さらに「.spe拡張子のみを選択肢にする」チェックボックスでフィルタ機能を提供。
    ユーザーが選択したファイル名を返す。
    """
    st.subheader("1. 調べるファイルを選択")
    if st.checkbox('.spe拡張子のみを選択肢にする', value=True):
        filtered_files = [f for f in files if f.endswith('.spe') and not f.startswith('.')]
        files = filtered_files

    file_name = st.selectbox("ファイルを選択", files)
    return file_name


def create_spe_object(path_to_files, file_name):
    """
    選択されたファイルから SpeWrapper オブジェクトを生成し、
    それをもとに RawSpectrumData オブジェクトも作成して返す。
    spe ファイル以外が選択されたら処理を停止する。
    """
    if not file_name.endswith('.spe'):
        logger.info('ファイル拡張子が .spe でないため停止')
        st.warning('ファイル拡張子が `.spe` ではありません。')
        st.stop()

    logger.info('SPEオブジェクトの作成')
    path_to_spe = os.path.join(path_to_files, file_name)
    spe = SpeWrapper(path_to_spe)
    original_radiation = RawSpectrumData(spe)

    # メタデータを入れる辞書を用意
    metadata = {}
    try:
        spe.get_params_from_xml()  # spe ver.2 だとここでエラー
        # フィルター
        metadata['フィルター'] = spe.OD
        logger.debug('フィルター情報が辞書に格納された')
        # フレームレート
        metadata['Framerate (fps)'] = spe.framerate
        logger.debug('フレームレート情報が辞書に格納された')
        # 日時（取得日時）
        date_obj = datetime.fromisoformat(spe.date[:26] + spe.date[-6:])
        metadata['取得日時'] = date_obj.strftime("%Y年%m月%d日 %H時%M分%S秒")
        logger.debug('取得日時情報が辞書に格納された')
    except Exception as e:
        logger.error(f"メタデータ取得時のエラー: {e}")

    # 辞書に格納された情報を表示（例: JSON形式）
    if metadata:
        st.write("### 取得したメタデータ")
        st.json(metadata)
    else:
        st.write("メタデータが取得できませんでした。")
    return spe, original_radiation


def display_frame_selector(spe, original_radiation, file_name):
    """
    Frame 選択用 UI を表示し、選択された frame の画像を描画する。
    単一 frame の場合はスキップし、複数 frame の場合はスライダーで選択可能。
    選択された frame の露光データ (2D array) を返す。
    """
    st.divider()
    st.subheader("2. Frameを選択")

    if spe.num_frames == 1:
        frame = 0
        st.info('1 frameのみなのでスライダー操作はスキップ')
        logger.info("単一フレームなのでスライダーはなし")
    else:
        frame = st.slider(
            "Frame数",
            min_value=0,
            max_value=spe.num_frames - 1,
            value=0
        )
        logger.info(f"ユーザーが選択した Frame = {frame}")

        # 最大強度の時間配列を可視化
        all_max_I = original_radiation.get_max_intensity_arr()
        up_max_I, down_max_I = original_radiation.get_separated_max_intensity_arr()
        fig, ax = FigureMaker.get_max_I_figure(file_name, all_max_I, up_max_I, down_max_I)
        st.pyplot(fig)
        logger.debug("最大強度の時間配列を描画完了")

    # 現在のフレームの露光データを描画
    original_image = spe.get_frame_data(frame=frame)
    fig, ax = FigureMaker.get_exposure_image_figure(file_name, frame, original_image)
    st.pyplot(fig)
    logger.debug("選択フレームの露光イメージを描画完了")

    return frame, original_image


# --------------------------------------------------------------------------------
# ここから「回転・(最大値表示とfitting)」パートのメソッド分割
# --------------------------------------------------------------------------------

def display_rotation_ui():
    """
    回転角度や回転中心に関する入力UIを表示し、ユーザー選択値を返す。
    """
    st.divider()
    st.subheader("3. 回転角度を試す")
    st.info("ファイル、frameは上で調節してください。 ※元ファイルは変更されません。")

    rotate_deg = st.slider(
        "a. 回転角度 (0.05°刻み、-2.0〜2.0まで)",
        min_value=-2.0,
        max_value=2.0,
        value=0.0,
        step=0.05
    )
    rotate_option = st.selectbox(
        label='b. 回転中心を選択',
        options=['whole', 'separate_half']
    )
    logger.info(f"選択された回転条件: rotate_deg={rotate_deg}, rotate_option={rotate_option}")
    return rotate_deg, rotate_option


def rotate_image(original_radiation, frame, rotate_deg, rotate_option):
    """
    指定された frame に対し、rotate_deg / rotate_option で回転を行い、
    回転後の画像（2D array）を返す。
    """
    rotated_image = original_radiation.get_rotated_image(
        frame=frame,
        rotate_deg=rotate_deg,
        rotate_option=rotate_option
    )
    logger.debug("回転処理が完了")
    return rotated_image


def display_threshold_slider(all_max_I):
    """
    閾値スライダーを表示し、ユーザーが選択した値を返す。
    """
    threshold = st.slider(
        "c. 中心位置を調べる際の、スペクトルの最大強度の下限",
        min_value=0,
        max_value=int(round(all_max_I.max())),
    )
    logger.info(f"最大強度に対する閾値(threshold) = {threshold}")
    return threshold


def display_max_pixel_positions(
        file_name,
        original_image, rotated_image,
        frame, rotate_deg, threshold,
        fitted_positions
):
    """
    最大値ピクセルをオーバーレイした図を作成して表示する。
    """
    st.divider()
    st.subheader("最大値波長ピクセルを表示")

    # 設定値を表示する
    st.write({
        "ファイル名": file_name,
        "Frame": frame,
        "回転角度": rotate_deg,
        "強度しきい値": threshold
    })

    max_wavelength_pixels = np.argmax(rotated_image, axis=1)

    # 露光イメージの描画
    fig, ax = FigureMaker.get_exposure_image_figure(file_name, frame, original_image)

    # fitted_positions に対応する行だけオーバーレイ
    ax = FigureMaker.overlap_by_center_positions(
        ax=ax,
        wavelength_pixels=max_wavelength_pixels[fitted_positions],
        center_pixels=fitted_positions,
        color='red'
    )
    ax.set_title(f"Max pixel\nRotated = {rotate_deg} deg / Frame = {frame}")
    st.pyplot(fig)
    logger.debug("最大値ピクセルを重ね書きした図を表示完了")


def fitting_and_display_center(
        rotated_image,
        file_name,
        frame,
        original_image,
        fitted_positions,
        rotate_deg
):
    """
    fitted_positions に対して非対称ガウスでフィッティングを行い、
    中心ピクセルを図上にオーバーレイして可視化する。
    """
    st.divider()
    st.subheader("fitting中心波長ピクセルを表示")

    x_data = np.arange(rotated_image.shape[1])
    fitted_center = []

    logger.info("Fitting開始")
    fitting_start = time.time()

    for position in fitted_positions:
        y_data = rotated_image[position]
        result = RadiationFitter.fit_by_asymmetric_gaussian(x_data, y_data)
        try:
            fitted_center.append(result["parameters"]["mu"])
        except Exception as e:
            logger.error(f"Fittingに失敗: position={position}, error={repr(e)}")
            st.subheader(f"Fittingに失敗しました。\n{repr(e)}")
            st.stop()

    elapsed = time.time() - fitting_start
    logger.info(f"Fitting完了 (処理時間: {elapsed:.4f}秒)")

    # fitted_center を重ね書き
    fig, ax = FigureMaker.get_exposure_image_figure(file_name, frame, original_image)
    ax = FigureMaker.overlap_by_center_positions(
        ax=ax,
        wavelength_pixels=fitted_center,
        center_pixels=fitted_positions,
        color='lightgreen'
    )
    ax.set_title(f"Fitted center by skew gaussian\nRotated = {rotate_deg} deg / Frame = {frame}")
    st.pyplot(fig)
    logger.debug("fitting中心を重ね書きした図の表示完了")
    st.success("表示完了")


def display_rotated_image(frame, original_radiation, original_image, file_name):
    """
    回転角度の試行、最大値ピクセル表示、そして「ボタン押下でfitting実行」のフローをまとめる。
    """
    # --- Step 1: 回転パラメータ入力と画像の回転 ---
    rotate_deg, rotate_option = display_rotation_ui()
    rotated_image = rotate_image(original_radiation, frame, rotate_deg, rotate_option)

    # --- Step 2: 閾値設定 → fitting対象行の抽出 ---
    all_max_I = original_radiation.get_max_intensity_arr()
    threshold = display_threshold_slider(all_max_I)
    are_fitted_positions = rotated_image.max(axis=1) > threshold
    fitted_positions = np.where(are_fitted_positions)[0]
    logger.debug(f"Fitting対象の行数: {len(fitted_positions)}")

    # --- Step 3: 最大値ピクセル位置の可視化 ---
    display_max_pixel_positions(file_name, original_image, rotated_image, frame, rotate_deg, threshold, fitted_positions)

    # --- Step 4: 「fittingを実行」ボタン ---
    # 押されたときだけFitting処理を実施
    st.divider()
    st.subheader("ひずみガウス関数で滑らかな中心位置を表示")
    if st.button("Fittingを実行"):
        st.success("Fittingを開始しました")
        fitting_and_display_center(rotated_image, file_name, frame, original_image, fitted_positions, rotate_deg)
    else:
        st.info("ボタンを押すとfittingを開始します。")


# --------------------------------------------------------------------------------
# メイン処理
# --------------------------------------------------------------------------------
# 1. 共通設定
configure_common_settings()

# 2. タイトル表示
display_title()

# 3. Set Folderで設定したフォルダパスの取得
setting = get_setting_instance()
path_to_files = setting.setting_json['read_path']

# 4. ファイルリスト取得 & ファイル選択
files = retrieve_files_from_path(path_to_files)
file_name = display_file_selector(files)

# 5. SPEオブジェクト生成
spe, original_radiation = create_spe_object(path_to_files, file_name)

# 6. Frame 選択
frame, original_image = display_frame_selector(spe, original_radiation, file_name)

# 7. 回転角度 (最大値ピクセル描画 & fitting実行ボタン)
display_rotated_image(frame, original_radiation, original_image, file_name)
