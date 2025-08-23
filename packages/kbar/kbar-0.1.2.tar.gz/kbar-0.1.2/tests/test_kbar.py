# test_kbar.py
import unittest
import pandas as pd
import numpy as np
from kbar import KBar, detect_font

class TestKBar(unittest.TestCase):
    def setUp(self):
        # 建立測試用的 DataFrame
        data = {
            'Open': [100, 102, 101, 105],
            'High': [103, 106, 104, 108],
            'Low': [99, 100, 98, 102],
            'Close': [102, 104, 103, 107],
            'Volume': [1000, 1500, 1200, 1300],
        }
        self.df = pd.DataFrame(data, index=pd.date_range(start="2023-01-01", periods=4))
        self.kbar = KBar(self.df)

    def test_initialization(self):
        # 測試初始化是否正確
        self.assertEqual(len(self.kbar.addplots), 0)
        pd.testing.assert_frame_equal(self.kbar.df, self.df)

    def test_font_detection(self):
        # 測試是否能偵測到字型（不保證一定有中文，但至少不應該 None）
        font = detect_font()
        self.assertIsNotNone(font)

    def test_addplot(self):
        # 測試 addplot 方法
        data = self.df['Close']
        self.kbar.addplot(data, color='red', linestyle='--', width=2)
        self.assertEqual(len(self.kbar.addplots), 1)

    def test_addplot_content(self):
        data = self.df['Close']
        self.kbar.addplot(data, color='blue')
        plot_obj = self.kbar.addplots[0]
        ydata = plot_obj.get('ydata') or plot_obj.get('data')
        self.assertEqual(len(ydata), len(self.df))

    def test_plot_without_returnfig(self):
        # 測試 plot 方法不傳回圖表
        try:
            self.kbar.plot(volume=True, title='Test Plot', ylabel='Price')
        except Exception as e:
            self.fail(f"plot() raised an exception: {e}")

    def test_plot_with_returnfig(self):
        # 測試 plot 方法傳回圖表
        fig, axes = self.kbar.plot(returnfig=True, volume=True, title='Test Plot')
        self.assertTrue(hasattr(fig, "axes"))
        self.assertGreaterEqual(len(fig.axes), 2)  # 檢查有主圖與成交量副圖

    def test_plot_with_returnfig_axes_labels(self):
        # 測試標題是否被正確設定
        fig, axes = self.kbar.plot(returnfig=True, volume=True, title='My Test Title')
        self.assertIn('My Test Title', fig._suptitle.get_text())

    def test_invalid_addplot_data(self):
        # 測試傳入錯誤型別資料
        with self.assertRaises(TypeError):
            self.kbar.addplot("invalid_data")

    def test_plot_with_custom_params(self):
        # 測試自訂參數的情況
        try:
            self.kbar.plot(
                volume=True,
                figscale=1.2,
                figratio=(10, 6),
                tight_layout=True,
                xrotation=30,
            )
        except Exception as e:
            self.fail(f"plot() raised an exception with custom params: {e}")


if __name__ == "__main__":
    unittest.main()