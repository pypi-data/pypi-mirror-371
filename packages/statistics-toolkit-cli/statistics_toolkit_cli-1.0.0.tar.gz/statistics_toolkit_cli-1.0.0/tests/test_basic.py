#!/usr/bin/env python3
"""
Basic tests for the Statistics Toolkit.
"""

import sys
import os
import unittest
import numpy as np

# Add parent directory to path to import stats_cli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats_cli import DescriptiveStats, HypothesisTests

class TestDescriptiveStats(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    def test_measures_of_center(self):
        """Test measures of center calculations."""
        result = DescriptiveStats.measures_of_center(self.sample_data, show_steps=False)
        
        self.assertAlmostEqual(result['mean'], 5.5, places=2)
        self.assertAlmostEqual(result['median'], 5.5, places=2)
        self.assertEqual(result['n'], 10)
    
    def test_measures_of_spread(self):
        """Test measures of spread calculations."""
        result = DescriptiveStats.measures_of_spread(self.sample_data, show_steps=False)
        
        self.assertAlmostEqual(result['variance'], 9.17, places=2)
        self.assertAlmostEqual(result['std_dev'], 3.03, places=2)
        self.assertEqual(result['range'], 9)

class TestHypothesisTests(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = np.array([12.1, 11.8, 12.3, 11.9, 12.0, 12.2])
    
    def test_one_sample_t_test(self):
        """Test one-sample t-test."""
        result = HypothesisTests.one_sample_t_test(
            data=self.sample_data,
            mu0=12.0,
            alpha=0.05,
            alternative='two-sided',
            show_steps=False
        )
        
        self.assertIsInstance(result.statistic, float)
        self.assertIsInstance(result.p_value, float)
        self.assertTrue(0 <= result.p_value <= 1)

if __name__ == '__main__':
    unittest.main()
