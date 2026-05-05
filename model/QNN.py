"""
QNN Modifié - Enhanced Quantile Neural Network
Based on the qnn_modifié.ipynb implementation
"""

import logging
import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential

# Setup logging
logger = logging.getLogger(__name__)
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib


class QuantileLoss:
    """Custom Quantile Loss for QNN models"""
    
    @staticmethod
    def quantile_loss(q):
        def loss(y_true, y_pred):
            error = y_true - y_pred
            return tf.reduce_mean(tf.maximum(q * error, (q - 1) * error))
        return loss


class QNNModified:
    """Enhanced QNN implementation based on qnn_modifié.ipynb"""
    
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.feature_cols = [
            "lag1", "lag2", "vol_lag1", "vol_lag2", 
            "ret_abs", "ret_sq", "ma5", "ma20", "std5", "std20"
        ]
        self.quantiles = [0.1, 0.5, 0.9]
        
    def build_qnn(self, input_dim, q):
        """Build QNN model for specific quantile"""
        model = Sequential()
        
        model.add(Input(shape=(input_dim,)))
        model.add(Dense(64, activation="relu"))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation="relu"))
        model.add(Dropout(0.2))
        model.add(Dense(1, activation="softplus"))
        
        model.compile(
            optimizer="adam",
            loss=QuantileLoss.quantile_loss(q)
        )
        
        return model
    
    def prepare_data(self, data_path="data/data_clean.csv"):
        """Prepare data for training"""
        df = pd.read_csv(data_path, sep=";")
        df.columns = df.columns.str.strip().str.lower()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        df = df.reset_index(drop=True)
        
        target_col = "volatility"
        df_model = df.dropna(subset=self.feature_cols + [target_col])
        
        X = df_model[self.feature_cols]
        y = df_model[target_col]
        
        # Split data
        split = int(len(df_model) * 0.8)
        X_train = X.iloc[:split]
        X_test = X.iloc[split:]
        y_train = y.iloc[:split]
        y_test = y.iloc[split:]
        
        # Scale data
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train(self, data_path="data/data_clean.csv"):
        """Train QNN models for all quantiles"""
        X_train_scaled, X_test_scaled, y_train, y_test = self.prepare_data(data_path)
        
        models = {}
        predictions = {}
        
        early_stop = EarlyStopping(
            monitor="val_loss",
            patience=15,
            restore_best_weights=True
        )
        
        for q in self.quantiles:
            logger.info(f"Training QNN for quantile: {q}")
            
            model = self.build_qnn(X_train_scaled.shape[1], q)
            
            model.fit(
                X_train_scaled,
                y_train,
                epochs=200,
                batch_size=32,
                validation_split=0.2,
                callbacks=[early_stop],
                verbose=0
            )
            
            pred = model.predict(X_test_scaled).flatten()
            
            models[q] = model
            predictions[q] = pred
        
        self.models = models
        return models, predictions, y_test
    
    def save_models(self, base_path="model_qnn_modified"):
        """Save trained models"""
        for q, model in self.models.items():
            model.save(f"{base_path}_{q}.keras")
        
        # Save scaler
        if self.scaler:
            joblib.dump(self.scaler, "scaler_qnn_modified.pkl")
        
        logger.info("Models saved successfully")
    
    def load_models(self, base_path="model_qnn_modified", scaler_path="scaler_qnn_modified.pkl"):
        """Load trained models"""
        for q in self.quantiles:
            try:
                model_path = f"{base_path}_{q}.keras"
                if os.path.exists(model_path):
                    custom_objects = {
                        'loss': QuantileLoss.quantile_loss(q),
                        'mse': 'mse',
                        'mae': 'mae'
                    }
                    self.models[q] = tf.keras.models.load_model(
                        model_path, 
                        custom_objects=custom_objects, 
                        safe_mode=False
                    )
                    logger.info(f"Loaded model for quantile {q}")
            except Exception as e:
                logger.error(f"Error loading model for quantile {q}: {e}")
        
        # Load scaler
        try:
            self.scaler = joblib.load(scaler_path)
            logger.info("Scaler loaded successfully")
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")
    
    def predict(self, X):
        """Make predictions with all quantiles"""
        if not self.models or not self.scaler:
            raise RuntimeError("Models not loaded. Call train() or load_models() first.")
        
        X_scaled = self.scaler.transform(X)
        predictions = {}
        
        for q, model in self.models.items():
            predictions[q] = model.predict(X_scaled).flatten()
        
        return predictions
    
    def evaluate(self, y_true, predictions):
        """Evaluate model performance"""
        results = []
        
        for q in self.quantiles:
            mae = mean_absolute_error(y_true, predictions[q])
            rmse = np.sqrt(mean_squared_error(y_true, predictions[q]))
            mape = np.mean(np.abs((y_true - predictions[q]) / y_true)) * 100
            
            results.append([q, mae, rmse, mape])
        
        return pd.DataFrame(results, columns=["Quantile", "MAE", "RMSE", "MAPE"])


if __name__ == "__main__":
    # Example usage
    qnn = QNNModified()
    models, predictions, y_test = qnn.train("data/data_clean.csv")
    
    # Evaluate
    results = qnn.evaluate(y_test, predictions)
    print("Evaluation Results:")
    print(results)
    
    # Save models
    qnn.save_models()
