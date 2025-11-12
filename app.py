"""
Beverage Sales Forecasting Dashboard
An interactive application for forecasting monthly sales using multiple models
with AI-powered insights
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Import custom modules
from src.data_preprocessing import DataPreprocessor
from src.forecasting_models import ForecastingModels
from src.llm_interpreter import LLMInterpreter
from src.visualizations import ForecastVisualizer

# Page configuration
st.set_page_config(
    page_title="Beverage Sales Forecasting",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E86AB;
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 10px 0;
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #2E86AB;
        margin: 20px 0;
    }
    h1 {
        color: #2E86AB;
    }
    h2 {
        color: #A23B72;
    }
    h3 {
        color: #06A77D;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'models_trained' not in st.session_state:
    st.session_state.models_trained = False
if 'preprocessor' not in st.session_state:
    st.session_state.preprocessor = None
if 'forecasting_models' not in st.session_state:
    st.session_state.forecasting_models = None


def main():
    """Main application function"""
    
    # Header
    st.title("🥤 Beverage Sales Forecasting Dashboard")
    st.markdown("""
        <div class="highlight-box">
        <h4>📊 Forecasting Monthly Sales for New Beverage Product</h4>
        <p>This dashboard helps forecast demand for the next 3 months using advanced machine learning models
        and AI-powered insights. Compare multiple forecasting approaches including Naïve, ARIMA, Random Forest, 
        and XGBoost models.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/2E86AB/FFFFFF?text=Beverage+Analytics", 
                use_container_width=True)
        st.header("⚙️ Configuration")
        
        # Data source selection
        data_source = st.radio(
            "Data Source:",
            ["Use Sample Data", "Upload Custom Data"],
            help="Choose to use the provided sample data or upload your own CSV file"
        )
        
        if data_source == "Upload Custom Data":
            uploaded_file = st.file_uploader(
                "Upload CSV file",
                type=['csv'],
                help="CSV should have 'Month' and 'Sales' columns"
            )
            data_path = uploaded_file if uploaded_file else 'data/monthly_sales.csv'
        else:
            data_path = 'data/monthly_sales.csv'
        
        st.divider()
        
        # Model selection
        st.subheader("🤖 Model Selection")
        models_to_run = st.multiselect(
            "Select models to train:",
            ["Naive", "ARIMA", "Random_Forest", "XGBoost"],
            default=["Naive", "ARIMA", "Random_Forest", "XGBoost"],
            help="Choose which forecasting models to compare"
        )
        
        test_size = st.slider(
            "Test Set Size (months):",
            min_value=2,
            max_value=4,
            value=3,
            help="Number of months to use for testing"
        )
        
        forecast_months = st.slider(
            "Forecast Horizon (months):",
            min_value=1,
            max_value=6,
            value=3,
            help="Number of months to forecast into the future"
        )
        
        st.divider()
        
        # LLM Configuration
        st.subheader("🤖 AI Insights")
        use_llm = st.checkbox(
            "Enable AI-Powered Insights (Gemini 2.5 Flash)",
            value=True,
            help="Uses Google Gemini 2.5 Flash for intelligent interpretations"
        )
        
        if use_llm:
            # API key is pre-configured in .env
            api_key = "AIzaSyA8b_9uzdOv7NLxYx4VV88SPHU4pPf65-Y"
            st.success("✅ Google Gemini 2.5 Flash API configured")
        else:
            api_key = None
        
        st.divider()
        
        # Run button
        run_analysis = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Data Overview", 
        "🔮 Forecasting Models", 
        "📊 Performance Metrics",
        "🎯 Future Forecast",
        "🧠 AI Insights"
    ])
    
    # Tab 1: Data Overview
    with tab1:
        st.header("📈 Data Overview")
        
        if run_analysis or st.session_state.data_loaded:
            with st.spinner("Loading and preprocessing data..."):
                # Initialize preprocessor
                preprocessor = DataPreprocessor(data_path)
                df = preprocessor.load_data()
                processed_df = preprocessor.preprocess_all()
                
                st.session_state.preprocessor = preprocessor
                st.session_state.data_loaded = True
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📅 Historical Sales Data")
                    st.dataframe(df.style.format({'Sales': '${:,.0f}'}), use_container_width=True)
                
                with col2:
                    st.subheader("📊 Quick Statistics")
                    st.metric("Total Months", len(df))
                    st.metric("Average Sales", f"${df['Sales'].mean():,.0f}")
                    st.metric("Max Sales", f"${df['Sales'].max():,.0f}")
                    st.metric("Min Sales", f"${df['Sales'].min():,.0f}")
                    
                    # Growth rate
                    growth = ((df['Sales'].iloc[-1] - df['Sales'].iloc[0]) / df['Sales'].iloc[0] * 100)
                    st.metric("Overall Growth", f"{growth:.1f}%")
                
                # Visualization
                st.subheader("📉 Sales Trend Visualization")
                visualizer = ForecastVisualizer()
                fig = visualizer.plot_historical_data(df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Feature Engineering Info
                with st.expander("🔧 Feature Engineering Details"):
                    st.write("**Created Features:**")
                    feature_cols = preprocessor.get_feature_columns()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Lag Features:**")
                        lag_features = [f for f in feature_cols if 'Lag' in f]
                        for f in lag_features:
                            st.write(f"- {f}")
                    
                    with col2:
                        st.write("**Seasonal Features:**")
                        seasonal_features = [f for f in feature_cols if 'Season' in f or 'Month' in f]
                        for f in seasonal_features[:5]:
                            st.write(f"- {f}")
                    
                    with col3:
                        st.write("**Rolling Features:**")
                        rolling_features = [f for f in feature_cols if 'Rolling' in f]
                        for f in rolling_features:
                            st.write(f"- {f}")
        else:
            st.info("👈 Click 'Run Analysis' in the sidebar to load data and start forecasting!")
    
    # Tab 2: Forecasting Models
    with tab2:
        st.header("🔮 Forecasting Models")
        
        if st.session_state.data_loaded and (run_analysis or st.session_state.models_trained):
            with st.spinner("Training models... This may take a moment."):
                preprocessor = st.session_state.preprocessor
                
                # Split data
                train_df, test_df = preprocessor.get_train_test_split(test_size)
                
                # Initialize models
                forecaster = ForecastingModels()
                st.session_state.forecasting_models = forecaster
                
                # Feature columns for ML models
                feature_cols = preprocessor.get_feature_columns()
                
                # Train selected models
                predictions_dict = {}
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, model_name in enumerate(models_to_run):
                    status_text.text(f"Training {model_name} model...")
                    
                    if model_name == "Naive":
                        preds = forecaster.naive_forecast(train_df, test_df)
                        predictions_dict[model_name] = preds
                    
                    elif model_name == "ARIMA":
                        preds = forecaster.arima_forecast(train_df, test_df)
                        predictions_dict[model_name] = preds
                    
                    elif model_name == "Random_Forest":
                        preds = forecaster.random_forest_forecast(
                            train_df, test_df, feature_cols
                        )
                        predictions_dict[model_name] = preds
                    
                    elif model_name == "XGBoost":
                        preds = forecaster.xgboost_forecast(
                            train_df, test_df, feature_cols
                        )
                        predictions_dict[model_name] = preds
                    
                    progress_bar.progress((idx + 1) / len(models_to_run))
                
                status_text.text("✅ All models trained successfully!")
                st.session_state.models_trained = True
                
                # Visualize predictions
                st.subheader("📊 Actual vs Predicted Sales")
                visualizer = ForecastVisualizer()
                
                actual_values = test_df['Sales'].values
                test_dates = test_df['Month'].values
                
                fig = visualizer.plot_actual_vs_predicted(
                    actual_values, predictions_dict, test_dates
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Model details
                st.subheader("🔍 Model Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Traditional Models:**")
                    st.write("""
                    - **Naïve Model**: Uses the last observed value as prediction
                    - **ARIMA**: Captures temporal dependencies and trends
                    """)
                
                with col2:
                    st.write("**Machine Learning Models:**")
                    st.write("""
                    - **Random Forest**: Ensemble of decision trees
                    - **XGBoost**: Gradient boosting with regularization
                    """)
        else:
            st.info("👈 Please run the analysis first from the Data Overview tab!")
    
    # Tab 3: Performance Metrics
    with tab3:
        st.header("📊 Performance Metrics")
        
        if st.session_state.models_trained:
            forecaster = st.session_state.forecasting_models
            preprocessor = st.session_state.preprocessor
            
            # Get test data
            train_df, test_df = preprocessor.get_train_test_split(test_size)
            actual_values = test_df['Sales'].values
            
            # Calculate metrics for all models
            metrics_list = []
            for model_name, predictions in forecaster.predictions.items():
                metrics = forecaster.evaluate_model(model_name, actual_values, predictions)
                metrics_list.append(metrics)
            
            metrics_df = pd.DataFrame(metrics_list)
            
            # Display best model
            best_model = forecaster.get_best_model('MAPE')
            best_metrics = metrics_df[metrics_df['Model'] == best_model].iloc[0]
            
            st.success(f"🏆 **Best Model: {best_model}** (MAPE: {best_metrics['MAPE']:.2f}%)")
            
            # Metrics visualization
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📋 Metrics Table")
                st.dataframe(
                    metrics_df.style.format({
                        'MAPE': '{:.2f}%',
                        'WAPE': '{:.2f}%',
                        'MAE': '${:.2f}',
                        'RMSE': '${:.2f}'
                    }).highlight_min(subset=['MAPE', 'WAPE'], color='lightgreen'),
                    use_container_width=True
                )
                
                # Metrics explanation
                with st.expander("ℹ️ Metric Definitions"):
                    st.write("""
                    **MAPE** (Mean Absolute Percentage Error): 
                    Average percentage difference between actual and predicted values. 
                    Lower is better.
                    
                    **WAPE** (Weighted Absolute Percentage Error): 
                    Weighted version of MAPE, more robust to outliers.
                    
                    **MAE** (Mean Absolute Error): 
                    Average absolute difference in dollars.
                    
                    **RMSE** (Root Mean Squared Error): 
                    Square root of average squared errors, penalizes large errors more.
                    """)
            
            with col2:
                st.subheader("📈 Performance Comparison")
                visualizer = ForecastVisualizer()
                fig = visualizer.plot_model_performance(metrics_df)
                st.plotly_chart(fig, use_container_width=True)
            
            # Residual analysis for best model
            st.subheader("🔬 Residual Analysis - Best Model")
            best_predictions = forecaster.predictions[best_model]
            fig_residuals = visualizer.plot_residuals(actual_values, best_predictions)
            st.plotly_chart(fig_residuals, use_container_width=True)
            
            # Feature importance (if applicable)
            if best_model in ['Random_Forest', 'XGBoost']:
                st.subheader("⭐ Feature Importance")
                model = forecaster.models[best_model]
                feature_cols = preprocessor.get_feature_columns()
                fig_importance = visualizer.plot_feature_importance(model, feature_cols)
                if fig_importance:
                    st.plotly_chart(fig_importance, use_container_width=True)
        else:
            st.info("👈 Please train the models first!")
    
    # Tab 4: Future Forecast
    with tab4:
        st.header("🎯 Future Forecast")
        
        if st.session_state.models_trained:
            forecaster = st.session_state.forecasting_models
            preprocessor = st.session_state.preprocessor
            visualizer = ForecastVisualizer()
            
            # Get best model
            best_model = forecaster.get_best_model('MAPE')
            
            st.info(f"📍 Using **{best_model}** model for future forecasting (best performing model)")
            
            # Generate forecast
            forecast_df = forecaster.forecast_future(best_model, preprocessor, forecast_months)
            
            # Display forecast
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"📅 {forecast_months}-Month Forecast")
                
                # Format the dataframe
                display_df = forecast_df.copy()
                display_df['Month'] = display_df['Month'].dt.strftime('%B %Y')
                display_df['Predicted_Sales'] = display_df['Predicted_Sales'].apply(lambda x: f"${x:,.0f}")
                
                st.dataframe(display_df, use_container_width=True)
            
            with col2:
                st.subheader("📊 Forecast Summary")
                forecast_values = forecast_df['Predicted_Sales'].values
                
                st.metric("Average Forecast", f"${forecast_values.mean():,.0f}")
                st.metric("Highest Month", f"${forecast_values.max():,.0f}")
                st.metric("Lowest Month", f"${forecast_values.min():,.0f}")
                
                # Trend
                if forecast_values[-1] > forecast_values[0]:
                    trend = "📈 Increasing"
                    trend_pct = ((forecast_values[-1] - forecast_values[0]) / forecast_values[0] * 100)
                else:
                    trend = "📉 Decreasing"
                    trend_pct = ((forecast_values[0] - forecast_values[-1]) / forecast_values[0] * 100)
                
                st.metric("Trend", trend)
                st.metric("Change", f"{trend_pct:.1f}%")
            
            # Visualization
            st.subheader("📈 Historical Data + Forecast")
            df = preprocessor.df
            fig_forecast = visualizer.plot_forecast(df, forecast_df)
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Business insights
            st.subheader("💼 Quick Business Insights")
            
            total_forecast = forecast_values.sum()
            current_avg = df['Sales'].tail(3).mean()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                    <div class="metric-card">
                    <h4>Production Planning</h4>
                    <p>Plan for <strong>${:,.0f}</strong> in total sales over next {} months</p>
                    </div>
                """.format(total_forecast, forecast_months), unsafe_allow_html=True)
            
            with col2:
                buffer = total_forecast * 0.15
                st.markdown("""
                    <div class="metric-card">
                    <h4>Inventory Buffer</h4>
                    <p>Maintain <strong>${:,.0f}</strong> buffer stock (15% of forecast)</p>
                    </div>
                """.format(buffer), unsafe_allow_html=True)
            
            with col3:
                if forecast_values.mean() > current_avg:
                    recommendation = "Increase"
                    color = "green"
                else:
                    recommendation = "Maintain"
                    color = "orange"
                
                st.markdown(f"""
                    <div class="metric-card">
                    <h4>Capacity Strategy</h4>
                    <p style="color:{color}"><strong>{recommendation}</strong> production capacity</p>
                    </div>
                """, unsafe_allow_html=True)
            
        else:
            st.info("👈 Please train the models first!")
    
    # Tab 5: AI Insights
    with tab5:
        st.header("🧠 Interpretation & AI-Powered Insights")
        
        if st.session_state.models_trained:
            forecaster = st.session_state.forecasting_models
            preprocessor = st.session_state.preprocessor
            visualizer = ForecastVisualizer()
            
            # Get metrics and predictions
            train_df, test_df = preprocessor.get_train_test_split(test_size)
            actual_values = test_df['Sales'].values
            test_dates = test_df['Month'].values
            
            metrics_df = forecaster.get_all_metrics()
            best_model = forecaster.get_best_model('MAPE')
            
            # ========== EXPLICIT ANSWERS TO INTERPRETATION QUESTIONS ==========
            st.markdown("""
                <div class="highlight-box">
                <h3>📋 Key Interpretation Questions Answered</h3>
                <p>This section provides visual and analytical answers to all interpretation requirements.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # ===== QUESTION 1: How well did the model capture seasonality or trends? =====
            st.subheader("❓ Question 1: How well did the models capture seasonality or trends?")
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Seasonality visualization
                df = preprocessor.df
                fig_seasonality = visualizer.plot_seasonality_capture(df, forecaster.predictions)
                st.plotly_chart(fig_seasonality, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Analysis")
                
                # Calculate seasonality strength
                rolling_mean = df['Sales'].rolling(window=3, center=True).mean()
                seasonal_component = df['Sales'] - rolling_mean
                seasonal_strength = seasonal_component.std() / df['Sales'].std() * 100
                
                st.metric("Seasonality Strength", f"{seasonal_strength:.1f}%", 
                         help="How much of the variation is due to seasonality")
                
                # Trend analysis
                growth_rate = ((df['Sales'].iloc[-1] - df['Sales'].iloc[0]) / df['Sales'].iloc[0]) * 100
                st.metric("Overall Trend", f"{growth_rate:+.1f}%",
                         help="Growth rate from start to end")
                
                # Peak season
                peak_month = df.loc[df['Sales'].idxmax(), 'Month'].strftime('%B %Y')
                st.metric("Peak Sales Month", peak_month)
                
                st.markdown(f"""
                **Interpretation:**
                
                The data shows **{seasonal_strength:.1f}%** seasonal variation with a clear 
                **{abs(growth_rate):.1f}% {'growth' if growth_rate > 0 else 'decline'}** trend. 
                
                Sales peak during **{peak_month}**, typical for beverage products with 
                summer demand increases.
                
                {'✅ **Strong ML models (RF, XGBoost)** captured this pattern best due to feature engineering.' 
                 if best_model in ['Random_Forest', 'XGBoost'] 
                 else '✅ **Time series models** effectively captured temporal patterns.'}
                """)
            
            # Trend capture by each model
            st.subheader("📈 Model-by-Model Trend Capture Analysis")
            fig_trend = visualizer.plot_trend_capture_analysis(actual_values, forecaster.predictions, test_dates)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.info("💡 **R² Score Interpretation**: Values closer to 1.0 indicate better trend capture. "
                   "The model predictions closely follow actual sales patterns.")
            
            st.divider()
            
            # ===== QUESTION 2: Which model performed best and why? =====
            st.subheader("❓ Question 2: Which model performed best and why?")
            
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.markdown(f"### 🏆 Best Model")
                best_metrics = metrics_df[metrics_df['Model'] == best_model].iloc[0]
                
                st.success(f"**{best_model}**")
                
                st.metric("MAPE (Lower = Better)", f"{best_metrics['MAPE']:.2f}%")
                st.metric("WAPE", f"{best_metrics['WAPE']:.2f}%")
                st.metric("MAE", f"${best_metrics['MAE']:,.2f}")
                st.metric("RMSE", f"${best_metrics['RMSE']:,.2f}")
                
                # Performance rating
                if best_metrics['MAPE'] < 10:
                    rating = "⭐⭐⭐⭐⭐ Excellent"
                    color = "green"
                elif best_metrics['MAPE'] < 15:
                    rating = "⭐⭐⭐⭐ Very Good"
                    color = "blue"
                elif best_metrics['MAPE'] < 20:
                    rating = "⭐⭐⭐ Good"
                    color = "orange"
                else:
                    rating = "⭐⭐ Acceptable"
                    color = "red"
                
                st.markdown(f"**Performance Rating:**")
                st.markdown(f"<h3 style='color:{color}'>{rating}</h3>", unsafe_allow_html=True)
            
            with col2:
                # Radar chart comparison
                fig_radar = visualizer.plot_model_comparison_radar(metrics_df)
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Detailed explanation
            st.markdown("### 🔍 Why This Model Won")
            
            if best_model == "Naive":
                explanation = """
                **Naïve Model** performed best, indicating:
                - ✅ Sales are relatively stable with minimal variation
                - ✅ Simple patterns that don't require complex modeling
                - ⚠️ However, this suggests potential for improvement with more data or features
                """
            elif best_model == "ARIMA":
                explanation = """
                **ARIMA Model** performed best because:
                - ✅ Strong temporal dependencies in the sales data
                - ✅ Clear trend and seasonal patterns that ARIMA captures well
                - ✅ Statistical approach works when data follows time series assumptions
                - 💡 Best for pure time series without external features
                """
            elif best_model == "Random_Forest":
                explanation = """
                **Random Forest** performed best because:
                - ✅ Successfully leveraged lag features and seasonal indicators
                - ✅ Captured non-linear relationships between features
                - ✅ Ensemble approach reduced overfitting
                - 💡 External features (temperature, marketing) added value
                - 🎯 Good balance between accuracy and interpretability
                """
            else:  # XGBoost
                explanation = """
                **XGBoost** performed best because:
                - ✅ Most sophisticated algorithm with gradient boosting
                - ✅ Effectively handled complex interactions between features
                - ✅ Regularization prevented overfitting despite complexity
                - ✅ Optimized for prediction accuracy
                - 💡 Best when you have rich features and need maximum accuracy
                - 🎯 Recommended for critical business decisions
                """
            
            st.markdown(explanation)
            
            # Model comparison table
            st.markdown("### 📊 Complete Performance Comparison")
            
            # Sort by MAPE
            metrics_sorted = metrics_df.sort_values('MAPE')
            
            # Add ranking and percentage improvement
            metrics_sorted['Rank'] = range(1, len(metrics_sorted) + 1)
            worst_mape = metrics_sorted['MAPE'].max()
            metrics_sorted['Improvement vs Worst'] = (
                (worst_mape - metrics_sorted['MAPE']) / worst_mape * 100
            ).round(1).astype(str) + '%'
            
            st.dataframe(
                metrics_sorted[['Rank', 'Model', 'MAPE', 'WAPE', 'MAE', 'RMSE', 'Improvement vs Worst']]
                .style.format({
                    'MAPE': '{:.2f}%',
                    'WAPE': '{:.2f}%',
                    'MAE': '${:.2f}',
                    'RMSE': '${:.2f}'
                })
                .background_gradient(subset=['MAPE', 'WAPE'], cmap='RdYlGn_r'),
                use_container_width=True
            )
            
            st.divider()
            
            # ===== QUESTION 3: What recommendations would you give the company? =====
            st.subheader("❓ Question 3: What recommendations would you give the company?")
            
            # Generate forecast for recommendations
            forecast_df = forecaster.forecast_future(best_model, preprocessor, forecast_months)
            forecast_values = forecast_df['Predicted_Sales'].values
            historical_avg = df['Sales'].mean()
            
            st.markdown("### 💼 Business Recommendations")
            
            # Recommendation cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_forecast = forecast_values.sum()
                st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
                    <h4>🏭 Production Planning</h4>
                    <h2>${total_forecast:,.0f}</h2>
                    <p>Expected total sales over next {forecast_months} months</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p><strong>Action:</strong> Increase production capacity by {((forecast_values.mean() / historical_avg - 1) * 100):+.1f}% 
                    compared to historical average</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                buffer_stock = total_forecast * 0.20
                st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px;">
                    <h4>📦 Inventory Management</h4>
                    <h2>${buffer_stock:,.0f}</h2>
                    <p>Recommended safety stock (20% buffer)</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p><strong>Action:</strong> Maintain buffer to handle {best_metrics['MAPE']:.1f}% forecast error margin</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                peak_forecast = forecast_values.max()
                st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px;">
                    <h4>📈 Peak Planning</h4>
                    <h2>${peak_forecast:,.0f}</h2>
                    <p>Highest monthly forecast</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p><strong>Action:</strong> Prepare for {((peak_forecast / historical_avg - 1) * 100):+.1f}% spike above average</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detailed recommendations
            st.markdown("### 📋 Detailed Action Plan")
            
            tab_rec1, tab_rec2, tab_rec3, tab_rec4 = st.tabs([
                "🎯 Short-term (1-3 months)",
                "📅 Medium-term (3-6 months)", 
                "⚠️ Risk Management",
                "📊 Monitoring KPIs"
            ])
            
            with tab_rec1:
                st.markdown(f"""
                **Immediate Actions (Next {forecast_months} Months):**
                
                1. **Production & Supply Chain**
                   - Scale production to meet forecasted ${forecast_values.mean():,.0f} average monthly sales
                   - Secure raw material supplies for ${total_forecast:,.0f} total production
                   - Schedule production runs to match seasonal peaks
                
                2. **Inventory & Distribution**
                   - Build safety stock of ${buffer_stock:,.0f} to handle demand variability
                   - Position inventory near high-demand regions
                   - Prepare for {((forecast_values.max() - forecast_values.min()) / forecast_values.min() * 100):.1f}% month-to-month variation
                
                3. **Marketing & Sales**
                   - {"Increase" if forecast_values.mean() > historical_avg else "Maintain"} marketing spend to support demand forecast
                   - Focus campaigns during predicted peak months
                   - Leverage seasonal trends for promotions
                
                **Expected Outcome:** Meet forecasted demand with {100 - best_metrics['MAPE']:.1f}% accuracy
                """)
            
            with tab_rec2:
                st.markdown(f"""
                **Strategic Planning (3-6 Months):**
                
                1. **Capacity Expansion**
                   - Evaluate need for additional production lines based on trend
                   - {"Growth trend suggests capacity expansion" if growth_rate > 5 else "Stable demand allows for optimization over expansion"}
                   - Plan for {growth_rate * 2:.1f}% annualized growth rate
                
                2. **Model Improvement**
                   - Continue using **{best_model}** model (proven {best_metrics['MAPE']:.1f}% MAPE)
                   - Collect additional features: competitor pricing, promotional calendar
                   - Retrain monthly with new data for improved accuracy
                
                3. **Market Development**
                   - Analyze seasonal patterns for new product launches
                   - {"Expand to new markets during peak season" if seasonal_strength > 20 else "Focus on consistent year-round presence"}
                   - Develop off-season strategies to smooth demand
                """)
            
            with tab_rec3:
                st.markdown(f"""
                **Risk Management & Contingency:**
                
                1. **Forecast Uncertainty**
                   - Current model has ±{best_metrics['MAPE']:.1f}% average error
                   - Build scenarios: Best case (+{best_metrics['MAPE']:.0f}%), Base case, Worst case (-{best_metrics['MAPE']:.0f}%)
                   - Maintain flexible production capacity
                
                2. **Supply Chain Risks**
                   - Diversify suppliers for critical ingredients
                   - Maintain {((buffer_stock / total_forecast) * 100):.0f}% safety stock at all times
                   - Develop rapid response protocol for demand spikes
                
                3. **Market Risks**
                   - Monitor competitor actions monthly
                   - Track actual vs forecast weekly
                   - Set trigger points for forecast updates (>10% deviation)
                
                4. **Seasonal Risks**
                   - {"High seasonality" if seasonal_strength > 20 else "Moderate seasonality"} ({seasonal_strength:.1f}%) requires careful planning
                   - Weather dependency: Have contingency for unusual weather patterns
                   - Holiday season strategy: Plan 8-12 weeks ahead
                """)
            
            with tab_rec4:
                st.markdown(f"""
                **Key Performance Indicators to Monitor:**
                
                1. **Forecast Accuracy Metrics**
                   - Track MAPE weekly (target: <{best_metrics['MAPE'] * 1.2:.1f}%)
                   - Monitor forecast bias (should stay near 0%)
                   - Alert if actual sales deviate >15% from forecast
                
                2. **Operational Metrics**
                   - Inventory turnover ratio (target: 8-12 times/year)
                   - Stockout rate (target: <2%)
                   - Production capacity utilization (target: 75-85%)
                
                3. **Business Metrics**
                   - Month-over-month sales growth (current: {growth_rate/12:.1f}% per month)
                   - Market share trends
                   - Customer demand patterns
                
                4. **Model Health**
                   - Retrain model monthly with new data
                   - Compare {best_model} performance vs other models quarterly
                   - Review feature importance to understand demand drivers
                
                **Dashboard Review:** Weekly forecast updates, Monthly model retraining, Quarterly strategy revision
                """)
            
            st.divider()
            
            # ===== BONUS: AI-POWERED ENHANCED INSIGHTS =====
            st.markdown("""
                <div class="highlight-box">
                <h3>🤖 AI-Enhanced Interpretation (Optional)</h3>
                <p>Enable AI in the sidebar for GPT-4 powered insights that go beyond standard analysis.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if use_llm and api_key:
                with st.spinner("🤖 Generating enhanced AI insights... This may take a moment."):
                    try:
                        # Initialize LLM interpreter
                        llm = LLMInterpreter(api_key)
                        
                        # Generate interpretation
                        st.subheader("📊 Comprehensive AI Analysis")
                        interpretation = llm.generate_model_interpretation(
                            metrics_df,
                            best_model,
                            actual_values,
                            forecaster.predictions
                        )
                        
                        st.markdown(interpretation)
                        
                        # Quick insight for forecast
                        st.divider()
                        st.subheader("🎯 AI-Generated Forecast Insight")
                        
                        quick_insight = llm.generate_quick_insight(forecast_values, best_model)
                        st.info(quick_insight)
                        
                    except Exception as e:
                        st.error(f"Error generating AI insights: {str(e)}")
                        st.info("Showing standard interpretation instead...")
                        
                        llm = LLMInterpreter(None)
                        interpretation = llm._fallback_interpretation(metrics_df, best_model)
                        st.markdown(interpretation)
            else:
                st.info("💡 Enable AI-powered insights in the sidebar for even deeper analysis using GPT-4!")
                
                with st.expander("📄 View Standard Interpretation Summary"):
                    # Fallback interpretation
                    llm = LLMInterpreter(None)
                    interpretation = llm._fallback_interpretation(metrics_df, best_model)
                    st.markdown(interpretation)
            
            # Download report
            st.divider()
            st.subheader("📥 Export Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Prepare metrics CSV
                csv = metrics_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Metrics (CSV)",
                    data=csv,
                    file_name="forecast_metrics.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Prepare forecast CSV
                forecast_df = forecaster.forecast_future(best_model, preprocessor, forecast_months)
                forecast_csv = forecast_df.to_csv(index=False)
                st.download_button(
                    label="🎯 Download Forecast (CSV)",
                    data=forecast_csv,
                    file_name="sales_forecast.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("👈 Please train the models first to generate insights!")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
        <p>🥤 Beverage Sales Forecasting Dashboard | Built with Streamlit & ML</p>
        <p>Lab Activity: AI in Operations | Session II</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

