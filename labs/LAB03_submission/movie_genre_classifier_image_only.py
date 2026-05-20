"""
Lab 3 — Part B: ResNet18 Drop-In Image Branch
==============================================
Copy your completed movie_genre_classifier.py into this file, then
replace the ImageBranch class with the ResNet18 version below.
Everything else (TabularBranch, FusionHead, Dataset, training) should
remain identical to Part A.
"""

# YOUR CODE HERE
# Paste your completed Part A code here, then replace ImageBranch
# with the class below. No other changes should be needed.


# =============================================================================
# PROVIDED: ResNet18 ImageBranch (replaces your Part A ImageBranch)
# =============================================================================

import torch
import torch.nn as nn
from torchvision import models





# =========================

"""
Lab 3 — Part A: Multimodal Movie Genre Classifier
==================================================
Complete this file to build and train your multimodal neural network.
How you structure the training script (entry point, argument handling, etc.)
is up to you.
"""

import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from tqdm import tqdm


# =============================================================================
# Constants — adjust these to control model complexity
# =============================================================================

GENRES = ["Animation", "Comedy", "Documentary", "Horror", "Romance", "Sci-Fi"]

NUMERIC_COLS = ["runtime", "vote_average", "vote_count",
                "release_year", "popularity", "budget", "revenue"]

# Pipe-separated list fields — each gets its own embedding vocabulary
LIST_FIELDS = ["cast", "directors", "writers", "production_companies"]

# Single-value categorical fields
SINGLE_CAT_FIELDS = ["mpaa_rating"]

IMAGE_SIZE   = 128   # poster resize target (pixels)
MAX_LIST_LEN = 20    # pad/truncate list fields to this many tokens
TOP_N_VOCAB  = 50    # keep only top-N tokens per field by training frequency
EMBED_DIM    = 32    # embedding dimension for all categorical fields


# =============================================================================
# PROVIDED: VocabBuilder
# =============================================================================

class VocabBuilder:
    """
    Builds integer vocabularies for pipe-separated categorical fields.
    Fit ONLY on training data — fitting on val/test is data leakage.

    Token index conventions:
        0 = <PAD>  — padding
        1 = <UNK>  — unknown token (not in top-N at training time)
        2+ = actual tokens, ordered by training frequency
    """

    PAD_IDX = 0
    UNK_IDX = 1

    def __init__(self, top_n=TOP_N_VOCAB):
        self.top_n  = top_n
        self.vocabs = {}
        self.sizes  = {}

    def fit(self, df):
        for field in LIST_FIELDS:
            if field not in df.columns:
                continue
            counts = Counter()
            for val in df[field].dropna():
                if val:
                    counts.update(v.strip() for v in str(val).split("|") if v.strip())
            top_tokens = [tok for tok, _ in counts.most_common(self.top_n)]
            vocab = {tok: idx + 2 for idx, tok in enumerate(top_tokens)}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2

        for field in SINGLE_CAT_FIELDS:
            if field not in df.columns:
                continue
            unique_vals = [v for v in df[field].unique()
                           if isinstance(v, str) and v.strip()]
            vocab = {v: idx + 2 for idx, v in enumerate(sorted(unique_vals))}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2
        return self

    def encode_list(self, val, field, max_len=MAX_LIST_LEN):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return [self.PAD_IDX] * max_len
        tokens = [v.strip() for v in val.split("|") if v.strip()]
        ids = [vocab.get(tok, self.UNK_IDX) for tok in tokens]
        ids = ids[:max_len]
        ids += [self.PAD_IDX] * (max_len - len(ids))
        return ids

    def encode_single(self, val, field):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return self.PAD_IDX
        return vocab.get(val.strip(), self.UNK_IDX)

    def save(self, path):
        data = {"vocabs": self.vocabs, "sizes": self.sizes, "top_n": self.top_n}
        Path(path).write_text(json.dumps(data))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        vb = cls(top_n=data["top_n"])
        vb.vocabs = data["vocabs"]
        vb.sizes  = data["sizes"]
        return vb


# =============================================================================
# PROVIDED: NumericScaler
# =============================================================================

class NumericScaler:
    """
    Standardises numeric features to zero mean, unit variance.
    Fit on training data only. Missing values are imputed with the training mean.
    """

    def __init__(self):
        self.means = {}
        self.stds  = {}

    def fit(self, df):
        for col in NUMERIC_COLS:
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce")
                self.means[col] = float(vals.mean())
                self.stds[col]  = max(float(vals.std()), 1e-8)
        return self

    def transform(self, df):
        result = {}
        for col in NUMERIC_COLS:
            vals = pd.to_numeric(df[col], errors="coerce") if col in df.columns \
                   else pd.Series([float("nan")] * len(df))
            vals = vals.fillna(self.means.get(col, 0.0))
            mean = self.means.get(col, 0.0)
            std  = self.stds.get(col, 1.0)
            result[col] = ((vals - mean) / std).values.astype(np.float32)
        return result

    def save(self, path):
        Path(path).write_text(json.dumps({"means": self.means, "stds": self.stds}))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        ns = cls()
        ns.means = data["means"]
        ns.stds  = data["stds"]
        return ns


# =============================================================================
# YOUR CODE: Dataset
# =============================================================================

class MoviePosterDataset(Dataset):
    """
    Loads a split (train / val / test) and returns one sample per film.

    Each sample should contain:
      - The poster image as a tensor
      - The numeric features as a tensor
      - Encoded list-field tensors (one per field in LIST_FIELDS)
      - The MPAA rating as an integer index
      - The genre label as an integer index
    """

    def __init__(self, df, image_dir, vocab_builder, numeric_scaler,
                 transform=None):
        # YOUR CODE HERE
        self.df = df.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.vocab_builder = vocab_builder
        self.transform = transform
        numeric_dict = numeric_scaler.transform(df)
        self.numeric = np.stack([numeric_dict[col] for col in NUMERIC_COLS], axis=1)
        self.label_map = {genre: idx for idx, genre in enumerate(GENRES)}
        
    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # YOUR CODE HERE
        row = self.df.iloc[idx]
        try:
            image = Image.open(self.image_dir / row["image_path"]).convert("RGB")
        except Exception as e:
            print(f"Error loading image for index {idx}: {e}")
            image = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE))
        image = self.transform(image)
        numeric = torch.tensor(self.numeric[idx])
        cat_fields = {field: torch.tensor(self.vocab_builder.encode_list(row[field], field), dtype=torch.long)
                       for field in LIST_FIELDS}
        cat_fields["mpaa_rating"] = torch.tensor(self.vocab_builder.encode_single(row["mpaa_rating"], "mpaa_rating"), dtype=torch.long)
        label = self.label_map[row["label"]]
        return {"image": image,
                "numeric": numeric,
                "cat_fields": cat_fields,
                "label": label}
        

# =============================================================================
# YOUR CODE: Image Branch
# =============================================================================

class ImageBranch(nn.Module):
    """
    Transfer learning image encoder: pretrained ResNet18 backbone
    with a small trainable projection head.

    The entire backbone is frozen by default (only the head trains).
    Optionally, the last residual block (layer4) can be unfrozen for
    fine-tuning once the head has converged.
    """

    BACKBONE_OUT_DIM = 512  # ResNet18 feature dimension after global average pool

    def __init__(self, out_dim=256, dropout=0.4, fine_tune=False):
        super().__init__()

        # Load ResNet18 with pretrained ImageNet weights
        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        # Freeze ALL backbone parameters
        for param in backbone.parameters():
            param.requires_grad = False

        # (Optional) Unfreeze the last residual block for fine-tuning
        if fine_tune:
            for param in backbone.layer4.parameters():
                param.requires_grad = True

        # Remove the original FC classification head; keep up to avgpool
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])
        # Output: (batch, 512, 1, 1)

        # Trainable projection head
        self.head = nn.Sequential(
            nn.Flatten(),                              # (batch, 512)
            nn.Dropout(dropout),
            nn.Linear(self.BACKBONE_OUT_DIM, out_dim),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        features = self.backbone(x)   # (batch, 512, 1, 1) — frozen
        return self.head(features)    # (batch, out_dim)   — trained


# =============================================================================
# YOUR CODE: Tabular Branch
# =============================================================================

class TabularBranch(nn.Module):
    """
    Takes numeric features and categorical embeddings and produces a feature vector.

    Consider two sub-branches:
      - Numeric: FC layers over the standardised numeric features
      - Embedding: one nn.Embedding table per field, pool tokens -> concat -> FC

    Then merge the two sub-branches into a single output vector.
    """

    def __init__(self, vocab_sizes, out_dim=256):
        super().__init__()
        # YOUR CODE HERE
        self.numeric_hidden = nn.Sequential(
            nn.Linear(len(NUMERIC_COLS), 128),
            nn.ReLU(),
            nn.Dropout(p=0.25)
        )
        self.embeddings = nn.ModuleDict({
            field: nn.Embedding(vocab_sizes[field], EMBED_DIM, padding_idx=0) for field in LIST_FIELDS + SINGLE_CAT_FIELDS
        })
        self.embed_hidden = nn.Sequential(
            nn.Linear(len(LIST_FIELDS + SINGLE_CAT_FIELDS)*EMBED_DIM, 128),
            nn.ReLU(),
            nn.Dropout(p=0.25)
        )
        self.final = nn.Linear(128 + 128, out_dim)
        # vocab_sizes is a dict: {field_name: int} from vocab_builder.sizes

    def forward(self, numeric, cat_fields):
        # YOUR CODE HERE
        numeric_features = self.numeric_hidden(numeric)
        embed_features = []
        for field, embedding in self.embeddings.items():
            if field in cat_fields:
                embedded = embedding(cat_fields[field])
                if len(embedded.shape) == 3:  # list field
                    mask = (cat_fields[field] != 0).float().unsqueeze(-1)
                    n = mask.sum(dim=1).clamp(min=1)
                    pooled = (embedded*mask).sum(dim=1) / n
                else:  # single-cat field
                    pooled = embedded
                embed_features.append(pooled)
            else:
                embed_features.append(torch.zeros(numeric.size(0), EMBED_DIM, device=numeric.device))
        embed_features = torch.stack(embed_features, dim=1).view(numeric.size(0), -1)
        embed_features = self.embed_hidden(embed_features)
        return self.final(torch.cat([numeric_features, embed_features], dim=1))
        # numeric:    (batch, len(NUMERIC_COLS)) float tensor
        # cat_fields: dict of {field_name: (batch, MAX_LIST_LEN) int tensor}
        #             plus mpaa_rating as a (batch,) int tensor


# =============================================================================
# YOUR CODE: Fusion Head
# =============================================================================

class FusionHead(nn.Module):
    """
    Concatenates image and tabular feature vectors and predicts genre.
    Output: (batch, num_classes) logits (no softmax — use CrossEntropyLoss).
    """

    def __init__(self, image_dim, tabular_dim, num_classes=len(GENRES)):
        super().__init__()
        # YOUR CODE HERE
        self.net = nn.Sequential(
            nn.Linear(image_dim + tabular_dim, 128),
            nn.ReLU(),
            nn.Dropout(p=0.25),
            nn.Linear(128, num_classes)
        )

    def forward(self, image_features, tabular_features):
        # YOUR CODE HERE
        return self.net(torch.cat([image_features, tabular_features], dim=1))


# =============================================================================
# YOUR CODE: Full Model
# =============================================================================

class MultimodalGenreClassifier(nn.Module):
    """Wires ImageBranch, TabularBranch, and FusionHead together."""

    def __init__(self, vocab_sizes):
        super().__init__()
        # YOUR CODE HERE
        self.image_branch = ImageBranch(out_dim=256)
        # self.tabular_branch = TabularBranch(vocab_sizes=vocab_sizes, out_dim=256)
        self.fusion_head = FusionHead(image_dim=256, tabular_dim=0, num_classes=len(GENRES))

    def forward(self, image, numeric, cat_fields):
        # YOUR CODE HERE
        image_features = self.image_branch(image)
        # tabular_features = self.tabular_branch(numeric, cat_fields)
        dummy = torch.zeros(image.size(0), 0, device=image.device)
        return self.fusion_head(image_features, dummy)


# =============================================================================
# YOUR CODE: Training
# =============================================================================
# How you structure training is up to you.
# Your script must:
#   - Load the three manifest CSVs
#   - Fit VocabBuilder and NumericScaler on the training set only
#   - Build Datasets and DataLoaders for each split
#   - Train for multiple epochs, reporting validation accuracy each epoch
#   - Save the best model checkpoint
#   - Print per-class accuracy on the test set at the end
#
# Device setup (works locally and on Colab GPU):
#   device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

DATA_DIR = Path("../../data/movie_posters")
CSV_PATHS = {
    "train": DATA_DIR / "train_manifest.csv",
    "val":   DATA_DIR / "val_manifest.csv",
    "test":  DATA_DIR / "test_manifest.csv"
}
BATCH_SIZE = 32
NUM_EPOCHS = 10
LEARNING_RATE = 0.001

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_df = pd.read_csv(CSV_PATHS["train"])
val_df = pd.read_csv(CSV_PATHS["val"])
test_df = pd.read_csv(CSV_PATHS["test"])

vocab_builder = VocabBuilder().fit(train_df)
numeric_scaler = NumericScaler().fit(train_df)

train_transform = transforms.Compose([
    transforms.Resize(128),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

eval_transform = transforms.Compose([
    transforms.Resize(128),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

train_ds = MoviePosterDataset(train_df, DATA_DIR, vocab_builder, numeric_scaler, train_transform)
val_ds = MoviePosterDataset(val_df, DATA_DIR, vocab_builder, numeric_scaler, eval_transform)
test_ds = MoviePosterDataset(test_df, DATA_DIR, vocab_builder, numeric_scaler, eval_transform)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

model = MultimodalGenreClassifier(vocab_sizes=vocab_builder.sizes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=0.0001)

best_val_acc = 0.0

for epoch in range(NUM_EPOCHS):
    model.train()
    total_loss = 0
    train_acc = 0
    correct, total = 0, 0
    for batch in train_loader:
        images = batch["image"].to(device)
        numeric = batch["numeric"].to(device)
        cat_fields = {field: batch["cat_fields"][field].to(device) for field in LIST_FIELDS + SINGLE_CAT_FIELDS}
        labels = batch["label"].to(device)
        outputs = model(images, numeric, cat_fields)
        loss = criterion(outputs, labels)
        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        train_acc = correct / total
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    avg_loss = total_loss / len(train_loader)
    model.eval()
    val_acc = 0
    correct, total = 0, 0
    with torch.no_grad():
        for batch in val_loader:
            images = batch["image"].to(device)
            numeric = batch["numeric"].to(device)
            cat_fields = {field: batch["cat_fields"][field].to(device) for field in LIST_FIELDS + SINGLE_CAT_FIELDS}
            labels = batch["label"].to(device)
            outputs = model(images, numeric, cat_fields)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            val_acc = correct / total
        print(f"Epoch {epoch+1}/{NUM_EPOCHS}, Train Loss: {avg_loss:.4f}, Train Accuracy: {(100 * train_acc):.2f}%, Val Accuracy: {(100 * val_acc):.2f}%")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_model.pth")
            print("Saved new best checkpoint!")

model.load_state_dict(torch.load("best_model.pth", map_location=device))
model.eval()
class_correct = [0] * len(GENRES)
class_total = [0] * len(GENRES)
with torch.no_grad():
    for batch in test_loader:
        images = batch["image"].to(device)
        numeric = batch["numeric"].to(device)
        cat_fields = {field: batch["cat_fields"][field].to(device) for field in LIST_FIELDS + SINGLE_CAT_FIELDS}
        labels = batch["label"].to(device)
        outputs = model(images, numeric, cat_fields)
        _, predicted = torch.max(outputs, 1)
        for i in range(labels.size(0)):
            label = labels[i].item()
            class_total[label] += 1
            if predicted[i].item() == label:
                class_correct[label] += 1

for i in range(len(GENRES)):
    if class_total[i] > 0:
        print(f"Accuracy for {GENRES[i]}: {(100 * class_correct[i] / class_total[i]):.2f}%")
