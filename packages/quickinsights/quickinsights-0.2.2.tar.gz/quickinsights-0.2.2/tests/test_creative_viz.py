"""
Tests for Creative Visualization module
"""

import pytest
import pandas as pd
import numpy as np
import warnings
from unittest.mock import patch, MagicMock

warnings.filterwarnings("ignore")

# Test if plotly is available
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    np.random.seed(42)
    
    # Numeric data for visualization
    numeric_df = pd.DataFrame({
        'A': np.random.normal(0, 1, 100),
        'B': np.random.normal(5, 2, 100),
        'C': np.random.uniform(0, 10, 100),
        'D': np.random.randint(0, 100, 100),
        'category': ['X', 'Y', 'Z'] * 33 + ['X']
    })
    
    # Time series data
    time_df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'value': np.random.normal(100, 20, 100),
        'trend': np.linspace(100, 120, 100) + np.random.normal(0, 5, 100)
    })
    
    return {
        'numeric': numeric_df,
        'time_series': time_df
    }


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not available")
class TestCreativeVizEngine:
    """Test CreativeVizEngine class"""
    
    def test_initialization(self, sample_data):
        """Test CreativeVizEngine initialization"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        assert engine.df is not None
        assert hasattr(engine, 'color_palette')
        assert len(engine.color_palette) > 0
    
    def test_create_radar_chart(self, sample_data):
        """Test radar chart creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        numeric_cols = ['A', 'B', 'C']
        fig = engine.create_radar_chart(numeric_cols, "Test Radar Chart")
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Test Radar Chart"
    
    def test_create_3d_scatter(self, sample_data):
        """Test 3D scatter plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_3d_scatter('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_heatmap(self, sample_data):
        """Test heatmap creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        numeric_cols = ['A', 'B', 'C']
        fig = engine.create_heatmap(numeric_cols, "Test Heatmap")
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Test Heatmap"
    
    def test_create_bubble_chart(self, sample_data):
        """Test bubble chart creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_bubble_chart('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_create_sunburst_chart(self, sample_data):
        """Test sunburst chart creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_sunburst_chart(['category', 'D'], 'A')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Sunburst Chart"
    
    def test_create_parallel_coordinates(self, sample_data):
        """Test parallel coordinates plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        numeric_cols = ['A', 'B', 'C']
        fig = engine.create_parallel_coordinates(numeric_cols, 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Parallel Coordinates Plot"
    
    def test_create_animated_scatter(self, sample_data):
        """Test animated scatter plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_animated_scatter('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Animated Scatter Plot"
    
    def test_create_3d_surface(self, sample_data):
        """Test 3D surface plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_3d_surface('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_waterfall_chart(self, sample_data):
        """Test waterfall chart creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_waterfall_chart('A', 'B')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Waterfall Chart"
    
    def test_create_funnel_chart(self, sample_data):
        """Test funnel chart creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_funnel_chart('A', 'B')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Funnel Chart"
    
    def test_create_gantt_chart(self, sample_data):
        """Test Gantt chart creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['time_series']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_gantt_chart('date', 'value', 'trend')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Gantt Chart"
    
    def test_create_sankey_diagram(self, sample_data):
        """Test Sankey diagram creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_sankey_diagram(['A', 'B', 'C'], 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Sankey Diagram"
    
    def test_create_treemap(self, sample_data):
        """Test treemap creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_treemap(['category', 'D'], 'A')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Treemap"
    
    def test_create_violin_plot(self, sample_data):
        """Test violin plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_violin_plot('A', 'category')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Violin Plot"
    
    def test_create_box_plot(self, sample_data):
        """Test box plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_box_plot('A', 'category')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Box Plot"
    
    def test_create_histogram(self, sample_data):
        """Test histogram creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_histogram('A', 'category')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Histogram"
    
    def test_create_density_plot(self, sample_data):
        """Test density plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_density_plot('A', 'category')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Density Plot"
    
    def test_create_contour_plot(self, sample_data):
        """Test contour plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_contour_plot('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Contour Plot"
    
    def test_create_quiver_plot(self, sample_data):
        """Test quiver plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_quiver_plot('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Quiver Plot"
    
    def test_create_streamtube_plot(self, sample_data):
        """Test streamtube plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_streamtube_plot('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_cone_plot(self, sample_data):
        """Test cone plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_cone_plot('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_volume_plot(self, sample_data):
        """Test volume plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_volume_plot('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_isosurface_plot(self, sample_data):
        """Test isosurface plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_isosurface_plot('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_mesh_3d_plot(self, sample_data):
        """Test 3D mesh plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_mesh_3d_plot('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_cone_3d_plot(self, sample_data):
        """Test 3D cone plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_cone_3d_plot('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.scene is not None
    
    def test_create_streamline_plot(self, sample_data):
        """Test streamline plot creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_streamline_plot('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Streamline Plot"
    
    def test_create_choropleth_map(self, sample_data):
        """Test choropleth map creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_choropleth_map('A', 'B')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Choropleth Map"
    
    def test_create_scatter_mapbox(self, sample_data):
        """Test scatter mapbox creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_scatter_mapbox('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Scatter Mapbox"
    
    def test_create_choropleth_mapbox(self, sample_data):
        """Test choropleth mapbox creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_choropleth_mapbox('A', 'B')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Choropleth Mapbox"
    
    def test_create_density_mapbox(self, sample_data):
        """Test density mapbox creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_density_mapbox('A', 'B')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Density Mapbox"
    
    def test_create_line_mapbox(self, sample_data):
        """Test line mapbox creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_line_mapbox('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Line Mapbox"
    
    def test_create_polygon_mapbox(self, sample_data):
        """Test polygon mapbox creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_polygon_mapbox('A', 'B')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Polygon Mapbox"
    
    def test_create_choropleth_mapbox_with_hover(self, sample_data):
        """Test choropleth mapbox with hover creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_choropleth_mapbox_with_hover('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Choropleth Mapbox with Hover"
    
    def test_create_scatter_mapbox_with_hover(self, sample_data):
        """Test scatter mapbox with hover creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_scatter_mapbox_with_hover('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Scatter Mapbox with Hover"
    
    def test_create_density_mapbox_with_hover(self, sample_data):
        """Test density mapbox with hover creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_density_mapbox_with_hover('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Density Mapbox with Hover"
    
    def test_create_line_mapbox_with_hover(self, sample_data):
        """Test line mapbox with hover creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_line_mapbox_with_hover('A', 'B', 'C', 'D')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Line Mapbox with Hover"
    
    def test_create_polygon_mapbox_with_hover(self, sample_data):
        """Test polygon mapbox with hover creation"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        fig = engine.create_polygon_mapbox_with_hover('A', 'B', 'C')
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Polygon Mapbox with Hover"


# Integration tests
@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not available")
class TestCreativeVizIntegration:
    """Test creative visualization integration"""
    
    def test_multiple_charts_creation(self, sample_data):
        """Test creation of multiple chart types"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        # Create multiple chart types
        charts = [
            engine.create_radar_chart(['A', 'B', 'C']),
            engine.create_3d_scatter('A', 'B', 'C'),
            engine.create_heatmap(['A', 'B', 'C']),
            engine.create_bubble_chart('A', 'B', 'C', 'D')
        ]
        
        # All should be valid Plotly figures
        for chart in charts:
            assert isinstance(chart, go.Figure)
    
    def test_chart_customization(self, sample_data):
        """Test chart customization options"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        engine = CreativeVizEngine(df)
        
        # Test custom title
        fig = engine.create_radar_chart(['A', 'B'], "Custom Title")
        assert fig.layout.title.text == "Custom Title"
        
        # Test custom colors
        fig = engine.create_3d_scatter('A', 'B', 'C', 'D')
        assert fig.layout.scene is not None


# Mock tests for when plotly is not available
class TestCreativeVizWithoutPlotly:
    """Test creative visualization behavior when plotly is missing"""
    
    def test_initialization_without_plotly(self, sample_data):
        """Test initialization when plotly is not available"""
        from quickinsights.creative_viz import CreativeVizEngine
        
        df = sample_data['numeric']
        
        # Should handle gracefully
        engine = CreativeVizEngine(df)
        assert engine.df is not None
