"""
Statistics Toolkit CLI - A comprehensive educational statistics tool.

A command-line statistics learning and analysis tool that provides 
step-by-step explanations for statistical concepts and calculations.
"""

__version__ = "1.0.0"
__author__ = "Connor O'Dea"
__email__ = "connorodea@users.noreply.github.com"
__description__ = "A comprehensive command-line statistics learning tool with step-by-step explanations"
__url__ = "https://github.com/connorodea/statistics-toolkit-cli"

# Import core classes with error handling
try:
    from .core.descriptive import DescriptiveStats
except ImportError as e:
    print(f"Warning: Could not import DescriptiveStats: {e}")
    DescriptiveStats = None

try:
    from .core.hypothesis import HypothesisTests
except ImportError as e:
    print(f"Warning: Could not import HypothesisTests: {e}")
    HypothesisTests = None

try:
    from .core.confidence import ConfidenceIntervals
except ImportError as e:
    print(f"Warning: Could not import ConfidenceIntervals: {e}")
    ConfidenceIntervals = None

try:
    from .core.probability import Probability
except ImportError as e:
    print(f"Warning: Could not import Probability: {e}")
    Probability = None

try:
    from .core.regression import RegressionAnalysis
except ImportError as e:
    print(f"Warning: Could not import RegressionAnalysis: {e}")
    RegressionAnalysis = None

try:
    from .core.visualization import Visualizations
except ImportError as e:
    print(f"Warning: Could not import Visualizations: {e}")
    Visualizations = None

try:
    from .utils.data_manager import DataManager
except ImportError as e:
    print(f"Warning: Could not import DataManager: {e}")
    DataManager = None

__all__ = [
    'DescriptiveStats',
    'HypothesisTests', 
    'ConfidenceIntervals',
    'Probability',
    'RegressionAnalysis',
    'Visualizations',
    'DataManager'
]
