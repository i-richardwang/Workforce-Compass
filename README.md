# Workforce Compass
## Organizational Talent Structure Forecasting

English | [简体中文](README.zh-CN.md)

A Streamlit-based application designed to forecast multi-year trends in organizational workforce structure. The system predicts changes in talent composition over 1-5 years based on current personnel data and key parameters, enabling HR and management teams to make strategic workforce planning decisions.

## Features

- **Multi-dimensional Forecasting**: Predicts organizational hierarchy, average level, age distribution, and recruitment mix
- **Configurable Parameters**: Adjust key variables including recruitment ratios, promotion rates, and attrition rates
- **Interactive Visualizations**: Trend charts and level distribution graphs for key metrics
- **Detailed Data Tables**: Year-by-year breakdown of prediction results
- **Data Export**: Export all forecasts to Excel for further analysis
- **Preset Templates**: Includes multiple sample templates (Sample A, B, C) to get started quickly

## Tech Stack

- **Frontend Framework**: [Streamlit](https://streamlit.io/) - Rapid data application development
- **Data Processing**: [Pandas](https://pandas.pydata.org/) + [NumPy](https://numpy.org/) - Data analysis and numerical computation
- **Data Visualization**: [Plotly](https://plotly.com/) - Interactive charts
- **Excel Processing**: [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel import/export
- **Package Management**: [uv](https://github.com/astral-sh/uv) - Modern Python package manager

## Requirements

- **Python**: 3.9 or higher
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Getting Started

### Option 1: Using uv (Recommended)

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Sync dependencies:
   ```bash
   uv sync
   ```

3. Launch the application:
   ```bash
   uv run streamlit run app.py
   ```

### Option 2: Using pip

1. Install dependencies:
   ```bash
   pip install streamlit pandas numpy openpyxl plotly
   ```

2. Launch the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
workforce-compass/
├── app.py                    # Application entry point
├── pyproject.toml           # Project configuration and dependencies
├── config/                  # Configuration modules
│   ├── constants.py        # Constant definitions
│   └── column_config.py    # UI column configuration
├── core/                   # Core business logic
│   ├── data_processor.py   # Data processing
│   └── predictor.py        # Prediction algorithms
├── ui/                     # User interface
│   ├── components.py       # UI components
│   └── layouts.py          # Application layout
├── utils/                  # Utility modules
│   └── plot_utils.py       # Visualization utilities
├── scripts/                # Utility scripts
│   └── generate_synthetic_presets.py  # Generate test data
└── data/                   # Data directory
    └── sample_*.csv        # Sample data files
```

## Data Preparation

### Using Preset Samples

The project includes several sample data files (`data/sample_*.csv`) that can be selected directly from the UI.

### Generating Test Data

Use the provided script to generate synthetic test data:

```bash
# Generate 2 test files in the data directory
python scripts/generate_synthetic_presets.py --output data --count 2 --seed 20241111
```

### Preparing Custom Data

Place your custom CSV parameter files in the `data` directory. The system will automatically detect and load them as preset templates.

CSV files must contain the following columns:
- `level`: Organizational level (L1-L7)
- `campus_employee`, `social_employee`: Current headcount by recruitment source
- `campus_age`, `social_age`: Average age by recruitment source
- `campus_leaving_age`, `social_leaving_age`: Average departure age by recruitment source
- `social_new_hire_age`: Average age of new social hires
- `campus_promotion_rate`, `social_promotion_rate`: Promotion rates by recruitment source
- `campus_attrition_rate`, `social_attrition_rate`: Attrition rates by recruitment source
- `hiring_ratio`: Distribution ratio for social recruitment across levels

**Note**: In this context, "campus recruitment" refers to fresh graduate hires, while "social recruitment" refers to experienced lateral hires from other organizations.

## Input Parameters

- **Basic Parameters**:
  - Campus recruitment ratio (overall proportion of fresh graduate hires)
  - Average age of new campus hires
  - Forecast period (1-5 years)
  - Target year-end headcount

- **Level-specific Parameters**:
  - Current headcount by level and recruitment source
  - Average age by level and recruitment source
  - Average departure age by level and recruitment source
  - Average age of new social hires by level
  - Promotion rates by level and recruitment source
  - Attrition rates by level and recruitment source
  - Social recruitment distribution ratios across levels

## Prediction Logic

The forecasting model employs a four-step calculation process:

1. **Promotion Forecast**: Calculates workforce movement across levels based on promotion rates
2. **Attrition Forecast**: Factors in differential attrition rates between campus and social recruitment cohorts
3. **Recruitment Forecast**: Allocates all campus hires to L1 (entry level), while distributing social hires across levels according to specified ratios
4. **Age Forecast**: Accounts for employee aging, departures, and the age profile of new hires

## Output

- **Key Metrics Overview**: Target headcount, campus hire count, campus recruitment ratio, etc.
- **Trend Analysis Charts**: Visualizes changes in average level, average age, and campus ratio
- **Level Structure Distribution**: Shows the evolution of workforce composition across organizational levels
- **Detailed Forecast Tables**: Year-by-year breakdown of all predicted metrics
- **Excel Export**: Download all prediction results in a multi-sheet Excel workbook
