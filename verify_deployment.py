"""
Deployment Checklist & Verification Script
"""
import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if file exists"""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ MISSING: {description}: {path}")
        return False

def check_directory_exists(path, description):
    """Check if directory exists"""
    if os.path.isdir(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ MISSING: {description}: {path}")
        return False

def run_checks():
    """Run all verification checks"""
    
    print("=" * 60)
    print("QNN PROJECT DEPLOYMENT CHECKLIST")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check directories
    print(" Checking Directories...")
    print("-" * 60)
    all_good &= check_directory_exists('app', 'Application')
    all_good &= check_directory_exists('app/core', 'Core Module')
    all_good &= check_directory_exists('app/api', 'API Module')
    all_good &= check_directory_exists('app/explainability', 'Explainability')
    all_good &= check_directory_exists('app/utils', 'Utils')
    all_good &= check_directory_exists('config', 'Config')
    all_good &= check_directory_exists('data', 'Data')
    all_good &= check_directory_exists('model', 'Model')
    all_good &= check_directory_exists('tests', 'Tests')
    all_good &= check_directory_exists('docs', 'Documentation')
    print()
    
    # Check model files
    print(" Checking Model Files...")
    print("-" * 60)
    all_good &= check_file_exists('model/model_volatility.h5', 'Trained Model')
    all_good &= check_file_exists('model/scaler.pkl', 'Feature Scaler')
    print()
    
    # Check data files
    print(" Checking Data Files...")
    print("-" * 60)
    all_good &= check_file_exists('data/data_clean.csv', 'Clean Data')
    print()
    
    # Check Python files
    print(" Checking Python Files...")
    print("-" * 60)
    all_good &= check_file_exists('app/core/model_loader.py', 'Model Loader')
    all_good &= check_file_exists('app/core/predictor.py', 'Predictor')
    all_good &= check_file_exists('app/api/flask_api.py', 'Flask API')
    all_good &= check_file_exists('app/explainability/shap_explainer.py', 'SHAP Explainer')
    all_good &= check_file_exists('app/utils/validators.py', 'Validators')
    all_good &= check_file_exists('app/utils/logger.py', 'Logger')
    all_good &= check_file_exists('config/config.py', 'Config')
    print()
    
    # Check configuration files
    print("  Checking Configuration Files...")
    print("-" * 60)
    all_good &= check_file_exists('requirements.txt', 'Requirements')
    all_good &= check_file_exists('Dockerfile', 'Docker Config')
    all_good &= check_file_exists('docker-compose.yml', 'Docker Compose')
    print()
    
    # Check documentation
    print(" Checking Documentation...")
    print("-" * 60)
    all_good &= check_file_exists('README.md', 'Main README')
    all_good &= check_file_exists('docs/API.md', 'API Documentation')
    all_good &= check_file_exists('docs/DEPLOYMENT.md', 'Deployment Guide')
    all_good &= check_file_exists('docs/ARCHITECTURE.md', 'Architecture')
    print()
    
    # Check examples
    print(" Checking Example Files...")
    print("-" * 60)
    all_good &= check_file_exists('example_predictions.py', 'Prediction Examples')
    all_good &= check_file_exists('example_shap_explanation.py', 'SHAP Examples')
    print()
    
    # Summary
    print("=" * 60)
    if all_good:
        print(" ALL CHECKS PASSED!")
        print("=" * 60)
        return 0
    else:
        print(" SOME CHECKS FAILED!")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(run_checks())
