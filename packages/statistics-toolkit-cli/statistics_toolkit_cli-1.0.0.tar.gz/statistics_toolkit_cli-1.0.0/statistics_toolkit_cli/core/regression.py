"""Linear regression analysis with detailed explanations."""

import numpy as np
from scipy import stats
from typing import Dict


class RegressionAnalysis:
    """Linear regression with detailed analysis."""
    
    @staticmethod
    def linear_regression(x_data: np.ndarray, y_data: np.ndarray, 
                         show_steps: bool = True) -> Dict:
        """Perform linear regression with step-by-step calculations."""
        n = len(x_data)
        
        if show_steps:
            print(f"\n=== LINEAR REGRESSION ANALYSIS ===")
            print(f"Sample size: n = {n}")
        
        # Basic calculations
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
        r_squared = r_value**2
        
        if show_steps:
            print(f"Slope (b₁): {slope:.6f}")
            print(f"Intercept (b₀): {intercept:.6f}")
            print(f"Correlation (r): {r_value:.6f}")
            print(f"R-squared: {r_squared:.6f}")
            print(f"Equation: ŷ = {intercept:.6f} + {slope:.6f}x")
        
        # Predictions and residuals
        y_pred = intercept + slope * x_data
        residuals = y_data - y_pred
        
        return {
            'slope': slope,
            'intercept': intercept,
            'correlation': r_value,
            'r_squared': r_squared,
            'standard_error': std_err,
            'residuals': residuals,
            'predictions': y_pred,
            'equation': f"y = {intercept:.6f} + {slope:.6f}x"
        }
