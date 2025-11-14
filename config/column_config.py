# Table column configuration
COLUMN_CONFIG = {
    "level": {
        "label": "职级",
        "step": 1,
        "format": "%d"
    },
    "campus_employee": {
        "label": "现有校招人数",
        "step": 1,
        "format": "%d"
    },
    "social_employee": {
        "label": "现有社招人数",
        "step": 1,
        "format": "%d"
    },
    "campus_age": {
        "label": "校招平均年龄",
        "help": "当前校招员工平均年龄",
        "min_value": 20,
        "max_value": 60,
        "step": 0.1,
        "format": "%.1f"
    },
    "social_age": {
        "label": "社招平均年龄",
        "help": "当前社招员工平均年龄",
        "min_value": 20,
        "max_value": 60,
        "step": 0.1,
        "format": "%.1f"
    },
    "campus_leaving_age": {
        "label": "校招离职年龄",
        "help": "离职校招员工平均年龄",
        "min_value": 20,
        "max_value": 60,
        "step": 0.1,
        "format": "%.1f"
    },
    "social_leaving_age": {
        "label": "社招离职年龄",
        "help": "离职社招员工平均年龄",
        "min_value": 20,
        "max_value": 60,
        "step": 0.1,
        "format": "%.1f"
    },
    "social_new_hire_age": {
        "label": "社招入职年龄",
        "help": "新入职社招员工平均年龄",
        "min_value": 20,
        "max_value": 60,
        "step": 0.1,
        "format": "%.1f"
    },
    "campus_promotion_rate": {
        "label": "校招晋升率",
        "help": "校招员工晋升比例",
        "min_value": 0.0,
        "max_value": 100.0,
        "step": 0.001,
        "format": "%.2f"
    },
    "social_promotion_rate": {
        "label": "社招晋升率",
        "help": "社招员工晋升比例",
        "min_value": 0.0,
        "max_value": 100.0,
        "step": 0.001,
        "format": "%.2f"
    },
    "campus_attrition_rate": {
        "label": "校招离职率",
        "help": "校招员工离职比例",
        "min_value": 0.0,
        "max_value": 100.0,
        "step": 0.001,
        "format": "%.2f"
    },
    "social_attrition_rate": {
        "label": "社招离职率",
        "help": "社招员工离职比例",
        "min_value": 0.0,
        "max_value": 100.0,
        "step": 0.001,
        "format": "%.2f"
    },
    "hiring_ratio": {
        "label": "社招分配比例",
        "help": "社招新员工在各职级的分配比例",
        "min_value": 0.0,
        "max_value": 100.0,
        "step": 0.001,
        "format": "%.2f"
    }
}
