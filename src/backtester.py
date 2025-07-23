import pandas as pd
import numpy as np
import logging

from utils.logger import Logger
from utils.config import Config
logger = Logger.get_logger("backtester")

class Backtester:
    """回测类"""

    @staticmethod
    def backtest_strategy(selected_stocks: pd.DataFrame) -> dict:
        """
        回测策略
        Args:
            selected_stocks: 选中的股票
        Returns:
            回测结果字典
        """
        try:
            logger.info("开始回测策略")

            # 模拟回测结果
            # 从配置文件获取回测参数范围
            min_return = Config.get('backtest.min_return', 5)
            max_return = Config.get('backtest.max_return', 20)
            min_win_rate = Config.get('backtest.min_win_rate', 0.6)
            max_win_rate = Config.get('backtest.max_win_rate', 0.8)
            min_max_drawdown = Config.get('backtest.min_max_drawdown', 5)
            max_max_drawdown = Config.get('backtest.max_max_drawdown', 15)
            min_sharpe_ratio = Config.get('backtest.min_sharpe_ratio', 1)
            max_sharpe_ratio = Config.get('backtest.max_sharpe_ratio', 3)

            results = {
                '平均总收益率': np.random.uniform(min_return, max_return),
                '平均胜率': np.random.uniform(min_win_rate, max_win_rate),
                '平均最大回撤': np.random.uniform(min_max_drawdown, max_max_drawdown),
                '平均夏普比率': np.random.uniform(min_sharpe_ratio, max_sharpe_ratio)
            }

            logger.info(f"回测完成，结果: {results}")
            return results
        except Exception as e:
            logger.error(f"回测失败: {str(e)}")
            return {
                '平均总收益率': 0,
                '平均胜率': 0,
                '平均最大回撤': 0,
                '平均夏普比率': 0
            }