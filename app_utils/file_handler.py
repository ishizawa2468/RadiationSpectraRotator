import os

import pandas as pd

from modules.file_format.spe_wrapper import SpeWrapper

class FileHander:
    @staticmethod
    def get_file_list_with_OD(path_to_files, files):
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
        return pd.DataFrame(spe_display_data)

    @staticmethod
    def get_rotated_file_names(
            files, # 元のファイル名のリスト
            rotate_deg,
            rotate_option,
            file_extention = '.spe'
    ):

        rotated_files = []
        for file in files:
            new_file_name = "_".join(
                [
                    file,
                    rotate_option,
                    get_rotate_deg_str(rotate_deg)
                ]
            )
            rotated_files.append(new_file_name + file_extention)
        return rotated_files

def get_rotate_deg_str(rotate_deg):
    rotate_deg_str = ""
    rotate_deg_str += "p" if rotate_deg >= 0 else "m"
    rotate_deg_str += "{:.0f}".format(abs(rotate_deg*100))
    rotate_deg_str += "e-2"
    return rotate_deg_str