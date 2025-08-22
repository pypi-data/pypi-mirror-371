"""
Tests for AI insights module
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Check if sklearn is available
try:
    import sklearn
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    np.random.seed(42)
    
    # Numeric data
    numeric_data = pd.DataFrame({
        'A': np.random.normal(0, 1, 100),
        'B': np.random.normal(5, 2, 100),
        'C': np.random.uniform(0, 10, 100),
        'D': np.random.exponential(2, 100)
    })
    
    # Mixed data
    mixed_data = pd.DataFrame({
        'numeric': np.random.normal(0, 1, 100),
        'categorical': np.random.choice(['A', 'B', 'C'], 100),
        'datetime': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    return {
        'numeric': numeric_data,
        'mixed': mixed_data
    }


class TestAIInsightEngine:
    """Test AIInsightEngine class"""
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_initialization(self, sample_data):
        """Test AIInsightEngine initialization"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        engine = AIInsightEngine(df)
        
        assert engine.df is not None
        assert len(engine.numeric_cols) > 0
        assert len(engine.categorical_cols) == 0
        assert hasattr(engine, 'insights')
        assert hasattr(engine, 'patterns')
        assert hasattr(engine, 'anomalies')
        assert hasattr(engine, 'trends')
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_initialization_mixed_data(self, sample_data):
        """Test AIInsightEngine with mixed data types"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['mixed']
        engine = AIInsightEngine(df)
        
        assert engine.df is not None
        assert len(engine.numeric_cols) > 0
        assert len(engine.categorical_cols) > 0
        assert hasattr(engine, 'df_scaled')
        assert hasattr(engine, 'df_encoded')
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_discover_patterns(self, sample_data):
        """Test pattern discovery"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        
        # Mock sklearn availability
        with patch('quickinsights.ai_insights.SKLEARN_AVAILABLE', True):
            engine = AIInsightEngine(df)
            patterns = engine.discover_patterns(max_patterns=5)
            
            assert isinstance(patterns, dict)
            # Check if patterns contain expected keys
            assert len(patterns) > 0
            # The actual keys depend on the data and available features
            assert any(key in patterns for key in ['correlations', 'feature_importance', 'categorical'])
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_detect_anomalies(self, sample_data):
        """Test anomaly detection"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        
        # Mock sklearn availability
        with patch('quickinsights.ai_insights.SKLEARN_AVAILABLE', True):
            engine = AIInsightEngine(df)
            anomalies = engine.detect_anomalies()
            
            assert isinstance(anomalies, dict)
            assert len(anomalies) > 0
            
            # Check if anomalies contain expected keys
            assert 'best_method' in anomalies
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_predict_trends(self, sample_data):
        """Test trend prediction"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        
        # Mock sklearn availability
        with patch('quickinsights.ai_insights.SKLEARN_AVAILABLE', True):
            engine = AIInsightEngine(df)
            trends = engine.predict_trends()
            
            assert isinstance(trends, dict)
            # Check if trends contain expected keys
            assert len(trends) > 0
            assert 'best_model' in trends
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_generate_insights_report(self, sample_data):
        """Test insights report generation"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        engine = AIInsightEngine(df)
        
        # First discover patterns and anomalies
        engine.discover_patterns()
        engine.detect_anomalies()
        
        report = engine.generate_insights_report()
        
        assert isinstance(report, dict)
        assert 'summary' in report
        assert 'patterns' in report
        assert 'anomalies' in report
        assert 'trends' in report
        assert 'recommendations' in report
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes"""
        from quickinsights.ai_insights import AIInsightEngine
        
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            AIInsightEngine(empty_df)
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_single_column_data(self, sample_data):
        """Test with single column data"""
        from quickinsights.ai_insights import AIInsightEngine
        
        single_col_df = sample_data['numeric'][['A']]
        engine = AIInsightEngine(single_col_df)
        
        # Should handle single column gracefully
        patterns = engine.discover_patterns()
        assert isinstance(patterns, dict)
        
        anomalies = engine.detect_anomalies()
        assert isinstance(anomalies, dict)


class TestAutoAIAnalysis:
    """Test auto_ai_analysis function"""
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_auto_ai_analysis_basic(self, sample_data):
        """Test basic auto AI analysis"""
        from quickinsights.ai_insights import auto_ai_analysis
        
        df = sample_data['numeric']
        result = auto_ai_analysis(df)
        
        assert isinstance(result, dict)
        assert 'patterns' in result
        assert 'anomalies' in result
        assert 'trends' in result
        assert 'report' in result
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_auto_ai_analysis_mixed_data(self, sample_data):
        """Test auto AI analysis with mixed data"""
        from quickinsights.ai_insights import auto_ai_analysis
        
        df = sample_data['mixed']
        result = auto_ai_analysis(df)
        
        assert isinstance(result, dict)
        assert 'patterns' in result
        assert 'anomalies' in result
        assert 'trends' in result
        assert 'report' in result
    
    @pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
    def test_auto_ai_analysis_error_handling(self):
        """Test error handling in auto AI analysis"""
        from quickinsights.ai_insights import auto_ai_analysis
        
        # Test with invalid data
        invalid_df = pd.DataFrame({'A': ['not', 'numeric', 'data']})
        
        # Should handle gracefully without crashing
        result = auto_ai_analysis(invalid_df)
        assert isinstance(result, dict)


@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn not available")
class TestAIInsightsIntegration:
    """Test AI insights integration with other modules"""
    
    def test_with_quick_insights(self, sample_data):
        """Test AI insights integration with quick_insights"""
        from quickinsights.ai_insights import AIInsightEngine
        from quickinsights.quick_insights import quick_insight
        
        df = sample_data['numeric']
        
        # Run quick insight first
        quick_result = quick_insight(df, include_viz=False)
        
        # Then run AI insights
        engine = AIInsightEngine(df)
        ai_result = engine.generate_insights_report()
        
        # Both should work together
        assert isinstance(quick_result, dict)
        assert isinstance(ai_result, dict)
        assert 'auto_insights' in quick_result
        assert 'patterns' in ai_result
    
    def test_with_smart_cleaner(self, sample_data):
        """Test AI insights integration with smart_cleaner"""
        from quickinsights.ai_insights import AIInsightEngine
        from quickinsights.smart_cleaner import smart_clean
        
        df = sample_data['mixed']
        
        # Clean data first
        clean_result = smart_clean(df)
        cleaned_df = clean_result['cleaned_data']
        
        # Then run AI insights on cleaned data
        engine = AIInsightEngine(cleaned_df)
        ai_result = engine.generate_insights_report()
        
        # Both should work together
        assert isinstance(clean_result, dict)
        assert isinstance(ai_result, dict)
        assert 'cleaned_data' in clean_result
        assert 'patterns' in ai_result


# Mock tests for when dependencies are not available
class TestAIInsightsWithoutDependencies:
    """Test AI insights behavior when dependencies are missing"""
    
    @patch('quickinsights.ai_insights.SKLEARN_AVAILABLE', False)
    def test_initialization_without_sklearn(self, sample_data):
        """Test initialization when sklearn is not available"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        
        # Mock test - sklearn olmadan da çalışmalı
        engine = AIInsightEngine(df)
        assert engine.df is not None
        assert not hasattr(engine, 'scaler')  # sklearn olmadan scaler olmamalı
    
    @patch('quickinsights.ai_insights.SCIPY_AVAILABLE', False)
    def test_initialization_without_scipy(self, sample_data):
        """Test initialization when scipy is not available"""
        from quickinsights.ai_insights import AIInsightEngine
        
        df = sample_data['numeric']
        
        # Mock test - scipy olmadan da çalışmalı
        engine = AIInsightEngine(df)
        assert engine.df is not None
        # scipy olmadan da temel özellikler çalışmalı
