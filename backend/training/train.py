"""
Training script for the misinformation detection transformer model.

Usage:
    python -m backend.training.train --dataset liar --model roberta-base --epochs 3

Supports:
  - Multiple dataset sources (LIAR, FakeNewsNet, ISOT, custom)
  - Multiple model architectures (BERT, RoBERTa, DeBERTa)
  - Mixed precision training
  - Early stopping
  - Checkpoint saving
  - Comprehensive logging with metrics
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup,
)

from backend.training.dataset_loader import DatasetLoader
from backend.training.preprocessing import TextPreprocessor
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger("training")


class NewsDataset(Dataset):
    """PyTorch dataset for news classification."""

    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])

        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "label": torch.tensor(label, dtype=torch.long),
        }


class Trainer:
    """Transformer model trainer for misinformation classification.

    Handles the full training loop including data preparation,
    optimization, evaluation, and checkpoint management.
    """

    def __init__(
        self,
        model_name: str = "roberta-base",
        num_labels: int = 2,
        max_length: int = 512,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        num_epochs: int = 3,
        warmup_ratio: float = 0.1,
        weight_decay: float = 0.01,
        output_dir: str = "./checkpoints",
        device: str = None,
    ):
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.warmup_ratio = warmup_ratio
        self.weight_decay = weight_decay
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Using device: %s", self.device)

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=num_labels
        )
        self.model.to(self.device)

        self.preprocessor = TextPreprocessor()
        self.training_history = []

    def prepare_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.15,
        val_size: float = 0.15,
    ):
        """Prepare train/val/test splits and create DataLoaders.

        Args:
            df: DataFrame with 'text' and 'label' columns.
            test_size: Fraction for test set.
            val_size: Fraction for validation set (from remaining after test split).
        """
        # Clean texts
        texts = self.preprocessor.clean_batch(df["text"].tolist())
        labels = df["label"].tolist()

        # Split: train -> (train + val) + test
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            train_texts, train_labels, test_size=val_size, random_state=42,
            stratify=train_labels,
        )

        logger.info(
            "Data splits - Train: %d, Val: %d, Test: %d",
            len(train_texts), len(val_texts), len(test_texts),
        )

        self.train_dataset = NewsDataset(
            train_texts, train_labels, self.tokenizer, self.max_length
        )
        self.val_dataset = NewsDataset(
            val_texts, val_labels, self.tokenizer, self.max_length
        )
        self.test_dataset = NewsDataset(
            test_texts, test_labels, self.tokenizer, self.max_length
        )

        self.train_loader = DataLoader(
            self.train_dataset, batch_size=self.batch_size, shuffle=True
        )
        self.val_loader = DataLoader(
            self.val_dataset, batch_size=self.batch_size
        )
        self.test_loader = DataLoader(
            self.test_dataset, batch_size=self.batch_size
        )

    def train(self) -> dict:
        """Execute the full training loop.

        Returns:
            Dictionary with training metrics and best checkpoint path.
        """
        # Optimizer
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_params = [
            {
                "params": [
                    p for n, p in self.model.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": self.weight_decay,
            },
            {
                "params": [
                    p for n, p in self.model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(optimizer_params, lr=self.learning_rate)

        total_steps = len(self.train_loader) * self.num_epochs
        warmup_steps = int(total_steps * self.warmup_ratio)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, warmup_steps, total_steps
        )

        # Mixed precision
        scaler = torch.amp.GradScaler("cuda") if self.device == "cuda" else None

        best_val_f1 = 0.0
        best_epoch = 0
        patience = 2
        patience_counter = 0

        logger.info("Starting training for %d epochs...", self.num_epochs)

        for epoch in range(self.num_epochs):
            # ---- Train ----
            self.model.train()
            total_loss = 0
            all_preds, all_labels = [], []

            for batch_idx, batch in enumerate(self.train_loader):
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                optimizer.zero_grad()

                if scaler:
                    with torch.amp.autocast("cuda"):
                        outputs = self.model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            labels=labels,
                        )
                    loss = outputs.loss
                    scaler.scale(loss).backward()
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels,
                    )
                    loss = outputs.loss
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    optimizer.step()

                scheduler.step()
                total_loss += loss.item()

                preds = torch.argmax(outputs.logits, dim=-1).cpu().tolist()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().tolist())

                if (batch_idx + 1) % 50 == 0:
                    logger.info(
                        "Epoch %d/%d | Batch %d/%d | Loss: %.4f",
                        epoch + 1, self.num_epochs,
                        batch_idx + 1, len(self.train_loader),
                        loss.item(),
                    )

            avg_train_loss = total_loss / len(self.train_loader)
            train_acc = accuracy_score(all_labels, all_preds)

            # ---- Validate ----
            val_metrics = self._evaluate(self.val_loader)

            epoch_metrics = {
                "epoch": epoch + 1,
                "train_loss": round(avg_train_loss, 4),
                "train_accuracy": round(train_acc, 4),
                "val_loss": val_metrics["loss"],
                "val_accuracy": val_metrics["accuracy"],
                "val_f1": val_metrics["f1"],
                "val_precision": val_metrics["precision"],
                "val_recall": val_metrics["recall"],
            }
            self.training_history.append(epoch_metrics)

            logger.info(
                "Epoch %d/%d | Train Loss: %.4f | Train Acc: %.4f | "
                "Val Loss: %.4f | Val F1: %.4f",
                epoch + 1, self.num_epochs,
                avg_train_loss, train_acc,
                val_metrics["loss"], val_metrics["f1"],
            )

            # Save best model
            if val_metrics["f1"] > best_val_f1:
                best_val_f1 = val_metrics["f1"]
                best_epoch = epoch + 1
                patience_counter = 0
                self._save_checkpoint(f"best_model")
                logger.info("New best model saved (F1: %.4f)", best_val_f1)
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    logger.info("Early stopping at epoch %d", epoch + 1)
                    break

        # ---- Test ----
        logger.info("Evaluating on test set...")
        self._load_checkpoint("best_model")
        test_metrics = self._evaluate(self.test_loader, detailed=True)

        results = {
            "model_name": self.model_name,
            "best_epoch": best_epoch,
            "best_val_f1": round(best_val_f1, 4),
            "test_metrics": test_metrics,
            "training_history": self.training_history,
            "checkpoint_path": str(self.output_dir / "best_model"),
        }

        # Save training report
        report_path = self.output_dir / "training_report.json"
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info("Training report saved to %s", report_path)

        return results

    def _evaluate(
        self, dataloader: DataLoader, detailed: bool = False
    ) -> dict:
        """Evaluate model on a given dataloader."""
        self.model.eval()
        total_loss = 0
        all_preds, all_labels = [], []

        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )

                total_loss += outputs.loss.item()
                preds = torch.argmax(outputs.logits, dim=-1).cpu().tolist()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().tolist())

        avg_loss = total_loss / len(dataloader)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average="binary", zero_division=0
        )
        accuracy = accuracy_score(all_labels, all_preds)

        metrics = {
            "loss": round(avg_loss, 4),
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }

        if detailed:
            metrics["classification_report"] = classification_report(
                all_labels, all_preds,
                target_names=["REAL", "FAKE"],
                output_dict=True,
            )
            metrics["confusion_matrix"] = confusion_matrix(
                all_labels, all_preds
            ).tolist()

            logger.info("\n%s", classification_report(
                all_labels, all_preds, target_names=["REAL", "FAKE"]
            ))

        return metrics

    def _save_checkpoint(self, name: str) -> None:
        """Save model checkpoint."""
        path = self.output_dir / name
        path.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)

    def _load_checkpoint(self, name: str) -> None:
        """Load model checkpoint."""
        path = self.output_dir / name
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        self.model.to(self.device)


def main():
    parser = argparse.ArgumentParser(description="Train misinformation detection model")
    parser.add_argument(
        "--dataset", type=str, default="liar",
        choices=["liar", "politifact", "gossipcop", "isot"],
        help="Dataset to train on",
    )
    parser.add_argument(
        "--model", type=str, default="roberta-base",
        help="HuggingFace model name",
    )
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--output-dir", type=str, default="./checkpoints")
    parser.add_argument("--data-dir", type=str, default="./data")

    args = parser.parse_args()

    # Load dataset
    loader = DatasetLoader(data_dir=args.data_dir)
    df = loader.load(args.dataset)

    # Initialize trainer
    trainer = Trainer(
        model_name=args.model,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_length=args.max_length,
        output_dir=args.output_dir,
    )

    # Prepare data and train
    trainer.prepare_data(df)
    results = trainer.train()

    logger.info("Training complete!")
    logger.info("Best Val F1: %.4f (Epoch %d)", results["best_val_f1"], results["best_epoch"])
    logger.info("Test metrics: %s", json.dumps(results["test_metrics"], indent=2))


if __name__ == "__main__":
    main()
