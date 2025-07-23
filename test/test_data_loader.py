import unittest
import pandas as pd
from src.data_loader import DataLoader


class TestDataLoader(unittest.TestCase):
    """测试数据加载器类"""

    def test_fetch_stock_data(self):
        """测试获取股票数据"""
        # 测试正常情况
        df = DataLoader.fetch_stock_data("000001", "2023-01-01", "2023-12-31")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn('日期', df.columns)
        self.assertIn('收盘价', df.columns)

        # 测试异常情况
        df = DataLoader.fetch_stock_data("", "2023-01-01", "2023-12-31")
        self.assertIsInstance(df, pd.DataFrame)

    def test_generate_performance_data(self):
        """测试生成历史表现数据"""
        df = DataLoader.generate_performance_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn('日期', df.columns)
        self.assertIn('策略累计收益', df.columns)
        self.assertIn('上证指数收益', df.columns)


if __name__ == '__main__':
    unittest.main()