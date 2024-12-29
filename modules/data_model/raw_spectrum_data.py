""" 露光データに対する操作を実装するクラス

ファイル形式が異なっても同様の操作感を保つようにする

"""
import functools

import numpy as np

from modules.file_format.spe_wrapper import SpeWrapper

class RawSpectrumData:
    """ ファイル形式によって分岐する """
    file_extension: str # データのファイル拡張子。__init__処理で設定される
    file_name: str # 元データがどのファイル由来なのかを覚えておく

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
                image = self.spe.get_frame_data([])
                position_pixel_num = image.shape[0] # 最初がposition
                center_pixel = round(position_pixel_num / 2) # 四捨五入でなく、round to evenなので注意
                wavelength_pixel_num = image.shape[1]
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

    def get_centers_arr_by_max(self):
        """ frame?全体?のimshowにscatterする中心位置を得る

        :return:
        """
        pass

    def get_centers_arr_by_skewfit(self):
        """ frame?全体?のimshowにscatterする中心位置を得る

        :return:
        """
        pass
