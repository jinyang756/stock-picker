# 天机罗盘 - AI选股系统

## 项目介绍

天机罗盘是一个基于AI算法的选股系统，结合市场趋势、技术指标和基本面分析，为用户提供专业的A股选股建议。

## 项目结构

```
stock-picker/
├── src/
│   ├── data_loader.py       # 数据加载模块
│   ├── feature_engineer.py  # 特征工程模块
│   ├── model_trainer.py     # 模型训练模块
│   ├── strategies.py        # 选股策略模块
│   ├── backtester.py        # 回测模块
│   ├── app.py               # 应用界面模块
│   └── main.py              # 主入口文件
├── models/                  # 模型保存目录
├── tests/                   # 测试目录
├── docs/                    # 文档目录
├── utils/                   # 工具函数目录
├── requirements.txt         # 依赖库列表
└── README.md                # 项目说明
```

## 功能特点

1. 基于市场趋势、风险偏好和行业选择生成选股结果
2. 实时展示股票涨跌幅、成交量等关键指标
3. 可视化分析历史表现和行业分布
4. 提供明日涨幅预测和风险评估
5. 基于多维度分析进行选股

## 安装说明

1. 克隆项目到本地

```bash
git clone https://github.com/yourusername/stock-picker.git
cd stock-picker
```

2. 创建虚拟环境

```bash
python -m venv .venv
```

3. 激活虚拟环境

- Windows:
  ```bash
  .venv\Scripts\activate
  ```

- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

4. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用说明

1. 运行应用

```bash
python src/main.py
```

2. 在浏览器中打开生成的URL，设置选股参数，然后点击"立即生成选股结果"按钮

3. 查看AI为您精选的股票组合和详细分析

## 注意事项

1. 本工具仅供参考，不构成投资建议。股市有风险，投资需谨慎。
2. 定期清理日志文件 `stock_picker.log` 以避免占用过多磁盘空间。
3. 如需重新训练模型，请在应用中勾选"重新训练AI模型"选项。

## 贡献指南

1.  Fork 项目
2.  创建特性分支
3.  提交更改
4.  推送至分支
5.  创建Pull Request

## 联系方式

如有问题或建议，请联系 [yourname@example.com]