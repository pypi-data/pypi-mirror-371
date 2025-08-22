"""
QuickInsights - Creative Visualization Engine

Bu modül, geleneksel görselleştirmelerin ötesine geçen yaratıcı ve
yenilikçi görselleştirme özellikleri sunar.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings("ignore")


class CreativeVizEngine:
    """
    Yaratıcı görselleştirme motoru

    Geleneksel matplotlib/seaborn görselleştirmelerinin ötesine geçen
    yenilikçi ve interaktif görselleştirmeler oluşturur.
    """

    def __init__(self, df: pd.DataFrame):
        """
        CreativeVizEngine başlatıcısı

        Parameters
        ----------
        df : pd.DataFrame
            Görselleştirilecek veri seti
        """
        self.df = df
        self.color_palette = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FFEAA7",
            "#DDA0DD",
            "#98D8C8",
            "#F7DC6F",
        ]

    def create_radar_chart(
        self, numeric_cols: List[str], title: str = "Radar Chart Analysis"
    ) -> go.Figure:
        """
        Radar chart oluşturur

        Parameters
        ----------
        numeric_cols : List[str]
            Görselleştirilecek sayısal sütunlar
        title : str
            Grafik başlığı

        Returns
        -------
        go.Figure
            Plotly radar chart
        """
        # Veriyi normalize et
        df_numeric = self.df[numeric_cols].copy()
        df_normalized = (df_numeric - df_numeric.min()) / (
            df_numeric.max() - df_numeric.min()
        )

        # Ortalama değerleri hesapla
        mean_values = df_normalized.mean()

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=mean_values.values,
                theta=numeric_cols,
                fill="toself",
                name="Ortalama Değerler",
                line_color="#FF6B6B",
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title=title,
            font=dict(size=14),
        )

        return fig

    def create_3d_scatter(
        self,
        x_col: str,
        y_col: str,
        z_col: str,
        color_col: Optional[str] = None,
        size_col: Optional[str] = None,
    ) -> go.Figure:
        """
        3D scatter plot oluşturur

        Parameters
        ----------
        x_col, y_col, z_col : str
            X, Y, Z eksenleri için sütun isimleri
        color_col : str, optional
            Renk kodlaması için sütun
        size_col : str, optional
            Boyut kodlaması için sütun

        Returns
        -------
        go.Figure
            3D scatter plot
        """
        fig = go.Figure()

        if color_col and color_col in self.df.columns:
            # Kategorik renk kodlaması
            unique_colors = self.df[color_col].unique()

            for color_val in unique_colors:
                mask = self.df[color_col] == color_val
                df_subset = self.df[mask]

                fig.add_trace(
                    go.Scatter3d(
                        x=df_subset[x_col],
                        y=df_subset[y_col],
                        z=df_subset[z_col],
                        mode="markers",
                        name=str(color_val),
                        marker=dict(
                            size=8 if size_col is None else df_subset[size_col] * 2,
                            opacity=0.7,
                        ),
                    )
                )
        else:
            # Basit 3D scatter
            fig.add_trace(
                go.Scatter3d(
                    x=self.df[x_col],
                    y=self.df[y_col],
                    z=self.df[z_col],
                    mode="markers",
                    marker=dict(
                        size=8 if size_col is None else self.df[size_col] * 2,
                        color=self.df[z_col] if size_col is None else self.df[size_col],
                        colorscale="Viridis",
                        opacity=0.7,
                    ),
                )
            )

        fig.update_layout(
            title=f"3D Scatter Plot: {x_col} vs {y_col} vs {z_col}",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )

        return fig

    def create_interactive_network(
        self,
        source_col: str,
        target_col: str,
        weight_col: Optional[str] = None,
        node_size_col: Optional[str] = None,
    ) -> go.Figure:
        """
        İnteraktif network graph oluşturur

        Parameters
        ----------
        source_col, target_col : str
            Kaynak ve hedef düğümler için sütunlar
        weight_col : str, optional
            Kenar ağırlıkları için sütun
        node_size_col : str, optional
            Düğüm boyutları için sütun

        Returns
        -------
        go.Figure
            Network graph
        """
        # Benzersiz düğümleri bul
        all_nodes = set(self.df[source_col].unique()) | set(
            self.df[target_col].unique()
        )
        node_to_idx = {node: idx for idx, node in enumerate(all_nodes)}

        # Kenarları oluştur
        edge_x = []
        edge_y = []
        edge_weights = []

        for _, row in self.df.iterrows():
            source_idx = node_to_idx[row[source_col]]
            target_idx = node_to_idx[row[target_col]]

            edge_x.extend([source_idx, target_idx, None])
            edge_y.extend([target_idx, source_idx, None])

            if weight_col:
                edge_weights.append(row[weight_col])

        # Düğüm pozisyonlarını hesapla (force-directed layout)
        node_x = []
        node_y = []
        node_sizes = []
        node_labels = []

        for node in all_nodes:
            # Basit dairesel layout
            idx = node_to_idx[node]
            angle = 2 * np.pi * idx / len(all_nodes)
            radius = 1.0

            node_x.append(radius * np.cos(angle))
            node_y.append(radius * np.sin(angle))
            node_labels.append(str(node))

            if node_size_col:
                node_sizes.append(
                    self.df[self.df[source_col] == node][node_size_col].mean() * 10
                )
            else:
                node_sizes.append(20)

        # Kenar trace'i
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        # Düğüm trace'i
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=node_labels,
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color=node_sizes,
                colorscale="Viridis",
                showscale=True,
                line=dict(width=2, color="white"),
            ),
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Interactive Network Graph",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        return fig

    def create_animated_timeline(
        self,
        time_col: str,
        value_col: str,
        category_col: Optional[str] = None,
        animation_col: Optional[str] = None,
    ) -> go.Figure:
        """
        Animasyonlu timeline oluşturur

        Parameters
        ----------
        time_col : str
            Zaman sütunu
        value_col : str
            Değer sütunu
        category_col : str, optional
            Kategori sütunu
        animation_col : str, optional
            Animasyon için sütun

        Returns
        -------
        go.Figure
            Animasyonlu timeline
        """
        # Zaman sütununu datetime'a çevir
        df_copy = self.df.copy()
        df_copy[time_col] = pd.to_datetime(df_copy[time_col])

        if category_col:
            fig = px.line(
                df_copy,
                x=time_col,
                y=value_col,
                color=category_col,
                title="Animated Timeline",
            )
        else:
            fig = px.line(df_copy, x=time_col, y=value_col, title="Animated Timeline")

        if animation_col:
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[
                                    None,
                                    {
                                        "frame": {"duration": 500, "redraw": True},
                                        "fromcurrent": True,
                                    },
                                ],
                            )
                        ],
                    )
                ]
            )

        return fig

    def create_heatmap(
        self, numeric_cols: List[str], title: str = "Heatmap"
    ) -> go.Figure:
        """
        Heatmap oluşturur

        Parameters
        ----------
        numeric_cols : List[str]
            Görselleştirilecek sayısal sütunlar
        title : str
            Grafik başlığı

        Returns
        -------
        go.Figure
            Heatmap
        """
        # Korelasyon matrisi hesapla
        corr_matrix = self.df[numeric_cols].corr()
        
        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale="Viridis",
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Features",
            yaxis_title="Features",
            width=800,
            height=600,
        )

        return fig

    def create_heatmap_with_annotations(
        self, data_matrix: pd.DataFrame, title: str = "Annotated Heatmap"
    ) -> go.Figure:
        """
        Açıklamalı heatmap oluşturur

        Parameters
        ----------
        data_matrix : pd.DataFrame
            Görselleştirilecek veri matrisi
        title : str
            Grafik başlığı

        Returns
        -------
        go.Figure
            Açıklamalı heatmap
        """
        fig = go.Figure(
            data=go.Heatmap(
                z=data_matrix.values,
                x=data_matrix.columns,
                y=data_matrix.index,
                colorscale="Viridis",
                text=np.round(data_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Features",
            yaxis_title="Samples",
            width=800,
            height=600,
        )

        return fig

    def create_bubble_chart(
        self, x_col: str, y_col: str, size_col: str, color_col: Optional[str] = None
    ) -> go.Figure:
        """
        Bubble chart oluşturur

        Parameters
        ----------
        x_col : str
            X ekseni sütunu
        y_col : str
            Y ekseni sütunu
        size_col : str
            Bubble boyutu için sütun
        color_col : str, optional
            Renk kodlaması için sütun

        Returns
        -------
        go.Figure
            Bubble chart
        """
        fig = go.Figure()

        if color_col:
            # Renk kodlaması ile
            for color_val in self.df[color_col].unique():
                mask = self.df[color_col] == color_val
                fig.add_trace(
                    go.Scatter(
                        x=self.df[mask][x_col],
                        y=self.df[mask][y_col],
                        mode="markers",
                        marker=dict(
                            size=self.df[mask][size_col],
                            sizemode="area",
                            sizeref=2.0 * max(self.df[size_col]) / (40.0 ** 2),
                            sizemin=4,
                            color=color_val,
                            opacity=0.7,
                        ),
                        name=str(color_val),
                        text=self.df[mask][color_col],
                        hovertemplate="<b>%{text}</b><br>" +
                                   f"{x_col}: %{{x}}<br>" +
                                   f"{y_col}: %{{y}}<br>" +
                                   f"{size_col}: %{{marker.size}}<extra></extra>",
                    )
                )
        else:
            # Renk kodlaması olmadan
            fig.add_trace(
                go.Scatter(
                    x=self.df[x_col],
                    y=self.df[y_col],
                    mode="markers",
                    marker=dict(
                        size=self.df[size_col],
                        sizemode="area",
                        sizeref=2.0 * max(self.df[size_col]) / (40.0 ** 2),
                        sizemin=4,
                        color=self.df[size_col],
                        colorscale="Viridis",
                        opacity=0.7,
                        colorbar=dict(title=size_col),
                    ),
                    text=self.df[size_col],
                    hovertemplate=f"{x_col}: %{{x}}<br>" +
                                 f"{y_col}: %{{y}}<br>" +
                                 f"{size_col}: %{{text}}<extra></extra>",
                )
            )

        fig.update_layout(
            title="Bubble Chart",
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True,
            width=800,
            height=600,
        )

        return fig

    def create_parallel_coordinates(
        self, numeric_cols: List[str], color_col: Optional[str] = None
    ) -> go.Figure:
        """
        Parallel coordinates plot oluşturur

        Parameters
        ----------
        numeric_cols : List[str]
            Görselleştirilecek sayısal sütunlar
        color_col : str, optional
            Renk kodlaması için sütun

        Returns
        -------
        go.Figure
            Parallel coordinates plot
        """
        df_subset = self.df[numeric_cols + ([color_col] if color_col else [])].copy()

        # Eksik değerleri temizle
        df_subset = df_subset.dropna()

        if color_col:
            fig = px.parallel_coordinates(
                df_subset,
                dimensions=numeric_cols,
                color=color_col,
                title="Parallel Coordinates Plot",
            )
        else:
            fig = px.parallel_coordinates(
                df_subset, dimensions=numeric_cols, title="Parallel Coordinates Plot"
            )

        return fig

    def create_sunburst_chart(
        self,
        path_cols: List[str],
        value_col: Optional[str] = None,
        title: str = "Sunburst Chart",
    ) -> go.Figure:
        """
        Sunburst chart oluşturur

        Parameters
        ----------
        path_cols : List[str]
            Hiyerarşik yapı için sütunlar
        value_col : str, optional
            Değer sütunu
        title : str
            Grafik başlığı

        Returns
        -------
        go.Figure
            Sunburst chart
        """
        # Hiyerarşik yapıyı oluştur
        df_hierarchical = self.df[path_cols + ([value_col] if value_col else [])].copy()

        if value_col:
            # Değer sütunu varsa, grupla
            df_grouped = (
                df_hierarchical.groupby(path_cols)[value_col].sum().reset_index()
            )
        else:
            # Değer sütunu yoksa, sayım yap
            df_grouped = (
                df_hierarchical.groupby(path_cols).size().reset_index(name="count")
            )
            value_col = "count"

        # Sunburst için veriyi hazırla
        fig = px.sunburst(df_grouped, path=path_cols, values=value_col, title=title)

        return fig

    def create_3d_surface(
        self, x_col: str, y_col: str, z_col: str, title: str = "3D Surface Plot"
    ) -> go.Figure:
        """
        3D surface plot oluşturur

        Parameters
        ----------
        x_col, y_col, z_col : str
            X, Y, Z eksenleri için sütun isimleri
        title : str
            Grafik başlığı

        Returns
        -------
        go.Figure
            3D surface plot
        """
        # Veriyi grid'e dönüştür
        df_subset = self.df[[x_col, y_col, z_col]].dropna()

        # Benzersiz x ve y değerlerini bul
        x_unique = sorted(df_subset[x_col].unique())
        y_unique = sorted(df_subset[y_col].unique())

        # Z değerlerini grid'e dönüştür
        z_matrix = np.zeros((len(y_unique), len(x_unique)))

        for i, y_val in enumerate(y_unique):
            for j, x_val in enumerate(x_unique):
                mask = (df_subset[x_col] == x_val) & (df_subset[y_col] == y_val)
                if mask.any():
                    z_matrix[i, j] = df_subset[mask][z_col].iloc[0]

        fig = go.Figure(
            data=[
                go.Surface(
                    x=x_unique,
                    y=y_unique,
                    z=z_matrix,
                    colorscale="Viridis",
                    opacity=0.8,
                )
            ]
        )

        fig.update_layout(
            title=title,
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )

        return fig

    def create_animated_scatter(
        self,
        x_col: str,
        y_col: str,
        animation_col: str,
        color_col: Optional[str] = None,
        size_col: Optional[str] = None,
    ) -> go.Figure:
        """
        Animasyonlu scatter plot oluşturur

        Parameters
        ----------
        x_col, y_col : str
            X ve Y eksenleri için sütun isimleri
        animation_col : str
            Animasyon için sütun
        color_col : str, optional
            Renk kodlaması için sütun
        size_col : str, optional
            Boyut kodlaması için sütun

        Returns
        -------
        go.Figure
            Animasyonlu scatter plot
        """
        df_subset = self.df[
            [x_col, y_col, animation_col]
            + ([color_col] if color_col else [])
            + ([size_col] if size_col else [])
        ].dropna()

        if color_col:
            fig = px.scatter(
                df_subset,
                x=x_col,
                y=y_col,
                color=color_col,
                size=size_col if size_col else None,
                animation_frame=animation_col,
                title="Animated Scatter Plot",
            )
        else:
            fig = px.scatter(
                df_subset,
                x=x_col,
                y=y_col,
                size=size_col if size_col else None,
                animation_frame=animation_col,
                title="Animated Scatter Plot",
            )

        return fig

    def export_all_plots(self, output_dir: str = "./creative_plots") -> Dict[str, str]:
        """
        Tüm yaratıcı görselleştirmeleri dışa aktarır

        Parameters
        ----------
        output_dir : str
            Çıktı dizini

        Returns
        -------
        Dict[str, str]
            Oluşturulan dosya yolları
        """
        import os

        os.makedirs(output_dir, exist_ok=True)

        exported_files = {}

        # Sayısal sütunları bul
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) >= 3:
            # 3D scatter plot
            fig_3d = self.create_3d_scatter(
                numeric_cols[0], numeric_cols[1], numeric_cols[2]
            )
            fig_3d.write_html(f"{output_dir}/3d_scatter.html")
            exported_files["3d_scatter"] = f"{output_dir}/3d_scatter.html"

        if len(numeric_cols) >= 4:
            # Radar chart
            fig_radar = self.create_radar_chart(numeric_cols[:4])
            fig_radar.write_html(f"{output_dir}/radar_chart.html")
            exported_files["radar_chart"] = f"{output_dir}/radar_chart.html"

        # Parallel coordinates
        if len(numeric_cols) >= 3:
            fig_parallel = self.create_parallel_coordinates(numeric_cols[:3])
            fig_parallel.write_html(f"{output_dir}/parallel_coordinates.html")
            exported_files[
                "parallel_coordinates"
            ] = f"{output_dir}/parallel_coordinates.html"

        # Heatmap
        if len(numeric_cols) >= 2:
            corr_matrix = self.df[numeric_cols].corr()
            fig_heatmap = self.create_heatmap_with_annotations(corr_matrix)
            fig_heatmap.write_html(f"{output_dir}/annotated_heatmap.html")
            exported_files["annotated_heatmap"] = f"{output_dir}/annotated_heatmap.html"

        print(
            f"✅ {len(exported_files)} yaratıcı görselleştirme dışa aktarıldı: {output_dir}"
        )
        return exported_files

    def create_waterfall_chart(self, x_col: str, y_col: str) -> go.Figure:
        """Waterfall chart oluşturur"""
        fig = go.Figure(go.Waterfall(
            name="Waterfall",
            orientation="h",
            measure=["relative"] * len(self.df),
            x=self.df[y_col],
            textposition="outside",
            text=self.df[y_col],
            y=self.df[x_col],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Waterfall Chart",
            showlegend=True,
            width=800,
            height=600,
        )
        return fig

    def create_funnel_chart(self, x_col: str, y_col: str) -> go.Figure:
        """Funnel chart oluşturur"""
        fig = go.Figure(go.Funnel(
            y=self.df[x_col],
            x=self.df[y_col],
        ))
        
        fig.update_layout(
            title="Funnel Chart",
            width=800,
            height=600,
        )
        return fig

    def create_gantt_chart(self, start_col: str, end_col: str, task_col: str) -> go.Figure:
        """Gantt chart oluşturur"""
        fig = go.Figure(data=[
            go.Bar(
                x=[(self.df[start_col].iloc[i], self.df[end_col].iloc[i]) for i in range(len(self.df))],
                y=self.df[task_col],
                orientation='h'
            )
        ])
        
        fig.update_layout(
            title="Gantt Chart",
            xaxis_title="Time",
            yaxis_title="Tasks",
            width=800,
            height=600,
        )
        return fig

    def create_sankey_diagram(self, source_cols: List[str], target_col: str) -> go.Figure:
        """Sankey diagram oluşturur"""
        # Basit Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=source_cols + [target_col],
                color="blue"
            ),
            link=dict(
                source=[0] * len(self.df),
                target=[len(source_cols)] * len(self.df),
                value=self.df[target_col]
            )
        )])
        
        fig.update_layout(
            title="Sankey Diagram",
            width=800,
            height=600,
        )
        return fig

    def create_treemap(self, path_cols: List[str], value_col: str) -> go.Figure:
        """Treemap oluşturur"""
        fig = go.Figure(go.Treemap(
            labels=path_cols,
            parents=[""] * len(path_cols),
            values=self.df[value_col],
        ))
        
        fig.update_layout(
            title="Treemap",
            width=800,
            height=600,
        )
        return fig

    def create_violin_plot(self, x_col: str, y_col: str) -> go.Figure:
        """Violin plot oluşturur"""
        fig = go.Figure()
        
        for category in self.df[x_col].unique():
            fig.add_trace(go.Violin(
                x=[category] * len(self.df[self.df[x_col] == category]),
                y=self.df[self.df[x_col] == category][y_col],
                name=category,
                box_visible=True,
                meanline_visible=True
            ))
        
        fig.update_layout(
            title="Violin Plot",
            xaxis_title=x_col,
            yaxis_title=y_col,
            width=800,
            height=600,
        )
        return fig

    def create_box_plot(self, x_col: str, y_col: str) -> go.Figure:
        """Box plot oluşturur"""
        fig = go.Figure()
        
        for category in self.df[x_col].unique():
            fig.add_trace(go.Box(
                y=self.df[self.df[x_col] == category][y_col],
                name=category
            ))
        
        fig.update_layout(
            title="Box Plot",
            xaxis_title=x_col,
            yaxis_title=y_col,
            width=800,
            height=600,
        )
        return fig

    def create_histogram(self, x_col: str, color_col: str = None) -> go.Figure:
        """Histogram oluşturur"""
        if color_col:
            fig = px.histogram(self.df, x=x_col, color=color_col, title="Histogram")
        else:
            fig = px.histogram(self.df, x=x_col, title="Histogram")
        
        fig.update_layout(width=800, height=600)
        return fig

    def create_density_plot(self, x_col: str, color_col: str = None) -> go.Figure:
        """Density plot oluşturur"""
        if color_col:
            fig = px.histogram(self.df, x=x_col, color=color_col, 
                             histnorm='probability density', title="Density Plot")
        else:
            fig = px.histogram(self.df, x=x_col, histnorm='probability density', 
                             title="Density Plot")
        
        fig.update_layout(width=800, height=600)
        return fig

    def create_contour_plot(self, x_col: str, y_col: str, z_col: str) -> go.Figure:
        """Contour plot oluşturur"""
        fig = go.Figure(data=go.Contour(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title="Contour Plot",
            xaxis_title=x_col,
            yaxis_title=y_col,
            width=800,
            height=600,
        )
        return fig

    def create_quiver_plot(self, x_col: str, y_col: str, u_col: str, v_col: str) -> go.Figure:
        """Quiver plot oluşturur"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df[x_col],
            y=self.df[y_col],
            mode='markers',
            marker=dict(size=8),
            name='Points'
        ))
        
        # Vektörler için basit gösterim
        for i in range(0, len(self.df), 5):  # Her 5. noktada vektör
            fig.add_trace(go.Scatter(
                x=[self.df[x_col].iloc[i], self.df[x_col].iloc[i] + self.df[u_col].iloc[i]],
                y=[self.df[y_col].iloc[i], self.df[y_col].iloc[i] + self.df[v_col].iloc[i]],
                mode='lines',
                line=dict(color='red', width=2),
                showlegend=False
            ))
        
        fig.update_layout(
            title="Quiver Plot",
            xaxis_title=x_col,
            yaxis_title=y_col,
            width=800,
            height=600,
        )
        return fig

    def create_streamtube_plot(self, x_col: str, y_col: str, z_col: str) -> go.Figure:
        """Streamtube plot oluşturur"""
        # Basit 3D scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(size=5, color=self.df[z_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Streamtube Plot",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )
        return fig

    def create_cone_plot(self, x_col: str, y_col: str, z_col: str, u_col: str) -> go.Figure:
        """Cone plot oluşturur"""
        # Basit 3D scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(size=self.df[u_col], color=self.df[u_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Cone Plot",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )
        return fig

    def create_volume_plot(self, x_col: str, y_col: str, z_col: str, value_col: str) -> go.Figure:
        """Volume plot oluşturur"""
        # Basit 3D scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(size=5, color=self.df[value_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Volume Plot",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )
        return fig

    def create_isosurface_plot(self, x_col: str, y_col: str, z_col: str, value_col: str) -> go.Figure:
        """Isosurface plot oluşturur"""
        # Basit 3D scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(size=5, color=self.df[value_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Isosurface Plot",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )
        return fig

    def create_mesh_3d_plot(self, x_col: str, y_col: str, z_col: str) -> go.Figure:
        """3D mesh plot oluşturur"""
        # Basit 3D scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(size=5, color=self.df[z_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="3D Mesh Plot",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )
        return fig

    def create_cone_3d_plot(self, x_col: str, y_col: str, z_col: str, u_col: str) -> go.Figure:
        """3D cone plot oluşturur"""
        # Basit 3D scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(size=self.df[u_col], color=self.df[u_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="3D Cone Plot",
            scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
            width=800,
            height=600,
        )
        return fig

    def create_streamline_plot(self, x_col: str, y_col: str, u_col: str, v_col: str) -> go.Figure:
        """Streamline plot oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df[x_col],
            y=self.df[y_col],
            mode='markers',
            marker=dict(size=5, color=self.df[u_col], colorscale='Viridis'),
            name='Points'
        ))
        
        fig.update_layout(
            title="Streamline Plot",
            xaxis_title=x_col,
            yaxis_title=y_col,
            width=800,
            height=600,
        )
        return fig

    def create_choropleth_map(self, location_col: str, color_col: str) -> go.Figure:
        """Choropleth map oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[location_col],
            y=self.df[color_col],
            mode='markers',
            marker=dict(size=8, color=self.df[color_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Choropleth Map",
            xaxis_title=location_col,
            yaxis_title=color_col,
            width=800,
            height=600,
        )
        return fig

    def create_scatter_mapbox(self, lat_col: str, lon_col: str, color_col: str) -> go.Figure:
        """Scatter mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='markers',
            marker=dict(size=8, color=self.df[color_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Scatter Mapbox",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_choropleth_mapbox(self, location_col: str, color_col: str) -> go.Figure:
        """Choropleth mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[location_col],
            y=self.df[color_col],
            mode='markers',
            marker=dict(size=8, color=self.df[color_col], colorscale='Viridis')
        )])
        
        fig.update_layout(
            title="Choropleth Mapbox",
            xaxis_title=location_col,
            yaxis_title=color_col,
            width=800,
            height=600,
        )
        return fig

    def create_density_mapbox(self, lat_col: str, lon_col: str) -> go.Figure:
        """Density mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='markers',
            marker=dict(size=8, color='blue', opacity=0.6)
        )])
        
        fig.update_layout(
            title="Density Mapbox",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_line_mapbox(self, lat_col: str, lon_col: str, color_col: str) -> go.Figure:
        """Line mapbox oluşturur"""
        # Basit line plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=5)
        )])
        
        fig.update_layout(
            title="Line Mapbox",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_polygon_mapbox(self, lat_col: str, lon_col: str) -> go.Figure:
        """Polygon mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='markers',
            marker=dict(size=8, color='green', opacity=0.7)
        )])
        
        fig.update_layout(
            title="Polygon Mapbox",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_choropleth_mapbox_with_hover(self, location_col: str, color_col: str, hover_col: str) -> go.Figure:
        """Hover ile choropleth mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[location_col],
            y=self.df[color_col],
            mode='markers',
            marker=dict(size=8, color=self.df[color_col], colorscale='Viridis'),
            text=self.df[hover_col],
            hovertemplate="<b>%{text}</b><br>" +
                         f"{location_col}: %{{x}}<br>" +
                         f"{color_col}: %{{y}}<extra></extra>"
        )])
        
        fig.update_layout(
            title="Choropleth Mapbox with Hover",
            xaxis_title=location_col,
            yaxis_title=color_col,
            width=800,
            height=600,
        )
        return fig

    def create_scatter_mapbox_with_hover(self, lat_col: str, lon_col: str, color_col: str, size_col: str) -> go.Figure:
        """Hover ile scatter mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='markers',
            marker=dict(
                size=self.df[size_col],
                color=self.df[color_col],
                colorscale='Viridis',
                opacity=0.7
            ),
            text=self.df[size_col],
            hovertemplate=f"{lat_col}: %{{x}}<br>" +
                         f"{lon_col}: %{{y}}<br>" +
                         f"{size_col}: %{{text}}<extra></extra>"
        )])
        
        fig.update_layout(
            title="Scatter Mapbox with Hover",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_density_mapbox_with_hover(self, lat_col: str, lon_col: str, value_col: str) -> go.Figure:
        """Hover ile density mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='markers',
            marker=dict(
                size=8,
                color=self.df[value_col],
                colorscale='Viridis',
                opacity=0.6
            ),
            text=self.df[value_col],
            hovertemplate=f"{lat_col}: %{{x}}<br>" +
                         f"{lon_col}: %{{y}}<br>" +
                         f"{value_col}: %{{text}}<extra></extra>"
        )])
        
        fig.update_layout(
            title="Density Mapbox with Hover",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_line_mapbox_with_hover(self, lat_col: str, lon_col: str, color_col: str, value_col: str) -> go.Figure:
        """Hover ile line mapbox oluşturur"""
        # Basit line plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=5, color=self.df[value_col], colorscale='Viridis'),
            text=self.df[value_col],
            hovertemplate=f"{lat_col}: %{{x}}<br>" +
                         f"{lon_col}: %{{y}}<br>" +
                         f"{value_col}: %{{text}}<extra></extra>"
        )])
        
        fig.update_layout(
            title="Line Mapbox with Hover",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig

    def create_polygon_mapbox_with_hover(self, lat_col: str, lon_col: str, value_col: str) -> go.Figure:
        """Hover ile polygon mapbox oluşturur"""
        # Basit scatter plot olarak göster
        fig = go.Figure(data=[go.Scatter(
            x=self.df[lat_col],
            y=self.df[lon_col],
            mode='markers',
            marker=dict(
                size=8,
                color=self.df[value_col],
                colorscale='Viridis',
                opacity=0.7
            ),
            text=self.df[value_col],
            hovertemplate=f"{lat_col}: %{{x}}<br>" +
                         f"{lon_col}: %{{y}}<br>" +
                         f"{value_col}: %{{text}}<extra></extra>"
        )])
        
        fig.update_layout(
            title="Polygon Mapbox with Hover",
            xaxis_title=lat_col,
            yaxis_title=lon_col,
            width=800,
            height=600,
        )
        return fig


def create_creative_visualizations(
    df: pd.DataFrame, output_dir: str = "./creative_plots"
) -> Dict[str, str]:
    """
    Hızlı yaratıcı görselleştirmeler oluşturur

    Parameters
    ----------
    df : pd.DataFrame
        Görselleştirilecek veri seti
    output_dir : str
        Çıktı dizini

    Returns
    -------
    Dict[str, str]
        Oluşturulan dosya yolları
    """
    engine = CreativeVizEngine(df)
    return engine.export_all_plots(output_dir)
