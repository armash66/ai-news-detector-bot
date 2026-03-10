# AI News Intelligence Model Training / Fine-tuning Guide

The backend includes a comprehensive training module to allow you to fine-tune standard Language Models (like `roberta-base` or `bert-base`) on your own custom datasets (like ISOT, FakeNewsNet, or LIAR).

## Step-by-Step Guide
All of the scripts for training are located in the `backend/training` directory.

### 1. Preparing the Dataset
You need a CSV file representing your structured dataset. 
- It must contain two key columns: `text` and `label`.
- `text`: The sequence/article body you want to model.
- `label`: Should be strictly numeric: `0` for **REAL**, `1` for **FAKE**.

Save your dataset anywhere on the disk, for instance `./data/my_custom_dataset.csv`.

### 2. Run the Training Script
Run the `train.py` script with your parameters. The script handles tokenization, shuffling, and the actual batch training with an elegant progress bar setup.

```powershell
python -m backend.training.train --dataset custom --train_file ./data/my_custom_dataset.csv --model roberta-base --epochs 3 --batch_size 16
```

#### Key Arguments:
- `--dataset`: Must be `custom` to use a custom file.
- `--train_file`: The direct path to your `.csv`.
- `--model`: Defines which HuggingFace model structure to load (e.g. `roberta-base`, `bert-base-uncased`, or `microsoft/deberta-v3-base`).
- `--epochs`: Number of learning epochs. Usually 3-5 is adequate for fine-tuning NLP.
- `--batch_size`: Based on your GPU memory. Use 8 or 16 for standard 8GB GPUs.

### 3. Evaluating 
Once trained, the `train.py` loop will automatically run an evaluation step against a validation slice of your data to show accuracy, precision, and f1-score.

The finalized model and its local tokenizer will be saved at `./checkpoints`.

### 4. Hooking the New Model into the API
To use your freshly trained model instead of the base web one, simply ensure your `.env` settings point to the checkpoint directory folder.

Update your `.env` file:
```env
MODEL_NAME=./checkpoints/roberta-base-finetuned
```
When you run `uvicorn backend.api.main:app`, the `ArticleAnalyzer` engine will automatically pick up your weights from the `./checkpoints` directory, and the dashboard will run off it instantly.
