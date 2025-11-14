# 人才金字塔预测
## Workforce Compass

[English](README.md) | 简体中文

该项目使用Streamlit构建，旨在预测组织人才职级结构的多年变化趋势。系统将根据当前的人员数据和各项关键参数，预测未来1-5年的人才结构变化，帮助HR和管理层进行战略性人才规划。

## 功能特点

- **多维度预测**：职级结构、平均职级、年龄结构、校招占比等
- **参数化配置**：支持调整校招比例、晋升率、离职率等关键参数
- **直观可视化**：关键指标趋势图和职级分布变化图
- **详细数据表**：每年预测结果的详细数据展示
- **数据导出**：支持将预测结果导出为Excel文件
- **预设模板**：提供多个样例模板（样例A、样例B、样例C）

## 技术栈

- **前端框架**: [Streamlit](https://streamlit.io/) - 快速构建数据应用
- **数据处理**: [Pandas](https://pandas.pydata.org/) + [NumPy](https://numpy.org/) - 数据分析和数值计算
- **数据可视化**: [Plotly](https://plotly.com/) - 交互式图表
- **Excel处理**: [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel文件导入导出
- **包管理**: [uv](https://github.com/astral-sh/uv) - 现代化的 Python 包管理工具

## 技术要求

- **Python**: 3.9 或更高版本
- **包管理器**: [uv](https://github.com/astral-sh/uv) (推荐) 或 pip

## 运行项目

### 方式一：使用 uv (推荐)

1. 安装 uv（如果尚未安装）：
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. 同步依赖：
   ```bash
   uv sync
   ```

3. 启动应用：
   ```bash
   uv run streamlit run app.py
   ```

### 方式二：使用 pip

1. 安装依赖：
   ```bash
   pip install streamlit pandas numpy openpyxl plotly
   ```

2. 启动应用：
   ```bash
   streamlit run app.py
   ```

## 项目结构

```
workforce-compass/
├── app.py                    # 应用入口
├── pyproject.toml           # 项目配置和依赖
├── config/                  # 配置模块
│   ├── constants.py        # 常量定义
│   └── column_config.py    # UI 列配置
├── core/                   # 核心业务逻辑
│   ├── data_processor.py   # 数据处理
│   └── predictor.py        # 预测算法
├── ui/                     # 用户界面
│   ├── components.py       # UI 组件
│   └── layouts.py          # 应用布局
├── utils/                  # 工具模块
│   └── plot_utils.py       # 可视化工具
├── scripts/                # 脚本工具
│   └── generate_synthetic_presets.py  # 生成测试数据
└── data/                   # 数据目录
    └── sample_*.csv        # 样例数据文件
```

## 数据文件准备

### 使用预设样例

项目自带多个样例数据文件（`data/sample_*.csv`），可直接在界面中选择使用。

### 生成测试数据

使用提供的脚本生成合成测试数据：

```bash
# 生成 2 个测试文件到 data 目录
python scripts/generate_synthetic_presets.py --output data --count 2 --seed 20241111
```

### 准备自定义数据

将参数预设CSV文件放入`data`目录下。系统自动识别并加载该目录中的CSV文件作为预设模板。

CSV文件格式必须包含以下列：
- level：职级（L1-L7）
- campus_employee, social_employee：现有校招、社招人数
- campus_age, social_age：校招、社招平均年龄
- campus_leaving_age, social_leaving_age：校招、社招离职平均年龄
- social_new_hire_age：社招新人平均年龄
- campus_promotion_rate, social_promotion_rate：校招、社招晋升率
- campus_attrition_rate, social_attrition_rate：校招、社招离职率
- hiring_ratio：社招各职级分配比例

## 输入参数

- **基础参数**：
  - 校招比例（整体校招人数占比）
  - 校招新人平均年龄
  - 预测年数（1-5年）
  - 目标年底总人数

- **表格参数**：
  - 各职级现有校招和社招人数
  - 各职级校招和社招平均年龄
  - 各职级校招和社招离职年龄
  - 各职级社招新入职平均年龄
  - 各职级校招和社招晋升率
  - 各职级校招和社招离职率
  - 社招人员各职级分配比例

## 预测逻辑

预测采用分步骤计算：
1. **晋升预测**：基于晋升率计算各职级人员流动
2. **离职预测**：考虑校招/社招的不同离职率
3. **招聘预测**：校招人员全部进入L1，社招按比例分配
4. **年龄预测**：考虑员工年龄增长、离职及新进人员年龄影响

## 结果展示

- **关键指标总览**：目标总人数、校招人数、校招比例等
- **趋势分析图表**：平均职级、平均年龄、校招比例的变化趋势
- **职级结构分布**：各职级人数占比的变化
- **详细预测数据**：各年度详细数据表格
- **Excel导出**：支持将所有预测数据导出为Excel文件
