#!/usr/bin/env python3
"""
Create sample datasets for the Statistics Toolkit.
"""

import numpy as np
import pandas as pd
import os

def create_sample_datasets():
    """Create sample CSV datasets for practice."""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Test scores dataset
    np.random.seed(42)
    test_scores = pd.DataFrame({
        'student_id': range(1, 51),
        'math_score': np.random.normal(78, 12, 50).round(1),
        'science_score': np.random.normal(82, 10, 50).round(1),
        'study_hours': np.random.gamma(2, 2, 50).round(1),
    })
    test_scores.to_csv('data/test_scores.csv', index=False)
    
    # Sales data
    np.random.seed(123)
    sales_data = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] * 10,
        'sales': np.random.lognormal(8, 0.5, 60).round(2),
        'advertising': np.random.gamma(3, 1000, 60).round(2),
    })
    sales_data.to_csv('data/sales_data.csv', index=False)
    
    # Simple regression data
    np.random.seed(456)
    hours_study = np.random.uniform(0, 10, 30)
    exam_scores = 60 + 3.5 * hours_study + np.random.normal(0, 5, 30)
    exam_scores = np.clip(exam_scores, 0, 100)  # Keep between 0-100
    
    regression_data = pd.DataFrame({
        'hours_studied': hours_study.round(1),
        'exam_score': exam_scores.round(1)
    })
    regression_data.to_csv('data/study_vs_scores.csv', index=False)
    
    print("Sample datasets created successfully:")
    print("- data/test_scores.csv")
    print("- data/sales_data.csv") 
    print("- data/study_vs_scores.csv")
    print("")
    print("Try loading them with:")
    print("  python stats_cli.py")
    print("  Choose option 2: Load from CSV file")
    print("  Enter: examples/data/test_scores.csv")

if __name__ == "__main__":
    create_sample_datasets()
