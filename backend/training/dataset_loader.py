"""
Dataset loader for misinformation detection datasets.

Supports:
  - LIAR dataset (6-class -> binary)
  - FakeNewsNet (PolitiFact / GossipCop)
  - ISOT Fake News dataset
  - Custom CSV/JSON datasets

All loaders return a unified format: list of (text, label) tuples
where label is 0 (REAL) or 1 (FAKE).
"""

import json
from pathlib import Path
from typing import Optional

import pandas as pd

from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger("dataset_loader")


class DatasetLoader:
    """Unified loader for multiple fake news datasets.

    Normalizes all datasets into a consistent (text, label) format
    suitable for training transformer classifiers.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else settings.data_dir

    def load_liar(self, split: str = "train") -> pd.DataFrame:
        """Load the LIAR dataset.

        The LIAR dataset uses 6-class labels which are mapped to binary:
          REAL: true, mostly-true, half-true
          FAKE: barely-true, false, pants-fire

        Expected files: train.tsv, valid.tsv, test.tsv in data_dir/liar/

        Args:
            split: One of 'train', 'valid', 'test'.

        Returns:
            DataFrame with 'text' and 'label' columns.
        """
        liar_dir = self.data_dir / "liar"
        file_map = {
            "train": "train.tsv",
            "valid": "valid.tsv",
            "test": "test.tsv",
        }
        filepath = liar_dir / file_map.get(split, "train.tsv")

        if not filepath.exists():
            raise FileNotFoundError(
                f"LIAR dataset not found at {filepath}. "
                f"Download from: https://www.cs.ucsb.edu/~william/data/liar_dataset.zip"
            )

        # LIAR TSV has no header; column 2 is label, column 3 is statement
        columns = [
            "id", "label_raw", "statement", "subject", "speaker",
            "job_title", "state_info", "party_affiliation",
            "barely_true", "false_count", "half_true",
            "mostly_true", "pants_on_fire", "context",
        ]
        df = pd.read_csv(filepath, sep="\t", header=None, names=columns)

        # Map to binary
        real_labels = {"true", "mostly-true", "half-true"}
        fake_labels = {"barely-true", "false", "pants-fire"}

        df["label"] = df["label_raw"].apply(
            lambda x: 0 if x in real_labels else (1 if x in fake_labels else -1)
        )
        df = df[df["label"] != -1]
        df["text"] = df["statement"]

        logger.info(
            "Loaded LIAR %s: %d samples (REAL: %d, FAKE: %d)",
            split, len(df),
            (df["label"] == 0).sum(),
            (df["label"] == 1).sum(),
        )
        return df[["text", "label"]].reset_index(drop=True)

    def load_fakenewsnet(
        self,
        source: str = "politifact",
    ) -> pd.DataFrame:
        """Load FakeNewsNet dataset (PolitiFact or GossipCop).

        Expected structure:
          data_dir/fakenewsnet/{source}/real.csv
          data_dir/fakenewsnet/{source}/fake.csv

        Each CSV should have at least a 'title' or 'text' column.

        Args:
            source: 'politifact' or 'gossipcop'.

        Returns:
            DataFrame with 'text' and 'label' columns.
        """
        base = self.data_dir / "fakenewsnet" / source

        real_path = base / "real.csv"
        fake_path = base / "fake.csv"

        if not real_path.exists() or not fake_path.exists():
            raise FileNotFoundError(
                f"FakeNewsNet data not found at {base}. "
                "Download from: https://github.com/KaiDMML/FakeNewsNet"
            )

        real_df = pd.read_csv(real_path)
        fake_df = pd.read_csv(fake_path)

        # Use 'text' or 'title' column
        text_col = "text" if "text" in real_df.columns else "title"

        real_df = real_df[[text_col]].rename(columns={text_col: "text"})
        real_df["label"] = 0

        fake_df = fake_df[[text_col]].rename(columns={text_col: "text"})
        fake_df["label"] = 1

        df = pd.concat([real_df, fake_df], ignore_index=True)
        df = df.dropna(subset=["text"])

        logger.info(
            "Loaded FakeNewsNet/%s: %d samples (REAL: %d, FAKE: %d)",
            source, len(df),
            (df["label"] == 0).sum(),
            (df["label"] == 1).sum(),
        )
        return df[["text", "label"]].reset_index(drop=True)

    def load_isot(self) -> pd.DataFrame:
        """Load ISOT Fake News dataset.

        Expected files:
          data_dir/isot/True.csv
          data_dir/isot/Fake.csv

        Returns:
            DataFrame with 'text' and 'label' columns.
        """
        isot_dir = self.data_dir / "isot"
        true_path = isot_dir / "True.csv"
        fake_path = isot_dir / "Fake.csv"

        if not true_path.exists() or not fake_path.exists():
            raise FileNotFoundError(
                f"ISOT dataset not found at {isot_dir}. "
                "Download from: https://www.uvic.ca/ecs/ece/isot/datasets/fake-news/index.php"
            )

        true_df = pd.read_csv(true_path)
        fake_df = pd.read_csv(fake_path)

        # Combine title and text
        true_df["text"] = true_df["title"] + ". " + true_df["text"]
        true_df["label"] = 0

        fake_df["text"] = fake_df["title"] + ". " + fake_df["text"]
        fake_df["label"] = 1

        df = pd.concat([true_df[["text", "label"]], fake_df[["text", "label"]]], ignore_index=True)
        df = df.dropna(subset=["text"])

        logger.info(
            "Loaded ISOT: %d samples (REAL: %d, FAKE: %d)",
            len(df),
            (df["label"] == 0).sum(),
            (df["label"] == 1).sum(),
        )
        return df

    def load_custom(
        self,
        filepath: str,
        text_column: str = "text",
        label_column: str = "label",
    ) -> pd.DataFrame:
        """Load a custom dataset from CSV or JSON.

        Args:
            filepath: Path to the dataset file.
            text_column: Name of the text column.
            label_column: Name of the label column.

        Returns:
            DataFrame with 'text' and 'label' columns.
        """
        path = Path(filepath)
        if path.suffix == ".csv":
            df = pd.read_csv(path)
        elif path.suffix == ".json":
            df = pd.read_json(path)
        elif path.suffix == ".jsonl":
            with open(path) as f:
                records = [json.loads(line) for line in f]
            df = pd.DataFrame(records)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        df = df.rename(columns={text_column: "text", label_column: "label"})
        df = df[["text", "label"]].dropna()

        logger.info("Loaded custom dataset: %d samples from %s", len(df), filepath)
        return df

    def load(
        self,
        dataset_name: str,
        **kwargs,
    ) -> pd.DataFrame:
        """Unified loader interface.

        Args:
            dataset_name: One of 'liar', 'politifact', 'gossipcop', 'isot'.
            **kwargs: Additional arguments for the specific loader.

        Returns:
            DataFrame with 'text' and 'label' columns.
        """
        loaders = {
            "liar": self.load_liar,
            "politifact": lambda **kw: self.load_fakenewsnet("politifact", **kw),
            "gossipcop": lambda **kw: self.load_fakenewsnet("gossipcop", **kw),
            "isot": self.load_isot,
        }

        loader = loaders.get(dataset_name.lower())
        if loader is None:
            raise ValueError(
                f"Unknown dataset: {dataset_name}. "
                f"Available: {list(loaders.keys())}"
            )
        return loader(**kwargs)
