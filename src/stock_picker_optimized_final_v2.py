import pandas as pd
import numpy as np
import random
import time
import logging
import plotly.express as px
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import joblib
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stock_picker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("stock_picker")

# 确保模型目录存在
os.makedirs('models', exist_ok=True)

class DataLoader:
    """数据加载器类，负责获取和处理股票数据"""
    @staticmethod
    def fetch_stock_data() -> pd.DataFrame:
        """获取股票数据"""
        try:
            logger.info("开始获取股票数据")
            # 模拟获取A股列表
            stocks = [f'股票{i}' for i in range(1, 101)]
            
            # 模拟获取最新行情
            stock_data = pd.DataFrame({
                '股票代码': [f'STock{i:03d}' for i in range(1, 101)],
                '股票名称': stocks,
                '最新价': np.random.uniform(5, 100, 100),
                '涨跌幅': np.random.uniform(-10, 10, 100),
                '成交量': np.random.randint(1000, 20000, 100),
                '所属行业': random.choices(
                    ['金融', '白酒', '新能源', '通信', '房地产', '有色金属'],
                    k=100
                )
            })
            
            logger.info(f"成功获取{len(stock_data)}条股票数据")
            return stock_data
        except Exception as e:
            logger.error(f"获取股票数据时出错: {str(e)}")
            st.error(f"获取股票数据时出错: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def generate_performance_data() -> pd.DataFrame:
        """生成历史表现数据"""
        try:
            logger.info("开始生成历史表现数据")
            # 生成日期序列
            dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
            
            # 生成策略收益和上证指数收益
            strategy_returns = [0]
            index_returns = [0]
            
            for i in range(1, len(dates)):
                # 模拟策略收益
                strategy_returns.append(strategy_returns[-1] + random.uniform(-1, 2))
                # 模拟上证指数收益
                index_returns.append(index_returns[-1] + random.uniform(-1.2, 1.5))
            
            performance_data = pd.DataFrame({
                '日期': dates,
                '策略累计收益': strategy_returns,
                '上证指数收益': index_returns
            })
            
            logger.info(f"成功生成{len(performance_data)}条历史表现数据")
            return performance_data
        except Exception as e:
            logger.error(f"生成历史表现数据时出错: {str(e)}")
            st.error(f"生成历史表现数据时出错: {str(e)}")
            return pd.DataFrame()

class FeatureEngineer:
    """特征工程类，负责计算维度得分和创建特征"""
    @staticmethod
    def calculate_dimensions(stock_data: pd.DataFrame) -> pd.DataFrame:
        """计算天道、地道、人道维度得分"""
        try:
            logger.info("开始计算维度得分")
            
            # 计算天道维度得分 (市场趋势)
            stock_data['天道得分'] = np.random.uniform(60, 95, len(stock_data))
            
            # 计算地道维度得分 (公司基本面)
            stock_data['PE'] = np.random.uniform(10, 50, len(stock_data))
            stock_data['ROE'] = np.random.uniform(5, 25, len(stock_data))
            stock_data['净利润增长率'] = np.random.uniform(-20, 50, len(stock_data))
            
            pe_score = 100 - ((stock_data['PE'] - 10) / (50 - 10) * 80).clip(0, 80)
            roe_score = ((stock_data['ROE'] - 5) / (25 - 5) * 80).clip(0, 80)
            profit_growth_score = ((stock_data['净利润增长率'] + 20) / (50 + 20) * 80).clip(0, 80)
            
            stock_data['地道得分'] = (
                0.3 * pe_score + 
                0.4 * roe_score + 
                0.3 * profit_growth_score
            )
            
            # 计算人道维度得分 (市场情绪)
            stock_data['成交量变化'] = np.random.uniform(-30, 50, len(stock_data))
            stock_data['分析师评级'] = random.choices(['买入', '增持', '持有', '减持', '卖出'], k=len(stock_data))
            
            rating_map = {'买入': 90, '增持': 75, '持有': 60, '减持': 45, '卖出': 30}
            stock_data['评级分数'] = stock_data['分析师评级'].map(rating_map)
            
            stock_data['人道得分'] = (
                0.5 * ((stock_data['成交量变化'] + 30) / (50 + 30) * 80).clip(0, 80) +
                0.5 * stock_data['评级分数']
            )
            
            logger.info("成功计算维度得分")
            return stock_data
        except Exception as e:
            logger.error(f"计算维度得分时出错: {str(e)}")
            st.error(f"计算维度得分时出错: {str(e)}")
            return stock_data

    @staticmethod
    def create_target_variable(stock_data: pd.DataFrame) -> pd.DataFrame:
        """创建目标变量"""
        try:
            logger.info("开始创建目标变量")
            
            # 模拟预测涨跌幅
            stock_data['预测涨跌幅'] = np.random.uniform(-5, 10, len(stock_data))
            
            # 创建分类目标变量 (上涨/下跌)
            stock_data['上涨标签'] = (stock_data['预测涨跌幅'] > 0).astype(int)
            
            logger.info("成功创建目标变量")
            return stock_data
        except Exception as e:
            logger.error(f"创建目标变量时出错: {str(e)}")
            st.error(f"创建目标变量时出错: {str(e)}")
            return stock_data

class ModelTrainer:
    """模型训练类，负责训练和加载模型"""
    @staticmethod
    def train_model(stock_data: pd.DataFrame, retrain: bool = False) -> tuple:
        """训练模型"""
        try:
            logger.info("开始训练模型")
            
            # 检查是否需要重新训练
            if not retrain and os.path.exists('models/classification_model.pkl') and os.path.exists('models/regression_model.pkl'):
                logger.info("加载已存在的模型")
                classification_model = joblib.load('models/classification_model.pkl')
                regression_model = joblib.load('models/regression_model.pkl')
                return classification_model, regression_model
            
            # 准备特征和目标变量
            features = stock_data[['天道得分', '地道得分', '人道得分', 'PE', 'ROE', '净利润增长率']]
            classification_target = stock_data['上涨标签']
            regression_target = stock_data['预测涨跌幅']
            
            # 划分训练集和测试集
            X_train, X_test, y_train_class, y_test_class = train_test_split(
                features, classification_target, test_size=0.2, random_state=42
            )
            _, _, y_train_reg, y_test_reg = train_test_split(
                features, regression_target, test_size=0.2, random_state=42
            )
            
            # 标准化处理
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 训练分类模型
            class_param_grid = {
                'n_estimators': [50, 100, 150],
                'max_depth': [None, 10, 20]
            }
            classification_model = GridSearchCV(
                RandomForestClassifier(random_state=42),
                class_param_grid,
                cv=5
            )
            classification_model.fit(X_train_scaled, y_train_class)
            
            # 训练回归模型
            reg_param_grid = {
                'n_estimators': [50, 100, 150],
                'max_depth': [None, 10, 20]
            }
            regression_model = GridSearchCV(
                RandomForestRegressor(random_state=42),
                reg_param_grid,
                cv=5
            )
            regression_model.fit(X_train_scaled, y_train_reg)
            
            # 保存模型
            joblib.dump(classification_model, 'models/classification_model.pkl')
            joblib.dump(regression_model, 'model/regression_model.pkl')
            
            logger.info("成功训练并保存模型")
            return classification_model, regression_model
        except Exception as e:
            logger.error(f"训练模型时出错: {str(e)}")
            st.error(f"训练模型时出错: {str(e)}")
            return None, None

class StockSelectionStrategies:
    """选股策略类，包含各种选股策略"""
    @staticmethod
    def jiuzhou_strategy(market_trend: str, risk_preference: str, industry_preference: str) -> pd.DataFrame:
        """九州战略罗盘策略"""
        try:
            logger.info(f"开始执行九州战略罗盘策略，市场趋势: {market_trend}, 风险偏好: {risk_preference}, 行业偏好: {industry_preference}")
            
            # 1. 获取股票数据
            stock_data = DataLoader.fetch_stock_data()
            if stock_data.empty:
                return pd.DataFrame()
            
            # 2. 计算维度得分
            stock_data = FeatureEngineer.calculate_dimensions(stock_data)
            
            # 3. 调整权重 based on 市场趋势和风险偏好
            if market_trend == "上涨趋势":
                sky_weight = 0.4
                earth_weight = 0.3
                human_weight = 0.3
            elif market_trend == "震荡整理":
                sky_weight = 0.3
                earth_weight = 0.4
                human_weight = 0.3
            else:  # 下跌趋势
                sky_weight = 0.2
                earth_weight = 0.5
                human_weight = 0.3
            
            # 调整风险偏好
            if risk_preference == "激进型":
                sky_weight *= 1.2
                earth_weight *= 0.9
                human_weight *= 0.9
            elif risk_preference == "稳健型":
                sky_weight *= 0.9
                earth_weight *= 1.2
                human_weight *= 0.9
            
            # 归一化权重
            total_weight = sky_weight + earth_weight + human_weight
            sky_weight /= total_weight
            earth_weight /= total_weight
            human_weight /= total_weight
            
            # 4. 计算战略指数
            stock_data['战略指数'] = (
                sky_weight * stock_data['天道得分'] +
                earth_weight * stock_data['地道得分'] +
                human_weight * stock_data['人道得分']
            )
            
            # 5. 行业偏好筛选
            if industry_preference != "全行业":
                industry_stocks = stock_data[stock_data['所属行业'] == industry_preference]
                if len(industry_stocks) >= 10:
                    stock_data = industry_stocks
                else:
                    # 行业股票不足时，补充其他行业优质股票
                    logger.warning(f"{industry_preference}行业股票不足，补充其他行业优质股票")
                    top_industry_stocks = industry_stocks.nlargest(len(industry_stocks), '战略指数')
                    other_stocks = stock_data[stock_data['所属行业'] != industry_preference]
                    top_other_stocks = other_stocks.nlargest(10 - len(industry_stocks), '战略指数')
                    stock_data = pd.concat([top_industry_stocks, top_other_stocks])
            
            # 6. 添加预测涨跌幅
            stock_data = FeatureEngineer.create_target_variable(stock_data)
            
            # 7. 选择前10只股票
            selected_stocks = stock_data.nlargest(10, '战略指数')
            
            logger.info(f"成功执行九州战略罗盘策略，选出{len(selected_stocks)}只股票")
            return selected_stocks
        except Exception as e:
            logger.error(f"执行九州战略罗盘策略时出错: {str(e)}")
            st.error(f"执行九州战略罗盘策略时出错: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def ai_strategy(market_trend: str, risk_preference: str, industry_preference: str, retrain: bool = False) -> pd.DataFrame:
        """AI选股策略"""
        try:
            logger.info(f"开始执行AI选股策略，市场趋势: {market_trend}, 风险偏好: {risk_preference}, 行业偏好: {industry_preference}")
            
            # 1. 获取股票数据
            stock_data = DataLoader.fetch_stock_data()
            if stock_data.empty:
                return pd.DataFrame()
            
            # 2. 计算维度得分
            stock_data = FeatureEngineer.calculate_dimensions(stock_data)
            
            # 3. 创建目标变量和特征
            stock_data = FeatureEngineer.create_target_variable(stock_data)
            
            # 4. 训练或加载模型
            classification_model, regression_model = ModelTrainer.train_model(stock_data, retrain)
            if classification_model is None or regression_model is None:
                return pd.DataFrame()
            
            # 5. 准备特征
            features = stock_data[['天道得分', '地道得分', '人道得分', 'PE', 'ROE', '净利润增长率']]
            
            # 6. 标准化处理
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # 7. 预测上涨概率和涨跌幅
            stock_data['上涨概率'] = classification_model.predict_proba(features_scaled)[:, 1]
            stock_data['预测涨跌幅'] = regression_model.predict(features_scaled)
            
            # 8. 结合市场趋势、风险偏好和行业偏好进行筛选
            if market_trend == "上涨趋势" and risk_preference == "激进型":
                filtered_stocks = stock_data[stock_data['上涨概率'] > 0.7]
            elif market_trend == "下跌趋势" and risk_preference == "稳健型":
                filtered_stocks = stock_data[stock_data['上涨概率'] > 0.8]
            else:
                filtered_stocks = stock_data[stock_data['上涨概率'] > 0.65]
            
            # 行业偏好筛选
            if industry_preference != "全行业":
                industry_stocks = filtered_stocks[filtered_stocks['所属行业'] == industry_preference]
                if len(industry_stocks) >= 10:
                    filtered_stocks = industry_stocks
                else:
                    # 行业股票不足时，补充其他行业优质股票
                    logger.warning(f"{industry_preference}行业股票不足，补充其他行业优质股票")
                    top_industry_stocks = industry_stocks.nlargest(len(industry_stocks), '上涨概率')
                    other_stocks = filtered_stocks[filtered_stocks['所属行业'] != industry_preference]
                    top_other_stocks = other_stocks.nlargest(10 - len(industry_stocks), '上涨概率')
                    filtered_stocks = pd.concat([top_industry_stocks, top_other_stocks])
            
            # 9. 选择前10只股票
            selected_stocks = filtered_stocks.nlargest(10, '上涨概率')
            
            logger.info(f"成功执行AI选股策略，选出{len(selected_stocks)}只股票")
            return selected_stocks
        except Exception as e:
            logger.error(f"执行AI选股策略时出错: {str(e)}")
            st.error(f"执行AI选股策略时出错: {str(e)}")
            return pd.DataFrame()

class Backtester:
    """回测类，负责回测策略表现"""
    @staticmethod
    def backtest_strategy(strategy_func, *args, **kwargs) -> dict:
        """回测策略"""
        try:
            logger.info("开始回测策略")
            
            # 模拟回测
            total_returns = []
            win_rates = []
            max_drawdowns = []
            sharpe_ratios = []
            
            for _ in range(10):  # 模拟10次回测
                selected_stocks = strategy_func(*args, **kwargs)
                if not selected_stocks.empty:
                    # 计算回测指标
                    total_return = selected_stocks['预测涨跌幅'].mean()
                    win_rate = len(selected_stocks[selected_stocks['预测涨跌幅'] > 0]) / len(selected_stocks)
                    max_drawdown = random.uniform(2, 8)
                    sharpe_ratio = random.uniform(1, 3)
                    
                    total_returns.append(total_return)
                    win_rates.append(win_rate)
                    max_drawdowns.append(max_drawdown)
                    sharpe_ratios.append(sharpe_ratio)
            
            # 计算平均指标
            backtest_results = {
                '平均总收益率': np.mean(total_returns) if total_returns else 0,
                '平均胜率': np.mean(win_rates) if win_rates else 0,
                '平均最大回撤': np.mean(max_drawdowns) if max_drawdowns else 0,
                '平均夏普比率': np.mean(sharpe_ratios) if sharpe_ratios else 0
            }
            
            logger.info("成功完成回测")
            return backtest_results
        except Exception as e:
            logger.error(f"回测策略时出错: {str(e)}")
            st.error(f"回测策略时出错: {str(e)}")
            return {
                '平均总收益率': 0,
                '平均胜率': 0,
                '平均最大回撤': 0,
                '平均夏普比率': 0
            }

class StockPickerApp:
    """主应用类"""
    def __init__(self):
        """初始化应用"""
        self.title = "天机罗盘 - 奇门遁甲AI选股系统"
        self.subtitle = "融汇五行八卦之玄机，推演奇门遁甲之妙算，洞察天机运转之奥秘"

    def run(self):
        """运行应用"""
        try:
            logger.info("开始运行应用")
            
            # 页面配置
            st.set_page_config(
                page_title=self.title,
                page_icon="🔮",
                layout="wide"
            )
            
            # 顶部标题区域 - 天机罗盘主题设计
            st.markdown('''
            <style>
                .compass-container {
                    position: relative;
                    width: 100%;
                    height: 400px;
                    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
                    border-radius: 15px;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border: 3px solid #C0C0C0;
                }
                .bagua {
                    position: absolute;
                    width: 280px;
                    height: 280px;
                    background-image: linear-gradient(45deg, rgba(192, 192, 192, 0.3) 0%, transparent 50%, rgba(192, 192, 192, 0.3) 100%),
                                      linear-gradient(-45deg, rgba(192, 192, 192, 0.3) 0%, transparent 50%, rgba(192, 192, 192, 0.3) 100%);
                    border-radius: 50%;
                    border: 2px solid #C0C0C0;
                    opacity: 0.8;
                }
                .compass-needle {
                    position: absolute;
                    width: 180px;
                    height: 6px;
                    background: linear-gradient(90deg, transparent 0%, #FFFFFF 50%, transparent 100%);
                    transform-origin: center;
                    animation: rotate 20s linear infinite;
                }
                .compass-needle::before {
                    content: '';
                    position: absolute;
                    width: 12px;
                    height: 12px;
                    background-color: #FFFFFF;
                    border-radius: 50%;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                }
                .title-text {
                    margin-top: 20px;
                    color: #FFFFFF;
                    text-align: center;
                    text-shadow: 0 0 10px #C0C0C0, 0 0 20px #808080;
                }
                .main-title {
                    font-size: 2.2rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                    background: linear-gradient(90deg, #FFFFFF, #C0C0C0);
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                }
                .subtitle {
                    font-size: 1.2rem;
                    margin-bottom: 8px;
                }
                .metric-container {
                    background-color: rgba(10, 10, 26, 0.7);
                    padding: 15px;
                    border-radius: 10px;
                    border: 2px solid #C0C0C0;
                    margin-bottom: 20px;
                }
                .data-container {
                    background-color: rgba(10, 10, 26, 0.7);
                    padding: 15px;
                    border-radius: 10px;
                    border: 2px solid #C0C0C0;
                    margin-bottom: 20px;
                }
                .plot-container {
                    background-color: rgba(10, 10, 26, 0.7);
                    padding: 15px;
                    border-radius: 10px;
                    border: 2px solid #C0C0C0;
                    margin-bottom: 20px;
                }
                @keyframes rotate {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
            <div class="compass-container">
                <div class="bagua"></div>
                <div class="compass-needle"></div>
            </div>
            <div class="title-text">
                <div class="main-title">天机罗盘 - 奇门遁甲AI选股系统</div>
                <div class="subtitle">融汇五行八卦之玄机，推演奇门遁甲之妙算，洞察天机运转之奥秘</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # 侧边栏 - 用户参数设置
            st.sidebar.markdown('<h2 style="color: #FFFFFF; text-align: center;">选股参数设置</h2>', unsafe_allow_html=True)
            
            # 选股策略选择
            strategy_type = st.sidebar.selectbox(
                "选股策略",
                ["九州战略罗盘", "AI智能选股"],
                index=0,
                help="选择选股策略类型"
            )

            market_trend = st.sidebar.selectbox(
                "市场趋势判断",
                ["上涨趋势", "震荡整理", "下跌趋势"],
                index=0,
                help="选择您对当前市场趋势的判断"
            )
            
            risk_preference = st.sidebar.selectbox(
                "风险偏好",
                ["激进型", "平衡型", "稳健型"],
                index=1,
                help="根据您的风险承受能力选择"
            )
            
            industry_preference = st.sidebar.selectbox(
                "行业偏好",
                ["全行业", "金融", "白酒", "新能源", "通信", "房地产", "有色金属"],
                index=0,
                help="选择您感兴趣的行业"
            )
            
            # AI模型重训练选项
            retrain_model = False
            if strategy_type == "AI智能选股":
                retrain_model = st.sidebar.checkbox(
                    "重新训练AI模型",
                    value=False,
                    help="勾选此项以重新训练AI模型"
                )
            
            # 选股按钮
            if st.sidebar.button("🔮立即生成选股结果"):
                with st.spinner("🚀AI正在分析市场数据..."):
                    # 显示动画效果
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    # 执行选股策略
                    if strategy_type == "九州战略罗盘":
                        selected_stocks = StockSelectionStrategies.jiuzhou_strategy(
                            market_trend, risk_preference, industry_preference
                        )
                    else:  # AI智能选股
                        selected_stocks = StockSelectionStrategies.ai_strategy(
                            market_trend, risk_preference, industry_preference, retrain_model
                        )
                    
                    # 执行回测
                    backtest_results = Backtester.backtest_strategy(
                        StockSelectionStrategies.jiuzhou_strategy,
                        market_trend, risk_preference, industry_preference
                    )
                    
                    # 显示选股结果
                    st.markdown("## 🎯今日精选股票")
                    
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
                    
                    # 股票表格 - 彩色编码
                    st.markdown('<div class="data-container">', unsafe_allow_html=True)
                    styled_df = selected_stocks.style.map(
                        lambda x: 'background-color: #FFE4E1' if x > 0 else 'background-color: #E0FFFF', 
                        subset=['涨跌幅', '预测涨跌幅']
                    ).format({
                        '涨跌幅': '{:.2f}%',
                        '预测涨跌幅': '{:.2f}%'
                    })
                    st.dataframe(styled_df, height=400)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 各维度得分分布
                    st.markdown("## 📊维度分析")
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    
                    # 计算各行业平均维度得分
                    industry_scores = selected_stocks.groupby('所属行业')[['天道得分', '地道得分', '人道得分']].mean().reset_index()
                    industry_scores = pd.melt(industry_scores, id_vars=['所属行业'], var_name='维度', value_name='平均得分')
                    
                    fig = px.bar(industry_scores, x='所属行业', y='平均得分', color='维度', barmode='group',
                                title='各行业维度得分对比',
                                color_discrete_sequence=['#4169E1', '#FF4500', '#228B22'])
                    
                    fig.update_layout(
                        font=dict(size=14),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 行业分布
                    st.markdown("## 📊行业分布")
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    
                    industry_distribution = selected_stocks['所属行业'].value_counts().reset_index()
                    industry_distribution.columns = ['行业', '数量']
                    
                    fig = px.pie(industry_distribution, values='数量', names='行业',
                                title='选股行业分布',
                                color_discrete_sequence=px.colors.qualitative.Set3)
                    
                    fig.update_layout(
                        font=dict(size=14),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 历史表现图表
                    st.markdown("## 📈策略历史表现")
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    performance_data = DataLoader.generate_performance_data()
                    
                    fig = px.line(performance_data, x="日期", y=["策略累计收益", "上证指数收益"], 
                                 title="策略历史收益率对比",
                                 labels={"value": "收益率(%)", "variable": "指标"},
                                 color_discrete_sequence=["#FF4500", "#4169E1"])
                    
                    fig.update_layout(
                        font=dict(size=14),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 回测结果
                    st.markdown("## 📊策略回测结果")
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    
                    backtest_df = pd.DataFrame({
                        '指标': ['平均总收益率', '平均胜率', '平均最大回撤', '平均夏普比率'],
                        '数值': [
                            f"{backtest_results['平均总收益率']:.2f}%",
                            f"{backtest_results['平均胜率']*100:.2f}%",
                            f"{backtest_results['平均最大回撤']:.2f}%",
                            f"{backtest_results['平均夏普比率']:.2f}"
                        ]
                    })
                    
                    st.dataframe(backtest_df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 底部说明
                    st.markdown("""
                    <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin-top: 20px;">
                        <p style="font-size: 0.9rem; color: #666;">
                            📌 注意：本工具仅供参考，不构成投资建议。股市有风险，投资需谨慎。
                        </p>
                        <p style="font-size: 0.9rem; color: #666;">
                            💡 策略说明：本系统基于先进的AI算法和多维度分析，为您提供专业的选股建议。
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
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
                """)
                
                # 模拟数据展示
                st.markdown("### 📈历史策略表现")
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                performance_data = DataLoader.generate_performance_data()
                
                fig = px.line(performance_data, x="日期", y=["策略累计收益", "上证指数收益"], 
                             title="策略历史收益率对比",
                             labels={"value": "收益率(%)", "variable": "指标"},
                             color_discrete_sequence=["#FF4500", "#4169E1"])
                
                fig.update_layout(
                    font=dict(size=14),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            logger.info("成功运行应用")
        except Exception as e:
            logger.error(f"运行应用时出错: {str(e)}")
            st.error(f"系统出错: {str(e)}")

def main() -> None:
    """主函数"""
    app = StockPickerApp()
    app.run()

if __name__ == "__main__":
    main()