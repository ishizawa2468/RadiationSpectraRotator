import matplotlib.pyplot as plt

"""plot用の設定"""
plt.rcParams['mathtext.fontset'] = 'cm'     #数式用のフォントejavuserif" or "cm"
plt.rcParams['xtick.direction'] = 'in'      #x軸の目盛線 #内in')か外向き('out')か双方向か('inout')
plt.rcParams['ytick.direction'] = 'in'      #y軸の目盛線 #内in')か外向き('out')か双方向か('inout')
plt.rcParams['xtick.major.width'] = 1.0     #x軸主目盛り線の線幅
plt.rcParams['ytick.major.width'] = 1.0     #y軸主目盛り線の線幅
plt.rcParams['font.size'] = 18               #フォントの大きさ
plt.rcParams['axes.linewidth'] = 0.8        #軸の線幅edge linewidth。囲みの太さ
plt.rcParams['figure.dpi'] = 300
plt.rcParams['figure.figsize'] = (8, 6)
# Arialフォントを設定
plt.rcParams.update({
    "font.family": "Arial",           # フォントをArialに設定
    "mathtext.fontset": "custom",     # カスタムフォントを指定
    "mathtext.rm": "Arial",           # 数式の通常テキスト部分
    "mathtext.it": "Arial",    # 数式のイタリック部分
    "mathtext.bf": "Arial"       # 数式の太字部分
})

class FigureMaker:

    @staticmethod
    def get_max_I_figure(file_name, all_max_I, up_max_I, down_max_I):
        fig, ax = plt.subplots()
        ax.plot(all_max_I, color='red', lw=0.5, label='All')
        ax.plot(up_max_I, color='blue', linestyle=":", label='Up')
        ax.plot(down_max_I, color='green', linestyle=":", label='Up')
        ax.set_xlabel("Frame")
        ax.set_ylabel("Intensity")
        ax.set_title(f"Max radiation intensity {file_name}")
        ax.legend()
        return fig, ax