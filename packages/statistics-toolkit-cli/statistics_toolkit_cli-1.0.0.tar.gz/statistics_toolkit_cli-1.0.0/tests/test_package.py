"""Test the package structure and imports."""

import unittest
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import statistics_toolkit_cli
from statistics_toolkit_cli import DescriptiveStats, DataManager
from statistics_toolkit_cli.cli import StatsCLI
import numpy as np


class TestPackageStructure(unittest.TestCase):
    """Test package structure and imports."""
    
    def test_package_imports(self):
        """Test that main classes can be imported."""
        self.assertTrue(hasattr(statistics_toolkit_cli, 'DescriptiveStats'))
        self.assertTrue(hasattr(statistics_toolkit_cli, 'DataManager'))
    
    def test_package_metadata(self):
        """Test package metadata."""
        self.assertEqual(statistics_toolkit_cli.__version__, "1.0.0")
        self.assertEqual(statistics_toolkit_cli.__author__, "Connor O'Dea")
    
    def test_descriptive_stats(self):
        """Test descriptive statistics functionality."""
        data = np.array([1, 2, 3, 4, 5])
        result = DescriptiveStats.measures_of_center(data, show_steps=False)
        
        self.assertEqual(result['mean'], 3.0)
        self.assertEqual(result['median'], 3.0)
        self.assertEqual(result['n'], 5)
    
    def test_data_manager(self):
        """Test data manager functionality."""
        dm = DataManager()
        sample_data = dm.get_sample_data("test_scores")
        
        self.assertIsInstance(sample_data, np.ndarray)
        self.assertEqual(len(sample_data), 10)
    
    def test_cli_creation(self):
        """Test CLI can be created."""
        cli = StatsCLI()
        self.assertIsInstance(cli, StatsCLI)


if __name__ == '__main__':
    unittest.main()
