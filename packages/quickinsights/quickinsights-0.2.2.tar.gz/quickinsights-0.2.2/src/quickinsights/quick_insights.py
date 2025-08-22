"""
QuickInsights - Instant Data Understanding Module

Bu modül veri analistlerinin en sık karşılaştığı "hızlı genel bakış" ihtiyacını karşılar.
Tek komutla veri setinin temel özelliklerini, potansiyel sorunlarını ve fırsatlarını gösterir.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

def quick_insight(df: pd.DataFrame, 
                 target_column: Optional[str] = None,
                 sample_size: Optional[int] = None,
                 include_viz: bool = True) -> Dict[str, Any]:
    """
    Veri setine 30 saniyede kapsamlı bir bakış sağlar.
    
    Veri analistlerinin ilk 5 dakikada öğrenmek istediklerini otomatik olarak keşfeder:
    - Veri kalitesi ve güvenilirlik skoru
    - En ilginç pattern'ler ve anomaliler  
    - Otomatik insight'lar ve öneriler
    - Hedef değişken varsa predictive power analizi
    
    Parameters
    ----------
    df : pd.DataFrame
        Analiz edilecek veri seti
    target_column : str, optional
        Hedef değişken (prediction/classification için)
    sample_size : int, optional
        Büyük veri setleri için örnekleme boyutu
    include_viz : bool, default=True
        Otomatik görselleştirme oluşturulsun mu
        
    Returns
    -------
    Dict[str, Any]
        Kapsamlı insight raporu
        
    Examples
    --------
    >>> import quickinsights as qi
    >>> insight = qi.quick_insight(df, target_column='target')
    >>> print(insight['executive_summary'])
    >>> insight['auto_insights']
    """
    
    if sample_size and len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"🔸 Large dataset detected. Using sample of {sample_size:,} rows for quick analysis.")
    else:
        df_sample = df.copy()
    
    # Ana analiz başlat
    result = {
        'timestamp': datetime.now().isoformat(),
        'dataset_info': _get_dataset_overview(df, df_sample),
        'data_quality': _assess_data_quality(df_sample),
        'auto_insights': _generate_auto_insights(df_sample, target_column),
        'recommendations': _generate_recommendations(df_sample, target_column),
        'executive_summary': None  # Son kısımda doldurulacak
    }
    
    # Hedef değişken analizi
    if target_column and target_column in df_sample.columns:
        result['target_analysis'] = _analyze_target_variable(df_sample, target_column)
        result['predictive_power'] = _assess_predictive_power(df_sample, target_column)
    
    # Görselleştirme
    if include_viz:
        result['visualizations'] = _create_quick_visualizations(df_sample, target_column)
    
    # Executive summary oluştur
    result['executive_summary'] = _create_executive_summary(result)
    
    return result

def _get_dataset_overview(df_full: pd.DataFrame, df_sample: pd.DataFrame) -> Dict[str, Any]:
    """Veri setinin genel görünümünü çıkarır"""
    
    numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df_sample.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df_sample.select_dtypes(include=['datetime64']).columns.tolist()
    
    return {
        'total_rows': len(df_full),
        'total_columns': len(df_full.columns),
        'sample_rows': len(df_sample),
        'memory_usage_mb': df_full.memory_usage(deep=True).sum() / 1024**2,
        'column_types': {
            'numeric': len(numeric_cols),
            'categorical': len(categorical_cols), 
            'datetime': len(datetime_cols),
            'other': len(df_sample.columns) - len(numeric_cols) - len(categorical_cols) - len(datetime_cols)
        },
        'column_details': {
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'datetime_columns': datetime_cols
        }
    }

def _assess_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Veri kalitesini skorlar ve sorunları tespit eder"""
    
    # Missing values analysis
    missing_analysis = df.isnull().sum()
    missing_pct = (missing_analysis / len(df) * 100).round(2)
    
    # Duplicate analysis
    duplicates = df.duplicated().sum()
    duplicate_pct = (duplicates / max(1, len(df)) * 100).round(2)
    
    # Data type consistency
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inconsistent_types = []
    
    for col in df.columns:
        if col not in numeric_cols:
            # Check if categorical column has too many unique values
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.95:  # Probably should be an ID column
                inconsistent_types.append(f"{col}: too many unique values ({unique_ratio:.2%})")
    
    # Calculate overall quality score (0-100)
    quality_score = 100
    
    # Deduct points for missing data
    quality_score -= min(missing_pct.mean() * 2, 40)  # Max 40 points deduction
    
    # Deduct points for duplicates
    quality_score -= min(duplicate_pct * 1.5, 20)  # Max 20 points deduction
    
    # Deduct points for inconsistent types
    quality_score -= min(len(inconsistent_types) * 5, 15)  # Max 15 points deduction
    
    quality_score = max(quality_score, 0)
    
    return {
        'overall_score': round(quality_score, 1),
        'quality_level': _get_quality_level(quality_score),
        'missing_data': {
            'columns_with_missing': missing_analysis[missing_analysis > 0].to_dict(),
            'worst_columns': missing_pct.nlargest(5).to_dict()
        },
        'duplicates': {
            'count': duplicates,
            'percentage': duplicate_pct
        },
        'type_issues': inconsistent_types,
        'recommendations': _get_quality_recommendations(quality_score, missing_pct, duplicate_pct)
    }

def _get_quality_level(score: float) -> str:
    """Kalite skoruna göre seviye belirler"""
    if score >= 90:
        return "Excellent ⭐⭐⭐⭐⭐"
    elif score >= 80:
        return "Good ⭐⭐⭐⭐"
    elif score >= 70:
        return "Fair ⭐⭐⭐"
    elif score >= 60:
        return "Poor ⭐⭐"
    else:
        return "Critical ⭐"

def _get_quality_recommendations(score: float, missing_pct: pd.Series, duplicate_pct: float) -> List[str]:
    """Kalite skoruna göre öneriler üretir"""
    recommendations = []
    
    if score < 80:
        recommendations.append("⚠️ Data quality needs improvement before analysis")
    
    if missing_pct.max() > 50:
        worst_col = missing_pct.idxmax()
        recommendations.append(f"🔴 Column '{worst_col}' has {missing_pct.max():.1f}% missing - consider dropping")
    elif missing_pct.max() > 20:
        recommendations.append("🟡 High missing values detected - investigate imputation strategies")
    
    if duplicate_pct > 10:
        recommendations.append(f"🔴 {duplicate_pct:.1f}% duplicate rows found - clean before analysis")
    elif duplicate_pct > 0:
        recommendations.append("🟡 Some duplicate rows detected - verify if intentional")
        
    return recommendations

def _generate_auto_insights(df: pd.DataFrame, target_column: Optional[str] = None) -> List[str]:
    """Otomatik insight'lar üretir"""
    insights = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Numeric insights
    if len(numeric_cols) > 0:
        numeric_df = df[numeric_cols]
        
        # High correlation detection
        if len(numeric_cols) > 1:
            corr_matrix = numeric_df.corr()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = abs(corr_matrix.iloc[i, j])
                    if corr_val > 0.8:
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        high_corr.append((col1, col2, corr_val))
            
            if high_corr:
                for col1, col2, corr_val in high_corr[:3]:  # Top 3
                    insights.append(f"🔗 Strong correlation detected: {col1} ↔ {col2} (r={corr_val:.2f})")
        
        # Outlier detection
        outlier_cols = []
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)][col]
            if len(outliers) / len(df) > 0.05:  # More than 5% outliers
                outlier_cols.append((col, len(outliers)/len(df)))
        
        if outlier_cols:
            for col, pct in outlier_cols[:2]:  # Top 2
                insights.append(f"📊 High outlier rate in '{col}': {pct:.1%} of values")
    
    # Categorical insights
    if len(categorical_cols) > 0:
        for col in categorical_cols[:3]:  # Analyze top 3 categorical columns
            unique_count = df[col].nunique()
            total_count = len(df)
            
            if unique_count == total_count:
                insights.append(f"🔑 '{col}' appears to be a unique identifier")
            elif unique_count / total_count > 0.9:
                insights.append(f"📝 '{col}' has very high cardinality ({unique_count} unique values)")
            elif unique_count <= 10:
                # Show value distribution for low cardinality
                top_value = df[col].value_counts().index[0]
                top_pct = df[col].value_counts().iloc[0] / len(df)
                insights.append(f"📈 '{col}': '{top_value}' dominates with {top_pct:.1%} of values")
    
    # Dataset size insights
    if len(df) < 100:
        insights.append("⚠️ Small dataset detected - statistical insights may be limited")
    elif len(df) > 1_000_000:
        insights.append("🚀 Large dataset detected - consider sampling for faster analysis")
    
    return insights

def _generate_recommendations(df: pd.DataFrame, target_column: Optional[str] = None) -> List[str]:
    """Analiz için öneriler üretir"""
    recommendations = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Target variable recommendations
    if target_column and target_column in df.columns:
        if target_column in numeric_cols:
            recommendations.append("📊 Regression analysis recommended for numeric target")
            recommendations.append("🔍 Consider feature engineering: polynomial features, interactions")
        elif target_column in categorical_cols:
            unique_targets = df[target_column].nunique()
            if unique_targets == 2:
                recommendations.append("🎯 Binary classification problem detected")
            else:
                recommendations.append(f"🎯 Multi-class classification with {unique_targets} classes")
    
    # Feature engineering recommendations
    if len(numeric_cols) > 1:
        recommendations.append("🔧 Consider creating interaction features between numeric variables")
    
    if len(categorical_cols) > 0:
        high_card_cols = [col for col in categorical_cols if df[col].nunique() > 50]
        if high_card_cols:
            recommendations.append(f"🏷️ High cardinality categorical features detected: {high_card_cols[:2]} - consider encoding strategies")
    
    # Analysis workflow recommendations
    recommendations.append("📈 Next steps: Detailed EDA → Feature Engineering → Model Selection")
    recommendations.append("💡 Use qi.analyze() for comprehensive statistical analysis")
    
    return recommendations

def _analyze_target_variable(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """Hedef değişkeni detaylı analiz eder"""
    target_series = df[target_column]
    
    analysis = {
        'column_name': target_column,
        'data_type': str(target_series.dtype),
        'missing_count': target_series.isnull().sum(),
        'missing_percentage': (target_series.isnull().sum() / len(target_series) * 100).round(2)
    }
    
    if pd.api.types.is_numeric_dtype(target_series):
        # Numeric target analysis
        analysis['variable_type'] = 'continuous'
        analysis['statistics'] = {
            'mean': target_series.mean(),
            'median': target_series.median(),
            'std': target_series.std(),
            'min': target_series.min(),
            'max': target_series.max(),
            'skewness': target_series.skew(),
            'kurtosis': target_series.kurtosis()
        }
        
        # Distribution insights
        if abs(analysis['statistics']['skewness']) > 1:
            analysis['distribution_note'] = f"Highly skewed distribution (skew={analysis['statistics']['skewness']:.2f})"
        elif abs(analysis['statistics']['skewness']) > 0.5:
            analysis['distribution_note'] = f"Moderately skewed distribution (skew={analysis['statistics']['skewness']:.2f})"
        else:
            analysis['distribution_note'] = "Approximately normal distribution"
            
    else:
        # Categorical target analysis  
        analysis['variable_type'] = 'categorical'
        value_counts = target_series.value_counts()
        analysis['class_distribution'] = value_counts.to_dict()
        analysis['class_balance'] = {
            'most_frequent': value_counts.index[0],
            'most_frequent_pct': (value_counts.iloc[0] / len(target_series) * 100).round(2),
            'least_frequent': value_counts.index[-1],
            'least_frequent_pct': (value_counts.iloc[-1] / len(target_series) * 100).round(2)
        }
        
        # Balance assessment
        max_pct = value_counts.iloc[0] / len(target_series)
        if max_pct > 0.9:
            analysis['balance_assessment'] = "Severely imbalanced - consider resampling techniques"
        elif max_pct > 0.7:
            analysis['balance_assessment'] = "Moderately imbalanced - monitor model performance"
        else:
            analysis['balance_assessment'] = "Reasonably balanced"
    
    return analysis

def _assess_predictive_power(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """Features'ların predictive power'ını değerlendirir"""
    
    numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                   if col != target_column]
    categorical_cols = [col for col in df.select_dtypes(include=['object', 'category']).columns 
                       if col != target_column]
    
    predictive_analysis = {
        'feature_count': len(numeric_cols) + len(categorical_cols),
        'numeric_features': len(numeric_cols),
        'categorical_features': len(categorical_cols),
        'top_correlations': [],
        'feature_importance_estimate': {}
    }
    
    target_series = df[target_column]
    
    # Numeric features correlation analysis
    if len(numeric_cols) > 0 and pd.api.types.is_numeric_dtype(target_series):
        correlations = []
        for col in numeric_cols:
            corr = df[col].corr(target_series)
            if not pd.isna(corr):
                correlations.append((col, abs(corr), corr))
        
        correlations.sort(key=lambda x: x[1], reverse=True)
        predictive_analysis['top_correlations'] = correlations[:5]
    
    # Simple feature importance estimation
    if len(numeric_cols) > 0:
        try:
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            
            # Prepare features
            X = df[numeric_cols].fillna(df[numeric_cols].median())
            y = target_series
            
            # Handle categorical target
            if not pd.api.types.is_numeric_dtype(y):
                le = LabelEncoder()
                y = le.fit_transform(y.astype(str))
                model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
            else:
                model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
            
            model.fit(X, y)
            feature_importance = dict(zip(numeric_cols, model.feature_importances_))
            predictive_analysis['feature_importance_estimate'] = feature_importance
            
        except ImportError:
            predictive_analysis['feature_importance_estimate'] = "Scikit-learn not available"
        except Exception as e:
            predictive_analysis['feature_importance_estimate'] = f"Error: {str(e)}"
    
    return predictive_analysis

def _create_quick_visualizations(df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, str]:
    """Hızlı görselleştirmeler oluşturur"""
    
    # Bu fonksiyon şimdilik placeholder - matplotlib/seaborn entegrasyonu için
    viz_recommendations = {
        'recommended_plots': [],
        'plot_commands': []
    }
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if target_column:
        if target_column in numeric_cols:
            viz_recommendations['recommended_plots'].extend([
                'Target distribution histogram',
                'Feature vs Target scatter plots',
                'Correlation heatmap'
            ])
        else:
            viz_recommendations['recommended_plots'].extend([
                'Target distribution bar chart',
                'Feature distributions by target',
                'Feature importance plot'
            ])
    else:
        viz_recommendations['recommended_plots'].extend([
            'Correlation matrix heatmap',
            'Distribution plots for numeric features',
            'Missing data heatmap'
        ])
    
    return viz_recommendations

def _create_executive_summary(analysis_result: Dict[str, Any]) -> str:
    """Executive summary oluşturur"""
    
    dataset_info = analysis_result['dataset_info']
    quality = analysis_result['data_quality']
    insights = analysis_result['auto_insights']
    
    summary = f"""
🎯 EXECUTIVE SUMMARY
==================

📊 Dataset: {dataset_info['total_rows']:,} rows × {dataset_info['total_columns']} columns
💾 Size: {dataset_info['memory_usage_mb']:.1f} MB
🏆 Quality Score: {quality['overall_score']}/100 ({quality['quality_level']})

🔍 KEY FINDINGS:
{chr(10).join(['• ' + insight for insight in insights[:5]])}

⚠️ ACTION ITEMS:
{chr(10).join(['• ' + rec for rec in quality['recommendations'][:3]])}

📈 NEXT STEPS:
{chr(10).join(['• ' + rec for rec in analysis_result['recommendations'][:3]])}
"""
    
    return summary.strip()

# Convenience function for memory optimization
def optimize_for_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Veri setini hız için optimize eder
    
    Parameters
    ----------
    df : pd.DataFrame
        Optimize edilecek veri seti
        
    Returns
    -------
    pd.DataFrame
        Optimize edilmiş veri seti
    """
    df_optimized = df.copy()
    
    # Numeric type optimization
    for col in df_optimized.select_dtypes(include=['int64']).columns:
        col_min = df_optimized[col].min()
        col_max = df_optimized[col].max()
        
        if col_min >= -128 and col_max <= 127:
            df_optimized[col] = df_optimized[col].astype('int8')
        elif col_min >= -32768 and col_max <= 32767:
            df_optimized[col] = df_optimized[col].astype('int16')
        elif col_min >= -2147483648 and col_max <= 2147483647:
            df_optimized[col] = df_optimized[col].astype('int32')
    
    for col in df_optimized.select_dtypes(include=['float64']).columns:
        df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
    
    # Category optimization
    for col in df_optimized.select_dtypes(include=['object']).columns:
        if df_optimized[col].nunique() / len(df_optimized) < 0.5:  # Less than 50% unique
            df_optimized[col] = df_optimized[col].astype('category')
    
    return df_optimized
