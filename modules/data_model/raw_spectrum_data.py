""" 露光データに対する操作を実装するクラス

ファイル形式が異なっても同様の操作感を保つようにする

"""
import functools

import numpy as np

from modules.file_format.spe_wrapper import SpeWrapper

class RawSpectrumData:
    """ ファイル形式によって分岐する """
    file_extension: str # データのファイル拡張子。__init__処理で設定される

    def __init__(self, file_format):
        """ データファイルをpythonクラスでインスタンス化したものを受け取る。
        主にファイル拡張子によって異なる部分をそれぞれのメソッドで調整する。
        それぞれのメソッドでどんなデータファイルが来たか判断できるようにファイル拡張子を設定する。

        :param file_format:

        :exception ValueError: 未実装のファイル形式の場合
        """
        # SPEファイルの場合
        if file_format.__class__ == SpeWrapper:
            self.file_extension = ".spe"
        # TODO: .hdfも実装
        else:
            raise ValueError("データ形式(拡張子)に対応していません。")

    @functools.cache
    def get_data_shape(self):
        """ 露光データの形(データ数)を返す

        :return tuple of (frame_num, wavelength_pixel_num, position_pixel_num):
        """
        match self.file_extension:
            case ".spe":
                # TODO
                frame_num = 0
                wavelength_pixel_num = 0
                position_pixel_num = 0
                return (frame_num, wavelength_pixel_num, position_pixel_num)
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
                # TODO
                max_intensity_arr = range(0, 10)
                return max_intensity_arr
            case _:
                raise ValueError("データ形式(拡張子)に対応していません。")
