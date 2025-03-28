import os
import shutil
import streamlit as st

from app_utils import setting_handler
from app_utils.file_handler import FileHander
from modules.data_model.raw_spectrum_data import RawSpectrumData
from log_util import logger


def configure_common_settings():
    """
    アプリ全体で必要となる共通設定を行う。
    """
    setting_handler.set_common_setting()


def get_setting_instance():
    """
    設定を管理する Setting インスタンスを生成して返す。
    """
    return setting_handler.Setting()


def display_title():
    """
    ページタイトルとログを表示する。
    """
    st.title("Rotate SPE")
    logger.info('Rotate SPE画面のロード開始')
    st.info('このページでは元ファイルを複製し、複製したファイルのデータを書き換えます', icon='💡')
    st.divider()


def retrieve_valid_files(path_to_files, file_ext='.spe'):
    """
    指定パスから拡張子 file_ext のファイル一覧を取得し、ソートして返す。
    存在しなければエラーを表示し、処理を停止する。
    """
    try:
        files = os.listdir(path_to_files)
        valid_files = [
            f for f in files
            if f.endswith(file_ext) and not f.startswith('.')
        ]
        if not valid_files:
            st.write(f'有効なファイルが {path_to_files} にありません。')
            logger.info(f'{path_to_files} に有効なファイルがありませんでした。')
            st.stop()
        valid_files.sort()
        logger.debug(f'ファイル一覧: {valid_files}')
        return valid_files
    except Exception as e:
        st.subheader('Error: pathが正しく設定されていません。ファイルが存在するフォルダを指定してください。')
        st.subheader(f'現在の設定されているpath: {path_to_files}')
        logger.error(f'ファイル取得でエラー発生: {e}')
        st.stop()


def display_file_list(path_to_files, files, file_ext='.spe'):
    """
    ファイル一覧のテーブルを表示し、ユーザーにマルチセレクトで選択させる。
    選択結果を返す。
    """
    st.subheader("1. 回転させるファイルを選択")
    # 一覧テーブルの表示
    st.table(FileHander.get_file_list_with_OD(path_to_files, files))
    # マルチセレクト
    selected_files = st.multiselect(
        label='回転させるファイルを選択 (複数可)',
        options=files,
        placeholder='Choose files',
    )
    st.write(selected_files)
    return selected_files


def display_rotate_options():
    """
    回転角度、回転中心、飽和フレームの扱い、上書き設定などのパラメータを
    ユーザーに選択させ、辞書にまとめて返す。
    """
    st.divider()
    st.subheader("2. 回転角度などを選択")

    rotate_deg = st.slider(
        "a. 回転角度 (0.05°刻み、-1.0〜1.0まで)",
        min_value=-1.0,
        max_value=1.0,
        value=0.0,
        step=0.05
    )
    logger.info(f"ユーザー指定の回転角度: {rotate_deg}")

    rotate_option = st.selectbox(
        label='b. 回転中心を選択',
        options=['whole', 'separate_half']
    )
    logger.info(f"ユーザー指定の回転中心: {rotate_option}")

    will_set_zero_with_saturation = st.checkbox(
        label='強度が飽和したフレームを0にする',
        value=False
    )
    if will_set_zero_with_saturation:
        saturation_threshold = st.slider(
            "飽和したと判断するしきい値 (これ以上の値があるframeを0にする)",
            min_value=60000,
            max_value=65535,
            value=65200,
            step=1
        )
        logger.debug(f"飽和しきい値の指定: {saturation_threshold}")
    else:
        saturation_threshold = None
        logger.debug("飽和フレームの処理: なし")

    is_overwrite = st.checkbox(
        label='すでに同じ回転ファイルがある場合に上書きする',
        value=False
    )
    logger.debug(f"上書き設定: {is_overwrite}")

    return {
        'rotate_deg': rotate_deg,
        'rotate_option': rotate_option,
        'saturation_threshold': saturation_threshold,  # 今回のコード内では未使用
        'is_overwrite': is_overwrite
    }


def display_summary_and_confirm(path_to_save_files, selected_files, file_ext, option_dict):
    """
    選択されたオプションや保存先を表示して確認を促し、
    実行ボタン押下を受け付ける。
    押下状態 (True/False) を返す。
    """
    st.divider()
    st.subheader('3. 確認して実行')
    if len(selected_files) == 0:
        st.write('ファイルが選択されていません。')
        st.stop()

    # オプションを確認
    st.info("オプションを確認", icon="👀")
    st.markdown(
        f"##### 設定値 ↓"
    )
    st.write(option_dict)

    # 保存先を確認
    new_files_with_ext = FileHander.get_rotated_file_names(
        selected_files,
        option_dict['rotate_deg'],
        option_dict['rotate_option'],
        file_ext
    )
    st.markdown(
        f"##### 保存先フォルダ: `{path_to_save_files}`"
    )
    st.markdown(
        f"##### 出力ファイル ↓"
    )
    st.write(new_files_with_ext)

    # 実行ボタン
    conduct_rotation = st.button(
        label='回転を実行する',
        icon='↪️',
        type='primary'
    )

    return conduct_rotation, new_files_with_ext


#
# ここからコピー処理・回転処理を専用メソッドとして分離
#

def copy_spe_file(
        src_path: str,
        dst_path: str,
        is_overwrite: bool
) -> bool:
    """
    SPEファイルをコピーする。
    コピー先ディレクトリが存在しない場合はエラーとして処理を停止。

    :param src_path: コピー元ファイルのパス
    :param dst_path: コピー先ファイルのパス
    :param is_overwrite: 上書き許可フラグ
    :return: スキップした場合 True / コピーを実行した場合 False
    """
    dst_dir = os.path.dirname(dst_path)

    if not os.path.isdir(dst_dir):
        # エラーとして表示し、処理を中断
        msg = f"保存先ディレクトリが存在しません: {dst_dir}"
        st.error(msg)
        logger.error(msg)
        st.stop()

    if not os.path.exists(dst_path):
        logger.debug(f"新規コピー: {src_path} -> {dst_path}")
        shutil.copyfile(src_path, dst_path)
        return False
    else:
        if is_overwrite:
            logger.debug(f"上書きコピー: {src_path} -> {dst_path}")
            shutil.copyfile(src_path, dst_path)
            return False
        else:
            logger.debug(f"コピーをスキップ (上書き設定OFF): {dst_path}")
            return True


def rotate_spe_file(
        src_path: str,
        dst_path: str,
        rotate_deg: float,
        rotate_option: str
) -> None:
    """
    SPEファイルを指定角度・指定オプションで回転し、結果を `dst_path` に上書き保存する。

    :param src_path: 回転前のオリジナルファイルパス
    :param dst_path: 回転先ファイルパス（既にコピー済み）
    :param rotate_deg: 回転角度
    :param rotate_option: 回転中心のオプション
    """
    logger.debug(f"回転開始: deg={rotate_deg}, option={rotate_option}")
    RawSpectrumData.overwrite_spe_image(
        before_spe_path=src_path,
        after_spe_path=dst_path,
        rotate_deg=rotate_deg,
        rotate_option=rotate_option
    )
    logger.debug("回転終了")


def execute_rotation(
        selected_files,
        new_files_with_ext,
        path_to_original_files,
        path_to_save_files,
        option_dict
):
    """
    回転処理を実際に実行する。
    ファイルのコピー → 回転処理 をループで行う。
    """
    rotate_deg = option_dict['rotate_deg']
    rotate_option = option_dict['rotate_option']
    is_overwrite = option_dict['is_overwrite']

    logger.info(f"回転処理を開始: ファイル数={len(selected_files)}")

    for i, selected_file in enumerate(selected_files): # NOTE: tqdm, stqdmはAppManagerからの起動では使えない。std出力先が無いため？
        path_to_original_file = os.path.join(path_to_original_files, selected_file)
        path_to_save_file = os.path.join(path_to_save_files, new_files_with_ext[i])

        st.info(f'{selected_file} -> {new_files_with_ext[i]}')
        logger.debug(f"コピー元: {path_to_original_file}, コピー先: {path_to_save_file}")

        # コピー処理
        st.write('複製中...')
        logger.debug('コピー処理を開始')
        is_skipped = copy_spe_file(path_to_original_file, path_to_save_file, is_overwrite)
        logger.debug('コピー処理を終了')

        # 回転処理（スキップされていない場合のみ）
        st.write('回転中...')
        if not is_skipped:
            rotate_spe_file(
                src_path=path_to_original_file,
                dst_path=path_to_save_file,
                rotate_deg=rotate_deg,
                rotate_option=rotate_option
            )
            st.write('回転終了')
        else:
            st.warning('上書きしない設定のため、回転をスキップしました。', icon='⚠️')

    st.success('すべて完了!')
    logger.info('回転処理が正常に完了')


# ------------------------------------------------------------------------------
# メイン処理フロー
# ------------------------------------------------------------------------------
# 1) 共通設定
configure_common_settings()

# 2) Settingインスタンスを取得
setting = get_setting_instance()

# 3) タイトル表示
display_title()

# 4) 有効ファイルの一覧取得
file_ext = '.spe'
path_to_original_files = setting.setting_json['read_path']
files = retrieve_valid_files(path_to_original_files, file_ext=file_ext)

# 5) ファイル選択画面
selected_files = display_file_list(path_to_original_files, files, file_ext)
logger.debug(f"選択されたファイル: {selected_files}")

# 6) 回転のオプション指定
option_dict = display_rotate_options()

# 7) 確認と実行ボタン
path_to_save_files = setting.setting_json['save_path']
conduct_rotation, new_files_with_ext = display_summary_and_confirm(
    path_to_save_files=path_to_save_files,
    selected_files=selected_files,
    file_ext=file_ext,
    option_dict=option_dict
)

# 8) ボタンが押されたら回転を実行
if conduct_rotation:
    st.divider()
    execute_rotation(
        selected_files=selected_files,
        new_files_with_ext=new_files_with_ext,
        path_to_original_files=path_to_original_files,
        path_to_save_files=path_to_save_files,
        option_dict=option_dict
    )
