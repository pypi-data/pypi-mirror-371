"""
QuickInsights - Easy Start Module for Beginners

This module provides a simplified interface for beginners.
It hides complex parameters and facilitates the most common usage scenarios.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union, List
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

def easy_load_data(file_path: Union[str, Path], 
                   encoding: str = 'utf-8',
                   auto_detect: bool = True) -> pd.DataFrame:
    """
    Automatically load data file
    
    Automatically detects file format and loads with the most appropriate parameters.
    Designed for beginner level users.
    
    Parameters
    ----------
    file_path : str or Path
        Path to the file to load
    encoding : str, default='utf-8'
        File encoding
    auto_detect : bool, default=True
        Whether to perform automatic format detection
        
    Returns
    -------
    pd.DataFrame
        Loaded dataset
        
    Examples
    --------
    >>> import quickinsights as qi
    >>> df = qi.easy_load_data('data.csv')
    >>> df = qi.easy_load_data('data.xlsx')
    >>> df = qi.easy_load_data('data.json')
    """
    
    file_path = Path(file_path)
    
    from .error_handling import ValidationUtils
    ValidationUtils.validate_file_path(file_path)
    
    print(f"📂 Loading: {file_path.name}")
    
    file_extension = file_path.suffix.lower()
    
    try:
        if file_extension == '.csv':
            # Try different separators and encodings
            separators = [',', ';', '\t', '|']
            encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
            
            for sep in separators:
                for enc in encodings:
                    try:
                        df = pd.read_csv(file_path, separator=sep, encoding=enc, low_memory=False)
                        if len(df.columns) > 1:  # Successfully parsed multiple columns
                            print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
                            print(f"📊 Separator: '{sep}', Encoding: {enc}")
                            return df
                    except:
                        continue
            
            # Fallback - basic load
            df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
            
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            print(f"✅ Excel loaded: {len(df)} rows, {len(df.columns)} columns")
            
        elif file_extension == '.json':
            df = pd.read_json(file_path)
            print(f"✅ JSON loaded: {len(df)} rows, {len(df.columns)} columns")
            
        elif file_extension == '.parquet':
            df = pd.read_parquet(file_path)
            print(f"✅ Parquet loaded: {len(df)} rows, {len(df.columns)} columns")
            
        else:
            print(f"⚠️ Unknown format '{file_extension}', trying as CSV...")
            df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
            
        # Basic validation
        if df.empty:
            print("⚠️ Warning: Dataset is empty!")
        elif len(df.columns) == 1:
            print("⚠️ Warning: Single column detected - separator problem possible")
            
        return df
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Hint: Check file format and encoding")
        raise

def easy_analyze(df: pd.DataFrame, 
                 target: Optional[str] = None,
                 quick: bool = True) -> Dict[str, Any]:
    """
    Easily analyze data set
    
    Simplified analysis interface for beginners.
    Hides complex parameters and provides clear results.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data set to analyze
    target : str, optional
        Target variable name (column to predict)
    quick : bool, default=True
        Quick analysis mode (for large datasets)
        
    Returns
    -------
    Dict[str, Any]
        Simplified analysis results
        
    Examples
    --------
    >>> result = qi.easy_analyze(df)
    >>> result = qi.easy_analyze(df, target='price')
    >>> print(result['summary'])
    """
    
    print("🔍 Starting data analysis...")
    
    # Import required functions
    from .quick_insights import quick_insight
    from .smart_cleaner import analyze_data_quality
    
    # Basic validation
    if df.empty:
        return {"error": "Dataset is empty!", "summary": "Analysis failed"}
    
    # Quick mode for large datasets
    sample_size = None
    if quick and len(df) > 50000:
        sample_size = 25000
        print(f"📊 Large dataset detected. Analyzing with {sample_size:,} samples.")
    
    try:
        # Run analysis
        quick_result = quick_insight(df, target_column=target, sample_size=sample_size, include_viz=False)
        quality_result = analyze_data_quality(df)
        
        # Simplify results for beginners
        simplified_result = {
            'data_summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage_mb': f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB",
                'missing_data_ratio': f"{(df.isnull().sum().sum() / df.size) * 100:.1f}%",
                'duplicate_row_count': df.duplicated().sum()
            },
            'column_types': quick_result['dataset_info']['column_types'],
            'data_quality': {
                'score': quality_result['missing_data']['missing_percentage'],
                'level': _get_simple_quality_level(quality_result['missing_data']['missing_percentage']),
                'main_issues': quality_result['recommendations'][:3]
            },
            'auto_insights': quick_result['auto_insights'][:5],
            'recommendations': quick_result['recommendations'][:5],
            'executive_summary': quick_result['executive_summary']
        }
        
        # Add target analysis if provided
        if target and 'target_analysis' in quick_result:
            simplified_result['target_variable_analysis'] = {
                'type': quick_result['target_analysis']['variable_type'],
                'missing_data': f"{quick_result['target_analysis']['missing_percentage']:.1f}%"
            }
            
            if quick_result['target_analysis']['variable_type'] == 'categorical':
                simplified_result['target_variable_analysis']['class_distribution'] = quick_result['target_analysis']['class_distribution']
                simplified_result['target_variable_analysis']['balance_assessment'] = quick_result['target_analysis']['balance_assessment']
        
        print("✅ Analysis complete!")
        print(f"📊 Data quality: {simplified_result['data_quality']['level']}")
        print(f"🔍 {len(simplified_result['auto_insights'])} auto insights detected")
        
        return simplified_result
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg, "summary": "Analysis failed"}

def _get_simple_quality_level(missing_pct: float) -> str:
    """Simplified quality level"""
    if missing_pct < 2:
        return "Excellent 🟢"
    elif missing_pct < 5:
        return "Good 🟡"
    elif missing_pct < 15:
        return "Moderate 🟠"
    else:
        return "Poor 🔴"

def easy_clean(df: pd.DataFrame, 
               target: Optional[str] = None,
               save_original: bool = True) -> Dict[str, Any]:
    """
    Easily clean data set
    
    Performs automatic data cleaning and reports results simply.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data set to clean
    target : str, optional
        Target variable (to be kept)
    save_original : bool, default=True
        Save original data
        
    Returns
    -------
    Dict[str, Any]
        Cleaning results and cleaned data
        
    Examples
    --------
    >>> result = qi.easy_clean(df)
    >>> clean_df = result['cleaned_data']
    >>> print(result['summary'])
    """
    
    print("🧹 Starting data cleaning...")
    
    from .smart_cleaner import smart_clean
    
    original_shape = df.shape
    original_memory = df.memory_usage(deep=True).sum() / 1024**2
    
    try:
        # Run smart cleaning
        cleaning_result = smart_clean(df, target_column=target, aggressive=False)
        
        cleaned_df = cleaning_result['cleaned_data']
        new_shape = cleaned_df.shape
        new_memory = cleaned_df.memory_usage(deep=True).sum() / 1024**2
        
        # Create simple summary
        simple_result = {
            'cleaned_data': cleaned_df,
            'previous_size': f"{original_shape[0]:,} rows × {original_shape[1]} columns",
            'new_size': f"{new_shape[0]:,} rows × {new_shape[1]} columns",
            'memory_savings': f"{original_memory - new_memory:.1f} MB",
            'performed_operations': [],
            'quality_improvement': cleaning_result['quality_improvement'],
            'recommendations': cleaning_result['recommendations'][:5],
            'summary': ""
        }
        
        # Summarize cleaning steps
        for step in cleaning_result['cleaning_steps']:
            step_name = step['step']
            if step_name == 'missing_data_handling' and step['actions_taken']:
                simple_result['performed_operations'].append(f"✅ Missing data filled ({len(step['actions_taken'])} columns)")
            elif step_name == 'duplicate_handling' and step['removed_count'] > 0:
                simple_result['performed_operations'].append(f"✅ {step['removed_count']} duplicate rows removed")
            elif step_name == 'outlier_handling' and step['actions_taken']:
                simple_result['performed_operations'].append(f"✅ Outliers handled ({len(step['actions_taken'])} columns)")
            elif step_name == 'data_type_optimization' and step['optimized_columns']:
                simple_result['performed_operations'].append(f"✅ Data types optimized ({len(step['optimized_columns'])} columns)")
        
        if not simple_result['performed_operations']:
            simple_result['performed_operations'].append("ℹ️ Data is already clean")
        
        # Create summary
        row_change = original_shape[0] - new_shape[0]
        if row_change > 0:
            simple_result['summary'] = f"Data cleaning complete! {row_change:,} rows and {original_memory - new_memory:.1f} MB memory saved."
        else:
            simple_result['summary'] = f"Data cleaning complete! {original_memory - new_memory:.1f} MB memory saved."
        
        print("✅ Cleaning complete!")
        print(f"📊 {simple_result['summary']}")
        
        return simple_result
        
    except Exception as e:
        error_msg = f"Error during cleaning: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg, "cleaned_data": df}

def easy_visualize(df: pd.DataFrame, 
                    target: Optional[str] = None,
                    max_plots: int = 5) -> Dict[str, Any]:
    """
    Easily visualize data set
    
    Automatically generates the most useful plots.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data set to visualize
    target : str, optional
        Target variable
    max_plots : int, default=5
        Maximum number of plots
        
    Returns
    -------
    Dict[str, Any]
        Visualization recommendations and commands
        
    Examples
    --------
    >>> viz_result = qi.easy_visualize(df, target='price')
    >>> print(viz_result['recommendations'])
    """
    
    print("📊 Preparing visualization recommendations...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    recommendations = {
        'plot_recommendations': [],
        'code_examples': [],
        'tips': []
    }
    
    # Basic distribution plots
    if len(numeric_cols) > 0:
        recommendations['plot_recommendations'].append("📈 Distribution plots for numerical variables")
        recommendations['code_examples'].append(f"df[{numeric_cols[:3]}].hist(figsize=(12, 8))")
    
    if len(categorical_cols) > 0:
        recommendations['plot_recommendations'].append("📊 Bar plots for categorical variables")
        for col in categorical_cols[:2]:
            recommendations['code_examples'].append(f"df['{col}'].value_counts().plot(kind='bar')")
    
    # Correlation analysis
    if len(numeric_cols) > 1:
        recommendations['plot_recommendations'].append("🔗 Correlation heatmap")
        recommendations['code_examples'].append("import seaborn as sns; sns.heatmap(df.corr(), annot=True)")
    
    # Target-specific plots
    if target and target in df.columns:
        if target in df.select_dtypes(include=[np.number]).columns:
            recommendations['plot_recommendations'].append(f"🎯 Distribution of {target} target variable")
            recommendations['code_examples'].append(f"df['{target}'].hist(bins=30)")
            
            if len(numeric_cols) > 0:
                recommendations['plot_recommendations'].append(f"📊 Scatter plots of {target} with other variables")
                for col in numeric_cols[:2]:
                    recommendations['code_examples'].append(f"df.plot.scatter(x='{col}', y='{target}')")
        else:
            recommendations['plot_recommendations'].append(f"🎯 Class distribution of {target}")
            recommendations['code_examples'].append(f"df['{target}'].value_counts().plot(kind='pie')")
    
    # Missing data visualization
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        recommendations['plot_recommendations'].append("❓ Missing data heatmap")
        recommendations['code_examples'].append("import seaborn as sns; sns.heatmap(df.isnull(), cbar=True)")
    
    # Tips
    recommendations['tips'] = [
        "💡 Use plt.show() with matplotlib.pyplot as plt",
        "💡 For better plots, install seaborn: pip install seaborn",
        "💡 For large datasets, use sample() to take a sample",
        "💡 Use plt.figure(figsize=(12, 8)) to set plot size"
    ]
    
    # Apply max_plots limit
    if max_plots > 0 and len(recommendations['plot_recommendations']) > max_plots:
        recommendations['plot_recommendations'] = recommendations['plot_recommendations'][:max_plots]
        recommendations['code_examples'] = recommendations['code_examples'][:max_plots]
    
    print(f"✅ {len(recommendations['plot_recommendations'])} visualization recommendations prepared!")
    
    return recommendations

def easy_export(df: pd.DataFrame, 
                filename: str = "cleaned_data",
                format: str = "csv") -> str:
    """
    Easily export data set
    
    Parameters
    ----------
    df : pd.DataFrame
        Data set to export
    filename : str, default="cleaned_data"
        File name (without extension)
    format : str, default="csv"
        File format (csv, excel, json)
        
    Returns
    -------
    str
        Path of the saved file
        
    Examples
    --------
    >>> qi.easy_export(df, "my_data", "csv")
    >>> qi.easy_export(df, "analysis_result", "excel")
    """
    
    print(f"💾 Data being saved in {format} format...")
    
    try:
        if format.lower() == "csv":
            filepath = f"{filename}.csv"
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif format.lower() in ["excel", "xlsx"]:
            filepath = f"{filename}.xlsx"
            df.to_excel(filepath, index=False)
        elif format.lower() == "json":
            filepath = f"{filename}.json"
            df.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"✅ Data saved: {filepath}")
        print(f"📊 {len(df)} rows, {len(df.columns)} columns")
        
        return filepath
        
    except Exception as e:
        error_msg = f"Saving error: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def easy_summary(df: pd.DataFrame) -> str:
    """
    Provides a simple summary of the data set
    
    Parameters
    ----------
    df : pd.DataFrame
        Data set to summarize
        
    Returns
    -------
    str
        Simple summary report
        
    Examples
    --------
    >>> print(qi.easy_summary(df))
    """
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    missing_total = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()
    memory_mb = df.memory_usage(deep=True).sum() / 1024**2
    
    summary = f"""
📊 DATASET SUMMARY
==================

📏 Size: {len(df):,} rows × {len(df.columns)} columns
💾 Memory: {memory_mb:.1f} MB

📈 Column Types:
   • Numerical: {len(numeric_cols)} columns
   • Categorical: {len(categorical_cols)} columns
   • Others: {len(df.columns) - len(numeric_cols) - len(categorical_cols)} columns

⚠️ Data Quality:
   • Missing values: {missing_total:,} cells ({(missing_total/df.size)*100:.1f}%)
   • Duplicate rows: {duplicates:,} ({(duplicates/len(df))*100:.1f}%)

🏷️ Column Names:
   {', '.join(df.columns[:10].tolist())}{' ...' if len(df.columns) > 10 else ''}
"""
    
    return summary.strip()

# Beginner-friendly aliases
load_data = easy_load_data
analyze = easy_analyze  
clean = easy_clean
visualize = easy_visualize
export = easy_export
summary = easy_summary
