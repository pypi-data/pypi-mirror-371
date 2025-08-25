# Extended Sklearn Metrics

A comprehensive evaluation library for scikit-learn models with advanced metrics, ROC/AUC analysis, feature importance, fairness evaluation, and professional visualizations.

## Features

### 🎯 Core Capabilities
- **Cross-validation evaluation** with custom thresholds for classification and regression
- **ROC/AUC analysis** with threshold optimization and multi-class support
- **Comprehensive model evaluation** with hold-out test sets
- **Feature importance analysis** (built-in + permutation importance)
- **Fairness evaluation** across demographic groups
- **Residual diagnostics** for regression models
- **Professional visualizations** and reporting

### 📊 ROC/AUC Analysis
- ROC curve calculation and visualization
- Precision-Recall curves and AUC-PR metrics
- Threshold optimization (Youden's Index, F1-optimal, balanced accuracy)
- Multi-class ROC analysis (one-vs-rest)
- Interactive threshold analysis plots

### 🔍 Comprehensive Evaluation
- Hold-out test evaluation with cross-validation stability
- Multi-method feature importance (built-in + permutation)
- Model interpretation and complexity assessment
- Error analysis and residual diagnostics
- Fairness evaluation by protected attributes
- Actionable recommendations and insights

### 📈 Advanced Visualizations
- ROC curves with confidence intervals
- Precision-Recall curves
- Multi-class ROC comparisons
- Feature importance plots
- Fairness comparison charts
- Comprehensive evaluation dashboards

## Installation

```bash
pip install extended-sklearn-metrics
```

## Quick Start

### Basic Classification Evaluation

```python
from extended_sklearn_metrics import evaluate_classification_model_with_cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# Create sample data
X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate with cross-validation
results = evaluate_classification_model_with_cross_validation(
    model, X_train, y_train, X_test, y_test, cv_folds=5
)

# Print results
print(f"Test Accuracy: {results['test_accuracy']:.3f}")
print(f"CV Accuracy: {results['cv_accuracy_mean']:.3f} ± {results['cv_accuracy_std']:.3f}")
```

### ROC/AUC Analysis

```python
from extended_sklearn_metrics import (
    calculate_roc_metrics, 
    create_roc_curve_plot, 
    find_optimal_thresholds,
    print_roc_auc_summary
)
from sklearn.linear_model import LogisticRegression

# Train model
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# Get predictions
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Calculate ROC metrics
roc_results = calculate_roc_metrics(y_test, y_pred_proba)

# Print summary
print_roc_auc_summary(roc_results)

# Find optimal thresholds
optimal_thresholds = find_optimal_thresholds(y_test, y_pred_proba)
print("Optimal Thresholds:")
for method, threshold in optimal_thresholds.items():
    print(f"  {method}: {threshold:.3f}")

# Create ROC curve plot
create_roc_curve_plot(roc_results, title="Model ROC Curve")
```

### Multi-class ROC Analysis

```python
from extended_sklearn_metrics import calculate_multiclass_roc_metrics, create_multiclass_roc_plot
from sklearn.datasets import make_classification

# Create multi-class data
X, y = make_classification(n_samples=1000, n_features=10, n_classes=3, 
                          n_informative=8, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(random_state=42, multi_class='ovr')
model.fit(X_train, y_train)

# Get class probabilities
y_pred_proba = model.predict_proba(X_test)

# Calculate multi-class ROC metrics
multiclass_roc = calculate_multiclass_roc_metrics(y_test, y_pred_proba)

print(f"Macro-average AUC: {multiclass_roc['macro_auc']:.3f}")
print(f"Micro-average AUC: {multiclass_roc['micro_auc']:.3f}")

# Create multi-class ROC plot
create_multiclass_roc_plot(multiclass_roc, title="Multi-class ROC Analysis")
```

### Comprehensive Model Evaluation

```python
from extended_sklearn_metrics import (
    final_model_evaluation,
    print_evaluation_summary,
    create_evaluation_report,
    create_comprehensive_evaluation_plots
)
import pandas as pd

# Create feature names
feature_names = [f'feature_{i}' for i in range(X.shape[1])]

# Convert to DataFrame for better analysis
X_train_df = pd.DataFrame(X_train, columns=feature_names)
X_test_df = pd.DataFrame(X_test, columns=feature_names)

# Comprehensive evaluation
evaluation_results = final_model_evaluation(
    model=model,
    X_train=X_train_df,
    y_train=y_train,
    X_test=X_test_df,
    y_test=y_test,
    task_type='classification',
    cv_folds=5,
    feature_names=feature_names,
    random_state=42
)

# Print summary
print_evaluation_summary(evaluation_results)

# Create detailed report
report_df = create_evaluation_report(evaluation_results)
print(report_df)

# Generate comprehensive visualizations
create_comprehensive_evaluation_plots(evaluation_results)
```

### Fairness Evaluation

```python
import numpy as np

# Create protected attributes (demographic information)
np.random.seed(42)
protected_attrs = {
    'gender': np.random.choice(['Male', 'Female'], size=len(y_test), p=[0.6, 0.4]),
    'age_group': np.random.choice(['Young', 'Senior'], size=len(y_test), p=[0.7, 0.3])
}

# Comprehensive evaluation with fairness analysis
evaluation_results = final_model_evaluation(
    model=model,
    X_train=X_train_df,
    y_train=y_train,
    X_test=X_test_df,
    y_test=y_test,
    task_type='classification',
    cv_folds=5,
    feature_names=feature_names,
    protected_attributes=protected_attrs,  # Enable fairness analysis
    random_state=42
)

# Create fairness report
from extended_sklearn_metrics import create_fairness_report, create_fairness_comparison_plot

fairness_report = create_fairness_report(evaluation_results)
if fairness_report is not None:
    print("Fairness Analysis:")
    print(fairness_report)
    
    # Create fairness visualization
    create_fairness_comparison_plot(evaluation_results)
```

### Regression Evaluation

```python
from extended_sklearn_metrics import evaluate_model_with_cross_validation
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression

# Create regression data
X, y = make_regression(n_samples=1000, n_features=10, noise=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train regression model
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Evaluate with cross-validation
results = evaluate_model_with_cross_validation(
    model, X_train, y_train, X_test, y_test, cv_folds=5
)

print(f"Test R²: {results['test_r2']:.3f}")
print(f"Test RMSE: {results['test_rmse']:.3f}")
print(f"CV R²: {results['cv_r2_mean']:.3f} ± {results['cv_r2_std']:.3f}")

# Comprehensive regression evaluation
feature_names = [f'feature_{i}' for i in range(X.shape[1])]
X_train_df = pd.DataFrame(X_train, columns=feature_names)
X_test_df = pd.DataFrame(X_test, columns=feature_names)

regression_results = final_model_evaluation(
    model=model,
    X_train=X_train_df,
    y_train=y_train,
    X_test=X_test_df,
    y_test=y_test,
    task_type='regression',
    cv_folds=5,
    feature_names=feature_names,
    random_state=42
)

# Print comprehensive summary
print_evaluation_summary(regression_results)
```

## API Reference

### Core Evaluation Functions

#### `evaluate_classification_model_with_cross_validation`
Comprehensive classification evaluation with cross-validation.

**Parameters:**
- `model`: Trained scikit-learn classifier
- `X_train`, `y_train`: Training data
- `X_test`, `y_test`: Test data  
- `cv_folds`: Number of cross-validation folds (default: 5)
- `custom_thresholds`: Custom decision thresholds to evaluate

**Returns:** Dictionary with classification metrics and cross-validation results

#### `evaluate_model_with_cross_validation`
General model evaluation supporting both classification and regression.

**Parameters:**
- `model`: Trained scikit-learn model
- `X_train`, `y_train`: Training data
- `X_test`, `y_test`: Test data
- `cv_folds`: Number of cross-validation folds (default: 5)

**Returns:** Dictionary with appropriate metrics based on model type

### ROC/AUC Analysis Functions

#### `calculate_roc_metrics`
Calculate ROC curve metrics for binary classification.

**Parameters:**
- `y_true`: True binary labels
- `y_pred_proba`: Predicted probabilities for positive class
- `pos_label`: Positive class label (default: 1)

**Returns:** Dictionary with FPR, TPR, thresholds, and AUC score

#### `calculate_multiclass_roc_metrics`
Calculate ROC metrics for multi-class classification using one-vs-rest approach.

**Parameters:**
- `y_true`: True class labels
- `y_pred_proba`: Predicted class probabilities
- `class_names`: List of class names (optional)

**Returns:** Dictionary with per-class ROC metrics and macro/micro averages

#### `find_optimal_thresholds`
Find optimal classification thresholds using various methods.

**Parameters:**
- `y_true`: True binary labels
- `y_pred_proba`: Predicted probabilities
- `methods`: List of optimization methods (default: ['youden', 'f1', 'balanced_accuracy'])

**Returns:** Dictionary mapping method names to optimal thresholds

### Comprehensive Evaluation

#### `final_model_evaluation`
Comprehensive model evaluation with hold-out testing, feature importance, and fairness analysis.

**Parameters:**
- `model`: Trained scikit-learn model
- `X_train`, `y_train`: Training data
- `X_test`, `y_test`: Test data
- `task_type`: 'classification' or 'regression'
- `cv_folds`: Number of cross-validation folds (default: 5)
- `feature_names`: List of feature names (optional)
- `protected_attributes`: Dictionary of protected attributes for fairness analysis (optional)
- `random_state`: Random seed (default: 42)

**Returns:** Comprehensive evaluation results dictionary

### Visualization Functions

#### `create_roc_curve_plot`
Create ROC curve visualization.

**Parameters:**
- `roc_results`: Results from `calculate_roc_metrics`
- `title`: Plot title (optional)
- `show_optimal_threshold`: Whether to highlight optimal threshold (default: True)

#### `create_multiclass_roc_plot`
Create multi-class ROC curve visualization.

**Parameters:**
- `multiclass_roc_results`: Results from `calculate_multiclass_roc_metrics`
- `title`: Plot title (optional)

#### `create_comprehensive_evaluation_plots`
Create comprehensive evaluation dashboard with multiple panels.

**Parameters:**
- `evaluation_results`: Results from `final_model_evaluation`
- `figsize`: Figure size tuple (optional)

### Reporting Functions

#### `print_evaluation_summary`
Print executive summary of evaluation results.

**Parameters:**
- `evaluation_results`: Results from `final_model_evaluation`

#### `create_evaluation_report`
Create detailed evaluation report as pandas DataFrame.

**Parameters:**
- `evaluation_results`: Results from `final_model_evaluation`

**Returns:** pandas DataFrame with evaluation metrics

#### `create_feature_importance_report`
Create feature importance analysis report.

**Parameters:**
- `evaluation_results`: Results from `final_model_evaluation`

**Returns:** pandas DataFrame with feature importance rankings

#### `create_fairness_report`
Create fairness analysis report by demographic groups.

**Parameters:**
- `evaluation_results`: Results from `final_model_evaluation`

**Returns:** pandas DataFrame with fairness metrics by group

## Advanced Examples

### Complete Workflow Example

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from extended_sklearn_metrics import *

# 1. Create sample data with feature names
np.random.seed(42)
X, y = make_classification(n_samples=2000, n_features=15, n_informative=10, 
                          n_redundant=3, weights=[0.7, 0.3], random_state=42)

feature_names = ['income', 'education', 'age', 'experience', 'debt_ratio',
                'credit_score', 'loan_amount', 'property_value', 'savings',
                'dependents', 'employment_type', 'payment_history', 
                'account_balance', 'investment_portfolio', 'insurance']

X_df = pd.DataFrame(X, columns=feature_names)
y_series = pd.Series(y, name='loan_approved')

# 2. Create protected attributes for fairness analysis
protected_attrs = {
    'gender': np.random.choice(['Male', 'Female'], size=len(y), p=[0.6, 0.4]),
    'age_group': np.random.choice(['Young', 'Middle', 'Senior'], size=len(y), p=[0.3, 0.5, 0.2])
}

# 3. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_df, y_series, test_size=0.2, random_state=42, stratify=y_series
)

# Get protected attributes for test set
test_indices = y_test.index
protected_attrs_test = {
    attr: values[test_indices] for attr, values in protected_attrs.items()
}

# 4. Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Comprehensive evaluation
evaluation_results = final_model_evaluation(
    model=model,
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    task_type='classification',
    cv_folds=5,
    feature_names=feature_names,
    protected_attributes=protected_attrs_test,
    random_state=42
)

# 6. Generate reports
print("=== EVALUATION SUMMARY ===")
print_evaluation_summary(evaluation_results)

print("\n=== DETAILED METRICS ===")
eval_report = create_evaluation_report(evaluation_results)
print(eval_report)

print("\n=== TOP 10 MOST IMPORTANT FEATURES ===")
fi_report = create_feature_importance_report(evaluation_results)
if fi_report is not None:
    print(fi_report.head(10))

print("\n=== FAIRNESS ANALYSIS ===")
fairness_report = create_fairness_report(evaluation_results)
if fairness_report is not None:
    print(fairness_report)

# 7. Create visualizations
create_comprehensive_evaluation_plots(evaluation_results)
create_feature_importance_plot(evaluation_results, top_n=12)
create_fairness_comparison_plot(evaluation_results)

print("\n✅ Complete evaluation finished!")
```

## Dependencies

- `numpy >= 1.24.0`
- `pandas >= 2.0.0`
- `scikit-learn >= 1.3.0`
- `matplotlib >= 3.5.0` (optional, for visualizations)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Version History

### v0.3.0 (Latest)
- Added comprehensive ROC/AUC analysis with threshold optimization
- Implemented multi-class ROC support (one-vs-rest)
- Added Precision-Recall curves and AUC-PR metrics
- Created comprehensive model evaluation framework
- Added feature importance analysis (built-in + permutation)
- Implemented fairness evaluation across demographic groups
- Added hold-out test evaluation with cross-validation stability
- Created professional reporting and visualization suite
- Added model interpretation and complexity assessment
- Enhanced error analysis and residual diagnostics

### v0.2.0
- Added residual diagnostics for regression models
- Enhanced visualization capabilities
- Improved cross-validation metrics

### v0.1.0
- Initial release with basic classification and regression evaluation
- Cross-validation support with custom thresholds
- Basic performance visualizations