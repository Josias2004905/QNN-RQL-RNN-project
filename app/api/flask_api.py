"""
Flask API Application for QNN Volatility Prediction
"""

import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.predictor import VolatilityPredictor
from app.utils.validators import PredictionValidator
from app.utils.logger import setup_logger
from app.explainability.shap_explainer import SHAPExplainer

# Setup logger
logger = setup_logger('api')

# Initialize Flask app with static folder
app = Flask(__name__, template_folder='../templates', static_folder='../static', static_url_path='/static')
CORS(app)

# Add web interface route before Flask-RESTX
@app.route('/')
def web_interface():
    """Serve the web interface"""
    return render_template('index.html')

# Initialize Flask-RESTX
api = Api(app, version='1.0', title='QNN Volatility Prediction API',
          description='Quantile Neural Networks for Financial Volatility Prediction')

# Create namespace
ns = api.namespace('api/v1', description='API endpoints')

# Initialize predictor
predictor = VolatilityPredictor()

# Models for documentation
feature_model = api.model('Features', {
    'lag1': fields.Float(required=True, description='Lag 1'),
    'lag2': fields.Float(required=True, description='Lag 2'),
    'vol_lag1': fields.Float(required=True, description='Volatility Lag 1'),
    'vol_lag2': fields.Float(required=True, description='Volatility Lag 2'),
    'ret_abs': fields.Float(required=True, description='Absolute Return'),
    'ret_sq': fields.Float(required=True, description='Squared Return'),
    'ma5': fields.Float(required=True, description='Moving Average 5'),
    'ma20': fields.Float(required=True, description='Moving Average 20'),
    'std5': fields.Float(required=True, description='Standard Deviation 5'),
    'std20': fields.Float(required=True, description='Standard Deviation 20'),
})

prediction_response_model = api.model('Prediction', {
    'q10': fields.Float(description='10th Quantile Prediction'),
    'q50': fields.Float(description='50th Quantile Prediction'),
    'q90': fields.Float(description='90th Quantile Prediction'),
})


@ns.route('/health')
class HealthCheck(Resource):
    """Health check endpoint"""
    
    def get(self):
        """Check API health"""
        return {
            'status': 'healthy',
            'model_loaded': predictor.model is not None,
            'version': '1.0.0'
        }, 200


@ns.route('/predict')
class Predict(Resource):
    """Single prediction endpoint"""
    
    @ns.expect(feature_model)
    @ns.marshal_with(prediction_response_model)
    def post(self):
        """
        Make a single volatility prediction
        
        Expected input:
        {
            "lag1": float,
            "lag2": float,
            "vol_lag1": float,
            "vol_lag2": float,
            "ret_abs": float,
            "ret_sq": float,
            "ma5": float,
            "ma20": float,
            "std5": float,
            "std20": float
        }
        """
        try:
            data = request.get_json()
            
            # Validate input
            PredictionValidator.validate_features(data, predictor.FEATURE_COLUMNS)
            
            # Make prediction
            prediction = predictor.predict(data)
            
            logger.info(f"Prediction made: {prediction}")
            return prediction, 200
        
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {'error': str(e)}, 500


@ns.route('/predict/batch')
class PredictBatch(Resource):
    """Batch prediction endpoint"""
    
    def post(self):
        """
        Make batch predictions
        
        Expected input:
        {
            "predictions": [
                {...feature dictionary...},
                {...feature dictionary...}
            ]
        }
        """
        try:
            data = request.get_json()
            
            if 'predictions' not in data:
                return {'error': 'Missing "predictions" field'}, 400
            
            features_list = data['predictions']
            
            # Validate batch
            PredictionValidator.validate_batch_features(features_list, predictor.FEATURE_COLUMNS)
            
            # Make predictions
            predictions = predictor.predict_batch(features_list)
            
            logger.info(f"Batch prediction made for {len(predictions)} samples")
            return {'predictions': predictions}, 200
        
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error(f"Batch prediction error: {str(e)}")
            return {'error': str(e)}, 500


@ns.route('/info')
class ModelInfo(Resource):
    """Model information endpoint"""
    
    def get(self):
        """Get model information"""
        return {
            'version': '1.0.0',
            'features': predictor.get_feature_columns(),
            'quantiles': predictor.get_quantiles(),
            'model_type': 'Quantile Neural Network',
            'description': 'QNN for Financial Volatility Prediction'
        }, 200


@ns.route('/explain')
class Explain(Resource):
    """Model explanation endpoint (SHAP)"""
    
    @ns.expect(feature_model)
    def post(self):
        """
        Get SHAP-based explanation for a prediction
        """
        try:
            data = request.get_json()
            
            # Validate input
            PredictionValidator.validate_features(data, predictor.FEATURE_COLUMNS)
            
            # Make prediction
            prediction = predictor.predict(data)
            
            # Try to get SHAP explanation
            try:
                import numpy as np
                feature_array = np.array([data[col] for col in predictor.FEATURE_COLUMNS]).reshape(1, -1)
                scaled_features = predictor.scaler.transform(feature_array)
                
                # Create SHAP explainer
                explainer = SHAPExplainer(predictor.model, scaled_features)
                explanation = explainer.explain_prediction(scaled_features, predictor.FEATURE_COLUMNS)
                
                response = {
                    'prediction': prediction,
                    'explanation': explanation
                }
            except Exception as shap_error:
                logger.warning(f"SHAP explanation failed: {str(shap_error)}")
                response = {
                    'prediction': prediction,
                    'explanation': None,
                    'warning': 'SHAP explanation not available'
                }
            
            return response, 200
        
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error(f"Explanation error: {str(e)}")
            return {'error': str(e)}, 500


def initialize_app(model_path: str, scaler_path: str):
    """Initialize the application with model paths"""
    try:
        predictor.initialize(model_path, scaler_path)
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise


if __name__ == '__main__':
    # Set default paths - adjust as needed
    # Get project root (go up from app/api to root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(project_root, 'model', 'model_volatility.h5')
    scaler_path = os.path.join(project_root, 'model', 'scaler.pkl')
    
    initialize_app(model_path, scaler_path)
    app.run(debug=False, host='0.0.0.0', port=5000)
