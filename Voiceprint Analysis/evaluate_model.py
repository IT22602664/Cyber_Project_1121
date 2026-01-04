"""
Model Evaluation Script
Calculates comprehensive metrics: Accuracy, Precision, Recall, F1-Score, EER, FAR, FRR
"""
import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, classification_report
)
from tqdm import tqdm
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Apply Windows symlink fix
if sys.platform == 'win32':
    import shutil
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    original_symlink = Path.symlink_to
    def copy_instead_of_symlink(self, target, target_is_directory=False):
        try:
            return original_symlink(self, target, target_is_directory)
        except OSError as e:
            if "WinError 1314" in str(e) or "privilege" in str(e).lower():
                if target_is_directory or Path(target).is_dir():
                    shutil.copytree(target, self, dirs_exist_ok=True)
                else:
                    self.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, self)
                return
            else:
                raise
    Path.symlink_to = copy_instead_of_symlink

from src.speaker_embedding import SpeakerEmbeddingModel
from src.audio_preprocessing import AudioPreprocessor
from src.config_loader import get_config


def calculate_eer(y_true, y_scores):
    """Calculate Equal Error Rate (EER)"""
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    fnr = 1 - tpr
    
    # Find where FPR and FNR intersect
    eer_threshold = thresholds[np.nanargmin(np.absolute((fnr - fpr)))]
    eer = fpr[np.nanargmin(np.absolute((fnr - fpr)))]
    
    return eer, eer_threshold, fpr, tpr


def evaluate_model(num_pairs=1000, save_plots=True):
    """
    Evaluate model on verification pairs
    
    Args:
        num_pairs: Number of verification pairs to test
        save_plots: Whether to save ROC curve and other plots
    """
    print("\n" + "="*70)
    print("📊 MODEL EVALUATION - COMPREHENSIVE METRICS")
    print("="*70)
    
    # Load configuration
    config = get_config()
    
    # Initialize models
    print("\n[1/6] Loading models...")
    embedding_model = SpeakerEmbeddingModel(config)
    preprocessor = AudioPreprocessor(config)
    print("✓ Models loaded successfully")
    
    # Load verification pairs
    print("\n[2/6] Loading verification pairs...")
    dataset_path = Path("Voice dataset - senath")
    veri_file = dataset_path / "veri_test2.txt"
    
    if not veri_file.exists():
        print(f"❌ Verification file not found: {veri_file}")
        return
    
    # Read verification pairs (handle malformed lines)
    pairs_data = []
    with open(veri_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                # Take only first 3 fields (label, path1, path2)
                pairs_data.append([int(parts[0]), parts[1], parts[2]])

    pairs_df = pd.DataFrame(pairs_data, columns=['label', 'path1', 'path2'])

    # Limit number of pairs for faster evaluation
    pairs_df = pairs_df.head(num_pairs)
    print(f"✓ Loaded {len(pairs_df)} verification pairs")
    print(f"  - Genuine pairs: {sum(pairs_df['label'] == 1)}")
    print(f"  - Impostor pairs: {sum(pairs_df['label'] == 0)}")
    
    # Process pairs and calculate similarities
    print("\n[3/6] Processing audio pairs and extracting embeddings...")
    
    y_true = []
    y_scores = []
    valid_pairs = 0
    failed_pairs = 0
    
    dev_audio = dataset_path / "vox1_dev_wav" / "wav"
    test_audio = dataset_path / "vox1_test_wav" / "wav"
    
    for idx, row in tqdm(pairs_df.iterrows(), total=len(pairs_df), desc="Processing pairs"):
        try:
            # Find audio files
            path1 = dev_audio / row['path1']
            path2 = dev_audio / row['path2']
            
            if not path1.exists():
                path1 = test_audio / row['path1']
            if not path2.exists():
                path2 = test_audio / row['path2']
            
            if not path1.exists() or not path2.exists():
                failed_pairs += 1
                continue
            
            # Load and preprocess audio
            audio1, sr1 = preprocessor.load_audio(str(path1))
            audio2, sr2 = preprocessor.load_audio(str(path2))
            
            # Extract embeddings
            emb1 = embedding_model.extract_embedding(audio1)
            emb2 = embedding_model.extract_embedding(audio2)
            
            # Calculate cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            y_true.append(row['label'])
            y_scores.append(similarity)
            valid_pairs += 1
            
        except Exception as e:
            failed_pairs += 1
            continue
    
    print(f"\n✓ Processed {valid_pairs} pairs successfully")
    print(f"  - Failed: {failed_pairs} pairs")
    
    if valid_pairs == 0:
        print("❌ No valid pairs processed. Cannot calculate metrics.")
        return
    
    # Convert to numpy arrays
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)
    
    # Calculate EER and optimal threshold
    print("\n[4/6] Calculating Equal Error Rate (EER)...")
    eer, eer_threshold, fpr, tpr = calculate_eer(y_true, y_scores)
    
    print(f"✓ EER: {eer*100:.2f}%")
    print(f"✓ Optimal Threshold: {eer_threshold:.4f}")
    
    # Calculate metrics at EER threshold
    print("\n[5/6] Calculating performance metrics...")
    y_pred = (y_scores >= eer_threshold).astype(int)
    
    # Calculate all metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # FAR and FRR
    far = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Acceptance Rate
    frr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Rejection Rate
    
    # ROC AUC
    roc_auc = auc(fpr, tpr)

    # Print comprehensive results
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE EVALUATION RESULTS")
    print("="*70)

    print("\n🎯 PRIMARY METRICS:")
    print(f"  • Accuracy:  {accuracy*100:.2f}%")
    print(f"  • Precision: {precision*100:.2f}%")
    print(f"  • Recall:    {recall*100:.2f}%")
    print(f"  • F1-Score:  {f1*100:.2f}%")

    print("\n🔒 SECURITY METRICS:")
    print(f"  • EER (Equal Error Rate):        {eer*100:.2f}%")
    print(f"  • FAR (False Acceptance Rate):   {far*100:.2f}%")
    print(f"  • FRR (False Rejection Rate):    {frr*100:.2f}%")
    print(f"  • ROC AUC:                       {roc_auc:.4f}")

    print("\n📈 CONFUSION MATRIX:")
    print(f"  • True Positives (TP):   {tp}")
    print(f"  • True Negatives (TN):   {tn}")
    print(f"  • False Positives (FP):  {fp}")
    print(f"  • False Negatives (FN):  {fn}")

    print("\n⚙️  THRESHOLD:")
    print(f"  • Optimal Threshold: {eer_threshold:.4f}")
    print(f"  • Target EER:        < 3.00%")
    print(f"  • Status:            {'✓ PASS' if eer < 0.03 else '✗ FAIL'}")

    print("\n📊 DETAILED CLASSIFICATION REPORT:")
    print(classification_report(y_true, y_pred, target_names=['Impostor', 'Genuine'], digits=4))

    # Save plots
    if save_plots:
        print("\n[6/6] Generating plots...")

        # Create results directory
        results_dir = Path("evaluation_results")
        results_dir.mkdir(exist_ok=True)

        # Plot 1: ROC Curve
        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.scatter([eer], [1-eer], color='red', s=100, zorder=5, label=f'EER = {eer*100:.2f}%')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate (FAR)', fontsize=12)
        plt.ylabel('True Positive Rate (1 - FRR)', fontsize=12)
        plt.title('ROC Curve - Speaker Verification', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.savefig(results_dir / 'roc_curve.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {results_dir / 'roc_curve.png'}")

        # Plot 2: Score Distribution
        plt.figure(figsize=(10, 6))
        genuine_scores = y_scores[y_true == 1]
        impostor_scores = y_scores[y_true == 0]

        plt.hist(impostor_scores, bins=50, alpha=0.6, label='Impostor', color='red', edgecolor='black')
        plt.hist(genuine_scores, bins=50, alpha=0.6, label='Genuine', color='green', edgecolor='black')
        plt.axvline(eer_threshold, color='blue', linestyle='--', linewidth=2, label=f'Threshold = {eer_threshold:.4f}')
        plt.xlabel('Similarity Score', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Score Distribution - Genuine vs Impostor', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.savefig(results_dir / 'score_distribution.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {results_dir / 'score_distribution.png'}")

        # Plot 3: Confusion Matrix Heatmap
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_true, y_pred)
        plt.imshow(cm, interpolation='nearest', cmap='Blues')
        plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
        plt.colorbar()
        tick_marks = np.arange(2)
        plt.xticks(tick_marks, ['Impostor', 'Genuine'], fontsize=11)
        plt.yticks(tick_marks, ['Impostor', 'Genuine'], fontsize=11)

        # Add text annotations
        thresh = cm.max() / 2.
        for i in range(2):
            for j in range(2):
                plt.text(j, i, format(cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black",
                        fontsize=16, fontweight='bold')

        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        plt.savefig(results_dir / 'confusion_matrix.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {results_dir / 'confusion_matrix.png'}")

        plt.close('all')

    # Save results to file
    results_file = results_dir / 'evaluation_metrics.txt'
    with open(results_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("MODEL EVALUATION RESULTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Dataset: VoxCeleb\n")
        f.write(f"Verification Pairs: {valid_pairs}\n")
        f.write(f"Genuine Pairs: {sum(y_true == 1)}\n")
        f.write(f"Impostor Pairs: {sum(y_true == 0)}\n\n")
        f.write("PRIMARY METRICS:\n")
        f.write(f"  Accuracy:  {accuracy*100:.2f}%\n")
        f.write(f"  Precision: {precision*100:.2f}%\n")
        f.write(f"  Recall:    {recall*100:.2f}%\n")
        f.write(f"  F1-Score:  {f1*100:.2f}%\n\n")
        f.write("SECURITY METRICS:\n")
        f.write(f"  EER:     {eer*100:.2f}%\n")
        f.write(f"  FAR:     {far*100:.2f}%\n")
        f.write(f"  FRR:     {frr*100:.2f}%\n")
        f.write(f"  ROC AUC: {roc_auc:.4f}\n\n")
        f.write("CONFUSION MATRIX:\n")
        f.write(f"  TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}\n\n")
        f.write(f"Optimal Threshold: {eer_threshold:.4f}\n")

    print(f"\n✓ Results saved to: {results_file}")

    print("\n" + "="*70)
    print("✅ EVALUATION COMPLETE!")
    print("="*70)

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'eer': eer,
        'far': far,
        'frr': frr,
        'roc_auc': roc_auc,
        'threshold': eer_threshold,
        'confusion_matrix': {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate speaker verification model')
    parser.add_argument('--pairs', type=int, default=1000, help='Number of verification pairs to test (default: 1000)')
    parser.add_argument('--no-plots', action='store_true', help='Skip generating plots')

    args = parser.parse_args()

    evaluate_model(num_pairs=args.pairs, save_plots=not args.no_plots)

