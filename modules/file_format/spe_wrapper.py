from typing import Optional, Sequence

import numpy as np
import pandas as pd

from modules.file_format.read_spe import SpeReference

# 自分で欲しい形式でデータを返してもらうためのラッパー
class SpeWrapper(SpeReference):
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self._filepath = filepath

    def get_one_data_df(self,
                        rois:Optional[Sequence[int]] = None,
                        frame:Optional[int] = None) -> pd.DataFrame:
        data_list = self.get_data(rois=rois, frames=[frame])[0][0] # list, ndarrayを外すして、二次元の露光データを取得
        return pd.DataFrame(data_list)

    # 指定されたframeのimgデータを返す
    def get_frame_data(self,
                       rois:Optional[Sequence[int]] = None,
                       frame:Optional[int] = None) -> np.ndarray:
        # NOTE: frameを指定しないと、shape=(1, 800, 512, 512)のように返ってくる。
        # numpy.ndarrayのlistなので四次元 (List(ndarray))
        return self.get_data(frames=[frame])[0][0] # list, ndarrayを外して、二次元の露光データを取得

    # (frame_num, pixel, pixel)の3次元のndarrayを返す
    def get_all_data_arr(self) -> np.ndarray:
        return self.get_data()[0]

    # 最大値配列を返す
    def get_max_intensity(self):
        return self.get_all_data_arr().max(axis=2).max(axis=1)

    # SpeFileからの借用
    def _read_at(self, pos, size, ntype):
        pos = int(pos)
        size = int(size)
        self._fid.seek(pos)
        return np.fromfile(self._fid, ntype, size)

    def _get_xml_string(self):
        """Reads out the xml string from the file end"""
        self._fid = open(self._filepath, 'rb')
        self.xml_offset = self._read_at(678, 1, np.int_)[0]
        self._fid.seek(int(self.xml_offset))
        self.xml_string = self._fid.read()

    def get_params_from_xml(self):
        self._get_xml_string()
        xml = self.xml_string
        str_xml = str(xml)
        list_xml = str_xml.split("<")

        # 特定の文字列が入っているものから情報を抜き出す
        for i, ele in enumerate(list_xml):
            if ('FrameRate r:readOnly' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }") # デバッグ用
                self.framerate = float(ele.split('>')[-1])
            if ('BaseFileName' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.basename = ele.split('>')[-1]
            if ('IncrementNumber' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.filenum = int(ele.split('>')[-1])
            if ('ReferenceFileDate r:readOnly' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.date = ele.split('>')[-1]
            if ('Date r:readOnly' in ele) and ('Reference' not in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.calibration_date = ele.split('>')[-1]
            if ('Name type' in ele) and ('/' not in ele):
                # print(f"{i}: {ele = }")
                self.OD = ele.split('>')[-1]
