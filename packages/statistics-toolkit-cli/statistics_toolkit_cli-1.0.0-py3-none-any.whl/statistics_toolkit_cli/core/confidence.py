"""Confidence interval calculations with explanations."""

import numpy as np
from scipy import stats
from typing import Dict, Optional


class ConfidenceIntervals:
    """Confidence interval calculations with explanations."""
    
    @staticmethod
    def mean_confidence_interval(data: np.ndarray, confidence: float = 0.95,
                                sigma: Optional[float] = None, show_steps: bool = True) -> Dict:
        """Confidence interval for population mean."""
        n = len(data)
        sample_mean = np.mean(data)
        alpha = 1 - confidence
        
        if show_steps:
            print(f"\n=== CONFIDENCE INTERVAL FOR μ ===")
            print(f"Sample size: n = {n}")
            print(f"Sample mean: x̄ = {sample_mean:.4f}")
            print(f"Confidence level: {confidence*100}%")
            print(f"α = {alpha}")
        
        if sigma is not None:
            # Known population standard deviation - use z
            critical_value = stats.norm.ppf(1 - alpha/2)
            margin_error = critical_value * sigma / np.sqrt(n)
            distribution = "z"
            
            if show_steps:
                print(f"Population σ known: σ = {sigma}")
                print(f"Using z-distribution")
                print(f"z₍α/2₎ = {critical_value:.4f}")
        else:
            # Unknown population standard deviation - use t
            sample_std = np.std(data, ddof=1)
            df = n - 1
            critical_value = stats.t.ppf(1 - alpha/2, df)
            margin_error = critical_value * sample_std / np.sqrt(n)
            distribution = "t"
            
            if show_steps:
                print(f"Population σ unknown: s = {sample_std:.4f}")
                print(f"Using t-distribution with df = {df}")
                print(f"t₍α/2₎ = {critical_value:.4f}")
        
        lower_bound = sample_mean - margin_error
        upper_bound = sample_mean + margin_error
        
        if show_steps:
            se = sigma/np.sqrt(n) if sigma else sample_std/np.sqrt(n)
            print(f"\nMARGIN OF ERROR:")
            print(f"SE = {'σ' if sigma else 's'}/√n = {se:.4f}")
            print(f"ME = {critical_value:.4f} × {se:.4f} = {margin_error:.4f}")
            print(f"\nCONFIDENCE INTERVAL:")
            print(f"({lower_bound:.4f}, {upper_bound:.4f})")
        
        return {
            'confidence_level': confidence,
            'sample_mean': sample_mean,
            'margin_error': margin_error,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'critical_value': critical_value,
            'distribution': distribution
        }
