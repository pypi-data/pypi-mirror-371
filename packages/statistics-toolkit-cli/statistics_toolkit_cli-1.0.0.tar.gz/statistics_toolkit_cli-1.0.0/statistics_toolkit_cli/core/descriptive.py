"""Descriptive statistics calculations with step-by-step explanations."""

import numpy as np
from typing import Dict


class DescriptiveStats:
    """Descriptive statistics calculations with step-by-step explanations."""
    
    @staticmethod
    def measures_of_center(data: np.ndarray, show_steps: bool = True) -> Dict:
        """Calculate and explain measures of center."""
        n = len(data)
        
        if show_steps:
            print("\n=== MEASURES OF CENTER ===")
            print(f"Sample size: n = {n}")
            print(f"Data: {data}")
        
        # Mean
        data_sum = np.sum(data)
        mean = np.mean(data)
        
        if show_steps:
            print(f"\nMEAN CALCULATION:")
            print(f"x̄ = Σx/n = {data_sum}/{n} = {mean:.4f}")
        
        # Median
        sorted_data = np.sort(data)
        median = np.median(data)
        
        if show_steps:
            print(f"\nMEDIAN CALCULATION:")
            print(f"Sorted data: {sorted_data}")
            if n % 2 == 0:
                mid1, mid2 = sorted_data[n//2-1], sorted_data[n//2]
                print(f"n is even: median = ({mid1} + {mid2})/2 = {median:.4f}")
            else:
                print(f"n is odd: median = {sorted_data[n//2]:.4f}")
        
        # Mode (for discrete data)
        values, counts = np.unique(data, return_counts=True)
        max_count = np.max(counts)
        modes = values[counts == max_count]
        
        if show_steps:
            print(f"\nMODE:")
            if len(modes) == 1:
                print(f"Mode = {modes[0]:.4f} (appears {max_count} times)")
            elif len(modes) == len(data):
                print("No mode (all values appear once)")
            else:
                print(f"Modes = {modes} (each appears {max_count} times)")
        
        return {
            'mean': mean,
            'median': median,
            'mode': modes,
            'n': n
        }
    
    @staticmethod
    def measures_of_spread(data: np.ndarray, show_steps: bool = True) -> Dict:
        """Calculate and explain measures of spread."""
        n = len(data)
        mean = np.mean(data)
        
        if show_steps:
            print("\n=== MEASURES OF SPREAD ===")
            print(f"Data: {data}")
            print(f"Mean: x̄ = {mean:.4f}")
        
        # Variance and Standard Deviation
        deviations = data - mean
        squared_deviations = deviations ** 2
        sum_squared_dev = np.sum(squared_deviations)
        
        # Sample variance and std dev
        variance = np.var(data, ddof=1)
        std_dev = np.std(data, ddof=1)
        
        if show_steps:
            print(f"\nVARIANCE CALCULATION:")
            print(f"Deviations from mean: {deviations}")
            print(f"Squared deviations: {squared_deviations}")
            print(f"Σ(x - x̄)² = {sum_squared_dev:.4f}")
            print(f"s² = Σ(x - x̄)²/(n-1) = {sum_squared_dev:.4f}/{n-1} = {variance:.4f}")
            print(f"\nSTANDARD DEVIATION:")
            print(f"s = √(s²) = √{variance:.4f} = {std_dev:.4f}")
        
        # Range
        data_range = np.max(data) - np.min(data)
        
        if show_steps:
            print(f"\nRANGE:")
            print(f"Range = max - min = {np.max(data):.4f} - {np.min(data):.4f} = {data_range:.4f}")
        
        return {
            'variance': variance,
            'std_dev': std_dev,
            'range': data_range,
            'min': np.min(data),
            'max': np.max(data)
        }
    
    @staticmethod
    def five_number_summary(data: np.ndarray, show_steps: bool = True) -> Dict:
        """Calculate five-number summary and check for outliers."""
        sorted_data = np.sort(data)
        
        q1 = np.percentile(data, 25)
        median = np.percentile(data, 50)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        if show_steps:
            print("\n=== FIVE-NUMBER SUMMARY ===")
            print(f"Sorted data: {sorted_data}")
            print(f"Min = {np.min(data):.4f}")
            print(f"Q1 = {q1:.4f}")
            print(f"Median = {median:.4f}")
            print(f"Q3 = {q3:.4f}")
            print(f"Max = {np.max(data):.4f}")
            print(f"\nIQR = Q3 - Q1 = {q3:.4f} - {q1:.4f} = {iqr:.4f}")
        
        # Outlier detection
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = data[(data < lower_fence) | (data > upper_fence)]
        
        if show_steps:
            print(f"\nOUTLIER DETECTION:")
            print(f"Lower fence = Q1 - 1.5×IQR = {q1:.4f} - 1.5×{iqr:.4f} = {lower_fence:.4f}")
            print(f"Upper fence = Q3 + 1.5×IQR = {q3:.4f} + 1.5×{iqr:.4f} = {upper_fence:.4f}")
            if len(outliers) > 0:
                print(f"Outliers: {outliers}")
            else:
                print("No outliers detected")
        
        return {
            'min': np.min(data),
            'q1': q1,
            'median': median,
            'q3': q3,
            'max': np.max(data),
            'iqr': iqr,
            'outliers': outliers,
            'lower_fence': lower_fence,
            'upper_fence': upper_fence
        }
