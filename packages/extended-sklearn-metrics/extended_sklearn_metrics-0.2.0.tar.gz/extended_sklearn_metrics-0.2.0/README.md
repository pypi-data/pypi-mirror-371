# extended-sklearn-metrics

A comprehensive Python library for evaluating both **regression and classification** models with advanced metrics, custom thresholds, and beautiful visualizations.

## Features

### 🔧 Core Functionality
- **Regression & Classification Support** - Comprehensive evaluation for both problem types
- **Cross-validation based model evaluation** - Robust performance estimation
- **Full sklearn Pipeline support** - Works seamlessly with preprocessing pipelines
- **Advanced Input Validation** - Comprehensive error checking and helpful warnings
- **Type Hints** - Full typing support for better IDE integration

### 📊 Metrics & Evaluation
- **Regression**: RMSE, MAE, R², Explained Variance with percentage calculations
- **Classification**: Accuracy, Precision, Recall, F1-Score, ROC AUC (binary)
- **Custom Performance Thresholds** - Define your own success criteria
- **Performance Classification** - Automatic categorization (Excellent, Good, etc.)
- **Multi-class Support** - Flexible averaging strategies (micro, macro, weighted)

### 📈 Visualization & Reporting
- **Interactive Plots** - Performance summaries, model comparisons, radar charts
- **Rich Console Reports** - Formatted reports with recommendations and emojis
- **Model Comparison** - Side-by-side comparison of multiple models
- **Pipeline Compatibility** - All features work with complex preprocessing pipelines

## Installation

### From PyPI

```bash
pip install extended-sklearn-metrics
```

### From Source

1. Clone this repository:
```bash
git clone https://github.com/SubaashNair/extended-sklearn-metrics.git
cd extended-sklearn-metrics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Here's a simple example using the California Housing dataset:

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from extended_sklearn_metrics import evaluate_model_with_cross_validation

# Load and prepare data
housing = fetch_california_housing(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    housing.data, housing.target, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Create and evaluate model
model = LinearRegression()
target_range = y_train.max() - y_train.min()

# Get performance metrics
performance_table = evaluate_model_with_cross_validation(
    model=model,
    X=X_train_scaled,
    y=y_train,
    cv=5,
    target_range=target_range
)

print(performance_table)
```

## Pipeline Support

The library works seamlessly with sklearn pipelines, including complex preprocessing:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from extended_sklearn_metrics import evaluate_model_with_cross_validation

# Basic pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('regressor', LinearRegression())
])

# Complex pipeline with mixed data types
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_columns),
    ('cat', OneHotEncoder(drop='first'), categorical_columns)
])

complex_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', Ridge(alpha=1.0))
])

# Evaluate any pipeline the same way
result = evaluate_model_with_cross_validation(
    model=pipeline,  # or complex_pipeline
    X=X_train,
    y=y_train,
    cv=5
)
```

## Classification Support

Evaluate classification models with comprehensive metrics:

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from extended_sklearn_metrics import evaluate_classification_model_with_cross_validation

# Load data
iris = load_iris(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.3)

# Evaluate classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
result = evaluate_classification_model_with_cross_validation(
    model=model,
    X=X_train,
    y=y_train,
    cv=5,
    average='weighted'  # Options: 'micro', 'macro', 'weighted'
)
```

## Custom Performance Thresholds

Define your own success criteria:

```python
from extended_sklearn_metrics import CustomThresholds

# Create custom thresholds
custom_thresholds = CustomThresholds(
    error_thresholds=(5, 15, 25),    # RMSE/MAE: <5% = Excellent, 5-15% = Good, etc.
    score_thresholds=(0.6, 0.8)      # R²/Accuracy: >0.8 = Good, 0.6-0.8 = Acceptable
)

# Use with any evaluation function
result = evaluate_model_with_cross_validation(
    model=model,
    X=X_train,
    y=y_train,
    cv=5,
    custom_thresholds=custom_thresholds
)
```

## Visualizations & Rich Reports

Create beautiful visualizations and reports:

```python
from extended_sklearn_metrics import (
    create_performance_summary_plot,
    create_model_comparison_plot,
    create_performance_radar_chart,
    print_performance_report
)

# Rich console report with recommendations
print_performance_report(result)

# Interactive plots (requires matplotlib)
create_performance_summary_plot(result, title="Model Performance")
create_performance_radar_chart(result)

# Compare multiple models
models_results = {
    'LinearRegression': result1,
    'RandomForest': result2,
    'SVM': result3
}
create_model_comparison_plot(models_results)
```

## Output Format

The library generates a DataFrame with the following columns:

| Column | Description |
|--------|-------------|
| Metric | Name of the metric (RMSE, MAE, R², etc.) |
| Value | Computed value of the metric |
| Threshold | Thresholds used for performance classification |
| Calculation | Formula/method used to compute the metric |
| Performance | Classification (Excellent, Good, Moderate, Poor) |

## Performance Thresholds

### RMSE and MAE
- < 10% of range: Excellent
- 10%–20% of range: Good
- 20%–30% of range: Moderate
- > 30% of range: Poor

### R² and Explained Variance
- > 0.7: Good
- 0.5–0.7: Acceptable
- < 0.5: Poor

## Requirements

### Core Dependencies
- Python 3.8+
- pandas >= 2.0.0
- scikit-learn >= 1.3.0
- numpy >= 1.24.0

### Optional Dependencies
- matplotlib >= 3.0.0 (for visualizations)

Install with visualizations:
```bash
pip install extended-sklearn-metrics matplotlib
```

## API Reference

### Core Functions

#### `evaluate_model_with_cross_validation(model, X, y, cv=5, target_range=None, custom_thresholds=None)`
Evaluate regression models with comprehensive metrics.

#### `evaluate_classification_model_with_cross_validation(model, X, y, cv=5, average='weighted')`
Evaluate classification models with comprehensive metrics.

#### `CustomThresholds(error_thresholds=(10, 20, 30), score_thresholds=(0.5, 0.7))`
Define custom performance thresholds for evaluation.

### Visualization Functions

#### `print_performance_report(results)`
Print a formatted console report with recommendations.

#### `create_performance_summary_plot(results, title=None, figsize=(10, 6))`
Create bar charts showing metric values and performance categories.

#### `create_model_comparison_plot(results_dict, figsize=(12, 8))`
Compare multiple models side-by-side.

#### `create_performance_radar_chart(results, title=None, figsize=(8, 8))`
Create radar/spider chart visualization.

## Examples

The library includes comprehensive examples in the `examples/` directory:
- `california_housing_example.py` - Basic regression usage
- `pipeline_examples.py` - Pipeline integration examples
- `classification_examples.py` - Classification evaluation examples  
- `custom_thresholds_example.py` - Custom threshold usage
- `visualization_examples.py` - Visualization capabilities

## License

This project is licensed under the MIT License - see the LICENSE file for details. 