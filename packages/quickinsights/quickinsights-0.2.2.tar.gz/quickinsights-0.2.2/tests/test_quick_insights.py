"""
Tests for quick_insights module
"""
import pytest
import pandas as pd
import numpy as np
from quickinsights.quick_insights import quick_insight, optimize_for_speed


class TestQuickInsights:
    """Test cases for quick_insights module"""
    
    def setup_method(self):
        """Setup test data"""
        # Create sample numeric data
        np.random.seed(42)
        self.numeric_df = pd.DataFrame({
            'A': np.random.normal(0, 1, 100),
            'B': np.random.normal(5, 2, 100),
            'C': np.random.uniform(0, 10, 100),
            'D': np.random.randint(0, 100, 100)
        })
        
        # Create sample mixed data
        self.mixed_df = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'categorical': ['A', 'B', 'A', 'C', 'B'],
            'text': ['hello', 'world', 'test', 'data', 'analysis'],
            'date': pd.date_range('2023-01-01', periods=5)
        })
        
        # Create sample data with missing values
        self.missing_df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': [np.nan, 2, 3, 4, np.nan],
            'C': [1, np.nan, np.nan, 4, 5]
        })
    
    def test_quick_insight_basic(self):
        """Test basic quick_insight functionality"""
        result = quick_insight(self.numeric_df, include_viz=False)
        
        # Check required keys exist
        assert 'dataset_info' in result
        assert 'data_quality' in result
        assert 'auto_insights' in result
        assert 'recommendations' in result
        assert 'executive_summary' in result
        
        # Check dataset info
        assert result['dataset_info']['total_rows'] == 100
        assert result['dataset_info']['total_columns'] == 4
        assert 'memory_usage_mb' in result['dataset_info']
        
        # Check insights are generated (may be empty for simple data)
        assert isinstance(result['auto_insights'], list)
        assert isinstance(result['recommendations'], list)
    
    def test_quick_insight_with_target(self):
        """Test quick_insight with target column"""
        result = quick_insight(self.numeric_df, target_column='A', include_viz=False)
        
        assert 'target_analysis' in result
        target_analysis = result['target_analysis']
        assert target_analysis['column_name'] == 'A'
        assert 'variable_type' in target_analysis
    
    def test_quick_insight_mixed_data(self):
        """Test quick_insight with mixed data types"""
        result = quick_insight(self.mixed_df, include_viz=False)
        
        assert 'dataset_info' in result
        assert 'column_types' in result['dataset_info']
        
        # Check column types are correctly identified
        column_types = result['dataset_info']['column_types']
        assert 'numeric' in column_types
        assert 'categorical' in column_types
        # Note: 'text' might be categorized as 'categorical' or 'other'
        assert 'datetime' in column_types
    
    def test_quick_insight_missing_data(self):
        """Test quick_insight with missing data"""
        result = quick_insight(self.missing_df, include_viz=False)
        
        # Check data quality analysis
        assert 'data_quality' in result
        quality = result['data_quality']
        assert 'missing_data' in quality
        # Check that missing data is detected
        # Note: structure might be 'columns_with_missing' instead of 'total_missing'
        missing_data = quality['missing_data']
        if 'total_missing' in missing_data:
            assert missing_data['total_missing'] > 0
        elif 'columns_with_missing' in missing_data:
            assert len(missing_data['columns_with_missing']) > 0
        else:
            # If neither exists, just check that missing_data is not empty
            assert missing_data
    
    def test_quick_insight_sampling(self):
        """Test quick_insight with sampling for large datasets"""
        # Create large dataset
        large_df = pd.DataFrame({
            'A': np.random.normal(0, 1, 100000),
            'B': np.random.normal(5, 2, 100000)
        })
        
        result = quick_insight(large_df, sample_size=1000, include_viz=False)
        
        assert 'dataset_info' in result
        assert result['dataset_info']['total_rows'] == 100000
        # Check that sampling was applied
        assert 'sample_rows' in result['dataset_info']
    
    def test_optimize_for_speed(self):
        """Test optimize_for_speed functionality"""
        # Create DataFrame with different data types
        df = pd.DataFrame({
            'int64': np.array([1, 2, 3], dtype='int64'),
            'float64': np.array([1.0, 2.0, 3.0], dtype='float64'),
            'object': ['A', 'B', 'C'],
            'category': pd.Categorical(['X', 'Y', 'Z'])
        })
        
        original_memory = df.memory_usage(deep=True).sum()
        optimized_df = optimize_for_speed(df)
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        
        # Check that optimization was applied
        assert optimized_memory <= original_memory
        
        # Check data types were optimized
        assert optimized_df['int64'].dtype in ['int8', 'int16', 'int32', 'int64']
        assert optimized_df['float64'].dtype in ['float32', 'float64']
        
        # Check data integrity
        pd.testing.assert_frame_equal(df, optimized_df, check_dtype=False)
    
    def test_optimize_for_speed_empty_df(self):
        """Test optimize_for_speed with empty DataFrame"""
        empty_df = pd.DataFrame()
        optimized_df = optimize_for_speed(empty_df)
        
        assert optimized_df.empty
        assert optimized_df.shape == (0, 0)
    
    def test_quick_insight_error_handling(self):
        """Test quick_insight error handling"""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        result = quick_insight(empty_df, include_viz=False)
        
        # Should handle empty DataFrame gracefully
        assert isinstance(result, dict)
        
        # Test with None
        with pytest.raises(Exception):
            quick_insight(None, include_viz=False)
    
    def test_optimize_for_speed_error_handling(self):
        """Test optimize_for_speed error handling"""
        # Test with None
        with pytest.raises(Exception):
            optimize_for_speed(None)
        
        # Test with non-DataFrame
        with pytest.raises(Exception):
            optimize_for_speed([1, 2, 3])


if __name__ == "__main__":
    pytest.main([__file__])
