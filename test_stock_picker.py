import unittest
import pandas as pd
import numpy as np
import random
from stock_picker import fetch_stock_data, generate_performance_data, jiuzhou_strategy

class TestStockPicker(unittest.TestCase):
    def setUp(self):
        # 设置随机种子以确保测试的可重复性
        random.seed(42)
        np.random.seed(42)
        
    def test_fetch_stock_data(self):
        # 测试获取股票数据函数
        try:
            df = fetch_stock_data()
            # 检查返回值是否为DataFrame
            self.assertIsInstance(df, pd.DataFrame)
            # 检查是否包含必要的列
            required_columns = ['代码', '名称', '最新价', '涨跌幅', '成交量', '所属行业', '概念']
            for col in required_columns:
                self.assertIn(col, df.columns)
        except Exception as e:
            self.fail(f"fetch_stock_data() 引发异常: {str(e)}")

    def test_generate_performance_data(self):
        # 测试生成表现数据函数
        try:
            df = generate_performance_data()
            # 检查返回值是否为DataFrame
            self.assertIsInstance(df, pd.DataFrame)
            # 检查是否包含必要的列
            required_columns = ['日期', '策略累计收益', '上证指数收益']
            for col in required_columns:
                self.assertIn(col, df.columns)
        except Exception as e:
            self.fail(f"generate_performance_data() 引发异常: {str(e)}")

    def test_jiuzhou_strategy(self):
        # 测试九州战略函数
        try:
            # 测试不同的市场趋势
            for market_trend in ['上涨趋势', '下跌趋势', '震荡整理']:
                # 测试不同的风险偏好
                for risk_preference in ['激进型', '稳健型', '保守型']:
                    # 测试不同的行业偏好
                    for industry_preference in ['全行业', '金融', '新能源']:
                        df = jiuzhou_strategy(market_trend, risk_preference, industry_preference)
                        # 检查返回值是否为DataFrame
                        self.assertIsInstance(df, pd.DataFrame)
                        # 检查是否包含必要的列
                        required_columns = ['代码', '名称', '最新价', '涨跌幅', '成交量', '所属行业', '概念', '天道得分', '地道得分', '人道得分', '战略指数', '预测涨跌幅']
                        for col in required_columns:
                            self.assertIn(col, df.columns)
        except Exception as e:
            self.fail(f"jiuzhou_strategy() 引发异常: {str(e)}")

if __name__ == '__main__':
    unittest.main()