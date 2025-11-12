"""
Forecasting Models Module
Implements Naïve, ARIMA, Random Forest, and XGBoost forecasting models
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')


class ForecastingModels:
    """Collection of forecasting models"""
    
    def __init__(self):
        self.models = {}
        self.predictions = {}
        self.metrics = {}
    
    def naive_forecast(self, train_data, test_data, target_col='Sales'):
        """
        Naïve Forecast: Uses the last observed value as the forecast
        """
        last_value = train_data[target_col].iloc[-1]
        predictions = np.full(len(test_data), last_value)
        
        self.predictions['Naive'] = predictions
        return predictions
    
    def seasonal_naive_forecast(self, train_data, test_data, target_col='Sales', season_length=3):
        """
        Seasonal Naïve Forecast: Uses values from the same season last year
        """
        predictions = []
        train_values = train_data[target_col].values
        
        for i in range(len(test_data)):
            if len(train_values) >= season_length:
                pred = train_values[-season_length]
            else:
                pred = train_values[-1]
            predictions.append(pred)
        
        self.predictions['Seasonal_Naive'] = np.array(predictions)
        return np.array(predictions)
    
    def arima_forecast(self, train_data, test_data, target_col='Sales', order=(1, 1, 1)):
        """
        ARIMA Forecast: AutoRegressive Integrated Moving Average
        """
        try:
            # Fit ARIMA model
            model = ARIMA(train_data[target_col], order=order)
            fitted_model = model.fit()
            
            # Make predictions
            predictions = fitted_model.forecast(steps=len(test_data))
            
            self.models['ARIMA'] = fitted_model
            self.predictions['ARIMA'] = predictions.values
            return predictions.values
        
        except Exception as e:
            print(f"ARIMA Error: {e}")
            # Fallback to simple forecast
            return self.naive_forecast(train_data, test_data, target_col)
    
    def sarima_forecast(self, train_data, test_data, target_col='Sales', 
                       order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
        """
        SARIMA Forecast: Seasonal ARIMA
        """
        try:
            model = SARIMAX(
                train_data[target_col],
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            fitted_model = model.fit(disp=False)
            
            predictions = fitted_model.forecast(steps=len(test_data))
            
            self.models['SARIMA'] = fitted_model
            self.predictions['SARIMA'] = predictions.values
            return predictions.values
        
        except Exception as e:
            print(f"SARIMA Error: {e}")
            return self.arima_forecast(train_data, test_data, target_col)
    
    def random_forest_forecast(self, train_data, test_data, feature_cols, target_col='Sales'):
        """
        Random Forest Forecast: ML-based ensemble method
        """
        # Prepare training data
        X_train = train_data[feature_cols].fillna(0)
        y_train = train_data[target_col]
        
        # Prepare test data
        X_test = test_data[feature_cols].fillna(0)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=2,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Make predictions
        predictions = model.predict(X_test)
        
        self.models['Random_Forest'] = model
        self.predictions['Random_Forest'] = predictions
        
        return predictions
    
    def xgboost_forecast(self, train_data, test_data, feature_cols, target_col='Sales'):
        """
        XGBoost Forecast: Gradient boosting method
        """
        # Prepare training data
        X_train = train_data[feature_cols].fillna(0)
        y_train = train_data[target_col]
        
        # Prepare test data
        X_test = test_data[feature_cols].fillna(0)
        
        # Train model
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Make predictions
        predictions = model.predict(X_test)
        
        self.models['XGBoost'] = model
        self.predictions['XGBoost'] = predictions
        
        return predictions
    
    def calculate_mape(self, actual, predicted):
        """Calculate Mean Absolute Percentage Error"""
        return mean_absolute_percentage_error(actual, predicted) * 100
    
    def calculate_wape(self, actual, predicted):
        """
        Calculate Weighted Absolute Percentage Error
        WAPE = Sum(|Actual - Predicted|) / Sum(|Actual|) * 100
        """
        return (np.sum(np.abs(actual - predicted)) / np.sum(np.abs(actual))) * 100
    
    def calculate_mae(self, actual, predicted):
        """Calculate Mean Absolute Error"""
        return mean_absolute_error(actual, predicted)
    
    def calculate_rmse(self, actual, predicted):
        """Calculate Root Mean Squared Error"""
        return np.sqrt(np.mean((actual - predicted) ** 2))
    
    def evaluate_model(self, model_name, actual, predicted):
        """Evaluate a model and store metrics"""
        metrics = {
            'Model': model_name,
            'MAPE': self.calculate_mape(actual, predicted),
            'WAPE': self.calculate_wape(actual, predicted),
            'MAE': self.calculate_mae(actual, predicted),
            'RMSE': self.calculate_rmse(actual, predicted)
        }
        
        self.metrics[model_name] = metrics
        return metrics
    
    def get_all_metrics(self):
        """Get metrics for all models as a DataFrame"""
        if not self.metrics:
            return pd.DataFrame()
        
        return pd.DataFrame(self.metrics.values())
    
    def get_best_model(self, metric='MAPE'):
        """Get the best performing model based on a metric"""
        if not self.metrics:
            return None
        
        metrics_df = self.get_all_metrics()
        best_model = metrics_df.loc[metrics_df[metric].idxmin(), 'Model']
        
        return best_model
    
    def forecast_future(self, model_name, preprocessor, n_months=3):
        """
        Generate forecasts for future months
        """
        future_dates = preprocessor.generate_future_dates(n_months)
        
        if model_name in ['Naive', 'Seasonal_Naive']:
            last_value = preprocessor.df['Sales'].iloc[-1]
            forecasts = np.full(n_months, last_value)
        
        elif model_name in ['ARIMA', 'SARIMA']:
            model = self.models.get(model_name)
            if model:
                forecasts = model.forecast(steps=n_months).values
            else:
                last_value = preprocessor.df['Sales'].iloc[-1]
                forecasts = np.full(n_months, last_value)
        
        elif model_name in ['Random_Forest', 'XGBoost']:
            # For ML models, we need to create features for future dates
            # This is a simplified approach - using last known feature values
            last_features = preprocessor.processed_df[preprocessor.get_feature_columns()].iloc[-1:].values
            forecasts = []
            
            model = self.models.get(model_name)
            for _ in range(n_months):
                pred = model.predict(last_features)[0]
                forecasts.append(pred)
        
        else:
            last_value = preprocessor.df['Sales'].iloc[-1]
            forecasts = np.full(n_months, last_value)
        
        forecast_df = pd.DataFrame({
            'Month': future_dates,
            'Predicted_Sales': forecasts
        })
        
        return forecast_df

