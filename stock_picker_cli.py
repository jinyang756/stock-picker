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
                # 系统默认使用战略罗盘推衍策略
                selected_stocks = StockSelectionStrategies.strategic_compass_derivation(
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


def calculate_match_score(row, strategy, market_trend, risk_preference):
    """计算策略匹配度评分"""
    # 初始化评分
    score = 100

    # 模拟评分逻辑
    # 量比 (假设这里用天道得分代替)
    if row['天道得分'] > 80:
        score += 10
    elif row['天道得分'] < 60:
        score -= 10

    # 涨幅
    if row['预测涨跌幅'] > 5:
        score += 10
    elif row['预测涨跌幅'] < 3:
        score -= 10

    # 风险偏好匹配
    if risk_preference == '中风险' and 60 < row['地道得分'] < 80:
        score += 5

    # 市场趋势匹配
    if market_trend == '震荡市' and 70 < row['人道得分'] < 90:
        score += 5

    # 确保分数在0-100之间
    score = max(0, min(100, score))
    return score

def get_risk_tips(row):
    """生成风险提示"""
    tips = []
    # 模拟风险提示逻辑
    if row['预测涨跌幅'] > 10:
        tips.append("涨幅过高，注意短期回调风险")
    if row['天道得分'] < 60:
        tips.append("天道得分较低，基本面可能存在隐患")
    if not tips:
        tips.append("暂无明显风险提示，但仍需关注大盘走势")
    return " | ".join(tips)

def main():
    """主函数"""
    cli = StockPickerCLI()
    print("欢迎使用天机罗盘 - AI选股系统")
    print("使用默认参数运行选股...")

    # 使用默认参数
    strategy = "战略罗盘推衍"
    market_trend = "震荡市"
    risk_preference = "中风险"
    industry_preference = ["全部"]
    retrain = False

    print("正在选股，请稍候...")
    selected_stocks = cli.run(
        strategy, market_trend, risk_preference, industry_preference, retrain
    )

    # 选股时间
    selection_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if not selected_stocks.empty:
        print(f"\n【选股时间】{selection_time} | 策略：{strategy}")
        print(f"【选股结果】共{len(selected_stocks)}支股票\n")

        for i, row in selected_stocks.iterrows():
            # 计算匹配度评分
            match_score = calculate_match_score(row, strategy, market_trend, risk_preference)
            # 匹配度等级
            if match_score >= 80:
                match_level = "高匹配"
                color_code = "\033[92m"  # 绿色
            elif match_score >= 60:
                match_level = "中匹配"
                color_code = "\033[93m"  # 黄色
            else:
                match_level = "低匹配"
                color_code = "\033[91m"  # 红色
            reset_color = "\033[0m"

            # 风险提示
            risk_tips = get_risk_tips(row)

            # 输出股票信息
            print(f"{i+1}. 【股票代码】{row['股票代码']} {row['股票名称']}（沪市 | {row['行业']}）")
            print("   ┌───────────────┬────────────┬────────────┐")
            print("   │ 核心指标       │ 数值        │ 说明        ")
            print("   ├───────────────┼────────────┼────────────┤")
            print(f"   │ 天道得分       │ {row['天道得分']:.2f}     │ 基本面评分    ")
            print(f"   │ 地道得分       │ {row['地道得分']:.2f}     │ 技术面评分    ")
            print(f"   │ 人道得分       │ {row['人道得分']:.2f}     │ 资金面评分    ")
            print(f"   │ 预测涨跌幅     │ {row['预测涨跌幅']:.2f}%    │ 未来涨幅预测  ")
            print("   └───────────────┴────────────┴────────────┘")
            print(f"   【策略匹配度】{color_code}{match_score}分（{match_level}）{reset_color}")
            print(f"   【风险提示】{risk_tips}")
            print(f"   【操作建议】若开盘后30分钟内保持强势，可考虑轻仓介入\n")
    else:
        print("没有找到符合条件的股票")

    # 通用免责声明
    print("\n【免责声明】选股结果仅供参考，不构成投资建议，操作前需结合自身风险承受能力。")


if __name__ == "__main__":
    main()