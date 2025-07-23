import pandas as pd
import numpy as np
import logging
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from utils.logger import Logger
from utils.config import Config
logger = Logger.get_logger("model_trainer")

class ModelTrainer:
    """模型训练类"""

    @staticmethod
    def train_model(train_data: pd.DataFrame, retrain: bool = False) -> bool:
        """
        训练模型
        Args:
            train_data: 训练数据
            retrain: 是否重新训练
        Returns:
            训练是否成功
        """
        try:
            # 检查模型是否已存在
            model_path = 'models/stock_model.pkl'
            if os.path.exists(model_path) and not retrain:
                logger.info("模型已存在，无需重新训练")
                return True

            logger.info("开始训练模型")
            # 准备训练数据
            X = train_data[['天道得分', '地道得分', '人道得分']]
            y = train_data['预测涨跌幅']

            # 分割训练集和测试集
            test_size = Config.get('model.test_size', 0.2)
            random_state = Config.get('model.random_state', 42)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

            # 训练随机森林模型
            n_estimators = Config.get('model.n_estimators', 100)
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
            model.fit(X_train, y_train)

            # 评估模型
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"模型训练完成，MSE: {mse:.2f}")

            # 保存模型
            os.makedirs('models', exist_ok=True)
            joblib.dump(model, model_path)
            logger.info(f"模型已保存至: {model_path}")
            return True
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return False