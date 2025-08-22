"""
QuickInsights - Creative and Innovative Big Data Analysis Library

A Python library that goes beyond standard data analysis libraries like NumPy and Pandas,
providing creative insights, performance optimizations, and innovative features for both
large and small datasets.

Author: Eren Ata
Version: 0.2.1
"""

# Core modules are intentionally NOT imported at package import time to avoid
# pulling heavy optional dependencies (e.g., matplotlib) during lightweight usage.
_CORE_AVAILABLE = False

# Import management - only essential utilities
from ._imports import check_dependencies

# Core functionality - expose essential functions with lazy loading
def _get_core_functions():
    """Get core functions when needed."""
    from .core import analyze, analyze_numeric, analyze_categorical, validate_dataframe
    from .utils import get_data_info, detect_outliers, create_output_directory
    return analyze, analyze_numeric, analyze_categorical, validate_dataframe, get_data_info, detect_outliers, create_output_directory

# Quick Insights - instant data understanding
def _get_quick_insights():
    """Get quick insights functions when needed."""
    from .quick_insights import quick_insight, optimize_for_speed
    return quick_insight, optimize_for_speed

# Smart Data Cleaning - automated data cleaning
def _get_smart_cleaner():
    """Get smart cleaner functions when needed."""
    from .smart_cleaner import smart_clean, analyze_data_quality, SmartCleaner
    return smart_clean, analyze_data_quality, SmartCleaner

# Easy Start - beginner-friendly interface
def _get_easy_start():
    """Get easy start functions when needed."""
    from .easy_start import (
        easy_load_data, easy_analyze, easy_clean, easy_visualize, easy_export, easy_summary,
        load_data, analyze, clean, visualize, export, summary  # aliases
    )
    return easy_load_data, easy_analyze, easy_clean, easy_visualize, easy_export, easy_summary, load_data, clean, visualize, export, summary

# Dashboard - interactive reporting
def _get_dashboard():
    """Get dashboard functions when needed."""
    from .dashboard import create_dashboard, DashboardGenerator
    return create_dashboard, DashboardGenerator

# Utility functions that are always available
def get_utility_status():
    """Get status of all utility functions."""
    from .utils import get_utility_status as _get_status
    return _get_status()

def print_utility_status():
    """Print status of all utility functions."""
    from .utils import print_utility_status as _print_status
    return _print_status()

def get_available_features():
    """Get list of available features."""
    from .utils import get_available_features as _get_features
    return _get_features()

def check_dependencies():
    """Check availability of all optional dependencies."""
    from ._imports import check_dependencies as _check_deps
    return _check_deps()

def get_system_info():
    """Get system information."""
    from .utils import get_system_info as _get_sys_info
    return _get_sys_info()

def create_utility_report():
    """Create utility report."""
    from .utils import create_utility_report as _create_report
    return _create_report()

# Lazy loading decorator
def lazy_import(func_name):
    """Decorator for lazy loading of functions."""
    def wrapper(*args, **kwargs):
        # Import the function when first called
        if func_name == 'analyze':
            analyze, _, _, _, _, _, _ = _get_core_functions()
            return analyze(*args, **kwargs)
        elif func_name == 'quick_insight':
            quick_insight, _ = _get_quick_insights()
            return quick_insight(*args, **kwargs)
        elif func_name == 'smart_clean':
            smart_clean, _, _ = _get_smart_cleaner()
            return smart_clean(*args, **kwargs)
        elif func_name == 'easy_load_data':
            easy_load_data, _, _, _, _, _, _, _, _, _, _, _ = _get_easy_start()
            return easy_load_data(*args, **kwargs)
        elif func_name == 'create_dashboard':
            create_dashboard, _ = _get_dashboard()
            return create_dashboard(*args, **kwargs)
        else:
            raise AttributeError(f"Function {func_name} not found")
    return wrapper

# Public API with lazy loading
__all__ = [
    # Core functions - most important for users
    "analyze",
    "analyze_numeric", 
    "analyze_categorical",
    "validate_dataframe",
    "get_data_info",
    "detect_outliers",
    "create_output_directory",
    # Quick Insights
    "quick_insight",
    "optimize_for_speed",
    # Smart Cleaning
    "smart_clean",
    "analyze_data_quality",
    "SmartCleaner",
    # Easy Start - Beginner Friendly
    "easy_load_data", "easy_analyze", "easy_clean", "easy_visualize", "easy_export", "easy_summary",
    "load_data", "clean", "visualize", "export", "summary",  # convenient aliases
    # Dashboard
    "create_dashboard", "DashboardGenerator",
    # Utility functions
    "get_utility_status",
    "print_utility_status",
    "get_available_features",
    "check_dependencies",
    "get_system_info",
    "create_utility_report",
]

# Version information
__version__ = "0.2.2"
__author__ = "Eren Ata"
__description__ = "Creative and Innovative Big Data Analysis Library"

# Avoid side effects and printing at import time
