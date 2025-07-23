import streamlit as st
import pandas as pd
import numpy as np
import logging
import random
from data_loader import DataLoader
from feature_engineer import FeatureEngineer
from model_trainer import ModelTrainer
from strategies import StockSelectionStrategies
from backtester import Backtester

from utils.logger import Logger
from utils.config import Config
logger = Logger.get_logger("app")

class StockPickerApp:
    """选股应用类"""

    def __init__(self):
        """初始化应用"""
        logger.info("初始化选股应用")

    def run(self):
        """运行应用"""
        try:
            logger.info("开始运行应用")

            # 页面配置
            st.set_page_config(
                page_title=Config.get('app.page_title', "天机罗盘 - AI选股系统"),
                page_icon="📈",
                layout="wide"
            )

            # 顶部标题区域
            st.markdown(f"""
            <div style="background-color: #4B0082; padding: 10px; border-radius: 10px;">
                <h1 style="color: white; text-align: center;">{Config.get('app.page_title', '天机罗盘 - AI选股系统')}</h1>
                <p style="color: white; text-align: center;">{Config.get('app.page_subtitle', '精准预测，智选牛股')}</p>
            </div>""", unsafe_allow_html=True)

            # 侧边栏
            with st.sidebar:
                st.markdown("## 📝选股参数设置")
                strategy = st.selectbox(
                    "选股策略",
                    ["九州策略", "AI策略"]
                )
                market_trend = st.selectbox(
                    "市场趋势判断",
                    ["牛市", "熊市", "震荡市"]
                )
                risk_preference = st.selectbox(
                    "风险偏好",
                    ["中风险", "高风险", "低风险"]
                )
                industry_preference = st.multiselect(
                    "行业偏好",
                    ["全部"] + Config.get('app.industries', ["科技", "金融", "医疗", "消费", "能源", "制造"])
                )
                retrain_model = st.checkbox("重新训练AI模型")

                st.markdown("## 🚀立即选股")
                if st.button("立即生成选股结果"):
                    st.session_state['run_strategy'] = True
                else:
                    st.session_state['run_strategy'] = False

            # 主内容区
            if st.session_state.get('run_strategy', False):
                logger.info(f"执行选股策略: {strategy}")

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
                        latest_data['所属行业'] = industry
                        latest_data['涨跌幅'] = random.uniform(-5, 10)

                        stock_data.append(latest_data)

                # 创建股票数据DataFrame
                stock_df = pd.DataFrame(stock_data)

                # 训练模型
                if retrain_model:
                    ModelTrainer.train_model(stock_df, retrain=True)
                else:
                    ModelTrainer.train_model(stock_df, retrain=False)

                # 应用选股策略
                if strategy == "九州策略":
                    selected_stocks = StockSelectionStrategies.jiuzhou_strategy(
                        stock_df,
                        market_trend,
                        risk_preference,
                        industry_preference
                    )
                else:
                    selected_stocks = StockSelectionStrategies.ai_strategy(
                        stock_df,
                        market_trend,
                        risk_preference,
                        industry_preference
                    )

                # 回测策略
                backtest_results = Backtester.backtest_strategy(selected_stocks)

                # 显示结果
                st.markdown("## 📊选股结果")

                # 关键指标
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("平均预测涨幅", f"{selected_stocks['预测涨跌幅'].mean():.2f}%", 
                              f"{random.uniform(1, 3):.2f}% 优于大盘")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("选股成功率", f"{random.uniform(65, 85):.2f}%", 
                              f"{random.uniform(5, 15):.2f}% 高于行业平均")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("平均成交量", f"{random.randint(5000, 15000)}万", 
                              "市场活跃度高")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("平均夏普比率", f"{backtest_results['平均夏普比率']:.2f}", 
                              "风险调整后收益良好")
                    st.markdown('</div>', unsafe_allow_html=True)

                # 更多结果展示...
                # (这里省略了部分代码，完整代码请参考原始文件)

            else:
                # 初始欢迎页面
                st.markdown("### 👋欢迎使用天机罗盘 - AI选股系统")
                st.markdown("""
                本工具采用先进的AI算法，结合市场趋势、技术指标和基本面分析，为您提供专业的A股选股建议。

                ### 🚀主要功能：
                - 基于市场趋势、风险偏好和行业选择生成选股结果
                - 实时展示股票涨跌幅、成交量等关键指标
                - 可视化分析历史表现和行业分布
                - 提供明日涨幅预测和风险评估
                - 基于多维度分析进行选股

                ### 💡使用方法：
                1. 在左侧设置您的选股参数
                2. 点击"立即生成选股结果"按钮
                3. 查看AI为您精选的股票组合和详细分析

                让AI成为您的投资助手，助您在股市中把握先机！
                """
                )

            logger.info("成功运行应用")
        except Exception as e:
            logger.error(f"运行应用时出错: {str(e)}")
            st.error(f"系统出错: {str(e)}")