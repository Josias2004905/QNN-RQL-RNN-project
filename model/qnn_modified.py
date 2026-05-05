"""
QNN Modifié - Enhanced Quantile Neural Network
Based on the qnn_modifié.ipynb implementation
"""

import logging
import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model

# Setup logging
logger = logging.getLogger(__name__)
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

def quantile_loss(q):
    def loss(y_true, y_pred):
        error = y_true - y_pred
        return tf.reduce_mean(tf.maximum(q * error, (q - 1) * error))
    return loss

class QuantileLoss(tf.keras.losses.Loss):
    def __init__(self, quantile):
        super().__init__()
        self.quantile = quantile
    
    def call(self, y_true, y_pred):
        error = y_true - y_pred
        return tf.reduce_mean(tf.maximum(self.quantile * error, (self.quantile - 1) * error))

def build_qnn(input_dim, q):
    model = Sequential()
    
    model.add(Input(shape=(input_dim,)))
    
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.2))
    
    model.add(Dense(32, activation="relu"))
    model.add(Dropout(0.2))
    
    model.add(Dense(1, activation="softplus"))
    
    model.compile(
        optimizer="adam",
        loss=quantile_loss(q)
    )
    
    return model

class QNNModified:
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.feature_cols = ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20']
        
    def train(self, data_path="data/data_clean.csv"):
        try:
            # Load data
            df = pd.read_csv(data_path)
            
            # Prepare features
            X = df[self.feature_cols].values
            y = df['volatility'].values
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train models for different quantiles
            quantiles = [0.1, 0.5, 0.9]
            
            for q in quantiles:
                logger.info(f"Training model for quantile {q}")
                model = build_qnn(X_scaled.shape[1], q)
                
                early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
                
                model.fit(
                    X_scaled, y,
                    epochs=100,
                    batch_size=32,
                    validation_split=0.2,
                    callbacks=[early_stopping],
                    verbose=1
                )
                
                self.models[q] = model
            
            # Make predictions
            predictions = {}
            for q in quantiles:
                predictions[q] = self.models[q].predict(X_scaled).flatten()
            
            return self.models, predictions, y
            
        except Exception as e:
            logger.error(f"Error training QNN: {str(e)}")
            raise
    
    def predict(self, X):
        if self.scaler is None or not self.models:
            raise RuntimeError("Model not trained or loaded")
        
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_cols].values
        
        X_scaled = self.scaler.transform(X)
        
        predictions = {}
        for q, model in self.models.items():
            predictions[f"quantile_{str(q).replace('.', '_')}"] = model.predict(X_scaled).flatten()
        
        return predictions
    
    def save_models(self, model_base_path="model_qnn_modified", scaler_path="scaler_qnn_modified.pkl"):
        try:
            # Save scaler
            if self.scaler:
                joblib.dump(self.scaler, scaler_path)
            
            # Save models
            for q, model in self.models.items():
                model_path = f"{model_base_path}_q{str(q).replace('.', '_')}.keras"
                model.save(model_path)
                logger.info(f"Saved model for quantile {q}")
                
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise
    
    def load_models(self, scaler_path="scaler_qnn_modified.pkl"):
        try:
            # Load scaler
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info("Scaler loaded successfully")
            else:
                raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
            
            # Load models
            quantiles = [0.1, 0.5, 0.9]
            model_base_path = "model_qnn_modified"
            
            for q in quantiles:
                model_path = f"{model_base_path}_q{str(q).replace('.', '_')}.keras"
                if os.path.exists(model_path):
                    custom_objects = {'QuantileLoss': lambda: QuantileLoss(q)}
                    self.models[q] = load_model(model_path, custom_objects=custom_objects)
                    logger.info(f"Loaded model for quantile {q}")
                else:
                    logger.warning(f"Model file not found: {model_path}")
            
            if not self.models:
                raise RuntimeError("No models could be loaded")
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
