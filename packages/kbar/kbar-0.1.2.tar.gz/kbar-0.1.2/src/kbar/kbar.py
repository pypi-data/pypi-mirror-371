# kbar.py
"""
kbar - K 線圖繪製工具
======================

本模組提供簡單的介面，在 matplotlib 與 mplfinance 上繪製中文化的 K 線圖。
支援自動偵測、安裝中文字型，確保在 Linux、Colab 與 Windows 環境下
皆能正常顯示中文。
"""

import mplfinance as mpf
import matplotlib as mpl
from matplotlib import font_manager
import os
import sys
import subprocess

def install_noto_cjk_linux():
    """
    在 Linux (Ubuntu/樹莓派) 安裝 Noto CJK 字型。
    
    Returns
    -------
    bool or None
        成功安裝回傳 True；失敗或例外回傳 None。
    """
    try:
        print('偵測到 Linux 環境，嘗試安裝 Noto CJK 字型...')
        result = subprocess.run(
            ['sudo', 'apt-get', 'install', '-y', 'fonts-noto-cjk'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f'字型安裝失敗: {result.stderr}')
            return None
        subprocess.run(['fc-cache', '-fv'], capture_output=True)
        font_manager._load_fontmanager(try_read_cache=False)
        print('Noto CJK 字型安裝完成')
        return True
    except Exception as e:
        print(f'安裝過程出錯: {e}')
        return None

def download_noto_cjk_colab():
    """
    在 Google Colab 下載 NotoSansCJK-Regular.ttc 字型。
    
    Returns
    -------
    str or None
        成功下載或已存在回傳字型路徑；失敗回傳 None。
    """
    font_path = '/content/NotoSansCJK-Regular.ttc'
    if not os.path.exists(font_path):
        print("正在下載中文字型...")
        url = 'https://github.com/googlefonts/noto-cjk/raw/main/' + \
              'Sans/OTC/NotoSansCJK-Regular.ttc'
        try:
            result = subprocess.run(
                ['wget', '-O', font_path, url],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f'下載失敗: {result.stderr}')
                return None
            print('中文字型下載完成')
            return font_path
        except Exception as e:
            print(f'字型下載失敗: {e}')
            return None
    else:
        print('字型檔案已存在')
        return font_path

def register_font_colab(font_path):
    """
    註冊 Colab 下載的字型，回傳可用的字型名稱。
    
    Parameters
    ----------
    font_path : str
        字型檔案的路徑。
    
    Returns
    -------
    str or None
        註冊成功回傳字型名稱；失敗回傳 None。
    """
    if not font_path or not os.path.exists(font_path):
        return None
    try:
        font_manager.fontManager.addfont(font_path)
        font_manager._load_fontmanager(try_read_cache=False)
        fonts = {f.name for f in font_manager.fontManager.ttflist}
        possible_names = [
            'Noto Sans CJK TC',
            'Noto Sans CJK JP', 
            'Noto Sans CJK SC',
            'Noto Sans CJK KR',
            'Noto Sans CJK'
        ]
        for name in possible_names:
            if name in fonts:
                print(f'成功註冊字型: {name}')
                return name
        print(f"字型註冊後可用名稱: {[f for f in fonts if 'Noto' in f or 'CJK' in f]}")
        return None
    except Exception as e:
        print(f"字型註冊失敗: {e}")
        return None

def detect_font():
    """
    偵測系統中文字型，並在需要時自動安裝或註冊。
    
    Returns
    -------
    str or None
        偵測或安裝成功回傳字型名稱；未找到回傳 None。
    """
    fonts = {f.name for f in font_manager.fontManager.ttflist}
    linux_chinese_fonts = ['Noto Sans CJK TC','Noto Sans CJK JP','Noto Sans CJK SC']
    if 'Microsoft JhengHei' in fonts:
        return 'Microsoft JhengHei'
    elif 'PingFang TC' in fonts:
        return 'PingFang TC'
    elif any(name in fonts for name in linux_chinese_fonts):
        return next(name for name in linux_chinese_fonts if name in fonts)
    else:
        in_colab = 'google.colab' in sys.modules
        in_linux = sys.platform.startswith('linux')
        if in_colab:
            print('Colab 環境偵測到，正在下載並設定中文字型...')
            font_path = download_noto_cjk_colab()
            if font_path:
                return register_font_colab(font_path)
        elif in_linux:
            print('Linux 環境偵測到，嘗試安裝 Noto CJK 字型...')
            if install_noto_cjk_linux():
                fonts = {f.name for f in font_manager.fontManager.ttflist}
                for name in linux_chinese_fonts:
                    if name in fonts:
                        return name
        return None

def check_font(font):
    """
    檢查指定字型是否存在，建立候選字型清單。
    
    Parameters
    ----------
    font : str
        指定字型名稱。
    
    Returns
    -------
    list[str]
        可用的字型候選清單。
    """
    fonts = {f.name for f in font_manager.fontManager.ttflist}
    candidates = []
    if font and font in fonts:
        candidates.append(font)
        print(f'使用指定字型: {font}')
    elif font:
        print(f"[警告] 找不到字型 '{font}'，將使用 fallback 字型")
    fallbacks = [
        'Microsoft JhengHei',
        'PingFang TC',
        'Noto Sans CJK TC',
        'Noto Sans CJK JP',
        'Noto Sans CJK SC',
        'DejaVu Sans',
        'Liberation Sans',
        'Arial',
        'sans-serif'
    ]
    for fallback in fallbacks:
        if fallback in fonts and fallback not in candidates:
            candidates.append(fallback)
    if candidates:
        print(f'字型候選清單: {candidates[:3]}')
        return candidates
    else:
        print('警告: 沒有找到合適的字型')
        return ['DejaVu Sans']

class KBar:
    """
    K 線圖繪製工具 (基於 mplfinance)

    Parameters
    ----------
    df : pandas.DataFrame
        股票或資產的 OHLCV 資料。
    font : str, optional
        指定字型名稱；若 None 則自動偵測中文字型。

    Examples
    --------
    >>> import pandas as pd
    >>> from kbar import KBar
    >>> df = pd.read_csv('stock.csv', index_col=0, parse_dates=True)
    >>> k = KBar(df)
    >>> k.addplot(df['Close'].rolling(5).mean(), color='blue', panel=0)
    >>> k.plot(volume=True, mav=(5,10,20))
    """

    def __init__(self, df, font=None):
        self.df = df
        self.addplots = []
        self.font = font or detect_font()
        if self.font:
            if 'font.sans-serif' in mpl.rcParams:
                current_fonts = mpl.rcParams['font.sans-serif'].copy()
                current_fonts = [f for f in current_fonts if f not in ['SimHei']]
                mpl.rcParams['font.sans-serif'] = [self.font] + current_fonts
            else:
                mpl.rcParams['font.sans-serif'] = [self.font, 'DejaVu Sans']
            mpl.rcParams['axes.unicode_minus'] = False
            print(f'設定字型為: {self.font}')
        else:
            print('警告: 未找到中文字型，中文可能無法正常顯示')

    def addplot(self, data, **kwargs):
        """
        新增技術指標圖層。

        Parameters
        ----------
        data : pandas.Series or numpy.ndarray
            要繪製的數據。
        **kwargs : dict
            傳遞給 mplfinance.make_addplot 的其他參數。
        """
        plot = mpf.make_addplot(data, **kwargs)
        self.addplots.append(plot)

    def plot(self, embedding=False, **kwargs):
        """
        繪製 K 線圖。

        Parameters
        ----------
        embedding : bool, optional
            是否內嵌顯示，預設 False。
        **kwargs : dict
            傳遞給 mplfinance.plot 的參數，例如 volume, mav, returnfig。

        Returns
        -------
        None 或 (fig, axes)
            若 returnfig=True 則回傳圖表物件。
        """
        color = mpf.make_marketcolors(up='red', down='green', inherit=True)
        font_candidates = check_font(self.font)
        style = mpf.make_mpf_style(
            base_mpf_style='default',
            marketcolors=color,
            rc={
                'font.family': font_candidates,
                'font.sans-serif': font_candidates,
                'axes.unicode_minus': False
            }
        )
        kwargs['type'] = 'candle'
        kwargs['style'] = style
        kwargs['addplot'] = self.addplots
        result = mpf.plot(self.df, **kwargs)
        if kwargs.get('returnfig', False):
            return result