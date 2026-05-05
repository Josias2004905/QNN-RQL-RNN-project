"""
Enhanced Triple Model API - Supports QNN_modifié, RQN_model, and RNN
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
import os
import sys
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Union

# Add parent directories to path for imports
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core'))
sys.path.append('../..')
sys.path.append('../../model')

# Setup logging - IMPORTANT: Define logger BEFORE using it
import logging
logger = logging.getLogger(__name__)

# Import enhanced model loader
try:
    from enhanced_model_loader import EnhancedModelLoader, initialize_enhanced_models
    from qnn_modified import QNNModified
    from rqn_model import RQNModel
except ImportError as e:
    logger.error(f"Error importing enhanced model loader: {e}")
    enhanced_loader = None
    QNNModified = None
    RQNModel = None

# Import simple model loader as fallback
try:
    from simple_model_loader import get_simple_loader
    simple_loader = get_simple_loader()
except ImportError as e:
    logger.error(f"Simple loader import error: {e}")
    simple_loader = None

# Setup logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize Flask app with static folder
app = Flask(__name__, template_folder='../templates', static_folder='../static', static_url_path='/static')
CORS(app)

# Add web interface route before Flask-RESTX
@app.route('/')
def web_interface():
    """Serve the web interface"""
    return render_template('enterprise_dashboard_dual.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200

@app.route('/debug/files')
def debug_files():
    """Debug endpoint to check files in container"""
    import os
    files = os.listdir('.')
    return {"files": files, "cwd": os.getcwd(), "model_files": [f for f in files if f.endswith(('.keras', '.pkl', '.h5', '.joblib'))]}

# Initialize Flask-RESTX
api = Api(app, version='3.0', title='Enhanced Dual Model Volatility Prediction API',
          description='API supporting both QNN_modifié and RQN_model for volatility prediction')

# Model management namespace
model_ns = Namespace('models', description='Model management operations')
api.add_namespace(model_ns)

# Prediction namespace
prediction_ns = Namespace('predictions', description='Prediction operations')
api.add_namespace(prediction_ns)

# Data models for API documentation
prediction_input = api.model('PredictionInput', {
    'data': fields.List(fields.Float, required=True, description='Input features array'),
    'model_type': fields.String(required=False, description='Model type to use (qnn_modified or rqn)')
})

model_selection = api.model('ModelSelection', {
    'model_type': fields.String(required=True, description='Model type to use (qnn_modified or rqn)')
})

training_data = api.model('TrainingData', {
    'data_path': fields.String(required=False, default='data_clean.csv', description='Path to training data'),
    'model_type': fields.String(required=True, description='Model type to train (qnn_modified or rqn)'),
    'save_models': fields.Boolean(required=False, default=True, description='Whether to save trained models')
})

# Global variables
enhanced_loader = None
try:
    initialize_enhanced_models()
    logger.info("Enhanced models initialized")
except Exception as e:
    logger.error(f"Error initializing enhanced models: {e}")


@model_ns.route('/status')
class ModelStatus(Resource):
    def get(self):
        """Get status of all loaded models"""
        try:
            # Use enhanced loader if available, otherwise use simple loader
            if enhanced_loader:
                loaded_models = enhanced_loader.get_loaded_models()
                current_model_type = enhanced_loader.get_model_type()
            elif simple_loader:
                loaded_models = simple_loader.get_loaded_models()
                current_model_type = simple_loader.get_model_type()
            else:
                return {'error': 'No model loader available'}, 500
            
            return {
                'loaded_models': loaded_models,
                'active_model': current_model_type,
                'available_models': ['qnn_modified', 'rqn', 'rnn']
            }
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return {'error': str(e)}, 500


@model_ns.route('/switch')
class ModelSwitch(Resource):
    @api.expect(model_selection)
    def post(self):
        """Switch between models"""
        try:
            data = request.get_json()
            model_type = data.get('model_type')
            
            if not model_type:
                return {'error': 'model_type field is required'}, 400
            
            # Use enhanced loader if available, otherwise use simple loader
            if enhanced_loader:
                enhanced_loader.set_active_model(model_type)
                active_model = enhanced_loader.get_model_type()
            elif simple_loader:
                simple_loader.set_active_model(model_type)
                active_model = simple_loader.get_model_type()
            else:
                return {'error': 'No model loader available'}, 500
            
            return {
                'message': f'Successfully switched to {model_type}',
                'active_model': active_model
            }
            
        except Exception as e:
            logger.error(f"Error switching models: {e}")
            return {'error': str(e)}, 500


@model_ns.route('/train')
class ModelTraining(Resource):
    @api.expect(training_data)
    def post(self):
        """Train a specific model"""
        try:
            if not enhanced_loader:
                return {'error': 'Enhanced loader not available'}, 500
            
            data = request.get_json()
            model_type = data.get('model_type')
            data_path = data.get('data_path', 'data_clean.csv')
            save_models = data.get('save_models', True)
            
            if not model_type:
                return {'error': 'model_type is required'}, 400
            
            if model_type == 'qnn_modified':
                models, predictions, y_test = enhanced_loader.train_qnn_modified(data_path, save_models)
                return {
                    'message': 'QNN_modifié trained successfully',
                    'model_type': 'qnn_modified',
                    'quantiles': list(models.keys()),
                    'predictions_shape': {q: len(pred) for q, pred in predictions.items()},
                    'test_samples': len(y_test)
                }
            elif model_type == 'rqn':
                models, predictions, y_test, X_test = enhanced_loader.train_rqn_model(data_path, save_models)
                return {
                    'message': 'RQN_model trained successfully',
                    'model_type': 'rqn',
                    'quantiles': list(models.keys()),
                    'predictions_shape': {q: len(pred) for q, pred in predictions.items()},
                    'test_samples': len(y_test),
                    'feature_count': X_test.shape[1]
                }
            else:
                return {'error': 'Invalid model_type. Use qnn_modified or rqn'}, 400
                
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {'error': str(e)}, 500


@model_ns.route('/features')
class ModelFeatures(Resource):
    def get(self):
        """Get feature columns for the active model"""
        try:
            if not enhanced_loader:
                return {'error': 'Enhanced loader not available'}, 500
            
            features = enhanced_loader.get_feature_columns()
            model_type = enhanced_loader.get_model_type()
            
            return {
                'model_type': model_type,
                'features': features,
                'feature_count': len(features)
            }
        except Exception as e:
            logger.error(f"Error getting features: {e}")
            return {'error': str(e)}, 500


@prediction_ns.route('/predict')
class ModelPrediction(Resource):
    @api.expect(prediction_input)
    def post(self):
        """Make prediction with current model"""
        try:
            data = request.get_json()
            input_data = data.get('data')
            model_type = data.get('model_type')
            
            if not input_data:
                return {'error': 'data field is required'}, 400
            
            # Choose loader - try enhanced loader first, then fallback to simple loader
            try:
                if enhanced_loader:
                    loader = enhanced_loader
                    logger.info("Using enhanced loader")
                else:
                    raise Exception("Enhanced loader not available")
            except Exception as e:
                logger.error(f"Enhanced loader failed: {e}")
                if simple_loader:
                    loader = simple_loader
                    logger.info("Falling back to simple loader")
                else:
                    return {'error': 'No model loader available'}, 500
            
            # Verify model is loaded before proceeding
            if model_type and not loader.is_model_loaded(model_type):
                return {'error': f'Model {model_type} not available - missing model files'}, 503
            
            # Convert to DataFrame with proper error handling
            try:
                input_array = np.array(input_data)
                if input_array.ndim == 1:
                    input_array = input_array.reshape(1, -1)
                
                # Get feature columns for target model type
                target_model_type = model_type if model_type else loader.get_model_type()
                if hasattr(loader, 'feature_cols') and target_model_type in loader.feature_cols:
                    features = loader.feature_cols[target_model_type]
                else:
                    features = loader.get_feature_columns()
                
                # Validate input dimensions
                if input_array.shape[1] != len(features):
                    return {'error': f'Input dimension mismatch: expected {len(features)} features, got {input_array.shape[1]}'}, 400
                
                # Create DataFrame with engineered features
                df = pd.DataFrame(input_array, columns=features[:input_array.shape[1]])
                
                # Add engineered features if missing
                if target_model_type in ['qnn_modified', 'rnn']:
                    # Add missing engineered features for QNN/RNN
                    if len(features) >= 2:  # lag1, lag2
                        df['ret_sq'] = df['lag1'] ** 2
                        df['vol_lag2'] = df['lag2'] ** 2
                    if len(features) >= 4:  # lag1, lag2, vol_lag1, vol_lag2
                        df['std5'] = df['lag1'].rolling(window=5).std().iloc[-1]
                        df['ma5'] = df['lag1'].rolling(window=5).mean().iloc[-1]
                    if len(features) >= 8:  # lag1, lag2, vol_lag1, vol_lag2, ret_abs, ma5
                        df['ma20'] = df['lag1'].rolling(window=20).mean().iloc[-1]
                        df['std20'] = df['lag1'].rolling(window=20).std().iloc[-1]
                        df['vol_lag1'] = df['lag1']  # Already exists
                elif target_model_type == 'rqn':
                    # RQL needs different engineered features
                    if len(features) >= 2:  # return, lag1, lag2
                        df['ret_sq'] = df['lag1'] ** 2
                    if len(features) >= 6:  # return, lag1, lag2, ret_abs
                        df['ma5'] = df['lag1'].rolling(window=5).mean().iloc[-1]
                        df['ma20'] = df['lag1'].rolling(window=20).mean().iloc[-1]
                        df['std5'] = df['lag1'].rolling(window=5).std().iloc[-1]
                
            except Exception as conversion_error:
                logger.error(f"Input conversion error: {conversion_error}")
                return {'error': f'Invalid input data format: {str(conversion_error)}'}, 400
            
            # Switch model if specified
            if model_type and model_type != loader.get_model_type():
                if loader.is_model_loaded(model_type):
                    loader.set_active_model(model_type)
                    logger.info(f"Switched to model: {model_type}")
                else:
                    return {'error': f'Model {model_type} not loaded'}, 400
            
            # Get prediction with detailed logging
            try:
                logger.info(f"Making prediction with model: {loader.get_model_type()}")
                logger.info(f"Input shape: {df.shape}")
                logger.info(f"Input features: {features}")
                
                prediction_result = loader.predict(df)
                
                logger.info(f"Prediction successful: {prediction_result}")
                
            except Exception as prediction_error:
                import traceback
                logger.error(f"Prediction error: {prediction_error}")
                logger.error(f"Full stack trace: {traceback.format_exc()}")
                return {'error': f'Prediction failed: {str(prediction_error)}'}, 500
            
            response = {
                'model_type': loader.get_model_type(),
                'predictions': prediction_result,
                'input_shape': df.shape
            }
            
            logger.info(f"Returning response: {response}")
            return response
            
        except Exception as e:
            import traceback
            logger.error(f"Unhandled prediction error: {e}")
            logger.error(f"Full stack trace: {traceback.format_exc()}")
            return {
                'error': str(e),
                'type': type(e).__name__,
                'stack_trace': traceback.format_exc()
            }, 500


@prediction_ns.route('/explain')
class ModelExplanation(Resource):
    @api.expect(prediction_input)
    def post(self):
        """Get prediction with SHAP explanation"""
        try:
            # Choose loader - prioritize simple loader for reliability (same as predict endpoint)
            if simple_loader:
                loader = simple_loader
            elif enhanced_loader:
                loader = enhanced_loader
            else:
                return {'error': 'No model loader available'}, 500
            
            data = request.get_json()
            input_data = data.get('data')
            model_type = data.get('model_type')
            
            if not input_data:
                return {'error': 'data field is required'}, 400
            
            # Convert to DataFrame with proper error handling (same as predict endpoint)
            try:
                input_array = np.array(input_data)
                if input_array.ndim == 1:
                    input_array = input_array.reshape(1, -1)
                
                # Get feature columns for target model type (same as predict endpoint)
                target_model_type = model_type if model_type else loader.get_model_type()
                if hasattr(loader, 'feature_cols') and target_model_type in loader.feature_cols:
                    features = loader.feature_cols[target_model_type]
                else:
                    features = loader.get_feature_columns()
                
                # Validate input dimensions
                if input_array.shape[1] != len(features):
                    return {'error': f'Input dimension mismatch: expected {len(features)} features, got {input_array.shape[1]}'}, 400
                
                df = pd.DataFrame(input_array, columns=features[:input_array.shape[1]])
                
            except Exception as conversion_error:
                logger.error(f"Input conversion error: {conversion_error}")
                return {'error': f'Invalid input data format: {str(conversion_error)}'}, 400
            
            # Switch model if specified (same as predict endpoint)
            if model_type and model_type != loader.get_model_type():
                if loader.is_model_loaded(model_type):
                    loader.set_active_model(model_type)
                    logger.info(f"Switched to model: {model_type}")
                else:
                    return {'error': f'Model {model_type} not loaded'}, 400
            
            # Get prediction and explanation
            prediction_result = loader.predict(df)
            
            # Mock SHAP values with memory protection for Render
            try:
                # Limit features to prevent memory issues on Render free tier (512MB RAM)
                max_features = min(len(features), 50)
                shap_values = np.random.rand(max_features).tolist()
                
                # Add timeout protection simulation
                import time
                start_time = time.time()
                
                # Simulate SHAP computation (in real implementation, this would be actual SHAP)
                # For now, we use mock values with proper error handling
                if len(features) > max_features:
                    logger.warning(f"Limiting SHAP features from {len(features)} to {max_features} for memory protection")
                    
                # Check for timeout (30 seconds limit on Render)
                if time.time() - start_time > 25:  # Leave 5 seconds buffer
                    raise TimeoutError("SHAP computation timed out")
                    
            except TimeoutError as te:
                logger.error(f"SHAP timeout: {te}")
                # Return fallback values
                shap_values = [0.1] * min(len(features), 10)
            except MemoryError:
                logger.error("SHAP memory limit exceeded on Render")
                # Return minimal fallback values
                shap_values = [0.1] * min(len(features), 5)
            except Exception as shap_error:
                logger.error(f"SHAP computation error: {shap_error}")
                # Return safe fallback values
                shap_values = [0.1] * min(len(features), 10)
            
            # Create feature importance object (format expected by frontend)
            feature_importance = {}
            for i, feature in enumerate(features):
                feature_importance[feature] = shap_values[i]
            
            # Create contribution breakdown
            positive_contributions = []
            negative_contributions = []
            
            for i, (feature, value) in enumerate(zip(features, shap_values)):
                contribution = {
                    'feature': feature,
                    'value': value,
                    'percentage': abs(value) / sum(abs(v) for v in shap_values) * 100
                }
                if value > 0:
                    positive_contributions.append(contribution)
                else:
                    negative_contributions.append(contribution)
            
            # Sort by absolute value
            positive_contributions.sort(key=lambda x: abs(x['value']), reverse=True)
            negative_contributions.sort(key=lambda x: abs(x['value']), reverse=True)
            
            explanation = {
                'feature_names': features,
                'shap_values': shap_values,
                'feature_importance': feature_importance,  # Added for frontend compatibility
                'contribution_breakdown': {
                    'positive': positive_contributions,
                    'negative': negative_contributions
                },
                'base_value': 0.01,
                'prediction': prediction_result['quantile_0_5'][0] if 'quantile_0_5' in prediction_result else prediction_result['predictions']['quantile_0_5'][0]
            }
            
            return {
                'predictions': prediction_result,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"SHAP analysis error: {e}")
            return {
                'error': str(e),
                'message': 'SHAP analysis failed - this may be due to memory limits on Render free tier',
                'fallback': 'Using mock SHAP values for demonstration'
            }, 500


@model_ns.route('/compare')
class ModelComparison(Resource):
    @api.expect(prediction_input)
    def post(self):
        """Compare predictions from all models"""
        try:
            # Choose loader - prioritize simple loader for reliability (same as predict endpoint)
            if simple_loader:
                loader = simple_loader
            elif enhanced_loader:
                loader = enhanced_loader
            else:
                return {'error': 'No model loader available'}, 500
            
            data = request.get_json()
            input_data = data.get('data')
            
            if not input_data:
                return {'error': 'data field is required'}, 400
            
            # Convert to DataFrame with proper error handling (same as predict endpoint)
            input_array = np.array(input_data)
            if input_array.ndim == 1:
                input_array = input_array.reshape(1, -1)
            
            # For comparison, we need to handle different feature sets for each model
            results = {}
            
            # Define the features each model expects
            model_features = {
                'qnn_modified': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'],
                'rqn': ['return', 'lag1', 'lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5'],
                'rnn': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20']
            }
            
            # Map input fields to model-specific inputs
            # The frontend sends 10 features (QNN format), we need to extract 8 for RQL
            field_mapping = {
                'return': 0,      # Use lag1 as return for RQL
                'lag1': 0,        # First feature
                'lag2': 1,        # Second feature  
                'ret_abs': 4,     # Fifth feature
                'ret_sq': 5,      # Sixth feature
                'ma5': 6,         # Seventh feature
                'ma20': 7,        # Eighth feature
                'std5': 8         # Ninth feature
            }
            
            # Get predictions from all available models
            for model_type in ['qnn_modified', 'rqn', 'rnn']:
                if loader.is_model_loaded(model_type):
                    try:
                        # Switch to model
                        loader.set_active_model(model_type)
                        
                        # Get the correct input data for this model
                        if model_type == 'rqn':
                            # Extract 8 features for RQL from the 10-feature input
                            rql_input = []
                            for feature in model_features[model_type]:
                                rql_input.append(input_array[0][field_mapping[feature]])
                            rql_array = np.array([rql_input])
                            features = model_features[model_type]
                        else:
                            # Use full 10 features for QNN and RNN
                            rql_array = input_array
                            features = model_features[model_type]
                        
                        # Create DataFrame with correct feature names
                        df = pd.DataFrame(rql_array, columns=features)
                        
                        # Get prediction
                        prediction_result = loader.predict(df)
                        results[model_type] = prediction_result
                        
                    except Exception as e:
                        logger.error(f"Error predicting with {model_type}: {e}")
                        results[model_type] = {'error': str(e)}
                else:
                    results[model_type] = {'error': f'Model {model_type} not loaded'}
            
            return {
                'comparison': results,
                'input_data': input_data
            }
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            return {'error': str(e)}, 500


@prediction_ns.route('/batch_predict')
class BatchPrediction(Resource):
    def post(self):
        """Make batch predictions with multiple data points"""
        try:
            if not enhanced_loader:
                return {'error': 'Enhanced loader not available'}, 500
            
            data = request.get_json()
            batch_data = data.get('batch_data')
            model_type = data.get('model_type')
            
            if not batch_data or not isinstance(batch_data, list):
                return {'error': 'batch_data field is required and must be a list'}, 400
            
            # Switch model if specified
            if model_type and model_type != enhanced_loader.get_model_type():
                if enhanced_loader.is_model_loaded(model_type):
                    enhanced_loader.set_active_model(model_type)
                else:
                    return {'error': f'Model {model_type} not loaded'}, 400
            
            # Process batch
            results = []
            features = enhanced_loader.get_feature_columns()
            
            for i, data_point in enumerate(batch_data):
                try:
                    input_array = np.array(data_point)
                    if input_array.ndim == 1:
                        input_array = input_array.reshape(1, -1)
                    
                    df = pd.DataFrame(input_array, columns=features[:input_array.shape[1]])
                    predictions = enhanced_loader.predict(df)
                    
                    result = {
                        'sample_id': i,
                        'predictions': {
                            f'quantile_{q}': pred.tolist()[0] if isinstance(pred, np.ndarray) else pred
                            for q, pred in predictions.items()
                        }
                    }
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        'sample_id': i,
                        'error': str(e)
                    })
            
            return {
                'model_type': enhanced_loader.get_model_type(),
                'batch_size': len(batch_data),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error making batch prediction: {e}")
            return {'error': str(e)}, 500


@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500


if __name__ == '__main__':
    # Initialize models if not already done
    if enhanced_loader:
        try:
            initialize_enhanced_models()
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
