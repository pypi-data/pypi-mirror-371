"""Statistical visualizations."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional


class Visualizations:
    """Statistical visualizations."""
    
    @staticmethod
    def histogram(data: np.ndarray, title: str = "Histogram", bins: int = 10):
        """Create histogram with statistics overlay."""
        try:
            plt.figure(figsize=(10, 6))
            plt.hist(data, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
            
            # Add statistics
            mean = np.mean(data)
            std = np.std(data, ddof=1)
            plt.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
            
            plt.title(title)
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.show()
        except Exception as e:
            print(f"Visualization error (this is normal in headless environments): {e}")
    
    @staticmethod
    def boxplot(data: np.ndarray, title: str = "Box Plot"):
        """Create box plot with outlier identification."""
        try:
            plt.figure(figsize=(8, 6))
            plt.boxplot(data, patch_artist=True)
            plt.title(title)
            plt.ylabel("Value")
            plt.grid(True, alpha=0.3)
            plt.show()
        except Exception as e:
            print(f"Visualization error (this is normal in headless environments): {e}")
