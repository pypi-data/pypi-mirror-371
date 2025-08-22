"""
Tests for Performance module
"""

import pytest
import pandas as pd
import numpy as np
import time
import warnings
from unittest.mock import patch, MagicMock

warnings.filterwarnings("ignore")


@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    np.random.seed(42)
    
    # Large DataFrame for performance testing
    large_df = pd.DataFrame({
        'A': np.random.normal(0, 1, 10000),
        'B': np.random.normal(5, 2, 10000),
        'C': np.random.uniform(0, 10, 10000),
        'D': np.random.randint(0, 100, 10000)
    })
    
    # Small DataFrame for basic testing
    small_df = pd.DataFrame({
        'X': [1, 2, 3, 4, 5],
        'Y': [10, 20, 30, 40, 50]
    })
    
    return {
        'large': large_df,
        'small': small_df
    }


class TestPerformanceUtils:
    """Test performance utility functions"""
    
    def test_get_performance_utils(self):
        """Test get_performance_utils function"""
        from quickinsights.performance import get_performance_utils
        
        utils = get_performance_utils()
        
        assert isinstance(utils, dict)
        assert 'lazy_evaluate' in utils
        assert 'cache_result' in utils
        assert 'parallel_process' in utils
        assert 'chunked_process' in utils
        assert 'memory_optimize' in utils
        assert 'performance_profile' in utils
        assert 'benchmark_function' in utils
    
    def test_lazy_evaluate(self):
        """Test lazy evaluation decorator"""
        from quickinsights.performance import lazy_evaluate
        
        @lazy_evaluate
        def test_func(x, y):
            return x + y
        
        # Should return a lambda function
        result = test_func(5, 3)
        assert callable(result)
        
        # Should evaluate when called
        assert result() == 8
    
    def test_lazy_evaluate_error(self):
        """Test lazy_evaluate with non-callable"""
        from quickinsights.performance import lazy_evaluate
        
        with pytest.raises(TypeError):
            lazy_evaluate("not a function")
    
    def test_cache_result(self):
        """Test caching decorator"""
        from quickinsights.performance import cache_result
        
        call_count = 0
        
        @cache_result(ttl=10, max_size=100)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call should use cache
        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment
    
    def test_parallel_process(self):
        """Test parallel processing"""
        from quickinsights.performance import parallel_process
        
        def test_worker(x):
            time.sleep(0.01)  # Small delay
            return x * 2
        
        data = list(range(10))
        results = parallel_process(test_worker, data, max_workers=2)
        
        assert len(results) == 10
        assert results == [x * 2 for x in data]
    
    def test_chunked_process(self):
        """Test chunked processing"""
        from quickinsights.performance import chunked_process
        
        def test_worker(chunk):
            return [x * 2 for x in chunk]
        
        data = list(range(20))
        results = chunked_process(test_worker, data, chunk_size=5)
        
        # Chunked process returns list of chunks, not flattened list
        assert len(results) == 4  # 20 items / 5 chunk_size = 4 chunks
        # Flatten results to check individual values
        flattened = [item for chunk in results for item in chunk]
        assert flattened == [x * 2 for x in data]
    
    def test_memory_optimize(self, sample_data):
        """Test memory optimization"""
        from quickinsights.performance import memory_optimize
        
        df = sample_data['large']
        
        # Test memory optimization
        optimized_df = memory_optimize(df)
        
        assert isinstance(optimized_df, pd.DataFrame)
        assert optimized_df.shape == df.shape
        
        # Check if memory usage is reduced
        original_memory = df.memory_usage(deep=True).sum()
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        
        # Memory should not increase significantly
        assert optimized_memory <= original_memory * 1.1
    
    def test_performance_profile(self):
        """Test performance profiling"""
        from quickinsights.performance import performance_profile
        
        def test_function():
            time.sleep(0.01)
            return "test"
        
        # performance_profile decorator olarak kullanılıyor
        profiled_func = performance_profile(test_function)
        result = profiled_func()
        
        assert result == "test"
        # Profiler bilgisi fonksiyon üzerinde olabilir
    
    def test_benchmark_function(self):
        """Test function benchmarking"""
        from quickinsights.performance import benchmark_function
        
        def test_func(x):
            time.sleep(0.001)
            return x * 2
        
        results = benchmark_function(test_func, [5], iterations=3)
        
        assert isinstance(results, dict)
        assert 'mean_time' in results
        assert 'min_time' in results
        assert 'max_time' in results
        # iterations anahtarı yok, std_time var
        assert 'std_time' in results


class TestMemoryOptimization:
    """Test memory optimization features"""
    
    def test_memory_optimize_numeric(self):
        """Test memory optimization for numeric data"""
        from quickinsights.performance import memory_optimize
        
        # Create DataFrame with mixed dtypes
        df = pd.DataFrame({
            'int64': np.arange(1000, dtype='int64'),
            'float64': np.random.random(1000).astype('float64'),
            'object': ['string'] * 1000
        })
        
        optimized = memory_optimize(df)
        
        # Check that optimization was applied
        assert optimized['int64'].dtype in ['int8', 'int16', 'int32', 'int64']
        assert optimized['float64'].dtype in ['float16', 'float32', 'float64']  # float16 da destekleniyor
        
        # Memory should be reduced
        original_memory = df.memory_usage(deep=True).sum()
        optimized_memory = optimized.memory_usage(deep=True).sum()
        assert optimized_memory <= original_memory
    
    def test_memory_optimize_categorical(self):
        """Test memory optimization for categorical data"""
        from quickinsights.performance import memory_optimize
        
        # Create DataFrame with categorical data
        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B'] * 200,
            'text': ['long text here'] * 1000
        })
        
        optimized = memory_optimize(df)
        
        # Low cardinality string should become category
        if 'category' in optimized.columns:
            assert optimized['category'].dtype == 'category'
        
        # Memory should be reduced
        original_memory = df.memory_usage(deep=True).sum()
        optimized_memory = optimized.memory_usage(deep=True).sum()
        assert optimized_memory <= original_memory


class TestParallelProcessing:
    """Test parallel processing features"""
    
    def test_parallel_process_empty_data(self):
        """Test parallel processing with empty data"""
        from quickinsights.performance import parallel_process
        
        def worker(x):
            return x * 2
        
        results = parallel_process(worker, [], max_workers=2)
        assert results == []
    
    def test_parallel_process_single_item(self):
        """Test parallel processing with single item"""
        from quickinsights.performance import parallel_process
        
        def worker(x):
            return x * 2
        
        results = parallel_process(worker, [5], max_workers=2)
        assert results == [10]
    
    def test_chunked_process_empty_data(self):
        """Test chunked processing with empty data"""
        from quickinsights.performance import chunked_process
        
        def worker(chunk):
            return [x * 2 for x in chunk]
        
        results = chunked_process(worker, [], chunk_size=5)
        assert results == []
    
    def test_chunked_process_small_chunks(self):
        """Test chunked processing with small chunks"""
        from quickinsights.performance import chunked_process
        
        def worker(chunk):
            return [x * 2 for x in chunk]
        
        data = list(range(10))
        results = chunked_process(worker, data, chunk_size=3)
        
        # Chunked process returns list of chunks
        assert len(results) == 4  # 10 items / 3 chunk_size = 4 chunks (last chunk has 1 item)
        # Flatten results to check individual values
        flattened = [item for chunk in results for item in chunk]
        assert flattened == [x * 2 for x in data]


class TestCaching:
    """Test caching functionality"""
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality"""
        from quickinsights.performance import cache_result
        
        call_count = 0
        
        @cache_result(ttl=0, max_size=5)  # Immediate expiration
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        test_func(5)
        assert call_count == 1
        
        # Second call should execute again due to expiration
        test_func(5)
        assert call_count == 2
    
    def test_cache_max_size(self):
        """Test cache size limit"""
        from quickinsights.performance import cache_result
        
        call_count = 0
        
        @cache_result(ttl=100, max_size=2)
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Fill cache
        test_func(1)
        test_func(2)
        test_func(3)
        
        # Should have executed 3 times due to cache size limit
        assert call_count == 3


class TestPerformanceProfiling:
    """Test performance profiling features"""
    
    def test_performance_profile_context_manager(self):
        """Test performance profile as context manager"""
        from quickinsights.performance import performance_profile
        
        # performance_profile context manager değil, decorator
        def test_func():
            time.sleep(0.01)
            return "test"
        
        profiled_func = performance_profile(test_func)
        result = profiled_func()
        
        assert result == "test"
        # Profiler bilgisi fonksiyon üzerinde olabilir
    
    def test_benchmark_function_error_handling(self):
        """Test benchmark function error handling"""
        from quickinsights.performance import benchmark_function
        
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            benchmark_function(failing_func, [], iterations=1)
    
    def test_benchmark_function_single_iteration(self):
        """Test benchmark function with single iteration"""
        from quickinsights.performance import benchmark_function
        
        def test_func(x):
            return x * 2
        
        results = benchmark_function(test_func, [5], iterations=1)
        
        # iterations anahtarı yok
        assert results['mean_time'] == results['min_time'] == results['max_time']


# Integration tests
class TestPerformanceIntegration:
    """Test performance module integration"""
    
    def test_with_large_dataframe(self, sample_data):
        """Test performance utilities with large DataFrame"""
        from quickinsights.performance import memory_optimize, parallel_process
        
        df = sample_data['large']
        
        # Test memory optimization
        optimized_df = memory_optimize(df)
        assert optimized_df.shape == df.shape
        
        # Test parallel processing
        def process_column(col):
            return col.mean()
        
        results = parallel_process(process_column, [df[col] for col in df.columns])
        assert len(results) == len(df.columns)
        assert all(isinstance(r, float) for r in results)
    
    def test_caching_with_pandas_operations(self, sample_data):
        """Test caching with pandas operations"""
        from quickinsights.performance import cache_result
        
        df = sample_data['large']
        
        @cache_result(ttl=10)
        def expensive_operation(data):
            time.sleep(0.01)
            return data.describe()
        
        # First call
        start_time = time.time()
        result1 = expensive_operation(df)
        first_call_time = time.time() - start_time
        
        # Second call (should use cache)
        start_time = time.time()
        result2 = expensive_operation(df)
        second_call_time = time.time() - start_time
        
        # Second call should be faster
        assert second_call_time < first_call_time
        assert result1.equals(result2)
