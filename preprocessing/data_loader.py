"""
Data Loading and Preprocessing Module for NASA C-MAPSS Turbofan Engine Dataset.

Handles:
- Loading train/test/RUL data files
- Column naming
- RUL label generation (piecewise linear, capped at 125)
- Sensor normalization (MinMaxScaler)
- Sliding window sequence creation for LSTM input
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler


# ──────────────────────────────────────────────
# Column definitions for the C-MAPSS dataset
# ──────────────────────────────────────────────
INDEX_COLS = ["engine_id", "cycle"]
SETTING_COLS = [f"op_setting_{i}" for i in range(1, 4)]
SENSOR_COLS = [f"sensor_{i}" for i in range(1, 22)]
ALL_COLS = INDEX_COLS + SETTING_COLS + SENSOR_COLS

# Sensors that remain nearly constant and carry no useful degradation signal
DROP_SENSORS = ["sensor_1", "sensor_5", "sensor_6", "sensor_10",
                "sensor_16", "sensor_18", "sensor_19"]
DROP_SETTINGS = ["op_setting_3"]

FEATURES = [c for c in SENSOR_COLS + SETTING_COLS
            if c not in DROP_SENSORS and c not in DROP_SETTINGS]

# Maximum RUL cap – standard practice for C-MAPSS
RUL_CAP = 125


# ──────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────
def load_data(data_dir: str, dataset_id: str = "FD001"):
    """Load train, test, and RUL files for a given sub-dataset.

    Args:
        data_dir: Path to the directory containing the .txt files.
        dataset_id: One of 'FD001', 'FD002', 'FD003', 'FD004'.

    Returns:
        train_df, test_df, rul_df
    """
    train_path = os.path.join(data_dir, f"train_{dataset_id}.txt")
    test_path = os.path.join(data_dir, f"test_{dataset_id}.txt")
    rul_path = os.path.join(data_dir, f"RUL_{dataset_id}.txt")

    train_df = pd.read_csv(train_path, sep=r"\s+", header=None, names=ALL_COLS)
    test_df = pd.read_csv(test_path, sep=r"\s+", header=None, names=ALL_COLS)
    rul_df = pd.read_csv(rul_path, sep=r"\s+", header=None, names=["rul"])

    return train_df, test_df, rul_df


# ──────────────────────────────────────────────
# RUL label generation
# ──────────────────────────────────────────────
def add_rul_labels(df: pd.DataFrame, cap: int = RUL_CAP) -> pd.DataFrame:
    """Add a piecewise-linear RUL column, capped at `cap`.

    For training data the last cycle of each engine is its failure point,
    so RUL = max_cycle - current_cycle, clipped to [0, cap].
    """
    max_cycles = df.groupby("engine_id")["cycle"].max().reset_index()
    max_cycles.columns = ["engine_id", "max_cycle"]
    df = df.merge(max_cycles, on="engine_id", how="left")
    df["rul"] = df["max_cycle"] - df["cycle"]
    df["rul"] = df["rul"].clip(upper=cap)
    df.drop(columns=["max_cycle"], inplace=True)
    return df


def add_test_rul(test_df: pd.DataFrame, rul_df: pd.DataFrame,
                 cap: int = RUL_CAP) -> pd.DataFrame:
    """Attach ground-truth RUL to test data (last cycle per engine)."""
    max_cycles = test_df.groupby("engine_id")["cycle"].max().reset_index()
    max_cycles.columns = ["engine_id", "max_cycle"]

    rul_df = rul_df.copy()
    rul_df["engine_id"] = max_cycles["engine_id"]
    rul_df["max_cycle"] = max_cycles["max_cycle"]

    test_df = test_df.merge(max_cycles, on="engine_id", how="left")
    test_df = test_df.merge(rul_df[["engine_id", "rul"]], on="engine_id",
                            how="left", suffixes=("", "_ground"))

    # RUL for each row = ground_truth_rul + (max_cycle - cycle)
    test_df["rul"] = test_df["rul"] + (test_df["max_cycle"] - test_df["cycle"])
    test_df["rul"] = test_df["rul"].clip(upper=cap)
    test_df.drop(columns=["max_cycle"], inplace=True)
    return test_df


# ──────────────────────────────────────────────
# Normalisation
# ──────────────────────────────────────────────
def normalize_features(train_df: pd.DataFrame, test_df: pd.DataFrame,
                       features: list = None):
    """Fit MinMaxScaler on train, transform both train and test.

    Returns:
        train_df, test_df, scaler
    """
    if features is None:
        features = FEATURES
    scaler = MinMaxScaler()
    train_df[features] = scaler.fit_transform(train_df[features])
    test_df[features] = scaler.transform(test_df[features])
    return train_df, test_df, scaler


def save_scaler(scaler, path: str = "data/scaler.joblib"):
    """Persist a fitted scaler to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(scaler, path)


def load_scaler(path: str = "data/scaler.joblib"):
    """Load a previously saved scaler."""
    return joblib.load(path)


def normalize_with_scaler(df: pd.DataFrame, scaler,
                          features: list = None) -> pd.DataFrame:
    """Apply an already-fitted scaler to a DataFrame.

    Used for user-uploaded data in the prediction tab.
    """
    if features is None:
        features = FEATURES
    avail = [f for f in features if f in df.columns]
    df[avail] = scaler.transform(df[avail])
    return df


# ──────────────────────────────────────────────
# Sequence generation
# ──────────────────────────────────────────────
def create_sequences(df: pd.DataFrame, window: int = 30,
                     features: list = None):
    """Create sliding-window sequences for LSTM input.

    For each engine, slides a window of `window` cycles across the
    feature columns and takes the RUL of the last row in the window
    as the label.

    Returns:
        X  – np.ndarray of shape (num_samples, window, num_features)
        y  – np.ndarray of shape (num_samples,)
    """
    if features is None:
        features = FEATURES
    sequences, labels = [], []
    for eid in df["engine_id"].unique():
        engine = df[df["engine_id"] == eid].sort_values("cycle")
        data = engine[features].values
        rul = engine["rul"].values
        for i in range(len(data) - window + 1):
            sequences.append(data[i:i + window])
            labels.append(rul[i + window - 1])
    return np.array(sequences), np.array(labels)


def create_test_sequences(df: pd.DataFrame, window: int = 30,
                          features: list = None):
    """Create one sequence per engine from the last `window` cycles.

    If an engine has fewer than `window` cycles, it is padded with zeros
    at the front.

    Returns:
        X  – np.ndarray of shape (num_engines, window, num_features)
        y  – np.ndarray of shape (num_engines,)  ground-truth RUL
        engine_ids – list of engine IDs
    """
    if features is None:
        features = FEATURES
    sequences, labels, engine_ids = [], [], []
    for eid in df["engine_id"].unique():
        engine = df[df["engine_id"] == eid].sort_values("cycle")
        data = engine[features].values
        rul_val = engine["rul"].values[-1]
        if len(data) >= window:
            sequences.append(data[-window:])
        else:
            pad = np.zeros((window - len(data), len(features)))
            sequences.append(np.vstack([pad, data]))
        labels.append(rul_val)
        engine_ids.append(eid)
    return np.array(sequences), np.array(labels), engine_ids


# ──────────────────────────────────────────────
# Convenience wrapper
# ──────────────────────────────────────────────
def prepare_data(data_dir: str, dataset_id: str = "FD001", window: int = 30):
    """Full pipeline: load → label → normalise → sequence.

    RUL labels are normalised to [0, 1] by dividing by RUL_CAP so they
    match the scale of the normalised input features.  Callers must
    multiply predictions back by RUL_CAP to get actual cycle values.

    Returns:
        X_train, y_train, X_test, y_test, test_engine_ids, scaler,
        train_df, test_df
    """
    train_df, test_df, rul_df = load_data(data_dir, dataset_id)

    train_df = add_rul_labels(train_df)
    test_df = add_test_rul(test_df, rul_df)

    train_df, test_df, scaler = normalize_features(train_df, test_df)

    X_train, y_train = create_sequences(train_df, window)
    X_test, y_test, test_engine_ids = create_test_sequences(
        test_df, window)

    # Normalise RUL targets to [0, 1]
    y_train = y_train / RUL_CAP
    y_test  = y_test  / RUL_CAP

    print(f"[DataLoader] Dataset {dataset_id}")
    print(f"  Train sequences : {X_train.shape}")
    print(f"  Test  sequences : {X_test.shape}")
    print(f"  y_train range   : [{y_train.min():.3f}, {y_train.max():.3f}]")

    return (X_train, y_train, X_test, y_test,
            test_engine_ids, scaler, train_df, test_df)
