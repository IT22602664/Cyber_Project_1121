"""
Training Script for Keystroke Dynamics Model
Trains the embedding model on keystroke timing data
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from tqdm import tqdm
from loguru import logger
import matplotlib.pyplot as plt
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config_loader import load_config
from src.keystroke_preprocessing import KeystrokePreprocessor
from src.keystroke_embedding import KeystrokeEmbeddingModel, TripletLoss, ContrastiveLoss
from src.anomaly_detection import AnomalyDetector


class KeystrokeTrainer:
    """Trainer for keystroke dynamics model"""
    
    def __init__(self, config):
        """Initialize trainer"""
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"Using device: {self.device}")
        
        # Initialize components
        self.preprocessor = KeystrokePreprocessor(config)
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        
    def load_data(self):
        """Load and preprocess dataset"""
        logger.info("Loading dataset...")

        # Check if using tuplet dataset
        use_tuplet = self.config.dataset.get('use_tuplet', False)

        if use_tuplet:
            logger.info("Using TUPLET dataset (pre-paired samples)")
            self.load_tuplet_data()
        else:
            logger.info("Using DSL dataset (original)")
            self.load_dsl_data()

    def augment_tuplet_data(self, X_A, X_B, labels, aug_factor):
        """
        Augment tuplet dataset with noise and time warping

        Args:
            X_A: Features for sample A
            X_B: Features for sample B
            labels: Labels (1=genuine, 0=impostor)
            aug_factor: Augmentation factor (e.g., 5 = 5x more data)

        Returns:
            Augmented X_A, X_B, labels
        """
        X_A_aug = [X_A]
        X_B_aug = [X_B]
        labels_aug = [labels]

        noise_level = self.config.training.get('noise_level', 0.02)

        for i in range(aug_factor - 1):
            # Add Gaussian noise
            noise_A = np.random.normal(0, noise_level, X_A.shape)
            noise_B = np.random.normal(0, noise_level, X_B.shape)

            X_A_noisy = X_A + noise_A
            X_B_noisy = X_B + noise_B

            # Ensure non-negative values (timing features should be positive)
            X_A_noisy = np.maximum(X_A_noisy, 0)
            X_B_noisy = np.maximum(X_B_noisy, 0)

            X_A_aug.append(X_A_noisy)
            X_B_aug.append(X_B_noisy)
            labels_aug.append(labels)

        # Concatenate all augmented data
        X_A_final = np.vstack(X_A_aug)
        X_B_final = np.vstack(X_B_aug)
        labels_final = np.concatenate(labels_aug)

        return X_A_final, X_B_final, labels_final

    def load_tuplet_data(self):
        """Load and preprocess tuplet dataset"""
        # Load tuplet dataset
        dataset_path = self.config.dataset.tuplet_path
        if not os.path.exists(dataset_path):
            # Try alternative path
            dataset_path = os.path.join('Keystroke Dynamics', dataset_path)

        X_A, X_B, labels, feature_names = self.preprocessor.load_tuplet_dataset(dataset_path)

        # Split data (80% train, 10% val, 10% test)
        n_samples = len(labels)
        indices = np.random.permutation(n_samples)

        train_size = int(0.8 * n_samples)
        val_size = int(0.1 * n_samples)

        train_idx = indices[:train_size]
        val_idx = indices[train_size:train_size + val_size]
        test_idx = indices[train_size + val_size:]

        # Split data
        X_A_train, X_B_train, y_train = X_A[train_idx], X_B[train_idx], labels[train_idx]
        X_A_val, X_B_val, y_val = X_A[val_idx], X_B[val_idx], labels[val_idx]
        X_A_test, X_B_test, y_test = X_A[test_idx], X_B[test_idx], labels[test_idx]

        # Apply data augmentation to training data
        if self.config.training.get('use_augmentation', False):
            aug_factor = self.config.training.get('augmentation_factor', 5)
            logger.info(f"Applying {aug_factor}x data augmentation to tuplet training data...")

            X_A_train_aug, X_B_train_aug, y_train_aug = self.augment_tuplet_data(
                X_A_train, X_B_train, y_train, aug_factor
            )

            logger.info(f"Training data augmented: {len(y_train)} -> {len(y_train_aug)} pairs")
            X_A_train, X_B_train, y_train = X_A_train_aug, X_B_train_aug, y_train_aug

        # Normalize features
        from sklearn.preprocessing import RobustScaler
        scaler = RobustScaler()

        # Fit on training data
        X_A_train = scaler.fit_transform(X_A_train)
        X_B_train = scaler.transform(X_B_train)

        # Transform validation and test data
        X_A_val = scaler.transform(X_A_val)
        X_B_val = scaler.transform(X_B_val)
        X_A_test = scaler.transform(X_A_test)
        X_B_test = scaler.transform(X_B_test)

        # Convert to tensors
        X_A_train = torch.FloatTensor(X_A_train)
        X_B_train = torch.FloatTensor(X_B_train)
        y_train = torch.LongTensor(y_train)

        X_A_val = torch.FloatTensor(X_A_val)
        X_B_val = torch.FloatTensor(X_B_val)
        y_val = torch.LongTensor(y_val)

        X_A_test = torch.FloatTensor(X_A_test)
        X_B_test = torch.FloatTensor(X_B_test)
        y_test = torch.LongTensor(y_test)

        # Create datasets - store pairs
        train_dataset = TensorDataset(X_A_train, X_B_train, y_train)
        val_dataset = TensorDataset(X_A_val, X_B_val, y_val)
        test_dataset = TensorDataset(X_A_test, X_B_test, y_test)

        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=True,
            num_workers=0
        )

        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            num_workers=0
        )

        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            num_workers=0
        )

        logger.info(f"Tuplet dataset loaded:")
        logger.info(f"  Train: {len(train_dataset)} pairs")
        logger.info(f"  Val: {len(val_dataset)} pairs")
        logger.info(f"  Test: {len(test_dataset)} pairs")
        logger.info(f"  Features: {X_A_train.shape[1]}")

        # Store for model initialization
        self.input_dim = X_A_train.shape[1]
        self.use_tuplet = True

    def load_dsl_data(self):
        """Load and preprocess DSL dataset (original method)"""
        # Load DSL dataset
        dataset_path = os.path.join('Dataset', 'DSL-StrongPasswordData-Original_Dataset.xls')
        if not os.path.exists(dataset_path):
            # Try alternative path
            dataset_path = os.path.join('Keystroke Dynamics', 'Dataset',
                                       'DSL-StrongPasswordData-Original_Dataset.xls')

        df = self.preprocessor.load_dsl_dataset(dataset_path)

        # Split by subject
        train_df, val_df, test_df = self.preprocessor.split_by_subject(
            df,
            train_ratio=self.config.training.train_ratio,
            val_ratio=self.config.training.val_ratio
        )

        # Preprocess
        logger.info("Preprocessing training data...")
        X_train, y_train = self.preprocessor.preprocess_pipeline(
            train_df, fit=True, augment=True
        )

        logger.info("Preprocessing validation data...")
        X_val, y_val = self.preprocessor.preprocess_pipeline(
            val_df, fit=False, augment=False
        )

        logger.info("Preprocessing test data...")
        X_test, y_test = self.preprocessor.preprocess_pipeline(
            test_df, fit=False, augment=False
        )

        # Create data loaders
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        test_dataset = TensorDataset(X_test, y_test)
        
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=True,
            num_workers=0
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            num_workers=0
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.training.batch_size,
            shuffle=False,
            num_workers=0
        )
        
        logger.info(f"DSL dataset loaded:")
        logger.info(f"  Train: {len(train_dataset)} samples")
        logger.info(f"  Val: {len(val_dataset)} samples")
        logger.info(f"  Test: {len(test_dataset)} samples")

        # Store for model initialization
        self.input_dim = X_train.shape[1]
        self.use_tuplet = False
    
    def build_model(self, input_dim):
        """Build model and training components"""
        logger.info("Building model...")
        
        # Create model
        self.model = KeystrokeEmbeddingModel(input_dim, self.config)
        self.model = self.model.to(self.device)
        
        # Create loss function
        if self.config.training.loss_type == 'triplet':
            self.criterion = TripletLoss(margin=self.config.training.triplet_margin)
        elif self.config.training.loss_type == 'contrastive':
            self.criterion = ContrastiveLoss(margin=1.0)
        else:
            self.criterion = nn.CrossEntropyLoss()
        
        # Create optimizer
        if self.config.training.optimizer == 'adam':
            self.optimizer = optim.Adam(
                self.model.parameters(),
                lr=self.config.training.learning_rate,
                weight_decay=self.config.training.weight_decay
            )
        elif self.config.training.optimizer == 'sgd':
            self.optimizer = optim.SGD(
                self.model.parameters(),
                lr=self.config.training.learning_rate,
                momentum=0.9,
                weight_decay=self.config.training.weight_decay
            )
        
        # Create scheduler
        if self.config.training.scheduler == 'cosine':
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config.training.epochs
            )
        elif self.config.training.scheduler == 'step':
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=30,
                gamma=0.1
            )
        
        logger.info(f"Model built with {sum(p.numel() for p in self.model.parameters())} parameters")

    def train_epoch(self, epoch):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0

        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}/{self.config.training.epochs}")

        for batch_idx, batch in enumerate(pbar):
            if self.use_tuplet:
                # Tuplet dataset: (X_A, X_B, labels)
                data_a, data_b, labels = batch
                data_a = data_a.to(self.device)
                data_b = data_b.to(self.device)
                labels = labels.to(self.device)
            else:
                # DSL dataset: (data, labels)
                data, labels = batch
                data = data.to(self.device)
                labels = labels.to(self.device)

            self.optimizer.zero_grad()

            # Forward pass
            if self.use_tuplet:
                # For tuplet data, compute embeddings for both samples
                embeddings_a = self.model(data_a)
                embeddings_b = self.model(data_b)

                # Compute contrastive loss (1=genuine, 0=impostor)
                loss = self.compute_contrastive_loss_tuplet(embeddings_a, embeddings_b, labels)
            else:
                # For DSL data, use triplet loss
                embeddings = self.model(data)

                # Compute loss based on type
                if self.config.training.loss_type == 'triplet':
                    # Create triplets
                    loss = self.compute_triplet_loss(embeddings, labels)
                elif self.config.training.loss_type == 'contrastive':
                    loss = self.compute_contrastive_loss(embeddings, labels)
                else:
                    # Classification loss (would need classifier head)
                    loss = self.criterion(embeddings, labels)

            # Backward pass
            loss.backward()

            # Gradient clipping to prevent explosion
            if self.config.training.get('gradient_clipping', 0) > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.training.gradient_clipping
                )

            self.optimizer.step()

            total_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(self.train_loader)
        return avg_loss

    def compute_triplet_loss(self, embeddings, labels):
        """Compute triplet loss"""
        batch_size = embeddings.size(0)

        # Simple triplet mining: for each anchor, find positive and negative
        loss = torch.tensor(0.0, device=self.device, requires_grad=True)
        count = 0

        for i in range(batch_size):
            anchor = embeddings[i]
            anchor_label = labels[i]

            # Find positive (same label)
            pos_mask = (labels == anchor_label) & (torch.arange(batch_size, device=self.device) != i)
            if pos_mask.sum() > 0:
                pos_idx = torch.where(pos_mask)[0][0]
                positive = embeddings[pos_idx]

                # Find negative (different label)
                neg_mask = labels != anchor_label
                if neg_mask.sum() > 0:
                    neg_idx = torch.where(neg_mask)[0][0]
                    negative = embeddings[neg_idx]

                    # Compute triplet loss
                    triplet_loss = self.criterion(anchor.unsqueeze(0),
                                                 positive.unsqueeze(0),
                                                 negative.unsqueeze(0))
                    loss = loss + triplet_loss
                    count += 1

        if count > 0:
            return loss / count
        else:
            return loss

    def compute_contrastive_loss(self, embeddings, labels):
        """Compute contrastive loss"""
        batch_size = embeddings.size(0)

        loss = torch.tensor(0.0, device=self.device, requires_grad=True)
        count = 0

        for i in range(batch_size):
            for j in range(i+1, batch_size):
                emb1 = embeddings[i].unsqueeze(0)
                emb2 = embeddings[j].unsqueeze(0)
                label = (labels[i] == labels[j]).float().unsqueeze(0)

                contrastive_loss = self.criterion(emb1, emb2, label)
                loss = loss + contrastive_loss
                count += 1

        if count > 0:
            return loss / count
        else:
            return loss

    def compute_contrastive_loss_tuplet(self, embeddings_a, embeddings_b, labels):
        """
        Compute improved contrastive loss for tuplet data with hard mining

        Args:
            embeddings_a: Embeddings for sample A
            embeddings_b: Embeddings for sample B
            labels: 1 for genuine (same user), 0 for impostor (different users)
        """
        # Compute cosine similarity
        similarity = torch.nn.functional.cosine_similarity(embeddings_a, embeddings_b)

        # Convert labels to float (1.0 for genuine, 0.0 for impostor)
        labels_float = labels.float()

        # Use smaller margin for tighter clustering
        margin = self.config.training.get('triplet_margin', 0.2)

        # Loss for genuine pairs: (1 - similarity)^2
        genuine_loss = labels_float * torch.pow(1 - similarity, 2)

        # Loss for impostor pairs: max(0, similarity - margin)^2
        impostor_loss = (1 - labels_float) * torch.pow(torch.clamp(similarity - margin, min=0), 2)

        # Hard mining: focus on hard examples
        if self.config.training.get('use_hard_mining', False):
            # For genuine pairs: focus on those with low similarity (hard positives)
            genuine_mask = labels_float == 1
            if genuine_mask.sum() > 0:
                genuine_similarities = similarity[genuine_mask]
                # Weight hard positives (low similarity) more
                hard_positive_weights = 1.0 + (1.0 - genuine_similarities)
                genuine_loss[genuine_mask] = genuine_loss[genuine_mask] * hard_positive_weights

            # For impostor pairs: focus on those with high similarity (hard negatives)
            impostor_mask = labels_float == 0
            if impostor_mask.sum() > 0:
                impostor_similarities = similarity[impostor_mask]
                # Weight hard negatives (high similarity) more
                hard_negative_weights = 1.0 + impostor_similarities
                impostor_loss[impostor_mask] = impostor_loss[impostor_mask] * hard_negative_weights

        # Total loss
        loss = torch.mean(genuine_loss + impostor_loss)

        return loss

    def validate(self):
        """Validate model"""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in self.val_loader:
                if self.use_tuplet:
                    # Tuplet dataset: (X_A, X_B, labels)
                    data_a, data_b, labels = batch
                    data_a = data_a.to(self.device)
                    data_b = data_b.to(self.device)
                    labels = labels.to(self.device)

                    # Compute embeddings
                    embeddings_a = self.model(data_a)
                    embeddings_b = self.model(data_b)

                    # Compute loss
                    loss = self.compute_contrastive_loss_tuplet(embeddings_a, embeddings_b, labels)
                else:
                    # DSL dataset: (data, labels)
                    data, labels = batch
                    data = data.to(self.device)
                    labels = labels.to(self.device)

                    embeddings = self.model(data)

                    if self.config.training.loss_type == 'triplet':
                        loss = self.compute_triplet_loss(embeddings, labels)
                    elif self.config.training.loss_type == 'contrastive':
                        loss = self.compute_contrastive_loss(embeddings, labels)
                    else:
                        loss = self.criterion(embeddings, labels)

                total_loss += loss.item()

        avg_loss = total_loss / len(self.val_loader)
        return avg_loss

    def train(self):
        """Main training loop"""
        logger.info("Starting training...")

        patience_counter = 0

        for epoch in range(self.config.training.epochs):
            # Train
            train_loss = self.train_epoch(epoch)
            self.train_losses.append(train_loss)

            # Validate
            val_loss = self.validate()
            self.val_losses.append(val_loss)

            # Update scheduler
            if self.scheduler:
                self.scheduler.step()

            logger.info(f"Epoch {epoch+1}/{self.config.training.epochs} - "
                       f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

            # Save best model
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.save_checkpoint('best_model.pth')
                patience_counter = 0
                logger.info(f"New best model saved! Val Loss: {val_loss:.4f}")
            else:
                patience_counter += 1

            # Early stopping
            if patience_counter >= self.config.training.early_stopping_patience:
                logger.info(f"Early stopping triggered after {epoch+1} epochs")
                break

            # Save checkpoint every 10 epochs
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth')

        logger.info("Training completed!")
        self.plot_training_history()

    def save_checkpoint(self, filename):
        """Save model checkpoint"""
        checkpoint_dir = self.config.paths.checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

        filepath = os.path.join(checkpoint_dir, filename)

        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'config': self.config.to_dict()
        }, filepath)

        logger.debug(f"Checkpoint saved: {filepath}")

    def plot_training_history(self):
        """Plot training history"""
        plt.figure(figsize=(10, 6))
        plt.plot(self.train_losses, label='Train Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training History')
        plt.legend()
        plt.grid(True)

        plot_path = os.path.join(self.config.paths.logs_dir, 'training_history.png')
        plt.savefig(plot_path)
        logger.info(f"Training history plot saved: {plot_path}")
        plt.close()


def main():
    """Main training function"""
    # Setup logging
    logger.add("logs/training_{time}.log", rotation="100 MB")

    # Load configuration
    config = load_config('config.yaml')

    # Create trainer
    trainer = KeystrokeTrainer(config)

    # Load data
    trainer.load_data()

    # Build model
    trainer.build_model(trainer.input_dim)

    # Train
    trainer.train()

    logger.info("Training script completed successfully!")


if __name__ == '__main__':
    main()

