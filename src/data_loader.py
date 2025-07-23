import pandas as pd
import numpy as np
import logging
import random
datetime

from utils.logger import Logger
logger = Logger.get_logger("data_loader")

class DataLoader:
    """
    股票数据加载器类
    提供股票历史数据获取和模拟性能数据生成功能
    实际环境中可替换为真实数据源API调用
    """

    @staticmethod
    def fetch_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指定日期范围的股票数据
        Args:
            stock_code: 股票代码，格式如"600000.SH"
            start_date: 开始日期，格式为"YYYY-MM-DD"
            end_date: 结束日期，格式为"YYYY-MM-DD"
        Returns:
            pd.DataFrame: 包含以下列的股票数据
                - 日期: datetime类型
                - 开盘价: float
                - 收盘价: float
                - 最高价: float
                - 最低价: float
                - 成交量: int
                - 成交额: float
            若获取失败则返回空DataFrame
        """
        try:
            logger.info(f"获取股票数据: {stock_code}, 日期范围: {start_date} 至 {end_date}")
            # 模拟股票数据
            dates = pd.date_range(start=start_date, end=end_date, freq='B')
            data = {
                '日期': dates,
                '开盘价': [random.uniform(10, 100) for _ in range(len(dates))],
                '收盘价': [random.uniform(10, 100) for _ in range(len(dates))],
                '最高价': [random.uniform(10, 100) for _ in range(len(dates))],
                '最低价': [random.uniform(10, 100) for _ in range(len(dates))],
                '成交量': [random.randint(1000, 100000) for _ in range(len(dates))],
                '成交额': [random.uniform(10000, 1000000) for _ in range(len(dates))]
            }
            df = pd.DataFrame(data)
            logger.info(f"成功获取股票数据: {stock_code}, 数据量: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def generate_performance_data() -> pd.DataFrame:
        """
        生成策略与指数的历史表现对比数据
        用于回测结果可视化和策略有效性评估
        Returns:
            pd.DataFrame: 包含以下列的表现数据
                - 日期: datetime类型
                - 策略累计收益: float，策略累计收益率(%)
                - 上证指数收益: float，上证指数累计收益率(%)
            若生成失败则返回空DataFrame
        """
        try:
            logger.info("生成历史表现数据")
            # 模拟历史表现数据
            dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
            strategy_returns = [0]
            index_returns = [0]
            
            for i in range(1, len(dates)):
                # 模拟策略收益
                strategy_returns.append(strategy_returns[-1] + random.uniform(-0.5, 1.0))
                # 模拟指数收益
                index_returns.append(index_returns[-1] + random.uniform(-0.5, 0.8))
                
            data = {
                '日期': dates,
                '策略累计收益': strategy_returns,
                '上证指数收益': index_returns
            }
            df = pd.DataFrame(data)
            logger.info(f"成功生成历史表现数据，数据量: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"生成历史表现数据失败: {str(e)}")
            return pd.DataFrame()