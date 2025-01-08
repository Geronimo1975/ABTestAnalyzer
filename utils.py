import numpy as np
from scipy import stats

def calculate_conversion_rate(conversions, total):
    """Calculate conversion rate"""
    return (conversions / total) if total > 0 else 0

def calculate_confidence_interval(conversions, total, confidence=0.95):
    """Calculate confidence interval using normal approximation"""
    if total == 0:
        return (0, 0)
    
    p = conversions / total
    z = stats.norm.ppf((1 + confidence) / 2)
    se = np.sqrt((p * (1 - p)) / total)
    
    lower = max(0, p - z * se)
    upper = min(1, p + z * se)
    
    return (lower, upper)

def calculate_statistical_significance(control_conv, control_size, 
                                    test_conv, test_size):
    """
    Calculate statistical significance using chi-square test
    Returns: chi-square statistic, p-value
    """
    if control_size == 0 or test_size == 0:
        return 0, 1.0
        
    contingency_table = [
        [control_conv, control_size - control_conv],
        [test_conv, test_size - test_conv]
    ]
    
    chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
    return chi2, p_value

def get_relative_improvement(control_rate, test_rate):
    """Calculate relative improvement percentage"""
    if control_rate == 0:
        return float('inf') if test_rate > 0 else 0
    return ((test_rate - control_rate) / control_rate) * 100
