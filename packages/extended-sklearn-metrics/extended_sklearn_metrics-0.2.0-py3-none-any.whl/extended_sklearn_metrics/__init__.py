"""
extended-sklearn-metrics - A Python package for enhanced scikit-learn model evaluation metrics
"""

__version__: str = "0.2.0"

from .model_evaluation import evaluate_model_with_cross_validation, CustomThresholds
from .classification_evaluation import evaluate_classification_model_with_cross_validation
from .visualizations import (
    create_performance_summary_plot, 
    create_model_comparison_plot,
    create_performance_radar_chart,
    print_performance_report
)

__all__: list[str] = [
    'evaluate_model_with_cross_validation', 
    'evaluate_classification_model_with_cross_validation',
    'CustomThresholds',
    'create_performance_summary_plot',
    'create_model_comparison_plot', 
    'create_performance_radar_chart',
    'print_performance_report'
] 