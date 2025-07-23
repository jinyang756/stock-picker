import pandas as pd
import numpy as np
import logging

from utils.logger import Logger
from utils.config import Config
logger = Logger.get_logger("strategies")

class StockSelectionStrategies:
    """选股策略类"""

    @staticmethod
    def jiuzhou_strategy(stock_data: pd.DataFrame, market_trend: str, risk_preference: str, industry_preference: list) -> pd.DataFrame:
        """
        九州策略选股
        Args:
            stock_data: 股票数据
            market_trend: 市场趋势
            risk_preference: 风险偏好
            industry_preference: 行业偏好
        Returns:
            选中的股票DataFrame
        """
        try:
            logger.info(f"应用九州策略选股，市场趋势: {market_trend}, 风险偏好: {risk_preference}, 行业偏好: {industry_preference}")

            # 模拟行业过滤
            if industry_preference and '全部' not in industry_preference:
                stock_data = stock_data[stock_data['所属行业'].isin(industry_preference)]

            # 模拟根据市场趋势调整权重
            if market_trend == '牛市':
                stock_data['综合得分'] = stock_data['天道得分'] * 0.4 + stock_data['地道得分'] * 0.3 + stock_data['人道得分'] * 0.3
            elif market_trend == '熊市':
                stock_data['综合得分'] = stock_data['天道得分'] * 0.3 + stock_data['地道得分'] * 0.4 + stock_data['人道得分'] * 0.3
            else:
                stock_data['综合得分'] = stock_data['天道得分'] * 0.3 + stock_data['地道得分'] * 0.3 + stock_data['人道得分'] * 0.4

            # 模拟根据风险偏好调整
            if risk_preference == '高风险':
                # 选择综合得分高且波动大的股票
                high_risk_count = Config.get('strategy.high_risk_count', 20)
                stock_data = stock_data.sort_values('综合得分', ascending=False).head(high_risk_count)
            elif risk_preference == '低风险':
                # 选择综合得分较高且波动小的股票
                low_risk_count = Config.get('strategy.low_risk_count', 10)
                stock_data = stock_data.sort_values('综合得分', ascending=False).head(low_risk_count)
            else:
                # 适中风险
                medium_risk_count = Config.get('strategy.medium_risk_count', 15)
                stock_data = stock_data.sort_values('综合得分', ascending=False).head(medium_risk_count)

            logger.info(f"九州策略选股完成，选中股票数量: {len(stock_data)}")
            return stock_data
        except Exception as e:
            logger.error(f"九州策略选股失败: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def ai_strategy(stock_data: pd.DataFrame, market_trend: str, risk_preference: str, industry_preference: list) -> pd.DataFrame:
        """
        AI策略选股
        Args:
            stock_data: 股票数据
            market_trend: 市场趋势
            risk_preference: 风险偏好
            industry_preference: 行业偏好
        Returns:
            选中的股票DataFrame
        """
        try:
            logger.info(f"应用AI策略选股，市场趋势: {market_trend}, 风险偏好: {risk_preference}, 行业偏好: {industry_preference}")

            # 模拟行业过滤
            if industry_preference and '全部' not in industry_preference:
                stock_data = stock_data[stock_data['所属行业'].isin(industry_preference)]

            # 模拟AI策略
            # 这里只是简单模拟，实际应用中会使用更复杂的算法
            stock_data['ai_score'] = np.random.uniform(60, 95, size=len(stock_data))

            # 模拟根据风险偏好调整
            if risk_preference == '高风险':
                high_risk_count = Config.get('strategy.high_risk_count', 20)
                stock_data = stock_data.sort_values('ai_score', ascending=False).head(high_risk_count)
            elif risk_preference == '低风险':
                low_risk_count = Config.get('strategy.low_risk_count', 10)
                stock_data = stock_data.sort_values('ai_score', ascending=False).head(low_risk_count)
            else:
                medium_risk_count = Config.get('strategy.medium_risk_count', 15)
                stock_data = stock_data.sort_values('ai_score', ascending=False).head(medium_risk_count)

            logger.info(f"AI策略选股完成，选中股票数量: {len(stock_data)}")
            return stock_data
        except Exception as e:
            logger.error(f"AI策略选股失败: {str(e)}")
            return pd.DataFrame()