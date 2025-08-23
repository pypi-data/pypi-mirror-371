"""Command-line interface for the Statistics Toolkit."""

import sys
import argparse
import numpy as np
from typing import Optional

from .core.descriptive import DescriptiveStats
from .core.hypothesis import HypothesisTests
from .utils.data_manager import DataManager


class StatsCLI:
    """Main command-line interface for the statistics toolkit."""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.descriptive = DescriptiveStats()
        self.hypothesis = HypothesisTests()
    
    def main_menu(self):
        """Display main menu and handle user input."""
        while True:
            print("\n" + "="*60)
            print("        STATISTICS TOOLKIT - MAIN MENU")
            print("="*60)
            print("1.  Descriptive Statistics")
            print("2.  Hypothesis Testing")
            print("3.  Sample Data Demo")
            print("4.  Help")
            print("0.  Exit")
            print("="*60)
            
            try:
                choice = input("Enter your choice (0-4): ").strip()
                
                if choice == '0':
                    print("Thank you for using the Statistics Toolkit!")
                    break
                elif choice == '1':
                    self.descriptive_menu()
                elif choice == '2':
                    self.hypothesis_menu()
                elif choice == '3':
                    self.sample_data_demo()
                elif choice == '4':
                    self.help_menu()
                else:
                    print("Invalid choice. Please enter a number from 0-4.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
    
    def descriptive_menu(self):
        """Descriptive statistics submenu."""
        print("\n=== DESCRIPTIVE STATISTICS ===")
        data = self.get_data_input()
        if data is None:
            return
        
        print("Choose analysis:")
        print("1. Measures of Center")
        print("2. Measures of Spread")  
        print("3. Five-Number Summary")
        print("4. All Statistics")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            self.descriptive.measures_of_center(data)
        elif choice == '2':
            self.descriptive.measures_of_spread(data)
        elif choice == '3':
            self.descriptive.five_number_summary(data)
        elif choice == '4':
            self.descriptive.measures_of_center(data)
            self.descriptive.measures_of_spread(data)
            self.descriptive.five_number_summary(data)
    
    def hypothesis_menu(self):
        """Hypothesis testing submenu."""
        print("\n=== HYPOTHESIS TESTING ===")
        print("1. One-Sample t-test")
        
        choice = input("Enter choice (1): ").strip()
        
        if choice == '1':
            data = self.get_data_input()
            if data is None:
                return
            mu0 = float(input("Enter hypothesized mean (μ₀): "))
            alpha = float(input("Enter significance level (default 0.05): ") or "0.05")
            
            alt_choice = input("Alternative hypothesis (1=two-sided, 2=greater, 3=less): ").strip()
            alternative = {'1': 'two-sided', '2': 'greater', '3': 'less'}.get(alt_choice, 'two-sided')
            
            result = self.hypothesis.one_sample_t_test(data, mu0, alpha, alternative)
    
    def sample_data_demo(self):
        """Demonstrate with sample data."""
        print("\n=== SAMPLE DATA DEMONSTRATION ===")
        
        # Use built-in sample data
        test_scores = self.data_manager.get_sample_data("test_scores")
        
        print("Using sample test scores:", test_scores)
        print("\nRunning complete analysis...")
        
        # Run all analyses
        self.descriptive.measures_of_center(test_scores)
        self.descriptive.measures_of_spread(test_scores)
        self.descriptive.five_number_summary(test_scores)
        
        # Hypothesis test
        print("\n" + "="*50)
        print("HYPOTHESIS TEST EXAMPLE")
        print("Testing if mean test score = 85")
        print("="*50)
        
        result = self.hypothesis.one_sample_t_test(test_scores, 85, 0.05, 'two-sided')
    
    def help_menu(self):
        """Display help information."""
        print("\n=== STATISTICS TOOLKIT HELP ===")
        print("This toolkit provides step-by-step statistical analysis.")
        print("\nFeatures:")
        print("• Descriptive Statistics - Mean, median, variance, etc.")
        print("• Hypothesis Testing - t-tests with full explanations")
        print("• Educational Focus - Shows all calculation steps")
        print("\nFor more help, visit: https://github.com/connorodea/statistics-toolkit-cli")
    
    def get_data_input(self) -> Optional[np.ndarray]:
        """Get data input from user."""
        print("\nData input options:")
        print("1. Enter values manually")
        print("2. Use sample data")
        
        choice = input("Choose option (1-2): ").strip()
        
        if choice == '1':
            data_str = input("Enter values separated by spaces or commas: ")
            try:
                data_str = data_str.replace(',', ' ')
                data = np.array([float(x) for x in data_str.split()])
                return data
            except ValueError:
                print("Invalid data format. Please enter numeric values.")
                return None
        elif choice == '2':
            return self.data_manager.get_sample_data("test_scores")
        
        return None


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Statistics Toolkit CLI - Educational statistics with step-by-step explanations"
    )
    parser.add_argument("--version", action="version", version="Statistics Toolkit CLI 1.0.0")
    parser.add_argument("--demo", action="store_true", help="Run sample data demonstration")
    
    args = parser.parse_args()
    
    cli = StatsCLI()
    
    if args.demo:
        cli.sample_data_demo()
    elif len(sys.argv) == 1:
        print("Welcome to the Statistics Toolkit CLI!")
        print("A comprehensive tool for statistical analysis and learning.")
        cli.main_menu()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
