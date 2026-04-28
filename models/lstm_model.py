"""
LSTM Deep Learning Model for Remaining Useful Life (RUL) Prediction.

Architecture:
- 2 stacked LSTM layers with dropout
- Dense output layer (single neuron for RUL regression)
- Adam optimiser, MSE loss
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


def build_lstm_model(input_shape: tuple,
                     lstm_units_1: int = 128,
                     lstm_units_2: int = 64,
                     dropout_rate: float = 0.2,
                     learning_rate: float = 0.001) -> Sequential:
    """Build a 2-layer LSTM model for RUL prediction.

    Args:
        input_shape: (window_size, num_features)
        lstm_units_1: Units in the first LSTM layer.
        lstm_units_2: Units in the second LSTM layer.
        dropout_rate: Dropout rate after each LSTM layer.
        learning_rate: Adam learning rate.

    Returns:
        Compiled Keras Sequential model.
    """
    model = Sequential([
        LSTM(lstm_units_1, return_sequences=True,
             input_shape=input_shape, name="lstm_1"),
        Dropout(dropout_rate, name="dropout_1"),
        LSTM(lstm_units_2, return_sequences=False, name="lstm_2"),
        Dropout(dropout_rate, name="dropout_2"),
        Dense(32, activation="relu", name="dense_hidden"),
        Dense(1, activation="sigmoid", name="rul_output"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mse",
    )
    return model


def train_model(model, X_train, y_train,
                epochs: int = 50,
                batch_size: int = 256,
                validation_split: float = 0.2,
                patience: int = 10):
    """Train the model with early stopping.

    Returns:
        history – Keras History object.
    """
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=patience,
        restore_best_weights=True,
        verbose=1,
    )

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[early_stop],
        verbose=1,
    )
    return history


def evaluate_model(model, X_test, y_test):
    """Evaluate model and return RMSE and predictions.

    Returns:
        rmse, y_pred
    """
    y_pred = model.predict(X_test).flatten()
    rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
    print(f"[Model] Test RMSE: {rmse:.2f}")
    return rmse, y_pred


def save_trained_model(model, path: str = "data/trained_model.keras"):
    """Save the trained Keras model to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    model.save(path)
    print(f"[Model] Saved to {path}")


def load_trained_model(path: str = "data/trained_model.keras"):
    """Load a previously saved Keras model."""
    model = load_model(path)
    print(f"[Model] Loaded from {path}")
    return model
