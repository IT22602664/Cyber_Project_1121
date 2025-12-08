"""
Diagnostic script to check for data issues that might cause NaN losses
"""

import numpy as np
import sys
from loguru import logger
from src.config_loader import load_config
from src.mouse_preprocessing import MousePreprocessor

def diagnose_data():
    """Check data for NaN, Inf, and other issues"""
    
    logger.info("Starting data diagnostics...")
    
    # Load config
    config = load_config('config.yaml')
    
    # Initialize preprocessor
    preprocessor = MousePreprocessor(config)
    
    # Load dataset
    logger.info("Loading training dataset...")
    dataset = preprocessor.load_balabit_dataset(
        config.dataset.training_files,
        config.dataset.labels_file,
        is_training=True
    )
    
    # Split data
    train_users, val_users, test_users = preprocessor.split_by_user(dataset)
    
    logger.info(f"Train users: {len(train_users)}")
    logger.info(f"Val users: {len(val_users)}")
    logger.info(f"Test users: {len(test_users)}")
    
    # Process a small sample
    logger.info("\nProcessing sample data...")
    sample_user = list(train_users.keys())[0]
    sample_sessions = train_users[sample_user][:2]  # Just 2 sessions
    
    all_features = []
    all_labels = []
    
    for session_file in sample_sessions:
        features = preprocessor.extract_session_features(session_file)
        if features is not None:
            user_id = sample_user
            label = int(user_id.replace('user', ''))
            
            for feature_vec in features:
                all_features.append(feature_vec)
                all_labels.append(label)
    
    if len(all_features) == 0:
        logger.error("No features extracted!")
        return
    
    X = np.array(all_features)
    y = np.array(all_labels)
    
    logger.info(f"\nFeature matrix shape: {X.shape}")
    logger.info(f"Labels shape: {y.shape}")
    
    # Check for NaN
    nan_count = np.isnan(X).sum()
    logger.info(f"\nNaN values: {nan_count} ({nan_count / X.size * 100:.2f}%)")
    
    # Check for Inf
    inf_count = np.isinf(X).sum()
    logger.info(f"Inf values: {inf_count} ({inf_count / X.size * 100:.2f}%)")
    
    # Check for zeros
    zero_count = (X == 0).sum()
    logger.info(f"Zero values: {zero_count} ({zero_count / X.size * 100:.2f}%)")
    
    # Check feature statistics
    logger.info("\nFeature statistics:")
    logger.info(f"Min: {np.nanmin(X):.4f}")
    logger.info(f"Max: {np.nanmax(X):.4f}")
    logger.info(f"Mean: {np.nanmean(X):.4f}")
    logger.info(f"Std: {np.nanstd(X):.4f}")
    
    # Check each feature column
    logger.info("\nPer-feature analysis:")
    for i in range(min(10, X.shape[1])):  # First 10 features
        col = X[:, i]
        nan_in_col = np.isnan(col).sum()
        inf_in_col = np.isinf(col).sum()
        logger.info(f"Feature {i}: NaN={nan_in_col}, Inf={inf_in_col}, "
                   f"Min={np.nanmin(col):.4f}, Max={np.nanmax(col):.4f}, "
                   f"Mean={np.nanmean(col):.4f}")
    
    # Normalize and check again
    logger.info("\nNormalizing features...")
    X_norm = preprocessor.normalize_features(X, fit=True)
    
    nan_count_norm = np.isnan(X_norm).sum()
    inf_count_norm = np.isinf(X_norm).sum()
    
    logger.info(f"After normalization:")
    logger.info(f"NaN values: {nan_count_norm} ({nan_count_norm / X_norm.size * 100:.2f}%)")
    logger.info(f"Inf values: {inf_count_norm} ({inf_count_norm / X_norm.size * 100:.2f}%)")
    logger.info(f"Min: {np.nanmin(X_norm):.4f}")
    logger.info(f"Max: {np.nanmax(X_norm):.4f}")
    logger.info(f"Mean: {np.nanmean(X_norm):.4f}")
    logger.info(f"Std: {np.nanstd(X_norm):.4f}")
    
    # Check labels
    logger.info(f"\nLabel statistics:")
    logger.info(f"Unique labels: {np.unique(y)}")
    logger.info(f"Label counts: {np.bincount(y)}")
    
    if nan_count_norm == 0 and inf_count_norm == 0:
        logger.info("\n✓ Data looks good! No NaN or Inf values after normalization.")
    else:
        logger.warning(f"\n✗ Data has issues: {nan_count_norm} NaN, {inf_count_norm} Inf values")
        logger.warning("This will cause NaN losses during training!")
    
    logger.info("\nDiagnostics complete!")

if __name__ == '__main__':
    diagnose_data()

