"""
Flask Backend for Enterprise Beverage Sales Forecasting Dashboard
Corporate-Level Features with Advanced Analytics
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
import os
import pandas as pd
import numpy as np
import json
from io import StringIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_preprocessing import DataPreprocessor
from src.forecasting_models import ForecastingModels
from src.llm_interpreter import LLMInterpreter

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Helper function to clean LLM text output
def clean_llm_text(text):
    """Clean and format LLM-generated text by removing unwanted characters and formatting"""
    if not text:
        return text
    
    import re
    
    # Remove markdown code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Remove excessive asterisks (markdown bold/italic artifacts)
    text = re.sub(r'\*{3,}', '', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove special characters that might cause display issues
    text = text.replace('**', '')  # Remove markdown bold
    text = text.replace('*', '')    # Remove markdown italic
    text = text.replace('`', '')    # Remove markdown code
    
    # Clean up whitespace
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    return text

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables
preprocessor = None
forecaster = None
models_trained = False
current_data_path = 'data/monthly_sales.csv'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Handle CSV file upload"""
    global current_data_path, preprocessor, models_trained, forecaster
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Validate CSV
            try:
                df = pd.read_csv(filepath)
                
                # Try to parse Month column
                df['Month'] = pd.to_datetime(df['Month'], errors='coerce')
                
                # Check required columns
                if 'Month' not in df.columns or 'Sales' not in df.columns:
                    os.remove(filepath)
                    return jsonify({
                        'success': False,
                        'message': 'CSV must contain "Month" and "Sales" columns'
                    }), 400
                
                # Check for valid data
                if df['Month'].isnull().any():
                    os.remove(filepath)
                    return jsonify({
                        'success': False,
                        'message': 'Month column contains invalid dates. Use YYYY-MM format.'
                    }), 400
                
                # Update current data path
                current_data_path = filepath
                models_trained = False
                preprocessor = None
                forecaster = None
                
                return jsonify({
                    'success': True,
                    'message': f'File uploaded successfully: {filename}',
                    'rows': len(df),
                    'columns': list(df.columns)
                })
                
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'success': False, 'message': f'Invalid CSV: {str(e)}'}), 400
        
        return jsonify({'success': False, 'message': 'Invalid file type. Only CSV allowed'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/load-data', methods=['GET'])
def load_data():
    """Load and preprocess the sales data"""
    global preprocessor, current_data_path
    
    try:
        preprocessor = DataPreprocessor(current_data_path)
        df = preprocessor.load_data()
        processed_df = preprocessor.preprocess_all()
        
        # Calculate statistics
        stats = {
            'total_months': len(df),
            'avg_sales': float(df['Sales'].mean()),
            'max_sales': float(df['Sales'].max()),
            'min_sales': float(df['Sales'].min()),
            'growth_rate': float(((df['Sales'].iloc[-1] - df['Sales'].iloc[0]) / df['Sales'].iloc[0]) * 100),
            'std_sales': float(df['Sales'].std()),
            'median_sales': float(df['Sales'].median()),
            'start_date': df['Month'].min().strftime('%Y-%m-%d'),
            'end_date': df['Month'].max().strftime('%Y-%m-%d')
        }
        
        # Prepare data for charts
        historical_data = {
            'dates': df['Month'].dt.strftime('%Y-%m').tolist(),
            'sales': df['Sales'].tolist()
        }
        
        # Get feature information
        feature_cols = preprocessor.get_feature_columns()
        lag_features = [f for f in feature_cols if 'Lag' in f]
        seasonal_features = [f for f in feature_cols if any(x in f for x in ['Season', 'Month', 'Quarter'])]
        rolling_features = [f for f in feature_cols if 'Rolling' in f or 'MA' in f]
        
        # Data quality metrics
        quality_metrics = {
            'missing_values': int(df.isnull().sum().sum()),
            'outliers': int(((df['Sales'] - df['Sales'].mean()).abs() > 3 * df['Sales'].std()).sum()),
            'data_completeness': float((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
        }
        
        return jsonify({
            'success': True,
            'stats': stats,
            'historical_data': historical_data,
            'features': {
                'lag_features': lag_features,
                'seasonal_features': seasonal_features,
                'rolling_features': rolling_features
            },
            'quality': quality_metrics
        })
    
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/train-single-model', methods=['POST'])
def train_single_model():
    """Train a single model with custom parameters"""
    global forecaster
    
    try:
        data = request.json
        model_name = data.get('model')
        test_size = data.get('test_size', 3)
        
        print(f"[DEBUG] Received model_name: '{model_name}' (type: {type(model_name)})")
        print(f"[DEBUG] Request data: {data}")
        
        # Model-specific parameters
        params = data.get('parameters', {})
        
        if not preprocessor:
            return jsonify({'success': False, 'message': 'Data not loaded'}), 400
        
        # Split data
        train_df, test_df = preprocessor.get_train_test_split(test_size)
        
        # Initialize or reuse forecaster
        if not forecaster:
            forecaster = ForecastingModels()
        
        # Get feature columns
        feature_cols = preprocessor.get_feature_columns()
        
        # Train selected model
        if model_name == "Naive":
            preds = forecaster.naive_forecast(train_df, test_df)
        
        elif model_name == "ARIMA":
            order = params.get('order', (1, 1, 1))
            preds = forecaster.arima_forecast(train_df, test_df, order=order)
        
        elif model_name == "Random_Forest":
            n_estimators = params.get('n_estimators', 100)
            max_depth = params.get('max_depth', 10)
            # Update model parameters
            from sklearn.ensemble import RandomForestRegressor
            X_train = train_df[feature_cols].fillna(0)
            y_train = train_df['Sales']
            X_test = test_df[feature_cols].fillna(0)
            
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42
            )
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            forecaster.models['Random_Forest'] = model
        
        elif model_name == "XGBoost":
            n_estimators = params.get('n_estimators', 100)
            learning_rate = params.get('learning_rate', 0.1)
            max_depth = params.get('max_depth', 5)
            
            import xgboost as xgb
            X_train = train_df[feature_cols].fillna(0)
            y_train = train_df['Sales']
            X_test = test_df[feature_cols].fillna(0)
            
            model = xgb.XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                random_state=42
            )
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            forecaster.models['XGBoost'] = model
        
        else:
            print(f"[ERROR] Invalid model name received: '{model_name}'")
            print(f"[ERROR] Valid model names are: Naive, ARIMA, Random_Forest, XGBoost")
            return jsonify({
                'success': False, 
                'message': f'Invalid model name: "{model_name}". Valid names: Naive, ARIMA, Random_Forest, XGBoost'
            }), 400
        
        # Calculate metrics
        actual_values = test_df['Sales'].values
        metrics = forecaster.evaluate_model(model_name, actual_values, preds)
        
        # Add R² Score
        from sklearn.metrics import r2_score
        metrics['R2_Score'] = float(r2_score(actual_values, preds))
        
        # Calculate additional metrics
        residuals = actual_values - preds
        metrics['mean_residual'] = float(np.mean(residuals))
        metrics['residual_std'] = float(np.std(residuals))
        
        forecaster.predictions[model_name] = preds
        
        print(f"[DEBUG] Model {model_name} trained successfully. MAPE: {metrics['MAPE']:.2f}%")
        
        return jsonify({
            'success': True,
            'model': model_name,
            'predictions': preds.tolist(),
            'actual': actual_values.tolist(),
            'test_dates': test_df['Month'].dt.strftime('%Y-%m').tolist(),
            'metrics': metrics,
            'residuals': residuals.tolist()
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Exception in train_single_model: {str(e)}")
        print(f"[ERROR] Traceback:\n{error_trace}")
        return jsonify({
            'success': False, 
            'message': f'Training error: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/train-models', methods=['POST'])
def train_models():
    """Train multiple forecasting models"""
    global forecaster, models_trained
    
    try:
        data = request.json
        selected_models = data.get('models', ['Naive', 'ARIMA', 'Random_Forest', 'XGBoost'])
        test_size = data.get('test_size', 3)
        
        if not preprocessor:
            return jsonify({'success': False, 'message': 'Data not loaded. Please load data first.'}), 400
        
        # Split data
        train_df, test_df = preprocessor.get_train_test_split(test_size)
        
        # Initialize forecaster
        forecaster = ForecastingModels()
        
        # Get feature columns
        feature_cols = preprocessor.get_feature_columns()
        
        # Train selected models
        predictions_dict = {}
        
        for model_name in selected_models:
            try:
                if model_name == "Naive":
                    preds = forecaster.naive_forecast(train_df, test_df)
                    predictions_dict[model_name] = preds.tolist()
                
                elif model_name == "ARIMA":
                    preds = forecaster.arima_forecast(train_df, test_df)
                    predictions_dict[model_name] = preds.tolist()
                
                elif model_name == "Random_Forest":
                    preds = forecaster.random_forest_forecast(train_df, test_df, feature_cols)
                    predictions_dict[model_name] = preds.tolist()
                
                elif model_name == "XGBoost":
                    preds = forecaster.xgboost_forecast(train_df, test_df, feature_cols)
                    predictions_dict[model_name] = preds.tolist()
            except Exception as model_error:
                print(f"Error training {model_name}: {str(model_error)}")
                # Continue with other models
                continue
        
        if not predictions_dict:
            return jsonify({'success': False, 'message': 'No models were trained successfully'}), 500
        
        # Calculate metrics
        actual_values = test_df['Sales'].values
        metrics_list = []
        
        for model_name in predictions_dict.keys():
            preds = np.array(predictions_dict[model_name])
            metrics = forecaster.evaluate_model(model_name, actual_values, preds)
            metrics_list.append(metrics)
        
        metrics_df = pd.DataFrame(metrics_list)
        best_model = forecaster.get_best_model('MAPE')
        
        models_trained = True
        
        return jsonify({
            'success': True,
            'predictions': predictions_dict,
            'actual': actual_values.tolist(),
            'test_dates': test_df['Month'].dt.strftime('%Y-%m').tolist(),
            'metrics': metrics_df.to_dict('records'),
            'best_model': best_model
        })
    
    except Exception as e:
        print(f"Error in train_models: {str(e)}")
        return jsonify({'success': False, 'message': f'Training failed: {str(e)}'}), 500

@app.route('/api/generate-forecast', methods=['POST'])
def generate_forecast():
    """Generate future forecast"""
    try:
        data = request.json
        months = data.get('months', 3)
        model_name = data.get('model_name', None)
        
        if not models_trained:
            return jsonify({'success': False, 'message': 'Please run comprehensive analysis first to train models'}), 400
        
        # Handle "best" model selection
        if not model_name or model_name == 'best':
            model_name = forecaster.get_best_model('MAPE')
        
        forecast_df = forecaster.forecast_future(model_name, preprocessor, months)
        
        # Calculate confidence intervals
        historical_std = preprocessor.df['Sales'].std()
        forecast_values = forecast_df['Predicted_Sales'].values
        
        upper_bound = forecast_values + 1.96 * historical_std
        lower_bound = forecast_values - 1.96 * historical_std
        
        return jsonify({
            'success': True,
            'forecast_dates': forecast_df['Month'].dt.strftime('%Y-%m').tolist(),
            'forecast_values': forecast_values.tolist(),
            'upper_bound': upper_bound.tolist(),
            'lower_bound': lower_bound.tolist(),
            'model_used': model_name
        })
    
    except Exception as e:
        print(f"Error generating forecast: {str(e)}")
        return jsonify({'success': False, 'message': f'Forecast generation failed: {str(e)}'}), 500

@app.route('/api/ai-insights', methods=['POST'])
def ai_insights():
    """Generate AI-powered insights using Gemini"""
    try:
        data = request.json
        api_key = 'AIzaSyA8b_9uzdOv7NLxYx4VV88SPHU4pPf65-Y'  # Hardcoded Gemini API key
        
        if not models_trained:
            return jsonify({'success': False, 'message': 'Please run comprehensive analysis first to train models'}), 400
        
        # Get data for interpretation
        train_df, test_df = preprocessor.get_train_test_split(3)
        actual_values = test_df['Sales'].values
        metrics_df = forecaster.get_all_metrics()
        best_model = forecaster.get_best_model('MAPE')
        
        # Initialize LLM
        llm = LLMInterpreter(api_key)
        
        # Generate comprehensive interpretation
        interpretation = llm.generate_model_interpretation(
            metrics_df,
            best_model,
            actual_values,
            forecaster.predictions
        )
        
        # Clean up the interpretation text
        interpretation = clean_llm_text(interpretation)
        
        # Generate forecast insight
        try:
            forecast_df = forecaster.forecast_future(best_model, preprocessor, 3)
            forecast_values = forecast_df['Predicted_Sales'].values
            quick_insight = llm.generate_quick_insight(forecast_values, best_model)
            
            # Clean up quick insight
            quick_insight = clean_llm_text(quick_insight)
            
            # Combine both insights
            combined_insights = f"{interpretation}\n\n### Future Forecast Insight\n\n{quick_insight}"
        except:
            combined_insights = interpretation
        
        return jsonify({
            'success': True,
            'insights': combined_insights
        })
    
    except Exception as e:
        print(f"Error generating AI insights: {str(e)}")
        # Return fallback insights if API fails
        if models_trained:
            best_model = forecaster.get_best_model('MAPE')
            metrics_df = forecaster.get_all_metrics()
            best_metrics = metrics_df[metrics_df['Model'] == best_model].iloc[0]
            
            fallback = f"""## Model Performance Analysis

**Best Performing Model: {best_model}**

The {best_model} model achieved the best performance with a MAPE of {best_metrics['MAPE']:.2f}%, indicating high forecast accuracy.

### Key Findings:
- MAPE: {best_metrics['MAPE']:.2f}% (Lower is better)
- WAPE: {best_metrics['WAPE']:.2f}%
- MAE: ${best_metrics['MAE']:.0f}
- RMSE: ${best_metrics['RMSE']:.0f}

### Recommendations:
1. Use the {best_model} model for future forecasting decisions
2. Monitor forecast accuracy regularly and retrain as needed
3. Consider external factors that may impact sales trends

*Note: Advanced AI insights are temporarily unavailable. Using fallback analysis.*
"""
            return jsonify({
                'success': True,
                'insights': fallback
            })
        else:
            return jsonify({'success': False, 'message': f'AI insights generation failed: {str(e)}'}), 500

@app.route('/api/seasonality-analysis', methods=['GET'])
def seasonality_analysis():
    """Analyze seasonality in the data"""
    try:
        if not preprocessor:
            return jsonify({'success': False, 'error': 'Data not loaded'}), 400
        
        df = preprocessor.df
        
        # Calculate seasonality
        rolling_mean = df['Sales'].rolling(window=3, center=True).mean()
        seasonal_component = df['Sales'] - rolling_mean
        seasonal_strength = (seasonal_component.std() / df['Sales'].std() * 100)
        
        # Growth rate
        growth_rate = ((df['Sales'].iloc[-1] - df['Sales'].iloc[0]) / df['Sales'].iloc[0]) * 100
        
        # Peak month
        peak_month = df.loc[df['Sales'].idxmax(), 'Month'].strftime('%B %Y')
        
        return jsonify({
            'success': True,
            'seasonality_strength': float(seasonal_strength),
            'growth_rate': float(growth_rate),
            'peak_month': peak_month,
            'seasonal_data': {
                'dates': df['Month'].dt.strftime('%Y-%m').tolist(),
                'seasonal_component': seasonal_component.fillna(0).tolist()
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/model-comparison', methods=['POST'])
def model_comparison():
    """Compare multiple models with different thresholds"""
    try:
        data = request.json
        threshold = data.get('threshold', 10.0)  # MAPE threshold
        
        if not models_trained:
            return jsonify({'success': False, 'error': 'Models not trained'}), 400
        
        metrics_df = forecaster.get_all_metrics()
        
        # Filter models by threshold
        passing_models = metrics_df[metrics_df['MAPE'] <= threshold]
        failing_models = metrics_df[metrics_df['MAPE'] > threshold]
        
        return jsonify({
            'success': True,
            'threshold': threshold,
            'passing_models': passing_models.to_dict('records'),
            'failing_models': failing_models.to_dict('records'),
            'pass_count': len(passing_models),
            'fail_count': len(failing_models)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/feature-importance', methods=['GET'])
def feature_importance():
    """Get feature importance from the best ML model"""
    try:
        if not models_trained:
            return jsonify({'success': False, 'message': 'Models not trained'}), 400
        
        # Get the best ML model (Random Forest or XGBoost)
        metrics_df = forecaster.get_all_metrics()
        ml_models = metrics_df[metrics_df['Model'].isin(['Random_Forest', 'XGBoost'])]
        
        if ml_models.empty:
            return jsonify({'success': False, 'message': 'No ML models trained'}), 400
        
        # Find best ML model by MAPE
        best_ml_model = ml_models.loc[ml_models['MAPE'].idxmin(), 'Model']
        
        # Get the model from forecaster
        if best_ml_model not in forecaster.models:
            return jsonify({'success': False, 'message': 'Model not found'}), 400
        
        model = forecaster.models[best_ml_model]
        
        # Get feature importances
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Get feature names
            feature_names = [col for col in preprocessor.df.columns 
                           if col not in ['Month', 'Sales']]
            
            # Create importance dictionary
            importance_dict = dict(zip(feature_names, importances))
            
            # Sort by importance
            sorted_importance = sorted(importance_dict.items(), 
                                      key=lambda x: x[1], reverse=True)
            
            return jsonify({
                'success': True,
                'model_name': best_ml_model,
                'features': [item[0] for item in sorted_importance],
                'importances': [float(item[1]) for item in sorted_importance]
            })
        else:
            return jsonify({'success': False, 'message': 'Model does not support feature importance'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/advanced-analytics', methods=['GET'])
def advanced_analytics():
    """Get advanced analytics metrics for the dashboard"""
    try:
        if not preprocessor or not models_trained:
            return jsonify({'success': False, 'message': 'Data not loaded or models not trained'}), 400
        
        df = preprocessor.df
        metrics_df = forecaster.get_all_metrics()
        
        # Calculate Trend Strength
        sales_values = df['Sales'].values
        if len(sales_values) > 1:
            # Linear regression to determine trend
            from sklearn.linear_model import LinearRegression
            X = np.arange(len(sales_values)).reshape(-1, 1)
            y = sales_values
            reg = LinearRegression().fit(X, y)
            trend_slope = reg.coef_[0]
            trend_strength = abs(trend_slope) / sales_values.mean() * 100
            
            if trend_slope > 0:
                trend_direction = "Increasing"
            elif trend_slope < 0:
                trend_direction = "Decreasing"
            else:
                trend_direction = "Stable"
            
            trend_strength_str = f"{trend_strength:.1f}% ({trend_direction})"
        else:
            trend_strength_str = "N/A"
        
        # Calculate Seasonality Detected
        rolling_mean = df['Sales'].rolling(window=3, center=True).mean()
        seasonal_component = df['Sales'] - rolling_mean
        seasonal_strength = (seasonal_component.std() / df['Sales'].std() * 100)
        
        if seasonal_strength > 20:
            seasonality_status = f"Yes ({seasonal_strength:.1f}% strength)"
        elif seasonal_strength > 10:
            seasonality_status = f"Moderate ({seasonal_strength:.1f}% strength)"
        else:
            seasonality_status = f"Low ({seasonal_strength:.1f}% strength)"
        
        # Get Best Feature (from feature importance)
        best_feature = "N/A"
        try:
            ml_models = metrics_df[metrics_df['Model'].isin(['Random_Forest', 'XGBoost'])]
            if not ml_models.empty:
                best_ml_model = ml_models.loc[ml_models['MAPE'].idxmin(), 'Model']
                if best_ml_model in forecaster.models:
                    model = forecaster.models[best_ml_model]
                    if hasattr(model, 'feature_importances_'):
                        importances = model.feature_importances_
                        # Use the same feature columns that were used for training
                        feature_cols = preprocessor.get_feature_columns()
                        if len(feature_cols) == len(importances):
                            importance_dict = dict(zip(feature_cols, importances))
                            best_feature = max(importance_dict.items(), key=lambda x: x[1])[0]
                        else:
                            print(f"[DEBUG] Feature mismatch: {len(feature_cols)} features vs {len(importances)} importances")
        except Exception as e:
            print(f"[DEBUG] Error getting best feature: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Model Consensus (how many models agree on similar performance)
        if len(metrics_df) > 1:
            mape_values = metrics_df['MAPE'].values
            mape_std = np.std(mape_values)
            mape_mean = np.mean(mape_values)
            cv = (mape_std / mape_mean) * 100  # Coefficient of variation
            
            if cv < 15:
                consensus = "High Agreement"
            elif cv < 30:
                consensus = "Moderate Agreement"
            else:
                consensus = "Low Agreement"
            
            consensus_str = f"{consensus} (CV: {cv:.1f}%)"
        else:
            consensus_str = "N/A"
        
        return jsonify({
            'success': True,
            'trend_strength': trend_strength_str,
            'seasonality_detected': seasonality_status,
            'best_feature': best_feature,
            'model_consensus': consensus_str
        })
    
    except Exception as e:
        import traceback
        print(f"Error in advanced analytics: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export-data', methods=['GET'])
def export_data():
    """Export forecast results and metrics to CSV"""
    try:
        if not preprocessor or not models_trained:
            return jsonify({'success': False, 'message': 'No data or models to export'}), 400
        
        metrics_df = forecaster.get_all_metrics()
        best_model = forecaster.get_best_model('MAPE')
        
        # Create export data
        export_data = {
            'metrics': metrics_df.to_dict('records'),
            'best_model': best_model,
            'data_summary': {
                'total_months': len(preprocessor.df),
                'date_range': {
                    'start': preprocessor.df['Month'].min().strftime('%Y-%m-%d'),
                    'end': preprocessor.df['Month'].max().strftime('%Y-%m-%d')
                },
                'avg_sales': float(preprocessor.df['Sales'].mean()),
                'total_sales': float(preprocessor.df['Sales'].sum())
            }
        }
        
        # Generate CSV content
        import io
        output = io.StringIO()
        
        # Write metrics
        output.write("=== MODEL PERFORMANCE METRICS ===\n\n")
        metrics_df.to_csv(output, index=False)
        output.write("\n\n")
        
        # Write summary
        output.write("=== SUMMARY ===\n")
        output.write(f"Best Model: {best_model}\n")
        output.write(f"Total Data Points: {export_data['data_summary']['total_months']}\n")
        output.write(f"Date Range: {export_data['data_summary']['date_range']['start']} to {export_data['data_summary']['date_range']['end']}\n")
        output.write(f"Average Sales: ${export_data['data_summary']['avg_sales']:.2f}\n")
        output.write(f"Total Sales: ${export_data['data_summary']['total_sales']:.2f}\n")
        
        # Write predictions if available
        if forecaster.predictions:
            output.write("\n\n=== PREDICTIONS ===\n")
            for model_name, preds in forecaster.predictions.items():
                output.write(f"\n{model_name} Predictions:\n")
                output.write(",".join([f"{p:.2f}" for p in preds]))
                output.write("\n")
        
        csv_content = output.getvalue()
        output.close()
        
        # Return as downloadable file
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=forecast_export_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
    
    except Exception as e:
        import traceback
        print(f"Error exporting data: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
