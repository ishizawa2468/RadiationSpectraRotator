""" 露光データに対する操作を実装するクラス

ファイル形式が異なっても同様の操作感を保つようにする

"""
import functools
from enum import Enum, StrEnum

import numpy as np
from scipy.ndimage import rotate

from modules.file_format.spe_wrapper import SpeWrapper

class RawSpectrumData:
    """ 元データのファイル形式によって分岐する """
    file_extension: str # ファイル拡張子
    file_name: str # 由来のファイル名
    position_pixel_num: int
    wavelength_pixel_num: int
    center_pixel: int

    def __init__(self, file_data):
        """ データファイルをpythonクラスでインスタンス化したものを受け取る。
        主にファイル拡張子によって異なる部分をそれぞれのメソッドで調整する。
        それぞれのメソッドでどんなデータファイルが来たか判断できるようにファイル拡張子を設定する。

        :param file_data:

        :exception ValueError: 未実装のファイル形式の場合
        """
        # SPEファイルの場合
        if file_data.__class__ == SpeWrapper:
            self.file_extension = ".spe"
            self.file_name = file_data.file_name
            self.spe = file_data
        # TODO: HDFファイルの場合
        # その他の場合: 実装されていないのでエラー
        else:
            raise ValueError("データ形式(拡張子)に対応していません。")

    def get_frame_data(self, frame):
        match self.file_extension:
            case ".spe":
                return self.spe.get_frame_data(frame=frame)
            case _:
                raise ValueError("データ形式(拡張子)に対応していません。")

    @functools.cache
    def get_data_shape(self) -> dict:
        """ 露光データの形(データ数)を返す

        :return dict of key=str, value=int / (frame_num, position_pixel_num, center_pixel, wavelength_pixel_num):
        """
        match self.file_extension:
            case ".spe":
                frame_num = self.spe.num_frames
                # NOTE: ↓ROIには対応できていないかも。ROI設定したこと無いのでわからない。
                # TODO: 本当にheightがposでwidthがwlか確かめる。labのデータが違うpixel数を持ってたはず
                position_pixel_num = self.spe.roi_list[0].height # 加熱位置
                center_pixel = round(position_pixel_num / 2) # 四捨五入でなく、round to evenなので注意
                wavelength_pixel_num = self.spe.roi_list[0].width

                # set
                self.position_pixel_num = position_pixel_num
                self.wavelength_pixel_num = wavelength_pixel_num
                self.center_pixel = center_pixel

                return {
                    "frame_num": frame_num,
                    "position_pixel_num": position_pixel_num,
                    "center_pixel": center_pixel,
                    "wavelength_pixel_num": wavelength_pixel_num
                }
            case _:
                raise ValueError("データ形式(拡張子)に対応していません。")

    @functools.cache
    def get_wavelength_arr(self):
        """ 測定された波長配列を返す

        :return:
        """
        match self.file_extension:
            case ".spe":
                # TODO
                wavelength_arr = np.range(0, 10)
                return wavelength_arr
            case _:
                raise ValueError("データ形式(拡張子)に対応していません。")

    @functools.cache
    def get_max_intensity_arr(self):
        """ それぞれのframeでの最大強度からなる配列を集計して返す
        
        :return: 
        """
        match self.file_extension:
            case ".spe":
                all_max_I = self.spe.get_all_data_arr().max(axis=(1, 2))
                return all_max_I
            case _:
                raise ValueError("データ形式(拡張子)に対応していません。")

    @functools.cache
    def get_separated_max_intensity_arr(self):
        """

        :return:
        """
        match self.file_extension:
            case ".spe":
                shape_params_dict = self.get_data_shape()
                center_pixel = shape_params_dict['center_pixel']
                all_data = self.spe.get_all_data_arr()
                up_max_I = all_data[:, 0:center_pixel - 1, :].max(axis=(1, 2))
                down_max_I = all_data[:, center_pixel:-1, :].max(axis=(1, 2))
                return up_max_I, down_max_I
            case _:
                raise ValueError("データ形式(拡張子)に対応していません。")

    def get_centers_arr_by_max(self, frame):
        """ frame?全体?のimshowにscatterする中心位置を得る

        :return:
        """
        # TODO
        pass

    def get_centers_arr_by_skewfit(self):
        """ frame?全体?のimshowにscatterする中心位置を得る

        :return:
        """
        # TODO
        pass

    def get_rotated_image(self, frame, rotate_deg, rotate_option):
        option_enum = RotateOption.from_str(rotate_option)
        image = self.get_frame_data(frame)
        match option_enum:
            case RotateOption.WHOLE:
                return rotate(image, angle=rotate_deg, reshape=False)
            case RotateOption.SEPARATE_HALF:
                up_image = image[0:self.center_pixel, :]
                down_image = image[self.center_pixel:self.position_pixel_num, :]

                # 上下の画像をそれぞれ回転
                print(up_image.shape, down_image.shape)
                rotated_up = rotate(up_image, angle=rotate_deg, reshape=False)
                rotated_down = rotate(down_image, angle=rotate_deg, reshape=False)

                # 再結合
                combined_image = np.vstack((rotated_up, rotated_down))
                return combined_image
            case _:
                pass


class RotateOption(StrEnum):
    WHOLE = "whole"
    SEPARATE_HALF = "separate_half"

    @classmethod
    def from_str(cls, option_str):
        try:
            return cls(option_str.lower())
        except ValueError:
            raise ValueError(f"回転オプションが不正です: {option_str}\n以下で指定してください: {', '.join(o.value for o in cls)}")

