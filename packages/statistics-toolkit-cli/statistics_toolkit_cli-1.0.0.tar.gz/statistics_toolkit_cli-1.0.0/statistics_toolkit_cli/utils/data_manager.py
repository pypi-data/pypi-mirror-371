"""Data management utilities for loading, saving, and managing datasets."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional


class DataManager:
    """Handles data loading, saving, and management."""
    
    def __init__(self):
        self.data_dir = Path.home() / ".statstoolkit"
        self.data_dir.mkdir(exist_ok=True)
        self.current_data = {}
    
    def load_csv(self, filepath: str, column: str = None) -> Optional[np.ndarray]:
        """Load data from CSV file."""
        try:
            df = pd.read_csv(filepath)
            if column and column in df.columns:
                return df[column].dropna().values
            else:
                # Return first numeric column if no specific column requested
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    return df[numeric_cols[0]].dropna().values
                else:
                    print(f"No numeric columns found in {filepath}")
                    return None
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
    
    def save_data(self, name: str, data: np.ndarray):
        """Save data array to file."""
        filepath = self.data_dir / f"{name}.npy"
        np.save(filepath, data)
        print(f"Data saved as '{name}' in {filepath}")
    
    def load_data(self, name: str) -> Optional[np.ndarray]:
        """Load saved data array."""
        filepath = self.data_dir / f"{name}.npy"
        if filepath.exists():
            return np.load(filepath)
        return None
    
    def list_saved_data(self) -> List[str]:
        """List all saved data files."""
        return [f.stem for f in self.data_dir.glob("*.npy")]
    
    def get_sample_data(self, dataset_name: str = "test_scores") -> Optional[np.ndarray]:
        """Get built-in sample datasets."""
        np.random.seed(42)  # For reproducibility
        
        sample_datasets = {
            "test_scores": np.array([85, 92, 78, 88, 95, 82, 79, 91, 87, 84]),
            "heights": np.random.normal(170, 10, 30),
            "sales": np.random.lognormal(8, 0.5, 25),
            "temperatures": np.random.normal(22, 5, 20)
        }
        
        return sample_datasets.get(dataset_name)
