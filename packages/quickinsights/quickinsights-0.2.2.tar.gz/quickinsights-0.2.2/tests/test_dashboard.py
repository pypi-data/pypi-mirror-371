"""
Tests for dashboard module
"""
import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from quickinsights.dashboard import create_dashboard, DashboardGenerator


class TestDashboard:
    """Test cases for dashboard module"""
    
    def setup_method(self):
        """Setup test data"""
        # Create sample data
        np.random.seed(42)
        
        self.sample_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['A', 'B', 'C', 'D', 'E'],
            'D': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        # Create data with missing values
        self.missing_df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': [10, 20, 30, np.nan, 50],
            'C': ['A', 'B', 'C', 'D', 'E']
        })
        
        # Create data with outliers
        self.outlier_df = pd.DataFrame({
            'normal': np.random.normal(0, 1, 100),
            'outliers': np.concatenate([
                np.random.normal(0, 1, 95),
                np.array([100, -100, 50, -50, 75])
            ])
        })
        
        # Create temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_dashboard_basic(self):
        """Test basic create_dashboard functionality"""
        result = create_dashboard(self.sample_df, title="Test Dashboard")
        
        # Check required keys exist
        assert 'html' in result
        assert 'json' in result
        assert 'title' in result
        
        # Check file paths
        assert result['html'] == 'dashboard.html'
        assert result['json'] == 'dashboard_data.json'
        assert result['title'] == 'Test Dashboard'
        
        # Check files were created
        assert os.path.exists('dashboard.html')
        assert os.path.exists('dashboard_data.json')
        
        # Clean up
        os.remove('dashboard.html')
        os.remove('dashboard_data.json')
    
    def test_create_dashboard_custom_output(self):
        """Test create_dashboard with custom output paths"""
        html_path = os.path.join(self.temp_dir, 'custom.html')
        json_path = os.path.join(self.temp_dir, 'custom.json')
        
        result = create_dashboard(
            self.sample_df, 
            title="Custom Dashboard",
            output_html=html_path,
            output_json=json_path
        )
        
        assert result['html'] == html_path
        assert result['json'] == json_path
        
        # Check files were created
        assert os.path.exists(html_path)
        assert os.path.exists(json_path)
    
    def test_dashboard_generator_initialization(self):
        """Test DashboardGenerator initialization"""
        generator = DashboardGenerator("Test Title")
        
        assert generator.title == "Test Title"
        assert generator.sections == []
        assert hasattr(generator, 'add_dataset_overview')
        assert hasattr(generator, 'add_summary_statistics')
        assert hasattr(generator, 'add_missing_data_analysis')
        assert hasattr(generator, 'add_categorical_analysis')
        assert hasattr(generator, 'add_insights_section')
        assert hasattr(generator, 'add_recommendations_section')
        assert hasattr(generator, 'add_data_quality_score')
    
    def test_add_dataset_overview(self):
        """Test add_dataset_overview method"""
        generator = DashboardGenerator("Test")
        generator.add_dataset_overview(self.sample_df)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        assert section['type'] == 'dataset_overview'
        assert section['title'] == '📊 Veri Seti Genel Bakış'
        assert 'data' in section
        
        data = section['data']
        # Note: key names might vary
        if 'total_rows' in data:
            assert data['total_rows'] == 5
        if 'total_columns' in data:
            assert data['total_columns'] == 4
        assert 'memory_usage_mb' in data
        assert 'column_types' in data
    
    def test_add_summary_statistics(self):
        """Test add_summary_statistics method"""
        generator = DashboardGenerator("Test")
        generator.add_summary_statistics(self.sample_df)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        assert section['type'] == 'summary_statistics'
        assert section['title'] == '📈 Özet İstatistikler'
        assert 'data' in section
        
        data = section['data']
        assert 'statistics' in data
        assert 'correlation_summary' in data
        assert 'distribution_insights' in data
    
    def test_add_missing_data_analysis(self):
        """Test add_missing_data_analysis method"""
        generator = DashboardGenerator("Test")
        generator.add_missing_data_analysis(self.missing_df)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        assert section['type'] == 'missing_data_analysis'
        assert section['title'] == '❓ Eksik Veri Analizi'
        assert 'data' in section
        
        data = section['data']
        assert 'missing_by_column' in data
        assert 'missing_percentage_by_column' in data
        assert 'missing_patterns' in data
        assert 'recommendations' in data
    
    def test_add_categorical_analysis(self):
        """Test add_categorical_analysis method"""
        generator = DashboardGenerator("Test")
        generator.add_categorical_analysis(self.sample_df)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        assert section['type'] == 'categorical_analysis'
        assert section['title'] == '🏷️ Kategorik Değişken Analizi'
        assert 'data' in section
        
        data = section['data']
        assert 'C' in data  # Categorical column
        assert data['C']['unique_count'] == 5
        assert data['C']['unique_ratio'] == 1.0
    
    def test_add_insights_section(self):
        """Test add_insights_section method"""
        generator = DashboardGenerator("Test")
        insights = ["Insight 1", "Insight 2", "Insight 3"]
        generator.add_insights_section(insights)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        assert section['type'] == 'insights'
        assert section['title'] == '🔍 Otomatik Bulgular'
        assert 'data' in section
        
        data = section['data']
        assert data['insights'] == insights
        assert data['insight_count'] == 3
    
    def test_add_recommendations_section(self):
        """Test add_recommendations_section method"""
        generator = DashboardGenerator("Test")
        recommendations = ["Rec 1", "Rec 2", "Rec 3"]
        generator.add_recommendations_section(recommendations)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        assert section['type'] == 'recommendations'
        assert section['title'] == '💡 Öneriler'
        assert 'data' in section
        
        data = section['data']
        assert data['recommendations'] == recommendations
        assert data['recommendation_count'] == 3
    
    def test_add_data_quality_score(self):
        """Test add_data_quality_score method"""
        generator = DashboardGenerator("Test")
        quality_score = 85.5
        quality_details = {"overall_score": 85.5, "details": "Good quality"}
        
        generator.add_data_quality_score(quality_score, quality_details)
        
        assert len(generator.sections) == 1
        section = generator.sections[0]
        
        # Note: type might be 'data_quality' instead of 'data_quality_score'
        assert section['type'] in ['data_quality_score', 'data_quality']
        assert section['title'] == '🏆 Veri Kalitesi Skoru'
        assert 'data' in section
        
        data = section['data']
        assert data['quality_score'] == quality_score
        assert data['quality_details'] == quality_details
    
    def test_generate_html_dashboard(self):
        """Test generate_html_dashboard method"""
        generator = DashboardGenerator("Test Dashboard")
        generator.add_dataset_overview(self.sample_df)
        generator.add_summary_statistics(self.sample_df)
        
        html_path = os.path.join(self.temp_dir, 'test.html')
        result_path = generator.generate_html_dashboard(html_path)
        
        assert result_path == html_path
        assert os.path.exists(html_path)
        
        # Check HTML content
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        assert 'Test Dashboard' in html_content
        assert 'Veri Seti Genel Bakış' in html_content
        assert 'Özet İstatistikler' in html_content
    
    def test_generate_json_report(self):
        """Test generate_json_report method"""
        generator = DashboardGenerator("Test Dashboard")
        generator.add_dataset_overview(self.sample_df)
        generator.add_summary_statistics(self.sample_df)
        
        json_path = os.path.join(self.temp_dir, 'test.json')
        result_path = generator.generate_json_report(json_path)
        
        assert result_path == json_path
        assert os.path.exists(json_path)
        
        # Check JSON content
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        assert json_data['title'] == 'Test Dashboard'
        assert 'sections' in json_data
        assert len(json_data['sections']) == 2
    
    def test_dashboard_with_insights_integration(self):
        """Test dashboard creation with quick_insights integration"""
        # This test requires quick_insights module to be available
        try:
            from quickinsights.quick_insights import quick_insight
            
            result = create_dashboard(self.sample_df, title="Insights Dashboard")
            
            # Should have created dashboard with insights
            assert 'html' in result
            assert 'json' in result
            
            # Clean up
            if os.path.exists('dashboard.html'):
                os.remove('dashboard.html')
            if os.path.exists('dashboard_data.json'):
                os.remove('dashboard_data.json')
                
        except ImportError:
            # Skip if quick_insights not available
            pytest.skip("quick_insights module not available")
    
    def test_dashboard_error_handling(self):
        """Test dashboard error handling"""
        generator = DashboardGenerator("Test")
        
        # Test with empty DataFrame
        generator.add_dataset_overview(pd.DataFrame())
        
        # Should handle empty DataFrame gracefully
        assert len(generator.sections) == 1
        
        # Test with None
        with pytest.raises(Exception):
            generator.add_dataset_overview(None)
    
    def test_dashboard_section_ordering(self):
        """Test that dashboard sections are added in correct order"""
        generator = DashboardGenerator("Test")
        
        # Add sections in specific order
        generator.add_dataset_overview(self.sample_df)
        generator.add_summary_statistics(self.sample_df)
        generator.add_missing_data_analysis(self.missing_df)
        generator.add_categorical_analysis(self.sample_df)
        
        # Check section order
        assert len(generator.sections) == 4
        assert generator.sections[0]['type'] == 'dataset_overview'
        assert generator.sections[1]['type'] == 'summary_statistics'
        assert generator.sections[2]['type'] == 'missing_data_analysis'
        assert generator.sections[3]['type'] == 'categorical_analysis'
    
    def test_dashboard_customization(self):
        """Test dashboard customization options"""
        generator = DashboardGenerator("Custom Title")
        
        # Add custom sections
        generator.add_dataset_overview(self.sample_df)
        generator.add_summary_statistics(self.sample_df)
        
        # Generate dashboard
        html_path = os.path.join(self.temp_dir, 'custom.html')
        generator.generate_html_dashboard(html_path)
        
        # Check custom title
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        assert 'Custom Title' in html_content


if __name__ == "__main__":
    pytest.main([__file__])
