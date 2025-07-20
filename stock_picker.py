import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import random
import time
from PIL import Image

# 页面设置 - 浮夸风格
st.set_page_config(
    page_title="财富魔方 - A股智能选股系统",
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

# 模拟数据生成 - 实际使用时替换为真实API调用
def fetch_stock_data():
    """生成模拟股票数据"""
    stock_list = [
        {"代码": "000001.SZ", "名称": "平安银行", "最新价": round(random.uniform(10, 30), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "银行", "概念": "金融科技"},
        {"代码": "000002.SZ", "名称": "万科A", "最新价": round(random.uniform(15, 35), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "房地产", "概念": "物业管理"},
        {"代码": "000063.SZ", "名称": "中兴通讯", "最新价": round(random.uniform(20, 50), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "通信设备", "概念": "5G"},
        {"代码": "000568.SZ", "名称": "泸州老窖", "最新价": round(random.uniform(150, 300), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "白酒", "概念": "消费升级"},
        {"代码": "002594.SZ", "名称": "比亚迪", "最新价": round(random.uniform(200, 350), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "汽车整车", "概念": "新能源车"},
        {"代码": "300750.SZ", "名称": "宁德时代", "最新价": round(random.uniform(350, 600), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "电力设备", "概念": "动力电池"},
        {"代码": "600030.SH", "名称": "中信证券", "最新价": round(random.uniform(20, 40), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "证券", "概念": "金融"},
        {"代码": "600519.SH", "名称": "贵州茅台", "最新价": round(random.uniform(1500, 2000), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "白酒", "概念": "消费"},
        {"代码": "601318.SH", "名称": "中国平安", "最新价": round(random.uniform(40, 80), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "保险", "概念": "金融科技"},
        {"代码": "601899.SH", "名称": "紫金矿业", "最新价": round(random.uniform(8, 15), 2), 
         "涨跌幅": round(random.uniform(-5, 5), 2), "成交量": f"{random.randint(1000, 10000)}万",
         "所属行业": "有色金属", "概念": "黄金"},
    ]
    
    # 随机选择5-8只股票作为选股结果
    selected_stocks = random.sample(stock_list, random.randint(5, 8))
    return pd.DataFrame(selected_stocks)

def generate_performance_data(days=30):
    """生成模拟的选股策略历史表现数据"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days, 0, -1)]
    
    # 生成模拟的收益率数据 - 整体呈上升趋势，但有波动
    base_return = 0.005  # 基础日收益率
    volatility = 0.02    # 波动率
    
    daily_returns = [base_return + random.uniform(-volatility, volatility) for _ in range(days)]
    cumulative_returns = [(1 + r) for r in daily_returns]
    for i in range(1, days):
        cumulative_returns[i] *= cumulative_returns[i-1]
    
    # 上证指数对比数据
    szzs_returns = [base_return * 0.7 + random.uniform(-volatility*0.8, volatility*0.8) for _ in range(days)]
    szzs_cumulative = [(1 + r) for r in szzs_returns]
    for i in range(1, days):
        szzs_cumulative[i] *= szzs_cumulative[i-1]
    
    return pd.DataFrame({
        '日期': dates,
        '策略累计收益': [r*100 for r in cumulative_returns],
        '上证指数收益': [r*100 for r in szzs_cumulative]
    })

# 选股策略函数 - 简易实现
def simple_strategy(market_trend, risk_preference, industry_preference):
    """根据用户选择的参数执行简易选股策略"""
    time.sleep(2)  # 模拟计算延迟
    
    # 获取股票数据
    stock_data = fetch_stock_data()
    
    # 基于用户偏好做简单筛选 - 实际应用中可替换为更复杂的策略
    if market_trend == "上涨趋势":
        stock_data = stock_data[stock_data['涨跌幅'] > 0].copy()
    elif market_trend == "下跌趋势":
        # 在下跌趋势中寻找逆势上涨的股票
        stock_data = stock_data[stock_data['涨跌幅'] > 1].copy()
    
    if risk_preference == "激进型":
        # 高波动股票
        stock_data = stock_data.sample(frac=0.8)
    elif risk_preference == "稳健型":
        # 筛选行业龙头
        leaders = ["贵州茅台", "宁德时代", "比亚迪", "中国平安", "中信证券"]
        stock_data = stock_data[stock_data['名称'].isin(leaders)].copy()
    
    if industry_preference != "全行业":
        stock_data = stock_data[stock_data['所属行业'] == industry_preference].copy()
    
    # 添加模拟的明日预测涨跌幅
    stock_data['预测涨跌幅'] = [round(random.uniform(-3, 5), 2) for _ in range(len(stock_data))]
    
    # 随机选择5-8只股票作为最终结果
    if len(stock_data) > 8:
        stock_data = stock_data.sample(8)
    elif len(stock_data) < 5:
        # 如果筛选后股票不足，补充一些随机股票
        all_stocks = fetch_stock_data()
        needed = 5 - len(stock_data)
        additional = all_stocks[~all_stocks['代码'].isin(stock_data['代码'])].sample(needed)
        stock_data = pd.concat([stock_data, additional])
    
    return stock_data.reset_index(drop=True)

# 主页面布局
def main():
    # 顶部标题区域 - 浮夸设计
    st.markdown('<h1 class="main-header">财富魔方 - A股智能选股系统</h1>', unsafe_allow_html=True)
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
            selected_stocks = simple_strategy(market_trend, risk_preference, industry_preference)
            
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
            
            # 历史表现图表
            st.markdown("## 📊策略历史表现")
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
            
            # 行业分布图表
            st.markdown("## 🏭行业分布分析")
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            industry_counts = selected_stocks['所属行业'].value_counts().reset_index()
            industry_counts.columns = ['行业', '数量']
            
            fig = px.pie(industry_counts, values='数量', names='行业', 
                         title='选股结果行业分布',
                         color_discrete_sequence=px.colors.qualitative.Set3)
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 底部说明
            st.markdown("""
            <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin-top: 20px;">
                <p style="font-size: 0.9rem; color: #666;">
                    📌 注意：本工具仅供参考，不构成投资建议。股市有风险，投资需谨慎。
                </p>
                <p style="font-size: 0.9rem; color: #666;">
                    💡 策略说明：本系统基于多因子模型和机器学习算法，结合市场趋势和技术指标进行选股。
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # 初始欢迎页面
        st.markdown("### 👋欢迎使用财富魔方选股系统")
        st.markdown("""
        本工具采用先进的AI算法，结合市场趋势、技术指标和基本面分析，为您提供专业的A股选股建议。
        
        ### 🚀主要功能：
        - 基于市场趋势、风险偏好和行业选择生成选股结果
        - 实时展示股票涨跌幅、成交量等关键指标
        - 可视化分析历史表现和行业分布
        - 提供明日涨幅预测和风险评估
        
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