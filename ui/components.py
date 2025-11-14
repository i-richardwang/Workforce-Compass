import streamlit as st
import pandas as pd
import os
import io
from typing import Dict, Tuple, List
from config.column_config import COLUMN_CONFIG
from config.constants import DEFAULT_CAMPUS_RATIO, LEVELS
from utils.plot_utils import plot_structure_distribution, plot_trend_charts

class SidebarComponent:
    """Sidebar component for handling parameter input and file selection"""
    
    @staticmethod
    def render(data_dir: str = "data") -> Tuple[float, float, int, str]:
        """Render sidebar component

        Returns:
            Tuple[float, float, int, str]: (campus_ratio, campus_new_hire_age, forecast_years, selected_file)
        """
        st.sidebar.header("基础参数配置")
        
        # Ensure data directory exists
        try:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                st.sidebar.warning(f"已创建{data_dir}目录，请放入CSV参数文件")
            
            # Get CSV file list
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            
            if not csv_files:
                st.sidebar.error(f"在{data_dir}目录中未找到CSV文件")
                st.sidebar.info("请将参数CSV文件放入data目录中")
        except Exception as e:
            st.sidebar.error(f"读取数据目录出错: {str(e)}")
            csv_files = []
        
        # File selection
        selected_file = None
        if csv_files:
            selected_file = st.sidebar.selectbox(
                "选择预设参数文件",
                csv_files,
                help="选择要使用的预设参数文件"
            )
        
        # Set default campus ratio
        default_campus_ratio = DEFAULT_CAMPUS_RATIO
        
        # Basic parameter settings
        campus_ratio = st.sidebar.slider(
            "校招比例", 
            0.0, 10.0, 
            default_campus_ratio * 100, 
            step=0.1, 
            format="%.1f%%"
        ) / 100
        
        campus_new_hire_age = st.sidebar.number_input(
            "校招新人平均年龄",
            min_value=20.0,
            max_value=30.0,
            value=24.2,
            step=0.1,
            help="校招新入职员工的平均年龄"
        )

        forecast_years = st.sidebar.slider(
            "预测年数",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            help="选择要预测的年数（1-5年）"
        )

        return campus_ratio, campus_new_hire_age, forecast_years, selected_file if csv_files else None

class DataEditorComponent:
    """Data editor component for displaying and editing parameter tables"""
    
    @staticmethod
    def render(param_df: pd.DataFrame) -> pd.DataFrame:
        """Render data editor component
        
        Args:
            param_df: DataFrame containing parameters
            
        Returns:
            pd.DataFrame: Edited DataFrame
        """
        st.subheader("职级参数配置")
        
        # Modify level display format
        param_df['level'] = param_df['level'].apply(lambda x: f"L{x}")
        
        # Calculate current level structure
        total_employees = param_df['campus_employee'] + param_df['social_employee']
        total_sum = total_employees.sum()
        param_df['level_structure'] = (total_employees / total_sum * 100) if total_sum > 0 else 0
        
        # Set table column configuration
        column_config = {
            "level": st.column_config.TextColumn(
                label="职级",
                help="职级范围从L1到L7",
                width="small"
            ),
            "campus_employee": st.column_config.NumberColumn(
                label="现有校招人数",
                help="当前各职级校招人数",
                format="%d"
            ),
            "social_employee": st.column_config.NumberColumn(
                label="现有社招人数",
                help="当前各职级社招人数",
                format="%d"
            ),
            "level_structure": st.column_config.NumberColumn(
                label="职级结构",
                help="当前各职级人数占总人数的百分比",
                format="%.2f%%"
            )
        }
        
        # Add configuration for other columns
        for col, config in COLUMN_CONFIG.items():
            if col not in ["level", "campus_employee", "social_employee"]:
                column_config[col] = st.column_config.NumberColumn(**config)
        
        # Convert rate data to percentage display
        rate_columns = [
            'campus_promotion_rate', 'social_promotion_rate',
            'campus_attrition_rate', 'social_attrition_rate',
            'hiring_ratio'
        ]
        for col in rate_columns:
            param_df[col] = param_df[col] * 100
        
        # Display data editor
        edited_df = st.data_editor(
            param_df,
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            column_config=column_config
        )
        
        # Convert percentage data back to decimal
        for col in rate_columns:
            edited_df[col] = edited_df[col] / 100
        
        # Convert level from L format back to number
        edited_df['level'] = edited_df['level'].apply(lambda x: int(x.replace('L', '')))
        
        return edited_df

class MetricsComponent:
    """Metrics display component for showing key metrics"""
    
    @staticmethod
    def render_current_metrics(current_metrics: Dict):
        """Render current metrics
        
        Args:
            current_metrics: Dictionary containing current metrics
        """
        st.markdown("""
        <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; margin-bottom: 20px;'>
            <h5>📊 关键指标总览</h5>
        </div>
        """, unsafe_allow_html=True)
        
        metrics = st.columns(3)
        with metrics[0]:
            st.metric("目标总人数", f"{current_metrics['target_total']:,d}")
        with metrics[1]:
            st.metric("校招人数", f"{round(current_metrics['target_total'] * current_metrics['campus_ratio']):,d}")
        with metrics[2]:
            st.metric("校招比例", f"{current_metrics['campus_ratio']:.1%}")

    @staticmethod
    def render_prediction_charts(years: List[str], metrics: Dict[str, List],
                               structures: List[Dict]):
        """Render prediction result charts
        
        Args:
            years: List of years
            metrics: Metrics data
            structures: Level structure data
        """
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. Trend analysis
        st.markdown("""
        <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; margin-bottom: 20px;'>
            <h5>📈 关键指标趋势分析</h5>
        </div>
        """, unsafe_allow_html=True)
        
        trend_fig = plot_trend_charts(years, metrics)
        st.plotly_chart(trend_fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Level structure distribution
        st.markdown("""
        <div style='border: 1px solid #ccc; padding: 20px; border-radius: 5px; margin-bottom: 20px;'>
            <h5>📊 职级结构分布分析</h5>
        </div>
        """, unsafe_allow_html=True)
        
        structure_fig = plot_structure_distribution(LEVELS, structures)
        st.plotly_chart(structure_fig, use_container_width=True)

class PredictionResultComponent:
    """Prediction result component for displaying detailed prediction data"""
    
    @staticmethod
    def render(results: List[Dict], campus_ratio: float = None):
        """Render prediction result tables
        
        Args:
            results: List of prediction results
            campus_ratio: Campus recruitment ratio set in basic parameters
        """
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("📋 查看详细预测数据", expanded=True):
            # Store DataFrames for all years for Excel export
            all_dfs = {}
            
            for i, result in enumerate(results):
                st.markdown(f"##### 第{result['year']}年详细预测数据")
                
                # Build detailed data table
                result_df = pd.DataFrame({
                    "职级": [f"L{l}" for l in LEVELS],
                    "现有校招": [result['current_campus'][l] for l in LEVELS],
                    "现有社招": [result['current_social'][l] for l in LEVELS],
                    "现有校招占比": [
                        100 * result['current_campus'][l] / 
                        (result['current_campus'][l] + result['current_social'][l])
                        if (result['current_campus'][l] + result['current_social'][l]) > 0 else 0 
                        for l in LEVELS
                    ],
                    "预测校招": [result['final_campus'][l] for l in LEVELS],
                    "预测社招": [result['final_social'][l] for l in LEVELS],
                    "预测校招占比": [
                        100 * result['final_campus'][l] / 
                        (result['final_campus'][l] + result['final_social'][l])
                        if (result['final_campus'][l] + result['final_social'][l]) > 0 else 0 
                        for l in LEVELS
                    ],
                    "预测总数": [result['final_structure'][l] for l in LEVELS]
                })
                
                # Calculate predicted level structure
                total_predicted = result_df["预测总数"].sum()
                result_df["预测职级结构"] = (
                    result_df["预测总数"] / total_predicted * 100
                ) if total_predicted > 0 else 0
                
                # Add summary row
                summary_row = pd.DataFrame({
                    "职级": ["合计"],
                    "现有校招": [sum(result['current_campus'][l] for l in LEVELS)],
                    "现有社招": [sum(result['current_social'][l] for l in LEVELS)],
                    "现有校招占比": [
                        100 * sum(result['current_campus'][l] for l in LEVELS) / 
                        sum(result['current_campus'][l] + result['current_social'][l] for l in LEVELS)
                        if sum(result['current_campus'][l] + result['current_social'][l] for l in LEVELS) > 0 else 0
                    ],
                    "预测校招": [sum(result['final_campus'][l] for l in LEVELS)],
                    "预测社招": [sum(result['final_social'][l] for l in LEVELS)],
                    "预测校招占比": [100 * result['campus_ratio']],
                    "预测总数": [sum(result['final_structure'][l] for l in LEVELS)],
                    "预测职级结构": [100.0]
                })
                
                # Merge original table and summary row
                result_df = pd.concat([result_df, summary_row], ignore_index=True)
                
                # Save DataFrame for Excel export
                all_dfs[f"第{result['year']}年"] = result_df.copy()
                
                # Display table
                st.dataframe(
                    result_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "职级": st.column_config.TextColumn(
                            label="职级",
                            help="L1-L7表示职级，最后一行为合计",
                            width="small"
                        ),
                        "现有校招": st.column_config.NumberColumn(
                            label="现有校招",
                            help="当前各职级校招人数",
                            format="%d"
                        ),
                        "现有社招": st.column_config.NumberColumn(
                            label="现有社招",
                            help="当前各职级社招人数",
                            format="%d"
                        ),
                        "现有校招占比": st.column_config.NumberColumn(
                            label="现有校招占比",
                            help="当前各职级校招人数占比",
                            format="%.2f%%"
                        ),
                        "预测校招": st.column_config.NumberColumn(
                            label="预测校招",
                            help="预测年底校招人数",
                            format="%d"
                        ),
                        "预测社招": st.column_config.NumberColumn(
                            label="预测社招",
                            help="预测年底社招人数",
                            format="%d"
                        ),
                        "预测校招占比": st.column_config.NumberColumn(
                            label="预测校招占比",
                            help="预测年底校招人数占比",
                            format="%.2f%%"
                        ),
                        "预测总数": st.column_config.NumberColumn(
                            label="预测总数",
                            help="预测年底总人数",
                            format="%d"
                        ),
                        "预测职级结构": st.column_config.NumberColumn(
                            label="预测职级结构",
                            help="预测年底各职级人数占总人数的百分比",
                            format="%.2f%%"
                        )
                    }
                )
            
            # Add Excel download button
            if all_dfs:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Create a function to generate Excel file
                def to_excel():
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for sheet_name, df in all_dfs.items():
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    output.seek(0)
                    return output
                
                # Create download button
                excel_file = to_excel()
                
                # Get forecast years and campus ratio info for filename
                forecast_years = len(results)  # How many years forecasted
                
                # Use passed campus ratio parameter
                campus_ratio_percentage = f"{campus_ratio*100:.1f}%"  # Format as percentage
                
                # Generate filename with years and campus ratio
                file_name = f"人才金字塔预测_{forecast_years}年_{campus_ratio_percentage}校招.xlsx"
                
                st.download_button(
                    label="📥 下载所有预测数据为Excel文件",
                    data=excel_file,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="将所有年份的预测数据下载为Excel文件，每个年份在单独的sheet中"
                )
