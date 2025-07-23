import unittest
import pandas as pd
import numpy as np
import os
import joblib
from src.model_trainer import ModelTrainer


class TestModelTrainer(unittest.TestCase):
    """测试模型训练类"""

    def setUp(self):
        """设置测试数据"""
        # 创建测试数据
        self.test_data = pd.DataFrame({
            '天道得分': np.random.uniform(60, 95, 100),
            '地道得分': np.random.uniform(60, 95, 100),
            '人道得分': np.random.uniform(60, 95, 100),
            '预测涨跌幅': np.random.uniform(-5, 10, 100)
        })

    def test_train_model(self):
        """测试训练模型"""
        # 测试重新训练
        result = ModelTrainer.train_model(self.test_data, retrain=True)
        self.assertTrue(result)

        # 检查模型是否保存
        model_path = 'models/stock_model.pkl'
        self.assertTrue(os.path.exists(model_path))

        # 测试不重新训练
        result = ModelTrainer.train_model(self.test_data, retrain=False)
        self.assertTrue(result)

        # 清理测试产生的文件
        if os.path.exists(model_path):
            os.remove(model_path)


if __name__ == '__main__':
    unittest.main()