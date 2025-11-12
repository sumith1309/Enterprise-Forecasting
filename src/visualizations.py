"""
Visualization Module
Creates interactive and static visualizations for forecasting results
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


class ForecastVisualizer:
    """Creates beautiful visualizations for forecasting analysis"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#06A77D',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'info': '#6A4C93'
        }
    
    def plot_historical_data(self, df, date_col='Month', value_col='Sales'):
        """Plot historical sales data with trend"""
        
        fig = go.Figure()
        
        # Add actual sales line
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df[value_col],
            mode='lines+markers',
            name='Actual Sales',
            line=dict(color=self.color_palette['primary'], width=3),
            marker=dict(size=8)
        ))
        
        # Add trend line
        z = np.polyfit(range(len(df)), df[value_col], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=p(range(len(df))),
            mode='lines',
            name='Trend',
            line=dict(color=self.color_palette['warning'], width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Historical Sales Data',
            xaxis_title='Month',
            yaxis_title='Sales ($)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_actual_vs_predicted(self, actual, predictions_dict, dates=None):
        """Plot actual vs predicted values for multiple models"""
        
        fig = go.Figure()
        
        # Plot actual values
        x_axis = dates if dates is not None else list(range(len(actual)))
        
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=actual,
            mode='lines+markers',
            name='Actual',
            line=dict(color=self.color_palette['success'], width=4),
            marker=dict(size=12, symbol='circle')
        ))
        
        # Plot predictions for each model
        colors = [self.color_palette['primary'], self.color_palette['secondary'], 
                 self.color_palette['info'], self.color_palette['warning'], 
                 self.color_palette['danger']]
        
        for idx, (model_name, predictions) in enumerate(predictions_dict.items()):
            color = colors[idx % len(colors)]
            fig.add_trace(go.Scatter(
                x=x_axis,
                y=predictions,
                mode='lines+markers',
                name=model_name,
                line=dict(color=color, width=2, dash='dot'),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title='Actual vs Predicted Sales (Test Period)',
            xaxis_title='Month',
            yaxis_title='Sales ($)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def plot_model_performance(self, metrics_df):
        """Plot model performance metrics comparison"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('MAPE (%)', 'WAPE (%)', 'MAE ($)', 'RMSE ($)'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        colors = [self.color_palette['primary'], self.color_palette['secondary'],
                 self.color_palette['info'], self.color_palette['success'],
                 self.color_palette['warning']]
        
        # MAPE
        fig.add_trace(
            go.Bar(x=metrics_df['Model'], y=metrics_df['MAPE'],
                   marker_color=colors[:len(metrics_df)],
                   name='MAPE',
                   showlegend=False),
            row=1, col=1
        )
        
        # WAPE
        fig.add_trace(
            go.Bar(x=metrics_df['Model'], y=metrics_df['WAPE'],
                   marker_color=colors[:len(metrics_df)],
                   name='WAPE',
                   showlegend=False),
            row=1, col=2
        )
        
        # MAE
        fig.add_trace(
            go.Bar(x=metrics_df['Model'], y=metrics_df['MAE'],
                   marker_color=colors[:len(metrics_df)],
                   name='MAE',
                   showlegend=False),
            row=2, col=1
        )
        
        # RMSE
        fig.add_trace(
            go.Bar(x=metrics_df['Model'], y=metrics_df['RMSE'],
                   marker_color=colors[:len(metrics_df)],
                   name='RMSE',
                   showlegend=False),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text='Model Performance Comparison',
            height=600,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def plot_forecast(self, historical_df, forecast_df, 
                     hist_date_col='Month', hist_value_col='Sales',
                     forecast_date_col='Month', forecast_value_col='Predicted_Sales'):
        """Plot historical data with future forecast"""
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_df[hist_date_col],
            y=historical_df[hist_value_col],
            mode='lines+markers',
            name='Historical Sales',
            line=dict(color=self.color_palette['primary'], width=3),
            marker=dict(size=8)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df[forecast_date_col],
            y=forecast_df[forecast_value_col],
            mode='lines+markers',
            name='Forecast',
            line=dict(color=self.color_palette['success'], width=3, dash='dash'),
            marker=dict(size=10, symbol='diamond')
        ))
        
        # Add confidence interval (simplified)
        forecast_values = forecast_df[forecast_value_col].values
        std_dev = historical_df[hist_value_col].std()
        
        fig.add_trace(go.Scatter(
            x=forecast_df[forecast_date_col],
            y=forecast_values + 1.96 * std_dev,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df[forecast_date_col],
            y=forecast_values - 1.96 * std_dev,
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            name='95% Confidence Interval',
            fillcolor='rgba(46, 134, 171, 0.2)'
        ))
        
        fig.update_layout(
            title='Sales Forecast for Next 3 Months',
            xaxis_title='Month',
            yaxis_title='Sales ($)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_feature_importance(self, model, feature_names, top_n=10):
        """Plot feature importance for ML models"""
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Create dataframe
            importance_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            }).sort_values('Importance', ascending=False).head(top_n)
            
            fig = go.Figure(go.Bar(
                x=importance_df['Importance'],
                y=importance_df['Feature'],
                orientation='h',
                marker_color=self.color_palette['info']
            ))
            
            fig.update_layout(
                title=f'Top {top_n} Feature Importance',
                xaxis_title='Importance',
                yaxis_title='Feature',
                height=400,
                template='plotly_white'
            )
            
            return fig
        
        return None
    
    def plot_residuals(self, actual, predicted):
        """Plot residual analysis"""
        
        residuals = actual - predicted
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Residuals over Time', 'Residual Distribution')
        )
        
        # Residuals over time
        fig.add_trace(
            go.Scatter(
                x=list(range(len(residuals))),
                y=residuals,
                mode='markers',
                marker=dict(color=self.color_palette['secondary'], size=10),
                name='Residuals'
            ),
            row=1, col=1
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
        
        # Residual distribution
        fig.add_trace(
            go.Histogram(
                x=residuals,
                marker_color=self.color_palette['info'],
                name='Distribution',
                nbinsx=20
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text='Residual Analysis',
            height=400,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def create_metrics_table(self, metrics_df):
        """Create a styled metrics table"""
        
        # Highlight best model (lowest MAPE)
        best_idx = metrics_df['MAPE'].idxmin()
        
        colors = ['lightgreen' if i == best_idx else 'white' 
                 for i in range(len(metrics_df))]
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(metrics_df.columns),
                fill_color=self.color_palette['primary'],
                align='center',
                font=dict(color='white', size=14)
            ),
            cells=dict(
                values=[metrics_df[col] for col in metrics_df.columns],
                fill_color=[colors * len(metrics_df.columns)],
                align='center',
                font=dict(size=12),
                format=[None, '.2f', '.2f', '.2f', '.2f']
            )
        )])
        
        fig.update_layout(
            title='Model Performance Metrics',
            height=300,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def plot_seasonality_capture(self, df, predictions_dict, date_col='Month', value_col='Sales'):
        """
        Visualize how well models captured seasonality
        Shows seasonal decomposition and model fit
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Actual Sales with Seasonal Pattern', 
                          'Model Predictions vs Seasonal Trend'),
            row_heights=[0.5, 0.5],
            vertical_spacing=0.15
        )
        
        # Top plot: Actual sales with trend
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[value_col],
                mode='lines+markers',
                name='Actual Sales',
                line=dict(color=self.color_palette['primary'], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add polynomial trend line
        x_numeric = np.arange(len(df))
        z = np.polyfit(x_numeric, df[value_col], 2)
        p = np.poly1d(z)
        
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=p(x_numeric),
                mode='lines',
                name='Trend (Polynomial)',
                line=dict(color=self.color_palette['warning'], width=2, dash='dash')
            ),
            row=1, col=1
        )
        
        # Bottom plot: Seasonal component
        # Calculate moving average
        rolling_mean = df[value_col].rolling(window=3, center=True).mean()
        seasonal = df[value_col] - rolling_mean
        seasonal = seasonal.fillna(0)
        
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=seasonal,
                mode='lines+markers',
                name='Seasonal Component',
                line=dict(color=self.color_palette['success'], width=2),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        fig.update_xaxes(title_text="Month", row=2, col=1)
        fig.update_yaxes(title_text="Sales ($)", row=1, col=1)
        fig.update_yaxes(title_text="Seasonal Effect ($)", row=2, col=1)
        
        fig.update_layout(
            height=700,
            showlegend=True,
            template='plotly_white',
            title_text='Seasonality and Trend Analysis',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_model_comparison_radar(self, metrics_df):
        """
        Create radar chart comparing models across multiple metrics
        """
        # Normalize metrics (lower is better, so invert for visualization)
        metrics_normalized = metrics_df.copy()
        
        for col in ['MAPE', 'WAPE', 'MAE', 'RMSE']:
            max_val = metrics_normalized[col].max()
            # Invert so higher is better on radar chart
            metrics_normalized[col] = 100 * (1 - metrics_normalized[col] / max_val)
        
        fig = go.Figure()
        
        colors = [self.color_palette['primary'], self.color_palette['secondary'],
                 self.color_palette['info'], self.color_palette['success']]
        
        for idx, row in metrics_normalized.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['MAPE'], row['WAPE'], row['MAE'], row['RMSE']],
                theta=['MAPE', 'WAPE', 'MAE', 'RMSE'],
                fill='toself',
                name=row['Model'],
                line_color=colors[idx % len(colors)]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title='Model Performance Comparison (Higher = Better)',
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def plot_trend_capture_analysis(self, actual, predictions_dict, dates=None):
        """
        Analyze how well each model captured the underlying trend
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=list(predictions_dict.keys()),
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        x_axis = dates if dates is not None else list(range(len(actual)))
        colors = [self.color_palette['primary'], self.color_palette['secondary'],
                 self.color_palette['info'], self.color_palette['warning']]
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for idx, (model_name, predictions) in enumerate(predictions_dict.items()):
            row, col = positions[idx]
            color = colors[idx % len(colors)]
            
            # Actual
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=actual,
                    mode='lines+markers',
                    name='Actual',
                    line=dict(color='gray', width=2),
                    marker=dict(size=8),
                    showlegend=(idx == 0)
                ),
                row=row, col=col
            )
            
            # Predicted
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=predictions,
                    mode='lines+markers',
                    name=model_name,
                    line=dict(color=color, width=2, dash='dot'),
                    marker=dict(size=8),
                    showlegend=False
                ),
                row=row, col=col
            )
            
            # Calculate R² for this model
            ss_res = np.sum((actual - predictions) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            
            # Add R² annotation
            fig.add_annotation(
                text=f"R² = {r2:.3f}",
                xref=f"x{idx+1 if idx > 0 else ''}", yref=f"y{idx+1 if idx > 0 else ''}",
                x=x_axis[0], y=max(actual),
                showarrow=False,
                bgcolor=color,
                font=dict(color='white', size=10),
                row=row, col=col
            )
        
        fig.update_layout(
            height=600,
            title_text='Trend Capture Analysis by Model (R² Score)',
            showlegend=True,
            template='plotly_white'
        )
        
        return fig

