"""
Face Recognition Model Accuracy Evaluation Script

This script evaluates the accuracy of the face verification model by testing it on 
pairs of images (positive and negative pairs) and computing metrics like accuracy,
precision, recall, and F1-score.

Usage:
    python evaluate_accuracy.py --test_dir <path_to_test_images> --pairs_file <path_to_pairs_file>
    
    Or organize test images in the following structure:
    test_dataset/
        person1/
            image1.jpg
            image2.jpg
        person2/
            image1.jpg
            image2.jpg
"""

import os
import argparse
import numpy as np
from itertools import combinations
from pathlib import Path
from src.embedding import generate_embedding
from src.similarity import compute_similarity


def load_image_pairs(test_dir, max_pairs_per_person=10):
    """
    Load positive and negative pairs from a directory structure.
    
    Args:
        test_dir: Directory containing subdirectories for each person
        max_pairs_per_person: Maximum number of positive pairs per person
    
    Returns:
        positive_pairs: List of tuples (path1, path2) for same person
        negative_pairs: List of tuples (path1, path2) for different persons
    """
    positive_pairs = []
    negative_pairs = []
    
    # Get all person directories
    person_dirs = [d for d in Path(test_dir).iterdir() if d.is_dir()]
    
    # Create positive pairs (same person)
    for person_dir in person_dirs:
        images = [str(f) for f in person_dir.glob('*.jpg')] + \
                 [str(f) for f in person_dir.glob('*.JPG')] + \
                 [str(f) for f in person_dir.glob('*.png')] + \
                 [str(f) for f in person_dir.glob('*.PNG')] + \
                 [str(f) for f in person_dir.glob('*.jpeg')] + \
                 [str(f) for f in person_dir.glob('*.JPEG')]
        
        if len(images) >= 2:
            # Create combinations of images for same person
            pairs = list(combinations(images, 2))
            # Limit pairs to avoid too many
            pairs = pairs[:max_pairs_per_person]
            positive_pairs.extend([(p[0], p[1], 1) for p in pairs])
    
    # Create negative pairs (different persons)
    all_images_by_person = {}
    for person_dir in person_dirs:
        person_name = person_dir.name
        images = [str(f) for f in person_dir.glob('*.jpg')] + \
                 [str(f) for f in person_dir.glob('*.JPG')] + \
                 [str(f) for f in person_dir.glob('*.png')] + \
                 [str(f) for f in person_dir.glob('*.PNG')] + \
                 [str(f) for f in person_dir.glob('*.jpeg')] + \
                 [str(f) for f in person_dir.glob('*.JPEG')]
        if images:
            all_images_by_person[person_name] = images
    
    # Create negative pairs by pairing images from different persons
    person_names = list(all_images_by_person.keys())
    negative_count = 0
    target_negative = len(positive_pairs)  # Balance positive and negative pairs
    
    for i, person1 in enumerate(person_names):
        for person2 in person_names[i+1:]:
            if negative_count >= target_negative:
                break
            # Take first image from each person
            if all_images_by_person[person1] and all_images_by_person[person2]:
                img1 = all_images_by_person[person1][0]
                img2 = all_images_by_person[person2][0]
                negative_pairs.append((img1, img2, 0))
                negative_count += 1
        if negative_count >= target_negative:
            break
    
    return positive_pairs, negative_pairs


def load_pairs_from_file(pairs_file):
    """
    Load pairs from a text file.
    Expected format: image1_path image2_path label (0 or 1)
    
    Args:
        pairs_file: Path to file containing pairs
    
    Returns:
        pairs: List of tuples (path1, path2, label)
    """
    pairs = []
    with open(pairs_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                img1, img2, label = parts[0], parts[1], int(parts[2])
                pairs.append((img1, img2, label))
    return pairs


def evaluate_model(pairs, threshold=0.6, verbose=True):
    """
    Evaluate the model on a set of image pairs.
    
    Args:
        pairs: List of tuples (path1, path2, label)
        threshold: Similarity threshold for classification
        verbose: Whether to print progress
    
    Returns:
        metrics: Dictionary containing accuracy, precision, recall, F1-score
    """
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    similarities = []
    labels = []
    
    total_pairs = len(pairs)
    print(f"\nEvaluating {total_pairs} pairs...")
    
    for idx, (img1_path, img2_path, label) in enumerate(pairs):
        if verbose and (idx + 1) % 10 == 0:
            print(f"Processing pair {idx + 1}/{total_pairs}...")
        
        try:
            # Generate embeddings
            emb1 = generate_embedding(img1_path)
            emb2 = generate_embedding(img2_path)
            
            # Compute similarity
            similarity = compute_similarity(emb1, emb2)
            similarities.append(similarity)
            labels.append(label)
            
            # Classify based on threshold
            prediction = 1 if similarity >= threshold else 0
            
            # Update confusion matrix
            if label == 1 and prediction == 1:
                true_positives += 1
            elif label == 0 and prediction == 0:
                true_negatives += 1
            elif label == 0 and prediction == 1:
                false_positives += 1
            elif label == 1 and prediction == 0:
                false_negatives += 1
                
        except Exception as e:
            print(f"Error processing pair {img1_path}, {img2_path}: {e}")
            continue
    
    # Calculate metrics
    accuracy = (true_positives + true_negatives) / total_pairs if total_pairs > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'true_positives': true_positives,
        'true_negatives': true_negatives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'threshold': threshold,
        'similarities': similarities,
        'labels': labels
    }
    
    return metrics


def find_optimal_threshold(pairs, threshold_range=np.arange(0.3, 0.95, 0.05)):
    """
    Find the optimal threshold by testing multiple values.
    
    Args:
        pairs: List of tuples (path1, path2, label)
        threshold_range: Range of thresholds to test
    
    Returns:
        best_threshold: Optimal threshold value
        best_metrics: Metrics at optimal threshold
    """
    print("\n" + "="*60)
    print("FINDING OPTIMAL THRESHOLD")
    print("="*60)
    
    best_accuracy = 0
    best_threshold = 0.6
    best_metrics = None
    
    results = []
    
    for threshold in threshold_range:
        metrics = evaluate_model(pairs, threshold=threshold, verbose=False)
        results.append((threshold, metrics))
        
        print(f"Threshold: {threshold:.2f} | Accuracy: {metrics['accuracy']:.4f} | "
              f"Precision: {metrics['precision']:.4f} | Recall: {metrics['recall']:.4f}")
        
        if metrics['accuracy'] > best_accuracy:
            best_accuracy = metrics['accuracy']
            best_threshold = threshold
            best_metrics = metrics
    
    return best_threshold, best_metrics, results


def print_evaluation_report(metrics):
    """Print a detailed evaluation report."""
    print("\n" + "="*60)
    print("EVALUATION REPORT")
    print("="*60)
    print(f"Threshold: {metrics['threshold']:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  True Positives:  {metrics['true_positives']}")
    print(f"  True Negatives:  {metrics['true_negatives']}")
    print(f"  False Positives: {metrics['false_positives']}")
    print(f"  False Negatives: {metrics['false_negatives']}")
    print(f"\nMetrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"  Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"  Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"  F1-Score:  {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Evaluate face recognition model accuracy')
    parser.add_argument('--test_dir', type=str, help='Directory containing test images organized by person')
    parser.add_argument('--pairs_file', type=str, help='File containing image pairs and labels')
    parser.add_argument('--threshold', type=float, default=0.6, help='Similarity threshold (default: 0.6)')
    parser.add_argument('--find_optimal', action='store_true', help='Find optimal threshold')
    parser.add_argument('--max_pairs', type=int, default=10, help='Max positive pairs per person')
    
    args = parser.parse_args()
    
    # Load pairs
    all_pairs = []
    
    if args.pairs_file:
        print(f"Loading pairs from file: {args.pairs_file}")
        all_pairs = load_pairs_from_file(args.pairs_file)
    elif args.test_dir:
        print(f"Loading pairs from directory: {args.test_dir}")
        positive_pairs, negative_pairs = load_image_pairs(args.test_dir, args.max_pairs)
        all_pairs = positive_pairs + negative_pairs
        print(f"Loaded {len(positive_pairs)} positive pairs and {len(negative_pairs)} negative pairs")
    else:
        print("Error: Please provide either --test_dir or --pairs_file")
        return
    
    if not all_pairs:
        print("No pairs found. Please check your test data.")
        return
    
    # Evaluate model
    if args.find_optimal:
        best_threshold, best_metrics, all_results = find_optimal_threshold(all_pairs)
        print(f"\n{'='*60}")
        print(f"OPTIMAL THRESHOLD: {best_threshold:.4f}")
        print(f"{'='*60}")
        print_evaluation_report(best_metrics)
    else:
        metrics = evaluate_model(all_pairs, threshold=args.threshold)
        print_evaluation_report(metrics)


if __name__ == "__main__":
    # If no command line arguments, provide a simple example
    import sys
    if len(sys.argv) == 1:
        print("\n" + "="*60)
        print("FACE RECOGNITION MODEL ACCURACY EVALUATOR")
        print("="*60)
        print("\nUsage Examples:")
        print("\n1. Evaluate with directory structure:")
        print("   python evaluate_accuracy.py --test_dir test_dataset --threshold 0.6")
        print("\n2. Find optimal threshold:")
        print("   python evaluate_accuracy.py --test_dir test_dataset --find_optimal")
        print("\n3. Evaluate with pairs file:")
        print("   python evaluate_accuracy.py --pairs_file pairs.txt --threshold 0.6")
        print("\nDirectory Structure:")
        print("   test_dataset/")
        print("       person1/")
        print("           image1.jpg")
        print("           image2.jpg")
        print("       person2/")
        print("           image1.jpg")
        print("           image2.jpg")
        print("\nPairs File Format (space-separated):")
        print("   path/to/img1.jpg path/to/img2.jpg 1  # Same person")
        print("   path/to/img3.jpg path/to/img4.jpg 0  # Different persons")
        print("="*60)
    else:
        main()
