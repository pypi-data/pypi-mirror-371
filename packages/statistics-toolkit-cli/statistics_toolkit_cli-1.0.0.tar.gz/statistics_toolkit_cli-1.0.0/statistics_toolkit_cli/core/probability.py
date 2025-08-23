"""Probability calculations and distributions."""

import numpy as np
from scipy import stats
from typing import Dict, Optional


class Probability:
    """Probability calculations and distributions."""
    
    @staticmethod
    def basic_probability(event_a: Optional[float] = None, event_b: Optional[float] = None, 
                         intersection: Optional[float] = None, show_steps: bool = True) -> Dict:
        """Calculate basic probability rules."""
        if show_steps:
            print("\n=== BASIC PROBABILITY RULES ===")
        
        results = {}
        
        if event_a is not None:
            complement_a = 1 - event_a
            results['complement_a'] = complement_a
            if show_steps:
                print(f"P(A') = 1 - P(A) = 1 - {event_a} = {complement_a}")
        
        if event_a is not None and event_b is not None and intersection is not None:
            union = event_a + event_b - intersection
            results['union'] = union
            if show_steps:
                print(f"P(A ∪ B) = P(A) + P(B) - P(A ∩ B) = {union}")
        
        return results
    
    @staticmethod
    def binomial_probability(n: int, p: float, k: Optional[int] = None, 
                           show_steps: bool = True) -> Dict:
        """Calculate binomial probabilities."""
        if show_steps:
            print(f"\n=== BINOMIAL DISTRIBUTION ===")
            print(f"n = {n} trials, p = {p} success probability")
        
        results = {}
        
        # Mean and standard deviation
        mean = n * p
        variance = n * p * (1 - p)
        std_dev = np.sqrt(variance)
        
        results.update({
            'mean': mean,
            'variance': variance,
            'std_dev': std_dev
        })
        
        if show_steps:
            print(f"μ = np = {n} × {p} = {mean}")
            print(f"σ = √(np(1-p)) = {std_dev:.4f}")
        
        if k is not None:
            prob_exact = stats.binom.pmf(k, n, p)
            prob_cumulative = stats.binom.cdf(k, n, p)
            
            results.update({
                'prob_exact': prob_exact,
                'prob_cumulative': prob_cumulative
            })
            
            if show_steps:
                print(f"P(X = {k}) = {prob_exact:.6f}")
                print(f"P(X ≤ {k}) = {prob_cumulative:.6f}")
        
        return results
