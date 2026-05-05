"""
RQN Model - Recurrent Quantile Network
Based on the RQN_model.ipynb implementation
"""

import logging
import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

# Setup logging
logger = logging.getLogger(__name__)
import joblib
import pickle

class RQNModel:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.feature_cols = ['return', 'lag1', 'lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5']
        
    def clean_number(self, x):
        """Clean and convert string to float"""
        x = str(x).strip()
        x = x.replace(' ', '')
        
        if x.count('.') > 1:
            parts = x.split('.')
            x = ''.join(parts[:-1]) + '.' + parts[-1]
        
        x = x.replace(',', '.')
        
        try:
            return float(x)
        except:
            return np.nan
    
    def prepare_data(self, data_path="data/data_clean.csv"):
        try:
            # Load data
            df = pd.read_csv(data_path)
            
            # Clean numeric columns
            numeric_cols = ['return', 'lag1', 'lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'volatility']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].apply(self.clean_number)
            
            # Drop rows with NaN values
            df = df.dropna()
            
            # Prepare features and target
            X = df[self.feature_cols]
            y = df['volatility']
            
            # Add constant for statsmodels
            X = sm.add_constant(X)
            
            # Scale features (excluding constant)
            feature_data = X.drop('const', axis=1)
            self.scaler = StandardScaler()
            scaled_features = self.scaler.fit_transform(feature_data)
            
            # Reconstruct X with scaled features
            X_scaled = pd.DataFrame(scaled_features, columns=feature_data.columns, index=X.index)
            X_scaled['const'] = X['const']
            
            return X_scaled, y
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            raise
    
    def train(self, data_path="data/data_clean.csv"):
        try:
            # Prepare data
            X, y = self.prepare_data(data_path)
            
            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train models for different quantiles
            quantiles = [0.1, 0.5, 0.9]
            predictions_test = {}
            
            for q in quantiles:
                logger.info(f"Training RQN model for quantile {q}")
                model = sm.QuantReg(y_train, X_train)
                res = model.fit(q=q)
                self.models[q] = res
                predictions_test[q] = res.predict(X_test)
            
            return self.models, predictions_test, y_test, X_test
            
        except Exception as e:
            logger.error(f"Error training RQN model: {str(e)}")
            raise
    
    def predict(self, X):
        if self.scaler is None or not self.models:
            raise RuntimeError("Model not trained or loaded")
        
        if isinstance(X, pd.DataFrame):
            X_data = X[self.feature_cols]
        else:
            X_data = pd.DataFrame(X, columns=self.feature_cols)
        
        # Scale features
        X_scaled = self.scaler.transform(X_data)
        
        # Add constant
        X_scaled = sm.add_constant(X_scaled)
        
        # Make predictions
        predictions = {}
        for q, model in self.models.items():
            predictions[f"quantile_{str(q).replace('.', '_')}"] = model.predict(X_scaled).flatten()
        
        return predictions
    
    def save_models(self, model_path="rqn_models.pkl", scaler_path="scaler_rqn.pkl", features_path="rqn_features.joblib"):
        try:
            # Save scaler
            if self.scaler:
                joblib.dump(self.scaler, scaler_path)
            
            # Save models
            with open(model_path, 'wb') as f:
                pickle.dump(self.models, f)
            
            # Save feature columns
            joblib.dump(self.feature_cols, features_path)
            
            logger.info("RQN models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving RQN models: {str(e)}")
            raise
    
    def load_models(self, model_path="rqn_models.pkl", scaler_path="scaler_rqn.pkl", features_path="rqn_features.joblib"):
        try:
            # Load scaler
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info("Scaler loaded successfully")
            else:
                raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
            
            # Load models
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models = pickle.load(f)
                logger.info("RQN models loaded successfully")
            else:
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Load feature columns
            if os.path.exists(features_path):
                self.feature_cols = joblib.load(features_path)
                logger.info("Feature columns loaded successfully")
            else:
                logger.warning(f"Feature columns file not found: {features_path}, using defaults")
                
        except Exception as e:
            logger.error(f"Error loading RQN models: {str(e)}")
            raise
