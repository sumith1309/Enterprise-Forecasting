"""
Data Preprocessing Module
Handles data loading, feature engineering, and preparation for forecasting models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataPreprocessor:
    """Preprocesses time series data for forecasting"""
    
    def __init__(self, data_path='data/monthly_sales.csv'):
        """Initialize with data path"""
        self.data_path = data_path
        self.df = None
        self.processed_df = None
        
    def load_data(self):
        """Load the sales data"""
        self.df = pd.read_csv(self.data_path)
        self.df['Month'] = pd.to_datetime(self.df['Month'])
        self.df = self.df.sort_values('Month').reset_index(drop=True)
        return self.df
    
    def create_lag_features(self, target_col='Sales', lags=[1, 2, 3, 6]):
        """Create lag features for time series"""
        if self.df is None:
            self.load_data()
            
        self.processed_df = self.df.copy()
        
        for lag in lags:
            self.processed_df[f'Sales_Lag_{lag}'] = self.processed_df[target_col].shift(lag)
        
        return self.processed_df
    
    def create_seasonal_features(self):
        """Create seasonal indicators and temporal features"""
        if self.processed_df is None:
            self.create_lag_features()
        
        # Extract month and quarter
        self.processed_df['Month_Num'] = self.processed_df['Month'].dt.month
        self.processed_df['Quarter'] = self.processed_df['Month'].dt.quarter
        
        # Create cyclical features for month (sine/cosine encoding)
        self.processed_df['Month_Sin'] = np.sin(2 * np.pi * self.processed_df['Month_Num'] / 12)
        self.processed_df['Month_Cos'] = np.cos(2 * np.pi * self.processed_df['Month_Num'] / 12)
        
        # Season indicator
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        self.processed_df['Season'] = self.processed_df['Month_Num'].apply(get_season)
        
        # One-hot encode season
        season_dummies = pd.get_dummies(self.processed_df['Season'], prefix='Season')
        self.processed_df = pd.concat([self.processed_df, season_dummies], axis=1)
        
        return self.processed_df
    
    def create_rolling_features(self, target_col='Sales', windows=[3, 6]):
        """Create rolling statistics features"""
        if self.processed_df is None:
            self.create_seasonal_features()
        
        for window in windows:
            self.processed_df[f'Sales_RollingMean_{window}'] = \
                self.processed_df[target_col].rolling(window=window, min_periods=1).mean()
            self.processed_df[f'Sales_RollingStd_{window}'] = \
                self.processed_df[target_col].rolling(window=window, min_periods=1).std()
        
        return self.processed_df
    
    def get_train_test_split(self, test_size=3):
        """Split data into train and test sets"""
        if self.processed_df is None:
            self.preprocess_all()
        
        train_df = self.processed_df.iloc[:-test_size].copy()
        test_df = self.processed_df.iloc[-test_size:].copy()
        
        return train_df, test_df
    
    def preprocess_all(self):
        """Run all preprocessing steps"""
        self.load_data()
        self.create_lag_features()
        self.create_seasonal_features()
        self.create_rolling_features()
        
        # Fill any remaining NaN values
        self.processed_df = self.processed_df.bfill()
        
        return self.processed_df
    
    def get_feature_columns(self):
        """Get list of feature columns (excluding target and date)"""
        if self.processed_df is None:
            return []
        
        exclude_cols = ['Month', 'Sales', 'Season']
        return [col for col in self.processed_df.columns if col not in exclude_cols]
    
    def prepare_for_forecasting(self, last_n_months=3):
        """
        Prepare data for forecasting future months
        Returns the last n months of data with features for making predictions
        """
        if self.processed_df is None:
            self.preprocess_all()
        
        return self.processed_df.tail(last_n_months)
    
    def generate_future_dates(self, n_months=3):
        """Generate future date range for forecasting"""
        if self.df is None:
            self.load_data()
        
        last_date = self.df['Month'].max()
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=n_months,
            freq='MS'
        )
        
        return future_dates

