
import numpy as np
from scipy.optimize import curve_fit

class RadiationFitter:
    @staticmethod
    def asymmetric_gaussian(x, A, mu, sigma1, sigma2):
        """
        非対称ガウシアン関数
        """
        return np.where(
            x <= mu,
            A * np.exp(-((x - mu) ** 2) / (2 * sigma1 ** 2)),
            A * np.exp(-((x - mu) ** 2) / (2 * sigma2 ** 2))
        )

    @staticmethod
    def fit_by_asymmetric_gaussian(x_data, y_data, initial_guess=None):
        """
        データに対して非対称ガウシアンをフィッティングします。

        Parameters:
            x_data (array-like): 入力のxデータ
            y_data (array-like): 入力のyデータ
            initial_guess (list): フィッティングの初期値 [A, mu, sigma1, sigma2]

        Returns:
            dict: フィッティング結果のパラメータと共分散行列
        """
        # 初期値が指定されていない場合のデフォルト値
        if initial_guess is None:
            initial_guess = [1.0, 0.0, 2.0, 2.0]

        # フィッティング
        try:
            popt, pcov = curve_fit(
                RadiationFitter.asymmetric_gaussian,
                x_data,
                y_data,
                p0=initial_guess
            )
            result = {
                "parameters": {
                    "A": popt[0],
                    "mu": popt[1],
                    "sigma1": popt[2],
                    "sigma2": popt[3]
                },
                "covariance": pcov
            }
        except RuntimeError as e:
            result = {
                "error": str(e)
            }

        return result
