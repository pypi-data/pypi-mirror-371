"""
Tests for QuickInsights Error Handling System
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from quickinsights.error_handling import (
    QuickInsightsError,
    DataValidationError,
    PerformanceError,
    DependencyError,
    ConfigurationError,
    ValidationUtils,
    ErrorHandler,
    global_error_handler,
    safe_execute
)

class TestQuickInsightsError:
    """Test QuickInsights base error class"""
    
    def test_basic_error_creation(self):
        """Test basic error creation"""
        error = QuickInsightsError("Test error message")
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.details == {}
        assert error.timestamp is not None
    
    def test_error_with_code_and_details(self):
        """Test error with error code and details"""
        error = QuickInsightsError(
            "Test error", 
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        assert error.error_code == "TEST_ERROR"
        assert error.details["key"] == "value"
    
    def test_user_friendly_message(self):
        """Test user-friendly error message generation"""
        error = QuickInsightsError("Test error message")
        message = error.get_user_friendly_message()
        assert "❌" in message
        assert "Test error message" in message
    
    def test_technical_details(self):
        """Test technical details retrieval"""
        error = QuickInsightsError("Test error", "TEST_CODE", {"detail": "value"})
        details = error.get_technical_details()
        assert details["error_code"] == "TEST_CODE"
        assert details["message"] == "Test error"
        assert details["details"]["detail"] == "value"

class TestDataValidationError:
    """Test DataValidationError class"""
    
    def test_basic_validation_error(self):
        """Test basic validation error"""
        error = DataValidationError("Invalid data")
        assert error.error_code == "DATA_VALIDATION_ERROR"
        assert error.get_user_friendly_message().startswith("❌ Veri doğrulama hatası")
    
    def test_validation_error_with_column(self):
        """Test validation error with column information"""
        error = DataValidationError("Invalid value", column="age", value="999")
        message = error.get_user_friendly_message()
        assert "age" in message
        assert error.details["column"] == "age"
        assert error.details["value"] == "999"
    
    def test_validation_error_with_expected_type(self):
        """Test validation error with expected type"""
        error = DataValidationError("Type mismatch", expected_type="numeric")
        assert error.details["expected_type"] == "numeric"

class TestValidationUtils:
    """Test ValidationUtils class"""
    
    def test_validate_dataframe_valid(self):
        """Test DataFrame validation with valid DataFrame"""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        # Should not raise any exception
        ValidationUtils.validate_dataframe(df)
    
    def test_validate_dataframe_not_dataframe(self):
        """Test DataFrame validation with non-DataFrame"""
        with pytest.raises(DataValidationError) as exc_info:
            ValidationUtils.validate_dataframe([1, 2, 3])
        assert "DataFrame olmalıdır" in str(exc_info.value)
    
    def test_validate_dataframe_empty(self):
        """Test DataFrame validation with empty DataFrame"""
        df = pd.DataFrame()
        with pytest.raises(DataValidationError) as exc_info:
            ValidationUtils.validate_dataframe(df)
        assert "boş olamaz" in str(exc_info.value)
    
    def test_validate_dataframe_empty_allowed(self):
        """Test DataFrame validation with empty DataFrame allowed"""
        df = pd.DataFrame()
        # Should not raise exception when allow_empty=True
        ValidationUtils.validate_dataframe(df, allow_empty=True)
    
    def test_validate_column_exists(self):
        """Test column existence validation"""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        # Should not raise exception for existing column
        ValidationUtils.validate_column_exists(df, "A")
        
        # Should raise exception for non-existing column
        with pytest.raises(DataValidationError) as exc_info:
            ValidationUtils.validate_column_exists(df, "C")
        assert "C" in str(exc_info.value)
        assert "available_columns" in exc_info.value.details
    
    def test_validate_numeric_column(self):
        """Test numeric column validation"""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        # Should not raise exception for numeric column
        ValidationUtils.validate_numeric_column(df, "A")
        
        # Should raise exception for non-numeric column
        with pytest.raises(DataValidationError) as exc_info:
            ValidationUtils.validate_numeric_column(df, "B")
        assert "sayısal olmalıdır" in str(exc_info.value)
    
    def test_validate_file_path_valid(self):
        """Test file path validation with valid file"""
        with tempfile.NamedTemporaryFile() as tmp_file:
            # Should not raise exception for existing file
            ValidationUtils.validate_file_path(tmp_file.name)
    
    def test_validate_file_path_not_exists(self):
        """Test file path validation with non-existing file"""
        with pytest.raises(DataValidationError) as exc_info:
            ValidationUtils.validate_file_path("/nonexistent/file.txt")
        assert "bulunamadı" in str(exc_info.value)
    
    def test_validate_file_path_directory(self):
        """Test file path validation with directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(DataValidationError) as exc_info:
                ValidationUtils.validate_file_path(tmp_dir)
            assert "bir dosya değil" in str(exc_info.value)

class TestErrorHandler:
    """Test ErrorHandler class"""
    
    def test_error_handler_creation(self):
        """Test ErrorHandler creation"""
        handler = ErrorHandler(log_errors=False, show_traceback=False)
        assert handler.error_count == 0
        assert len(handler.error_history) == 0
    
    def test_handle_quickinsights_error(self):
        """Test handling QuickInsights errors"""
        handler = ErrorHandler(log_errors=False)
        error = DataValidationError("Test error")
        
        message = handler.handle_error(error, {"context": "test"})
        assert "❌ Veri doğrulama hatası" in message
        assert handler.error_count == 1
        assert len(handler.error_history) == 1
    
    def test_handle_generic_error(self):
        """Test handling generic errors"""
        handler = ErrorHandler(log_errors=False)
        error = ValueError("Generic error")
        
        message = handler.handle_error(error, {"context": "test"})
        assert "❌ Beklenmeyen hata" in message
        assert handler.error_count == 1
    
    def test_error_summary(self):
        """Test error summary generation"""
        handler = ErrorHandler(log_errors=False)
        handler.handle_error(DataValidationError("Error 1"))
        handler.handle_error(ValueError("Error 2"))
        handler.handle_error(DataValidationError("Error 3"))
        
        summary = handler.get_error_summary()
        assert summary["total_errors"] == 3
        assert summary["error_types"]["DataValidationError"] == 2
        assert summary["error_types"]["ValueError"] == 1
        assert len(summary["recent_errors"]) == 3
    
    def test_clear_history(self):
        """Test error history clearing"""
        handler = ErrorHandler(log_errors=False)
        handler.handle_error(ValueError("Test error"))
        assert handler.error_count == 1
        
        handler.clear_history()
        assert handler.error_count == 0
        assert len(handler.error_history) == 0

class TestSafeExecute:
    """Test safe_execute function"""
    
    def test_safe_execute_success(self):
        """Test successful execution"""
        def test_func(x, y):
            return x + y
        
        success, result, error = safe_execute(test_func, 2, 3)
        assert success is True
        assert result == 5
        assert error is None
    
    def test_safe_execute_error(self):
        """Test error handling in execution"""
        def test_func(x, y):
            raise ValueError("Test error")
        
        success, result, error = safe_execute(test_func, 2, 3, {"context": "test"})
        assert success is False
        assert result is None
        assert error is not None
        assert "❌ Beklenmeyen hata" in error

class TestGlobalErrorHandler:
    """Test global error handler"""
    
    def test_global_handler_exists(self):
        """Test that global error handler exists"""
        assert global_error_handler is not None
        assert isinstance(global_error_handler, ErrorHandler)
    
    def test_global_handler_functionality(self):
        """Test global error handler functionality"""
        initial_count = global_error_handler.error_count
        
        # Handle an error
        error = DataValidationError("Test error")
        message = global_error_handler.handle_error(error)
        
        assert global_error_handler.error_count == initial_count + 1
        assert "❌ Veri doğrulama hatası" in message

class TestIntegration:
    """Test integration with other components"""
    
    def test_validation_in_dataframe_operations(self):
        """Test validation in DataFrame operations"""
        # Create a valid DataFrame
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        
        # Should not raise exception
        ValidationUtils.validate_dataframe(df)
        ValidationUtils.validate_column_exists(df, "A")
        ValidationUtils.validate_numeric_column(df, "A")
    
    def test_error_handling_in_validation(self):
        """Test error handling during validation"""
        # Test with invalid data
        with pytest.raises(DataValidationError):
            ValidationUtils.validate_dataframe(None)
        
        # Test with empty DataFrame
        with pytest.raises(DataValidationError):
            ValidationUtils.validate_dataframe(pd.DataFrame())
        
        # Test with non-existing column
        df = pd.DataFrame({"A": [1, 2, 3]})
        with pytest.raises(DataValidationError):
            ValidationUtils.validate_column_exists(df, "B")

if __name__ == "__main__":
    pytest.main([__file__])
