"""Hypothesis testing with step-by-step explanations."""

import numpy as np
from scipy import stats
from typing import Optional
from dataclasses import dataclass


@dataclass
class StatResult:
    """Container for statistical test results."""
    test_name: str
    statistic: float
    p_value: float
    critical_value: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    interpretation: str = ""


class HypothesisTests:
    """Comprehensive hypothesis testing with step-by-step explanations."""
    
    @staticmethod
    def one_sample_t_test(data: np.ndarray, mu0: float, alpha: float = 0.05,
                         alternative: str = 'two-sided', show_steps: bool = True) -> StatResult:
        """One-sample t-test with full explanation."""
        n = len(data)
        sample_mean = np.mean(data)
        sample_std = np.std(data, ddof=1)
        
        if show_steps:
            print(f"\n=== ONE-SAMPLE T-TEST ===")
            print(f"Sample size: n = {n}")
            print(f"Sample mean: x̄ = {sample_mean:.4f}")
            print(f"Sample std dev: s = {sample_std:.4f}")
            print(f"Hypothesized mean: μ₀ = {mu0}")
            print(f"Significance level: α = {alpha}")
        
        # Hypotheses
        if show_steps:
            print(f"\nSTEP 1: HYPOTHESES")
            print(f"H₀: μ = {mu0}")
            if alternative == 'two-sided':
                print(f"H₁: μ ≠ {mu0}")
            elif alternative == 'greater':
                print(f"H₁: μ > {mu0}")
            else:
                print(f"H₁: μ < {mu0}")
        
        # Test statistic
        t_stat = (sample_mean - mu0) / (sample_std / np.sqrt(n))
        df = n - 1
        
        if show_steps:
            print(f"\nSTEP 2: TEST STATISTIC")
            print(f"t = (x̄ - μ₀)/(s/√n)")
            print(f"t = ({sample_mean:.4f} - {mu0})/({sample_std:.4f}/√{n})")
            print(f"t = {t_stat:.4f} (df = {df})")
        
        # P-value
        if alternative == 'two-sided':
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
        elif alternative == 'greater':
            p_value = 1 - stats.t.cdf(t_stat, df)
        else:
            p_value = stats.t.cdf(t_stat, df)
        
        # Critical value
        if alternative == 'two-sided':
            critical_value = stats.t.ppf(1 - alpha/2, df)
        else:
            critical_value = stats.t.ppf(1 - alpha, df)
        
        if show_steps:
            print(f"\nSTEP 3: P-VALUE")
            print(f"P-value = {p_value:.6f}")
        
        # Decision
        reject_null = p_value < alpha
        
        if show_steps:
            print(f"\nSTEP 4: DECISION")
            print(f"α = {alpha}")
            if reject_null:
                print(f"P-value ({p_value:.6f}) < α ({alpha}): REJECT H₀")
            else:
                print(f"P-value ({p_value:.6f}) ≥ α ({alpha}): FAIL TO REJECT H₀")
        
        interpretation = f"{'Reject' if reject_null else 'Fail to reject'} H₀ at α = {alpha}"
        
        return StatResult(
            test_name="One-Sample t-test",
            statistic=t_stat,
            p_value=p_value,
            critical_value=critical_value,
            interpretation=interpretation
        )
