import unittest
import pandas as pd
import numpy as np
from src.feature_engineer import FeatureEngineer


class TestFeatureEngineer(unittest.TestCase):
    """测试特征工程类"""

    def setUp(self):
        """设置测试数据"""
        # 创建测试数据
        self.test_data = pd.DataFrame({
            '日期': pd.date_range(start='2023-01-01', end='2023-01-10'),
            '收盘价': np.random.uniform(10, 100, 10)
        })

    def test_calculate_dimensions(self):
        """测试计算维度得分"""
        df = FeatureEngineer.calculate_dimensions(self.test_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('天道得分', df.columns)
        self.assertIn('地道得分', df.columns)
        self.assertIn('人道得分', df.columns)

    def test_create_target_variable(self):
        """测试创建目标变量"""
        df = FeatureEngineer.create_target_variable(self.test_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('预测涨跌幅', df.columns)


if __name__ == '__main__':
    unittest.main()