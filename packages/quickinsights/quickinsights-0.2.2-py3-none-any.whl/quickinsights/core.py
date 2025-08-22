"""
QuickInsights Core Analysis Module

This module contains the main analysis functions for datasets.
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from typing import Dict

from .visualizer import (
    correlation_matrix,
    distribution_plots,
    summary_stats,
    create_interactive_plots,
    box_plots,
)
from .utils import (
    get_data_info,
    detect_outliers,
)


def validate_dataframe(df) -> bool:
    """
    Check if DataFrame is valid.

    Parameters
    ----------
    df : Any
        Data to check

    Returns
    -------
    bool
        True if DataFrame is valid, False otherwise

    Raises
    ------
    DataValidationError
        If DataFrame is invalid
    """
    from .error_handling import ValidationUtils
    ValidationUtils.validate_dataframe(df)
    return True


def analyze(df, show_plots=True, save_plots=False, output_dir="./quickinsights_output"):
    """
    Perform comprehensive analysis on dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to analyze
    show_plots : bool, default True
        Show plots
    save_plots : bool, default False
        Save plots
    output_dir : str, default "./quickinsights_output"
        Directory to save plots

    Returns
    -------
    dict
        Analysis results
    """
    # DataFrame validation
    validate_dataframe(df)

    print("🔍 QuickInsights - Dataset Analysis Starting...")
    print("=" * 60)

    # Create output directory
    if save_plots:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")

    # Dataset information
    print("\n📊 Dataset Information:")
    print(f"   📏 Size: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   💾 Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    # Data types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    print(f"   🔢 Numeric variables: {len(numeric_cols)}")
    print(f"   📝 Categorical variables: {len(categorical_cols)}")

    # Missing value analysis
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print("\n⚠️  Missing Values:")
        for col, missing_count in missing_data[missing_data > 0].items():
            percentage = (missing_count / len(df)) * 100
            print(f"   {col}: {missing_count} ({percentage:.1f}%)")
    else:
        print("\n✅ No missing values found!")

    # Analysis sections
    print("\n🔢 Numeric Variable Analysis:")
    numeric_results = analyze_numeric(df)
    
    print("\n📝 Categorical Variable Analysis:")
    categorical_results = analyze_categorical(df)

    # Visualization
    if show_plots or save_plots:
        if save_plots:
            print("\n📈 Creating and saving visualizations...")
        else:
            print("\n📈 Creating visualizations...")
        
        # Create visualizations
        try:
            if len(numeric_cols) > 0:
                # Correlation matrix
                correlation_matrix(df[numeric_cols], save_path=f"{output_dir}/correlation_matrix.png" if save_plots else None)
                
                # Distribution plots
                distribution_plots(df[numeric_cols], save_path=f"{output_dir}/distributions.png" if save_plots else None)
                
                # Box plots
                box_plots(df[numeric_cols], save_path=f"{output_dir}/box_plots.png" if save_plots else None)
            
            if len(categorical_cols) > 0:
                # Categorical analysis plots
                for col in categorical_cols:
                    if df[col].nunique() <= 20:  # Only plot if not too many unique values
                        summary_stats(df, col, save_path=f"{output_dir}/{col}_summary.png" if save_plots else None)
                        
        except Exception as e:
            print(f"⚠️  Visualization error: {e}")

    # Summary statistics
    print("\n📊 Summary Statistics:")
    summary_stats = {
        'dataset_info': {
            'rows': df.shape[0],
            'columns': df.shape[1],
            'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'missing_values': missing_data.sum(),
            'duplicate_rows': df.duplicated().sum()
        },
        'numeric_analysis': numeric_results,
        'categorical_analysis': categorical_results
    }
    
    print(f"   📏 Total rows: {summary_stats['dataset_info']['rows']}")
    print(f"   📊 Total columns: {summary_stats['dataset_info']['columns']}")
    print(f"   💾 Memory usage: {summary_stats['dataset_info']['memory_mb']:.2f} MB")
    print(f"   ❓ Missing values: {summary_stats['dataset_info']['missing_values']}")
    print(f"   🔄 Duplicate rows: {summary_stats['dataset_info']['duplicate_rows']}")

    print("\n✅ Analysis completed!")
    
    return summary_stats


def analyze_numeric(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> dict:
    """
    Perform detailed analysis on numeric variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing only numeric variables
    show_plots : bool, default=True
        Whether to show plots
    save_plots : bool, default=False
        Whether to save plots
    output_dir : str, default="./quickinsights_output"
        Directory to save plots

    Returns
    -------
    dict
        Numeric analysis results
    """

    if df.empty:
        print("⚠️  No numeric variables found!")
        return {}

    # Filter only numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) == 0:
        print("⚠️  No numeric variables found!")
        return {}
    
    # Create a DataFrame with only numeric columns
    numeric_df = df[numeric_cols]

    print(f"\n🔢 NUMERIC VARIABLE ANALYSIS ({len(numeric_cols)} variables)")
    print("-" * 50)

    # Statistical summary
    summary = summary_stats(numeric_df)

    # Vectorized printing - process all columns at once
    col_names = numeric_cols
    means = [summary[col]["mean"] for col in col_names]
    medians = [summary[col]["median"] for col in col_names]
    stds = [summary[col]["std"] for col in col_names]
    mins = [summary[col]["min"] for col in col_names]
    maxs = [summary[col]["max"] for col in col_names]
    q1s = [summary[col]["q1"] for col in col_names]
    q3s = [summary[col]["q3"] for col in col_names]

    # Print results for each column
    for i, col in enumerate(col_names):
        print(f"\n📊 {col}:")
        print(f"   Mean: {means[i]:.4f}")
        print(f"   Median: {medians[i]:.4f}")
        print(f"   Standard deviation: {stds[i]:.4f}")
        print(f"   Minimum: {mins[i]:.4f}")
        print(f"   Maximum: {maxs[i]:.4f}")
        print(f"   Quartiles: Q1={q1s[i]:.4f}, Q3={q3s[i]:.4f}")

    # Visualizations
    if show_plots:
        distribution_plots(numeric_df, save_plots=save_plots, output_dir=output_dir)

    # Return results
    results = {}
    for col in col_names:
        results[col] = {
            "mean": means[col_names.index(col)],
            "median": medians[col_names.index(col)],
            "std": stds[col_names.index(col)],
            "min": mins[col_names.index(col)],
            "max": maxs[col_names.index(col)],
            "q1": q1s[col_names.index(col)],
            "q3": q3s[col_names.index(col)],
        }

    return results


def analyze_categorical(
    df: pd.DataFrame,
    show_plots: bool = True,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> dict:
    """
    Perform detailed analysis on categorical variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing only categorical variables
    show_plots : bool, default=True
        Whether to show plots
    save_plots : bool, default=False
        Whether to save plots
    output_dir : str, default="./quickinsights_output"
        Directory to save plots

    Returns
    -------
    dict
        Categorical analysis results
    """

    if df.empty:
        print("⚠️  No categorical variables found!")
        return {}

    print(f"\n🏷️  CATEGORICAL VARIABLE ANALYSIS ({len(df.columns)} variables)")
    print("-" * 50)

    # Vectorized operations - process all columns at once
    col_names = df.columns.tolist()

    # Calculate value_counts for all columns at once
    value_counts_list = [df[col].value_counts() for col in col_names]
    missing_counts = df.isnull().sum()

    results = {}

    # Batch processing - process all columns at once
    for i, col in enumerate(col_names):
        value_counts = value_counts_list[i]
        missing = missing_counts[col]

        print(f"\n📊 {col}:")
        print(f"   Number of unique values: {len(value_counts)}")
        print(
            f"   Most common value: '{value_counts.index[0]}' ({value_counts.iloc[0]} times)"
        )

        if missing > 0:
            print(f"   Missing values: {missing}")

        print(f"   First 5 values: {list(value_counts.head().index)}")

        results[col] = {
            "unique_count": len(value_counts),
            "most_common": value_counts.index[0],
            "most_common_count": value_counts.iloc[0],
            "missing_count": missing,
            "value_counts": value_counts,
        }

    return results


def summary_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to analyze

    Returns
    -------
    Dict[str, Dict[str, float]]
        Summary statistics for each column
    """
    stats = {}

    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                stats[col] = {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q1": float(col_data.quantile(0.25)),
                    "q3": float(col_data.quantile(0.75)),
                }

    return stats


def box_plots(
    df: pd.DataFrame,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Create box plots for numeric variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing only numeric variables
    save_plots : bool, default=False
        Whether to save plots
    output_dir : str, default="./quickinsights_output"
        Directory to save plots
    """
    if df.empty:
        print("⚠️  No numeric variables found for box plots!")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        print("⚠️  No numeric variables found for box plots!")
        return

    print(f"\n📦 Creating box plots ({len(numeric_cols)} variables)...")

    # Create box plots
    fig, axes = plt.subplots(1, len(numeric_cols), figsize=(5 * len(numeric_cols), 6))

    if len(numeric_cols) == 1:
        axes = [axes]

    for i, col in enumerate(numeric_cols):
        df[col].plot(kind="box", ax=axes[i])
        axes[i].set_title(f"Box Plot - {col}")
        axes[i].set_ylabel("Value")

    plt.tight_layout()

    if save_plots:
        output_dir = create_output_directory(output_dir)
        plt.savefig(f"{output_dir}/box_plots.png", dpi=300, bbox_inches="tight")
        print(f"💾 Box plots saved: {output_dir}/box_plots.png")
        plt.close()
    else:
        plt.show()


def create_interactive_plots(
    df: pd.DataFrame,
    save_plots: bool = False,
    output_dir: str = "./quickinsights_output",
) -> None:
    """
    Create interactive plots for numeric variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing only numeric variables
    save_plots : bool, default=False
        Whether to save plots
    output_dir : str, default="./quickinsights_output"
        Directory to save plots
    """
    if df.empty:
        print("⚠️  No numeric variables found for interactive plots!")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        print("⚠️  No numeric variables found for interactive plots!")
        return

    print(f"\n🎨 Creating interactive plots ({len(numeric_cols)} variables)...")

    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # Scatter plot matrix
        if len(numeric_cols) > 1:
            fig = px.scatter_matrix(df[numeric_cols], title="Scatter Plot Matrix")

            if save_plots:
                output_dir = create_output_directory(output_dir)
                fig.write_html(f"{output_dir}/scatter_matrix.html")
                print(f"💾 Scatter matrix saved: {output_dir}/scatter_matrix.html")
            else:
                fig.show()

        # Histogram's
        for col in numeric_cols:
            fig = px.histogram(df, x=col, title=f"Histogram - {col}")

            if save_plots:
                output_dir = create_output_directory(output_dir)
                fig.write_html(f"{output_dir}/histogram_{col}.html")
                print(f"💾 Histogram saved: {output_dir}/histogram_{col}.html")
            else:
                fig.show()

    except ImportError:
        print("⚠️  Plotly not found. Interactive plots cannot be created.")
        print("   Installation: pip install plotly")


def create_output_directory(output_dir: str) -> str:
    """
    Create output directory.

    Parameters
    ----------
    output_dir : str
        Path to create

    Returns
    -------
    str
        Created path
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Output directory created: {output_dir}")
    return output_dir


class LazyAnalyzer:
    """
    Lazy evaluation for data analysis.

    This class performs analyses only when needed and caches results.
    This makes repeated analyses much faster.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize LazyAnalyzer.

        Parameters
        ----------
        df : pd.DataFrame
            Dataset to analyze
        """
        self.df = df
        self._results = {}
        self._data_info = None
        self._numeric_analysis = None
        self._categorical_analysis = None
        self._correlation_matrix = None
        self._outliers = None

        # Determine column types without copying the dataframe
        self._numeric_cols = df.select_dtypes(include=[np.number]).columns
        self._categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns

        print("🚀 LazyAnalyzer initialized!")
        print(f"   📊 Dataset size: {df.shape}")
        print(
            f"   💾 Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        )

    def get_data_info(self):
        """Get general dataset information (lazy)"""
        if self._data_info is None:
            print("🔍 Calculating dataset information...")
            self._data_info = get_data_info(self.df)
        return self._data_info

    def get_numeric_analysis(self):
        """Get numeric analysis results (lazy)"""
        if self._numeric_analysis is None:
            print("🔢 Performing numeric analysis...")
            if len(self._numeric_cols) > 0:
                self._numeric_analysis = analyze_numeric(
                    self.df[self._numeric_cols], show_plots=False
                )
            else:
                self._numeric_analysis = {}
        return self._numeric_analysis

    def get_categorical_analysis(self):
        """Get categorical analysis results (lazy)"""
        if self._categorical_analysis is None:
            print("🏷️  Performing categorical analysis...")
            if len(self._categorical_cols) > 0:
                self._categorical_analysis = analyze_categorical(
                    self.df[self._categorical_cols], show_plots=False
                )
            else:
                self._categorical_analysis = {}
        return self._categorical_analysis

    def get_correlation_matrix(self):
        """Get correlation matrix (lazy)"""
        if self._correlation_matrix is None:
            print("📊 Calculating correlation matrix...")
            if len(self._numeric_cols) > 1:
                # Calculate correlation
                self._correlation_matrix = self.df[self._numeric_cols].corr()
            else:
                self._correlation_matrix = pd.DataFrame()
        return self._correlation_matrix

    def get_outliers(self, method: str = "iqr", threshold: float = 1.5):
        """Get outliers (lazy)"""
        if self._outliers is None:
            print("⚠️  Detecting outliers...")
            if len(self._numeric_cols) > 0:
                self._outliers = detect_outliers(
                    self.df[self._numeric_cols], method=method, threshold=threshold
                )
            else:
                self._outliers = {}
        return self._outliers

    def compute(self):
        """Perform all analyses and return results"""
        print("🚀 Performing all analyses...")

        results = {
            "data_info": self.get_data_info(),
            "numeric_analysis": self.get_numeric_analysis(),
            "categorical_analysis": self.get_categorical_analysis(),
            "correlation_matrix": self.get_correlation_matrix(),
            "outliers": self.get_outliers(),
        }

        print("✅ All analyses completed!")
        return results

    def get_summary(self):
        """Get a summary of all analyses"""
        print("📋 Performing all analyses for summary...")

        summary = {
            "data_info": self.get_data_info(),
            "numeric_analysis": self.get_numeric_analysis(),
            "categorical_analysis": self.get_categorical_analysis(),
            "correlation_matrix": self.get_correlation_matrix(),
            "outliers": self.get_outliers(),
        }

        return summary

    def show_plots(
        self, save_plots: bool = False, output_dir: str = "./quickinsights_output"
    ):
        """Display visualizations"""
        print("📈 Creating visualizations...")

        # Correlation matrix
        if len(self._numeric_cols) > 1:
            correlation_matrix(
                self.df[self._numeric_cols], save_plot=save_plots, output_dir=output_dir
            )

        # Distribution plots
        if len(self._numeric_cols) > 0:
            distribution_plots(
                self.df[self._numeric_cols],
                save_plots=save_plots,
                output_dir=output_dir,
            )

    def get_cache_status(self):
        """Show cache status"""
        status = {
            "data_info": self._data_info is not None,
            "numeric_analysis": self._numeric_analysis is not None,
            "categorical_analysis": self._categorical_analysis is not None,
            "correlation_matrix": self._correlation_matrix is not None,
            "outliers": self._outliers is not None,
        }

        print("📊 Cache Status:")
        for key, cached in status.items():
            status_icon = "✅" if cached else "⏳"
            cache_text = "Cached" if cached else "Not yet calculated"
            print(f"   {status_icon} {key}: {cache_text}")

        return status

    def clear_cache(self):
        """Clear cache"""
        self._results = {}
        self._data_info = None
        self._numeric_analysis = None
        self._categorical_analysis = None
        self._correlation_matrix = None
        self._outliers = None
        print("🗑️  Cache cleared!")
