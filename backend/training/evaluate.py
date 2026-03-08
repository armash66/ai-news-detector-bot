"""
Evaluation script for trained models.

Usage:
    python -m backend.training.evaluate --checkpoint ./checkpoints/best_model --dataset liar --split test

Produces:
  - Classification report
  - Confusion matrix
  - Per-class metrics
  - Saves evaluation report to JSON
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from backend.training.dataset_loader import DatasetLoader
from backend.training.preprocessing import TextPreprocessor
from backend.training.train import NewsDataset
from backend.utils.logger import get_logger

logger = get_logger("evaluation")


def evaluate_model(
    checkpoint_path: str,
    dataset_name: str,
    split: str = "test",
    data_dir: str = "./data",
    batch_size: int = 32,
    max_length: int = 512,
    output_file: str = None,
) -> dict:
    """Evaluate a trained model on a dataset split.

    Args:
        checkpoint_path: Path to model checkpoint.
        dataset_name: Dataset to evaluate on.
        split: Dataset split ('train', 'valid', 'test').
        data_dir: Root data directory.
        batch_size: Evaluation batch size.
        max_length: Max sequence length.
        output_file: Optional path to save results JSON.

    Returns:
        Dictionary with evaluation metrics.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Device: %s", device)

    # Load model
    logger.info("Loading model from %s", checkpoint_path)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
    model.to(device)
    model.eval()

    # Load data
    loader = DatasetLoader(data_dir=data_dir)
    if dataset_name == "liar":
        df = loader.load_liar(split=split)
    else:
        df = loader.load(dataset_name)

    preprocessor = TextPreprocessor()
    texts = preprocessor.clean_batch(df["text"].tolist())
    labels = df["label"].tolist()

    dataset = NewsDataset(texts, labels, tokenizer, max_length)
    dataloader = DataLoader(dataset, batch_size=batch_size)

    # Evaluate
    all_preds = []
    all_labels = []
    all_probs = []

    logger.info("Evaluating on %d samples...", len(dataset))

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            batch_labels = batch["label"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()

            preds = np.argmax(probs, axis=-1).tolist()
            all_preds.extend(preds)
            all_labels.extend(batch_labels.cpu().tolist())
            all_probs.extend(probs.tolist())

    # Compute metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average="binary", zero_division=0
    )
    accuracy = accuracy_score(all_labels, all_preds)

    # AUC
    try:
        probs_positive = [p[1] for p in all_probs]
        auc = roc_auc_score(all_labels, probs_positive)
    except Exception:
        auc = None

    report = classification_report(
        all_labels, all_preds,
        target_names=["REAL", "FAKE"],
        output_dict=True,
    )
    cm = confusion_matrix(all_labels, all_preds).tolist()

    results = {
        "checkpoint": checkpoint_path,
        "dataset": dataset_name,
        "split": split,
        "num_samples": len(dataset),
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "auc_roc": round(auc, 4) if auc else None,
        "classification_report": report,
        "confusion_matrix": cm,
    }

    # Print results
    logger.info("\n--- Evaluation Results ---")
    logger.info("Accuracy:  %.4f", accuracy)
    logger.info("Precision: %.4f", precision)
    logger.info("Recall:    %.4f", recall)
    logger.info("F1 Score:  %.4f", f1)
    if auc:
        logger.info("AUC-ROC:   %.4f", auc)
    logger.info("\n%s", classification_report(
        all_labels, all_preds, target_names=["REAL", "FAKE"]
    ))
    logger.info("Confusion Matrix:\n%s", np.array(cm))

    # Save results
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info("Results saved to %s", output_file)

    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate misinformation detection model")
    parser.add_argument(
        "--checkpoint", type=str, required=True,
        help="Path to model checkpoint directory",
    )
    parser.add_argument(
        "--dataset", type=str, default="liar",
        choices=["liar", "politifact", "gossipcop", "isot"],
    )
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--data-dir", type=str, default="./data")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--output", type=str, default=None)

    args = parser.parse_args()

    evaluate_model(
        checkpoint_path=args.checkpoint,
        dataset_name=args.dataset,
        split=args.split,
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        max_length=args.max_length,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
