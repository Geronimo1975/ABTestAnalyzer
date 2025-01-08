import numpy as np
from scipy import stats

def calculate_efficiency_rate(completed_tasks, total_time):
    """Calculate efficiency rate (tasks per hour)"""
    return (completed_tasks / total_time) if total_time > 0 else 0

def calculate_accuracy_rate(correct_items, total_items):
    """Calculate accuracy rate for warehouse operations"""
    return (correct_items / total_items) if total_items > 0 else 0

def calculate_confidence_interval(successes, total, confidence=0.95):
    """Calculate confidence interval using normal approximation"""
    if total == 0:
        return (0, 0)

    p = successes / total
    z = stats.norm.ppf((1 + confidence) / 2)
    se = np.sqrt((p * (1 - p)) / total)

    lower = max(0, p - z * se)
    upper = min(1, p + z * se)

    return (lower, upper)

def calculate_statistical_significance(control_success, control_total, 
                                    test_success, test_total):
    """
    Calculate statistical significance using chi-square test
    Returns: chi-square statistic, p-value
    """
    if control_total == 0 or test_total == 0:
        return 0, 1.0

    contingency_table = [
        [control_success, control_total - control_success],
        [test_success, test_total - test_success]
    ]

    chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
    return chi2, p_value

def get_relative_improvement(control_rate, test_rate):
    """Calculate relative improvement percentage"""
    if control_rate == 0:
        return float('inf') if test_rate > 0 else 0
    return ((test_rate - control_rate) / control_rate) * 100

def calculate_utilization_rate(used_capacity, total_capacity):
    """Calculate storage utilization rate"""
    return (used_capacity / total_capacity) if total_capacity > 0 else 0