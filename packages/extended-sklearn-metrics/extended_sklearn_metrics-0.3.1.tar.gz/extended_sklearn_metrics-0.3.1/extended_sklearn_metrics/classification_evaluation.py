import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
from typing import Union, Optional
import warnings

from .model_evaluation import SklearnEstimator


def evaluate_classification_model_with_cross_validation(
    model: SklearnEstimator,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    cv: int = 5,
    average: str = 'weighted'
) -> pd.DataFrame:
    """
    Evaluates a classification model using cross-validation and generates a performance summary table.
    
    Parameters
    ----------
    model : estimator object
        The machine learning model to evaluate (must implement fit and predict).
    X : array-like of shape (n_samples, n_features)
        Training data.
    y : array-like of shape (n_samples,)
        Target values (class labels).
    cv : int, default=5
        Number of cross-validation folds.
    average : str, default='weighted'
        Averaging strategy for multiclass/multilabel targets:
        'micro', 'macro', 'weighted', 'samples', or None.
        
    Returns
    -------
    pd.DataFrame
        A summary table containing performance metrics and their interpretations.
    """
    # Input validation (reuse logic from regression function)
    if not hasattr(model, 'fit') or not hasattr(model, 'predict'):
        raise ValueError("Model must have 'fit' and 'predict' methods (sklearn-compatible estimator)")
    
    # Convert inputs to arrays for validation
    X_array = np.asarray(X)
    y_array = np.asarray(y)
    
    # Validate X
    if X_array.size == 0:
        raise ValueError("X cannot be empty")
    if X_array.ndim != 2:
        raise ValueError(f"X must be 2-dimensional, got {X_array.ndim} dimensions")
    
    # Validate y
    if y_array.size == 0:
        raise ValueError("y cannot be empty")
    if y_array.ndim != 1:
        raise ValueError(f"y must be 1-dimensional, got {y_array.ndim} dimensions")
    
    # Check length compatibility
    if len(X_array) != len(y_array):
        raise ValueError(f"X and y must have same number of samples. X: {len(X_array)}, y: {len(y_array)}")
    
    # Validate cv parameter
    if not isinstance(cv, int) or cv < 2:
        raise ValueError(f"cv must be an integer >= 2, got {cv}")
    if cv > len(y_array):
        raise ValueError(f"cv ({cv}) cannot be greater than number of samples ({len(y_array)})")
    
    # Check for NaN/inf values in y
    if np.any(pd.isnull(y_array)):
        raise ValueError("y contains NaN values")
    
    # Check for NaN/inf values in X (handle mixed data types)
    try:
        if X_array.dtype.kind in ['i', 'f']:  # integer or float
            if np.any(np.isnan(X_array)) or np.any(np.isinf(X_array)):
                raise ValueError("X contains NaN or infinite values")
        elif isinstance(X, pd.DataFrame):
            # For DataFrames, check only numeric columns
            numeric_cols = X.select_dtypes(include=[np.number])
            if len(numeric_cols.columns) > 0:
                if numeric_cols.isnull().any().any() or np.isinf(numeric_cols.values).any():
                    raise ValueError("X contains NaN or infinite values")
    except (TypeError, ValueError) as e:
        if "NaN or infinite values" in str(e):
            raise e
        pass
    
    # Check if model appears to be for classification
    if hasattr(model, '_estimator_type'):
        if model._estimator_type != 'classifier':
            warnings.warn(f"Model appears to be a '{model._estimator_type}', but this function is designed for classification models.", 
                         UserWarning)
    
    # Determine if it's binary or multiclass
    unique_labels = np.unique(y_array)
    n_classes = len(unique_labels)
    is_binary = n_classes == 2
    
    # Define scoring metrics
    scoring = {
        'accuracy': 'accuracy',
        'precision': make_scorer(precision_score, average=average, zero_division=0),
        'recall': make_scorer(recall_score, average=average, zero_division=0),
        'f1': make_scorer(f1_score, average=average, zero_division=0)
    }
    
    # Add ROC AUC for binary classification
    if is_binary:
        scoring['roc_auc'] = 'roc_auc'
    
    # Perform cross-validation
    cv_results = cross_validate(
        model, X, y,
        cv=cv,
        scoring=scoring,
        return_train_score=False
    )
    
    # Calculate mean scores
    accuracy = np.mean(cv_results['test_accuracy'])
    precision = np.mean(cv_results['test_precision'])
    recall = np.mean(cv_results['test_recall'])
    f1 = np.mean(cv_results['test_f1'])
    
    # Define performance categories
    def get_classification_performance(score: float) -> str:
        """Get performance category for classification metrics (0-1 scale)"""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Good"
        elif score >= 0.7:
            return "Acceptable"
        elif score >= 0.6:
            return "Poor"
        else:
            return "Very Poor"
    
    # Prepare results data
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    values = [accuracy, precision, recall, f1]
    thresholds = [
        '≥0.9 = Excellent, 0.8-0.9 = Good, 0.7-0.8 = Acceptable, 0.6-0.7 = Poor, <0.6 = Very Poor'
    ] * 4
    calculations = [
        f'{accuracy:.4f} (correctly classified samples / total samples)',
        f'{precision:.4f} (true positives / predicted positives, {average} average)',
        f'{recall:.4f} (true positives / actual positives, {average} average)',
        f'{f1:.4f} (harmonic mean of precision and recall, {average} average)'
    ]
    performances = [
        get_classification_performance(accuracy),
        get_classification_performance(precision),
        get_classification_performance(recall),
        get_classification_performance(f1)
    ]
    
    # Add ROC AUC for binary classification
    if is_binary:
        roc_auc = np.mean(cv_results['test_roc_auc'])
        metrics.append('ROC AUC')
        values.append(roc_auc)
        thresholds.append('≥0.9 = Excellent, 0.8-0.9 = Good, 0.7-0.8 = Acceptable, 0.6-0.7 = Poor, <0.6 = Very Poor')
        calculations.append(f'{roc_auc:.4f} (area under ROC curve)')
        performances.append(get_classification_performance(roc_auc))
    
    # Create results DataFrame
    results = pd.DataFrame({
        'Metric': metrics,
        'Value': values,
        'Threshold': thresholds,
        'Calculation': calculations,
        'Performance': performances
    })
    
    return results