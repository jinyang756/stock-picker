import os
import sys
import pandas as pd
import numpy as np
import logging
import random
import datetime

# 设置路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from src.data_loader import DataLoader
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer
from src.strategies import StockSelectionStrategies
from src.backtester import Backtester
from utils.logger import Logger
from utils.config import Config

# 配置日志
logger = Logger.get_logger("cli")

class StockPickerCLI:
    """选股系统命令行界面"""

    def __init__(self):
        """初始化"""
        logger.info("初始化选股系统命令行界面")

    def run(self, strategy="九州策略", market_trend="震荡市", risk_preference="中风险",
            industry_preference=["全部"], retrain_model=False):
        """运行选股系统

        Args:
            strategy: 选股策略
            market_trend: 市场趋势判断
            risk_preference: 风险偏好
            industry_preference: 行业偏好
            retrain_model: 是否重新训练AI模型

        Returns:
            list: 选股结果
        """
        try:
            logger.info(f"开始运行选股系统，策略: {strategy}")

            # 模拟股票数据
            max_stock_codes = Config.get('app.max_stock_codes', 100)
            stock_codes = [f"{i:06d}" for i in range(1, max_stock_codes + 1)]
            stock_data = []

            for code in stock_codes:
                # 模拟股票基本信息
                industry = random.choice(["科技", "金融", "医疗", "消费", "能源", "制造"])
                name = f"股票{code}"

                # 模拟股票数据
                start_date = Config.get('app.stock_start_date', "2023-01-01")
                end_date = Config.get('app.stock_end_date', "2023-12-31")
                df = DataLoader.fetch_stock_data(code, start_date, end_date)
                if not df.empty:
                    # 计算维度得分
                    df = FeatureEngineer.calculate_dimensions(df)
                    # 创建目标变量
                    df = FeatureEngineer.create_target_variable(df)

                    # 获取最新数据
                    latest_data = df.iloc[-1].to_dict()
                    latest_data['股票代码'] = code
                    latest_data['股票名称'] = name
                    latest_data['行业'] = industry

                    # 检查行业偏好
                    if "全部" in industry_preference or industry in industry_preference:
                        stock_data.append(latest_data)

            # 训练模型
            if stock_data:
                # 准备训练数据
                train_data = pd.DataFrame(stock_data)
                ModelTrainer.train_model(train_data, retrain_model)

                # 选股策略
                if strategy == "九州策略":
                    selected_stocks = StockSelectionStrategies.jiuzhou_strategy(
                        pd.DataFrame(stock_data), market_trend, risk_preference, industry_preference
                    )
                else:
                    # 默认为九州策略
                    selected_stocks = StockSelectionStrategies.jiuzhou_strategy(
                        pd.DataFrame(stock_data), market_trend, risk_preference, industry_preference
                    )

                logger.info(f"选股完成，共选出{len(selected_stocks)}支股票")
                return selected_stocks
            else:
                logger.warning("没有找到符合条件的股票数据")
                return []

        except Exception as e:
            logger.error(f"运行选股系统失败: {str(e)}")
            return []


def main():
    """主函数"""
    cli = StockPickerCLI()
    print("欢迎使用天机罗盘 - AI选股系统")
    print("使用默认参数运行选股...")

    # 使用默认参数
    strategy = "九州策略"
    market_trend = "震荡市"
    risk_preference = "中风险"
    industry_preference = ["全部"]
    retrain = False

    print("正在选股，请稍候...")
    selected_stocks = cli.run(
        strategy, market_trend, risk_preference, industry_preference, retrain
    )

    if not selected_stocks.empty:
        print("\n选股结果:")
        for i, row in selected_stocks.iterrows():
            print(f"{i+1}. 股票名称: {row['股票名称']}, 股票代码: {row['股票代码']}")
            print(f"   行业: {row['行业']}")
            print(f"   天道得分: {row['天道得分']:.2f}")
            print(f"   地道得分: {row['地道得分']:.2f}")
            print(f"   人道得分: {row['人道得分']:.2f}")
            print(f"   预测涨跌幅: {row['预测涨跌幅']:.2f}%\n")
    else:
        print("没有找到符合条件的股票")


if __name__ == "__main__":
    main()