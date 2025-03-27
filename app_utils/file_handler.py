import os

import pandas as pd

from modules.file_format.spe_wrapper import SpeWrapper
from log_util import logger

class FileHander:
    @staticmethod
    def get_file_list_with_OD(path_to_files, files):
        logger.debug('OD付きのSPEファイルリストを取得開始 ->')
        spe_list = []
        spe_display_data = []
        for file in files:
            if not file.endswith('.spe'):
                raise Exception(".spe以外のファイルが含まれています。")
            spe_list.append(SpeWrapper(os.path.join(path_to_files, file)))
        for spe in spe_list:
            try:
                spe.get_params_from_xml()
                OD = spe.OD
            except Exception as e:
                OD = None
            spe_display_data.append({"File Name": spe.file_name, "OD": OD})
        logger.debug('-> 終了')
        return pd.DataFrame(spe_display_data)

    @staticmethod
    def get_rotated_file_names(
            files, # 元のファイル名のリスト
            rotate_deg,
            rotate_option,
            file_extention = '.spe'
    ):
        logger.debug('回転後のファイル名の取得を開始 ->')
        rotated_files = []
        for file in files:
            new_file_name = "_".join( # アンスコで要素をつなげる
                [
                    file[:-4], # 拡張子を取り除く
                    rotate_option, # 回転中心
                    get_rotate_deg_str(rotate_deg) # 回転角度
                ]
            )
            rotated_files.append(new_file_name + file_extention)
        logger.debug('-> 終了')
        return rotated_files

def get_rotate_deg_str(rotate_deg):
    rotate_deg_str = ""
    rotate_deg_str += "p" if rotate_deg >= 0 else "m"
    rotate_deg_str += "{:.0f}".format(abs(rotate_deg*100))
    rotate_deg_str += "e-2"
    return rotate_deg_str
