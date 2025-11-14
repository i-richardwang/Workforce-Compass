import os
from typing import Dict, List, Any, Union, Optional

import pandas as pd

from config.constants import LEVELS, DEFAULT_CAMPUS_RATIO


class DataProcessor:
    """
    Data Processor Class for handling input data and creating default parameters

    This class provides functionality for loading data from CSV files,
    calculating current metrics, and preparing prediction parameters
    """

    # Define required column name constants
    REQUIRED_COLUMNS: List[str] = [
        "level", "campus_employee", "social_employee",
        "campus_age", "social_age", "campus_leaving_age",
        "social_leaving_age", "social_new_hire_age",
        "campus_promotion_rate", "social_promotion_rate",
        "campus_attrition_rate", "social_attrition_rate",
        "hiring_ratio"
    ]

    # Define integer and float columns
    INTEGER_COLUMNS: List[str] = ['campus_employee', 'social_employee']

    FLOAT_COLUMNS: List[str] = [
        'campus_age', 'social_age', 'campus_leaving_age',
        'social_leaving_age', 'social_new_hire_age',
        'campus_promotion_rate', 'social_promotion_rate',
        'campus_attrition_rate', 'social_attrition_rate',
        'hiring_ratio'
    ]

    @staticmethod
    def normalize_level(level_value) -> int:
        """
        Convert L1-L7 format to numeric format for calculations
        
        L1->1, L2->2, L3->3, L4->4, L5->5, L6->6, L7->7
        
        Args:
            level_value: Level value (L1-L7 format)
            
        Returns:
            int: Numeric level (1-7)
        """
        if isinstance(level_value, str) and level_value.startswith('L'):
            level_num = int(level_value[1:])  # Extract number after 'L'
            if 1 <= level_num <= 7:
                return level_num  # L1->1, L2->2, ..., L7->7
            else:
                raise ValueError(f"Invalid level number: {level_num}. Expected 1-7.")
        else:
            raise ValueError(f"Invalid level format: {level_value}. Expected L1-L7 format.")

    @staticmethod
    def load_preset_from_csv(file_path: str) -> pd.DataFrame:
        """
        Load preset parameters from CSV file

        Args:
            file_path: CSV file path

        Returns:
            pd.DataFrame: DataFrame containing all parameters

        Raises:
            ValueError: When CSV file is missing required columns
            Exception: Other errors when loading CSV file
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)

            # Check if required columns exist
            missing_columns = [col for col in DataProcessor.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                raise ValueError(f"CSV file is missing required columns: {', '.join(missing_columns)}")

            # Convert level column from L1-L7 to numeric 1-7
            df['level'] = df['level'].apply(DataProcessor.normalize_level)

            # Handle NaN values in integer columns
            df[DataProcessor.INTEGER_COLUMNS] = df[DataProcessor.INTEGER_COLUMNS].fillna(0).astype(int)

            # Handle NaN values in float columns
            df[DataProcessor.FLOAT_COLUMNS] = df[DataProcessor.FLOAT_COLUMNS].fillna(0.0).astype(float)

            return df

        except Exception as e:
            raise Exception(f"Error loading CSV file: {str(e)}")

    @staticmethod
    def create_default_param_df() -> pd.DataFrame:
        """
        Create default parameter DataFrame

        Returns:
            pd.DataFrame: DataFrame containing default parameters

        Raises:
            Exception: Need to load CSV file to provide parameters
        """
        raise Exception("Need to load preset parameter CSV file, cannot create default parameters")

    @staticmethod
    def calculate_current_metrics(df: pd.DataFrame) -> Dict[str, Union[int, float]]:
        """
        Calculate current metrics

        Args:
            df: DataFrame containing current data

        Returns:
            Dict[str, Union[int, float]]: Dictionary containing calculated current metrics
        """
        # Calculate total headcount (sum of campus and social recruitment)
        total_employees = df['campus_employee'] + df['social_employee']
        current_total = int(total_employees.sum())

        # Calculate current average level
        current_average_level = (
            sum(df['level'] * (df['campus_employee'] + df['social_employee'])) /
            current_total if current_total != 0 else 0.0
        )

        # Calculate current total age and average age
        current_total_age = sum(
            df['campus_employee'] * df['campus_age'] +
            df['social_employee'] * df['social_age']
        )
        current_average_age = current_total_age / current_total if current_total != 0 else 0.0

        # Calculate current campus recruitment ratio
        current_campus_ratio = (
            df['campus_employee'].sum() / current_total if current_total > 0 else 0.0
        )

        return {
            'current_total': current_total,
            'current_average_level': current_average_level,
            'current_average_age': current_average_age,
            'current_campus_ratio': current_campus_ratio
        }

    @staticmethod
    def prepare_prediction_params(
        df: pd.DataFrame,
        campus_ratio: float,
        campus_new_hire_age: float,
        target_total: int
    ) -> Dict[str, Any]:
        """
        Prepare parameter dictionary required for prediction

        Args:
            df: DataFrame containing base data
            campus_ratio: Campus recruitment ratio
            campus_new_hire_age: Average age of new campus hires
            target_total: Target total headcount

        Returns:
            Dict[str, Any]: Dictionary containing all parameters required for prediction
        """
        # Convert DataFrame to dictionary format for use by prediction model
        params = {
            'current_campus_employees': df.set_index('level')['campus_employee'].to_dict(),
            'current_social_employees': df.set_index('level')['social_employee'].to_dict(),
            'current_campus_ages': df.set_index('level')['campus_age'].to_dict(),
            'current_social_ages': df.set_index('level')['social_age'].to_dict(),
            'campus_leaving_ages': df.set_index('level')['campus_leaving_age'].to_dict(),
            'social_leaving_ages': df.set_index('level')['social_leaving_age'].to_dict(),
            'social_new_hire_ages': df.set_index('level')['social_new_hire_age'].to_dict(),
            'campus_new_hire_age': campus_new_hire_age,
            'campus_promotion_rates': df.set_index('level')['campus_promotion_rate'].to_dict(),
            'social_promotion_rates': df.set_index('level')['social_promotion_rate'].to_dict(),
            'campus_attrition_rates': df.set_index('level')['campus_attrition_rate'].to_dict(),
            'social_attrition_rates': df.set_index('level')['social_attrition_rate'].to_dict(),
            'hiring_ratios': df.set_index('level')['hiring_ratio'].to_dict(),
            'campus_ratio': campus_ratio,
            'target_total': target_total
        }
        return params
