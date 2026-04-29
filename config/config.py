"""
Configuration Module - Centralized configuration management
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Base configuration"""
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / 'data'
    MODEL_DIR = PROJECT_ROOT / 'model'
    LOGS_DIR = PROJECT_ROOT / 'logs'
    
    # Model paths
    MODEL_PATH = MODEL_DIR / 'model_volatility.h5'
    SCALER_PATH = MODEL_DIR / 'scaler.pkl'
    
    # API configuration
    API_DEBUG = False
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    
    # Model configuration
    BATCH_SIZE = 32
    VERBOSE = 0
    
    # Feature columns
    FEATURE_COLUMNS = [
        'lag1', 'lag2', 'vol_lag1', 'vol_lag2',
        'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'
    ]
    
    # Quantiles
    QUANTILES = [0.1, 0.5, 0.9]
    
    # Logging
    LOG_LEVEL = 'INFO'


@dataclass
class DevelopmentConfig(Config):
    """Development configuration"""
    API_DEBUG = True
    LOG_LEVEL = 'DEBUG'


@dataclass
class ProductionConfig(Config):
    """Production configuration"""
    API_DEBUG = False
    LOG_LEVEL = 'INFO'


@dataclass
class TestingConfig(Config):
    """Testing configuration"""
    API_DEBUG = True
    LOG_LEVEL = 'DEBUG'
    MODEL_PATH = None  # Will be mocked in tests


def get_config(env: Optional[str] = None) -> Config:
    """
    Get configuration based on environment
    
    Args:
        env: Environment name (development, production, testing)
    
    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
