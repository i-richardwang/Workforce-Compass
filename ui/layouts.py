import os
from typing import Dict, List, Tuple, Any, Optional, Union, cast

import streamlit as st

from config.constants import DEFAULT_CAMPUS_RATIO, LEVELS
from core.predictor import HRPredictor
from core.data_processor import DataProcessor
from .components import (
    SidebarComponent,
    DataEditorComponent,
    MetricsComponent,
    PredictionResultComponent
)


class AppLayout:
    """
    Application Main Layout Class

    Responsible for the layout and rendering of the entire application,
    coordinating the display of various components
    """

    # Prediction logic description text
    PREDICTION_LOGIC_DESCRIPTION = """
    ### 预测模型说明

    本模型采用分步骤预测方法，主要包含以下步骤：

    **1. 晋升预测**
    - 分别计算校招和社招渠道的晋升影响
    - 对每个职级：当前人数 - 晋升出去的人数 + 从低职级晋升上来的人数

    **2. 离职预测**
    - 基于晋升后的人数计算离职影响
    - 分别计算校招和社招渠道的离职人数
    - 考虑不同职级的离职率差异

    **3. 招聘预测**
    - 校招名额：按设定的校招比例分配（全部进入L1）
    - 社招名额：按各职级的分配比例分配到不同职级

    **4. 年龄预测**
    - 考虑以下因素：
      - 现有员工年龄增长
      - 离职人员带走的年龄结构
      - 新进人员带来的年龄结构

    **主要参数**
    - **晋升率**：各职级的晋升概率（校招/社招分开设置）
    - **离职率**：各职级的离职概率（校招/社招分开设置）
    - **招聘配置**：校招总比例和社招各职级分配比例
    - **年龄参数**：现有员工年龄、离职员工年龄、新员工年龄
    """

    def __init__(self) -> None:
        """
        Initialize application layout

        Create predictor and data processor instances, set page configuration
        """
        # Create core component instances
        self.predictor = HRPredictor()
        self.data_processor = DataProcessor()

        # Set page to wide screen mode
        st.set_page_config(
            page_title="人才金字塔预测 | Workforce Compass",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def render_description(self) -> None:
        """
        Render prediction logic description

        Display detailed description of prediction model in a collapsible area
        """
        with st.expander("📖 预测逻辑说明", expanded=False):
            st.markdown(self.PREDICTION_LOGIC_DESCRIPTION)

    def prepare_chart_data(
        self,
        current_metrics: Dict[str, Union[int, float]],
        prediction_results: List[Dict[str, Any]],
        edited_df: Any
    ) -> Tuple[List[str], Dict[str, List[float]], List[Dict[str, Any]]]:
        """
        Prepare data required for charts

        Args:
            current_metrics: Current metrics data
            prediction_results: List of prediction results
            edited_df: Edited parameter DataFrame

        Returns:
            Tuple containing:
            - years: List of years
            - metrics_data: Metrics data dictionary
            - structures: List of level structure data
        """
        # Prepare year labels
        years = ['Current'] + [f'Year {r["year"]}' for r in prediction_results]

        # Prepare metrics data
        metrics_data = {
            'average_level': [current_metrics['current_average_level']] +
                           [r['average_level'] for r in prediction_results],
            'average_age': [current_metrics['current_average_age']] +
                          [r['average_age'] for r in prediction_results],
            'campus_ratio': [current_metrics['current_campus_ratio']] +
                           [r['campus_ratio'] for r in prediction_results]
        }

        # Prepare level structure data
        current_structure = {
            'year': 'Current',
            **{
                level: edited_df[edited_df['level'] == level]['campus_employee'].iloc[0] +
                      edited_df[edited_df['level'] == level]['social_employee'].iloc[0]
                for level in edited_df['level']
            }
        }

        structures = [current_structure] + [
            {'year': f'Year {r["year"]}'} | r['final_structure']
            for r in prediction_results
        ]

        return years, metrics_data, structures

    def render(self) -> None:
        """
        Render the entire application interface

        Coordinate component display, handle data flow, and show prediction results
        """
        # Render sidebar component
        sidebar_result = SidebarComponent.render()
        campus_ratio, campus_new_hire_age, forecast_years, selected_file = sidebar_result

        # Display title
        title = "Workforce Compass · 人才金字塔预测"
        if selected_file:
            file_name = os.path.splitext(selected_file)[0]
            title += f" ({file_name})"
        st.title(title)

        # Render prediction logic description
        self.render_description()

        # Check if CSV file is selected
        if not selected_file:
            st.error("请在侧边栏选择预设参数CSV文件以进行预测")
            st.info("您可以在data目录中添加CSV文件作为预设参数模板")
            return

        try:
            # Load parameter DataFrame
            param_df = self.data_processor.load_preset_from_csv(
                os.path.join("data", selected_file)
            )

            # Render data editor component
            edited_df = DataEditorComponent.render(param_df)

            # Calculate current metrics
            current_metrics = self.data_processor.calculate_current_metrics(edited_df)

            # Set target total headcount (default same as current total)
            with st.sidebar:
                st.markdown(f"**当前总人数**: {current_metrics['current_total']:,d}")
                target_total = st.number_input(
                    "目标年底总人数",
                    min_value=1,
                    value=current_metrics['current_total'],
                    help="默认与当前总人数相同"
                )

            # Update current metrics
            current_metrics.update({
                'target_total': target_total,
                'campus_ratio': campus_ratio
            })

            # Prepare prediction parameters
            prediction_params = self.data_processor.prepare_prediction_params(
                edited_df,
                campus_ratio,
                campus_new_hire_age,
                target_total
            )

            # Perform multi-year prediction
            prediction_results = self.predictor.predict_multiple_years(
                prediction_params,
                forecast_years
            )

            # Prepare chart data
            years, metrics_data, structures = self.prepare_chart_data(
                current_metrics,
                prediction_results,
                edited_df
            )

            # Render metrics component
            MetricsComponent.render_current_metrics(current_metrics)
            MetricsComponent.render_prediction_charts(years, metrics_data, structures)

            # Render prediction result component
            PredictionResultComponent.render(prediction_results, campus_ratio)

        except Exception as e:
            st.error(f"处理数据时出错: {str(e)}")
            st.exception(e)
