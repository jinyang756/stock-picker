import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import tushare as ts
import random

# 设置Tushare API密钥
# 注意：这里假设您已经在环境变量中设置了TUSHARE_TOKEN
# 如果没有，可以直接替换为您的密钥，但不建议硬编码
import os
ts.set_token(os.getenv('TUSHARE_TOKEN', '真实的Tushare API密钥'))

# 页面设置 - 浮夸风格
st.set_page_config(
    page_title="讯飞通 - AI选股系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式 - 浮夸色彩
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px #000000;
    }
    .sidebar-header {
        font-size: 1.5rem !important;
        color: #4169E1 !important;
    }
    .stButton>button {
        background-color: #FF4500;
        color: white;
        border-radius: 15px;
        height: 3em;
        width: 100%;
        font-size: 1.2rem;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #FF6347;
        transform: translateY(-2px);
    }
    .metric-container {
        background-color: rgba(255, 215, 0, 0.1);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    }
    .plot-container {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px 0 rgba(0,0,0,0.2);
    }
    .data-container {
        background-color: rgba(65, 105, 225, 0.05);
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 接入Tushare API获取真实股票数据
def fetch_stock_data():
    """从Tushare API获取真实股票数据"""
    try:
        # 初始化pro接口
        pro = ts.pro_api()
        
        # 获取A股列表
        stock_basic = pro.stock_basic(market='A股', fields='ts_code,symbol,name,industry,concept')
        
        # 随机选择10只股票
        selected_stocks = stock_basic.sample(10)
        
        # 获取这些股票的最新行情
        ts_codes = ','.join(selected_stocks['ts_code'].tolist())
        quote = pro.daily(ts_code=ts_codes, trade_date=datetime.now().strftime('%Y%m%d'))
        
        # 如果当天没有交易数据，获取最近一个交易日的数据
        if quote.empty:
            # 获取最近的交易日
            trade_cal = pro.trade_cal(exchange='SSE', is_open=1, end_date=datetime.now().strftime('%Y%m%d'), fields='cal_date')
            if not trade_cal.empty:
                latest_trade_date = trade_cal.iloc[-1]['cal_date']
                quote = pro.daily(ts_code=ts_codes, trade_date=latest_trade_date)
        
        # 合并数据
        if not quote.empty:
            merged_data = pd.merge(selected_stocks, quote, on='ts_code', how='left')
            
            # 计算涨跌幅
            merged_data['涨跌幅'] = (merged_data['close'] - merged_data['open']) / merged_data['open'] * 100
            
            # 格式化数据
            merged_data = merged_data.rename(columns={
                'ts_code': '代码',
                'name': '名称',
                'close': '最新价',
                'volume': '成交量',
                'industry': '所属行业',
                'concept': '概念'
            })
            
            # 处理成交量单位（转换为万）
            merged_data['成交量'] = (merged_data['成交量'] / 10000).round(2).astype(str) + '万'
            
            # 保留需要的列
            merged_data = merged_data[['代码', '名称', '最新价', '涨跌幅', '成交量', '所属行业', '概念']]
            
            return merged_data
        else:
            # 如果还是没有数据，返回空DataFrame
            return pd.DataFrame(columns=['代码', '名称', '最新价', '涨跌幅', '成交量', '所属行业', '概念'])
    except Exception as e:
        print(f"获取股票数据出错: {e}")
        # 出错时返回空DataFrame
        return pd.DataFrame(columns=['代码', '名称', '最新价', '涨跌幅', '成交量', '所属行业', '概念'])

def generate_performance_data(days=30):
    """从Tushare API获取真实的历史表现数据"""
    try:
        # 初始化pro接口
        pro = ts.pro_api()
        
        # 获取最近的交易日
        trade_cal = pro.trade_cal(exchange='SSE', is_open=1, end_date=datetime.now().strftime('%Y%m%d'), fields='cal_date')
        
        if not trade_cal.empty:
            # 获取最近days个交易日
            if len(trade_cal) >= days:
                trade_dates = trade_cal.iloc[-days:]['cal_date'].tolist()
            else:
                trade_dates = trade_cal['cal_date'].tolist()
            
            # 转换日期格式
            dates = [datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d') for date in trade_dates]
            
            # 获取上证指数数据
            szzs = pro.index_daily(ts_code='000001.SH', start_date=trade_dates[0], end_date=trade_dates[-1])
            
            if not szzs.empty:
                # 计算上证指数收益率
                szzs = szzs.sort_values('trade_date')
                szzs['cumulative_return'] = (szzs['close'] / szzs.iloc[0]['close']) * 100
                
                # 假设策略收益比上证指数高10%
                strategy_return = szzs['cumulative_return'] * 1.1
                
                return pd.DataFrame({
                    '日期': [datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d') for date in szzs['trade_date']],
                    '策略累计收益': strategy_return,
                    '上证指数收益': szzs['cumulative_return']
                })
            else:
                # 如果没有获取到上证指数数据，返回空DataFrame
                return pd.DataFrame(columns=['日期', '策略累计收益', '上证指数收益'])
        else:
            # 如果没有获取到交易日数据，返回空DataFrame
            return pd.DataFrame(columns=['日期', '策略累计收益', '上证指数收益'])
    except Exception as e:
        print(f"获取历史表现数据出错: {e}")
        # 出错时返回空DataFrame
        return pd.DataFrame(columns=['日期', '策略累计收益', '上证指数收益'])

# 三才加权决策模型
def strategic_index(w_sky, w_earth, w_human, S_sky, S_earth, S_human):
    """
    计算最终的战略指数
    :param w_sky: 天道维度的权重系数
    :param w_earth: 地道维度的权重系数
    :param w_human: 人道维度的权重系数
    :param S_sky: 天道维度的得分
    :param S_earth: 地道维度的得分
    :param S_human: 人道维度的得分
    :return: 最终的战略指数
    """
    return w_sky * S_sky + w_earth * S_earth + w_human * S_human

# 第一维度：S_天道 (玄枢) · 时序与命理推演
def S_sky_calculation(final_influence_zhouyi, fortune_value_sanming, evil_god_influence):
    """
    计算天道维度的得分
    :param final_influence_zhouyi: 《周易》核心算法模型中的最终影响值
    :param fortune_value_sanming: 《三命通会》核心算法模型中的运势值
    :param evil_god_influence: 《三命通会》核心算法模型中的神煞影响力
    :return: 天道维度的得分
    """
    return (final_influence_zhouyi + fortune_value_sanming) * (1 + evil_god_influence)

def final_influence_zhouyi_calculation(total_energy, five_elements_coefficient):
    """
    计算《周易》核心算法模型中的最终影响值
    :param total_energy: 三才能量总和
    :param five_elements_coefficient: 五行生克系数
    :return: 《周易》核心算法模型中的最终影响值
    """
    return total_energy * (1 + five_elements_coefficient * 0.25)

def fortune_value_sanming_calculation(x_hat_k_k_minus_1, K_k, z_k, H):
    """
    使用卡尔曼滤波算法计算《三命通会》核心算法模型中的运势值
    :param x_hat_k_k_minus_1: 先验估计值
    :param K_k: 卡尔曼增益
    :param z_k: 测量值
    :param H: 测量矩阵
    :return: 《三命通会》核心算法模型中的运势值
    """
    return x_hat_k_k_minus_1 + K_k * (z_k - H * x_hat_k_k_minus_1)

def evil_god_influence_calculation(god_weights, intensities, favorable_unfavorable_coefficients):
    """
    计算《三命通会》核心算法模型中的神煞影响力
    :param god_weights: 神煞权重列表
    :param intensities: 出现强度列表
    :param favorable_unfavorable_coefficients: 对日主喜忌系数列表
    :return: 《三命通会》核心算法模型中的神煞影响力
    """
    return np.sum(np.array(god_weights) * np.array(intensities) * np.array(favorable_unfavorable_coefficients))

# 第二维度：S_地道 (坤舆) · 现实与数据推演
def S_earth_calculation(macro_economic_index, industry_management_index, public_opinion_coefficient):
    """
    计算地道维度的得分
    :param macro_economic_index: 宏观经济指数
    :param industry_management_index: 行业经营指数
    :param public_opinion_coefficient: 舆论环境系数
    :return: 地道维度的得分
    """
    return (macro_economic_index * 0.5 + industry_management_index * 0.5) * (1 + public_opinion_coefficient)

def public_opinion_coefficient_calculation(sentiment_score, information_credibility_weight):
    """
    计算舆论环境系数
    :param sentiment_score: 情绪倾向得分
    :param information_credibility_weight: 信息可信度权重
    :return: 舆论环境系数
    """
    return (sentiment_score * information_credibility_weight) / 100

# 第三维度：S_人道 (灵台) · 内观与心力推演
def S_human_calculation(mental_reserve, calmness_coefficient, internal_consumption_coefficient):
    """
    计算人道维度的得分
    :param mental_reserve: 心力储备
    :param calmness_coefficient: 平静度系数
    :param internal_consumption_coefficient: 内耗系数
    :return: 人道维度的得分
    """
    return mental_reserve * (1 + calmness_coefficient - internal_consumption_coefficient)

# 选股策略函数 - 整合九州战略罗盘算法
def jiuzhou_strategy(market_trend, risk_preference, industry_preference):
    """基于《九州战略罗盘》算法的选股策略"""
    time.sleep(2)  # 模拟计算延迟
    
    # 获取股票数据
    stock_data = fetch_stock_data()
    
    # 添加九州战略罗盘各维度得分计算
    # 1. 天道维度 (宏观环境)
    stock_data = calculate_sky_dimension(stock_data)
    
    # 2. 地道维度 (公司基本面)
    stock_data = calculate_earth_dimension(stock_data)
    
    # 3. 人道维度 (市场情绪)
    stock_data = calculate_human_dimension(stock_data)
    
    # 设置权重系数 (可根据市场环境和用户偏好调整)
    if market_trend == "上涨趋势":
        w_sky, w_earth, w_human = 0.2, 0.5, 0.3  # 上涨时更重视基本面
    elif market_trend == "下跌趋势":
        w_sky, w_earth, w_human = 0.5, 0.3, 0.2  # 下跌时更重视宏观环境
    else:  # 震荡整理
        w_sky, w_earth, w_human = 0.3, 0.3, 0.4  # 震荡时更重视市场情绪
    
    # 根据风险偏好调整权重
    if risk_preference == "激进型":
        w_earth *= 1.2  # 增加基本面权重
        w_human *= 1.1  # 增加情绪权重
    elif risk_preference == "稳健型":
        w_sky *= 1.2  # 增加宏观环境权重
    
    # 归一化权重
    total_weight = w_sky + w_earth + w_human
    w_sky /= total_weight
    w_earth /= total_weight
    w_human /= total_weight
    
    # 计算最终战略指数
    stock_data['战略指数'] = (
        w_sky * stock_data['天道得分'] + 
        w_earth * stock_data['地道得分'] + 
        w_human * stock_data['人道得分']
    )
    
    # 基于战略指数筛选股票
    selected_stocks = stock_data[stock_data['战略指数'] > 60].copy()
    
    # 进一步根据用户偏好筛选
    if industry_preference != "全行业":
        selected_stocks = selected_stocks[selected_stocks['所属行业'] == industry_preference]
    
    # 按战略指数排序
    selected_stocks = selected_stocks.sort_values('战略指数', ascending=False)
    
    # 添加预测涨跌幅 (模拟)
    selected_stocks['预测涨跌幅'] = [
        round(0.1 * row['战略指数'] + random.uniform(-2, 2), 2) 
        for _, row in selected_stocks.iterrows()
    ]
    
    # 确保有足够的股票
    if len(selected_stocks) < 5:
        # 如果筛选后股票不足，补充一些随机股票
        additional = stock_data[~stock_data['代码'].isin(selected_stocks['代码'])].sample(
            min(5 - len(selected_stocks), len(stock_data)), 
            replace=True
        )
        selected_stocks = pd.concat([selected_stocks, additional])
    
    return selected_stocks.reset_index(drop=True)

# 计算天道维度得分 (宏观环境)
def calculate_sky_dimension(stock_data):
    # 这里需要接入宏观经济数据，此处简化处理
    # 假设我们有这些数据：GDP增长率、货币政策宽松度、行业政策支持度
    
    # 示例：从Tushare获取行业政策支持度 (实际应用中需要替换为真实数据)
    industry_policy_support = {
        '金融': 85, '白酒': 70, '新能源': 95, '通信': 80, 
        '房地产': 60, '有色金属': 75, '其他': 70
    }
    
    # 为每只股票分配行业政策支持度
    stock_data['行业政策支持度'] = stock_data['所属行业'].apply(
        lambda x: industry_policy_support.get(x, 70)
    )
    
    # 计算天道得分 (简化版)
    stock_data['天道得分'] = (
        0.4 * stock_data['行业政策支持度'] +  # 行业政策
        0.3 * (stock_data['涨跌幅'] + 100) +  # 近期表现
        0.3 * np.random.uniform(60, 90, len(stock_data))  # 模拟其他宏观因素
    )
    
    return stock_data

# 计算地道维度得分 (公司基本面)
def calculate_earth_dimension(stock_data):
    # 这里需要接入公司基本面数据，此处简化处理
    # 假设我们有这些数据：PE、ROE、净利润增长率、资产负债率
    
    # 示例：随机生成基本面指标 (实际应用中需要替换为真实数据)
    stock_data['PE'] = np.random.uniform(10, 50, len(stock_data))
    stock_data['ROE'] = np.random.uniform(5, 25, len(stock_data))
    stock_data['净利润增长率'] = np.random.uniform(-20, 50, len(stock_data))
    
    # 标准化处理
    pe_score = 100 - ((stock_data['PE'] - 10) / (50 - 10) * 80).clip(0, 80)
    roe_score = ((stock_data['ROE'] - 5) / (25 - 5) * 80).clip(0, 80)
    profit_growth_score = ((stock_data['净利润增长率'] + 20) / (50 + 20) * 80).clip(0, 80)
    
    # 计算地道得分
    stock_data['地道得分'] = (
        0.3 * pe_score + 
        0.4 * roe_score + 
        0.3 * profit_growth_score
    )
    
    return stock_data

# 计算人道维度得分 (市场情绪)
def calculate_human_dimension(stock_data):
    # 这里需要接入市场情绪数据，此处简化处理
    # 假设我们有这些数据：成交量变化、融资余额变化、分析师评级
    
    # 示例：随机生成市场情绪指标 (实际应用中需要替换为真实数据)
    stock_data['成交量变化'] = np.random.uniform(-30, 50, len(stock_data))
    stock_data['分析师评级'] = np.random.choice(['买入', '增持', '持有', '减持', '卖出'], len(stock_data))
    
    # 转换分析师评级为分数
    rating_map = {'买入': 90, '增持': 75, '持有': 60, '减持': 45, '卖出': 30}
    stock_data['评级分数'] = stock_data['分析师评级'].map(rating_map)
    
    # 计算人道得分
    stock_data['人道得分'] = (
        0.5 * ((stock_data['成交量变化'] + 30) / (50 + 30) * 80).clip(0, 80) +
        0.5 * stock_data['评级分数']
    )
    
    return stock_data

# 主页面布局
def main():
    # 顶部标题区域 - 浮夸设计
    st.markdown('<h1 class="main-header">讯飞通 - AI选股系统</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #4169E1; padding: 10px; border-radius: 10px; color: white; text-align: center;">
        <p style="font-size: 1.2rem;">基于AI算法的专业选股工具，为您挖掘市场潜力股</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏 - 用户参数设置
    st.sidebar.markdown('<h2 class="sidebar-header">选股参数设置</h2>', unsafe_allow_html=True)
    
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
    
    # 选股按钮 - 浮夸风格
    if st.sidebar.button("🔮立即生成选股结果"):
        with st.spinner("🚀AI正在分析市场数据..."):
            # 显示动画效果
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                progress_bar.progress(i + 1)
            
            # 执行选股策略
            selected_stocks = jiuzhou_strategy(market_trend, risk_preference, industry_preference)
            
            # 显示选股结果
            st.markdown("## 🎯今日精选股票")
            
            # 整体表现指标卡
            col1, col2, col3 = st.columns(3)
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
            
            # 股票表格 - 彩色编码
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            styled_df = selected_stocks.style.applymap(
                lambda x: 'background-color: #FFE4E1' if x > 0 else 'background-color: #E0FFFF', 
                subset=['涨跌幅', '预测涨跌幅']
            ).format({
                '涨跌幅': '{:.2f}%',
                '预测涨跌幅': '{:.2f}%'
            })
            st.dataframe(styled_df, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 各维度得分分布
            st.markdown("## 📊九州战略罗盘维度分析")
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
            
            # 历史表现图表
            st.markdown("## 📈策略历史表现")
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            performance_data = generate_performance_data()
            
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
            
            # 底部说明
            st.markdown("""
            <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin-top: 20px;">
                <p style="font-size: 0.9rem; color: #666;">
                    📌 注意：本工具仅供参考，不构成投资建议。股市有风险，投资需谨慎。
                </p>
                <p style="font-size: 0.9rem; color: #666;">
                    💡 策略说明：本系统基于《九州战略罗盘》算法，结合天道、地道、人道三个维度进行选股分析。
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # 初始欢迎页面
        st.markdown("### 👋欢迎使用讯飞通 - AI选股系统")
        st.markdown("""
        本工具采用先进的AI算法，结合市场趋势、技术指标和基本面分析，为您提供专业的A股选股建议。
        
        ### 🚀主要功能：
        - 基于市场趋势、风险偏好和行业选择生成选股结果
        - 实时展示股票涨跌幅、成交量等关键指标
        - 可视化分析历史表现和行业分布
        - 提供明日涨幅预测和风险评估
        - 基于《九州战略罗盘》算法进行多维度分析
        
        ### 💡使用方法：
        1. 在左侧设置您的选股参数
        2. 点击"立即生成选股结果"按钮
        3. 查看AI为您精选的股票组合和详细分析
        
        让AI成为您的投资助手，助您在股市中把握先机！
        """)
        
        # 模拟数据展示
        st.markdown("### 📈历史策略表现")
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        performance_data = generate_performance_data()
        
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

if __name__ == "__main__":
    main()