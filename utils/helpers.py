"""
Plotting and general utility functions.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (safe for servers)
import matplotlib.pyplot as plt
import seaborn as sns


def plot_sensor_trends(engine_df: pd.DataFrame,
                       sensor_cols: list,
                       engine_id: int = None,
                       max_sensors: int = 6):
    """Plot selected sensor values vs cycle for one engine.

    Returns a matplotlib Figure.
    """
    cols = sensor_cols[:max_sensors]
    n = len(cols)
    fig, axes = plt.subplots(n, 1, figsize=(10, 2.5 * n), sharex=True)
    if n == 1:
        axes = [axes]

    title = "Sensor Degradation Trends"
    if engine_id is not None:
        title += f" — Engine {engine_id}"
    fig.suptitle(title, fontsize=14, fontweight="bold")

    for ax, col in zip(axes, cols):
        ax.plot(engine_df["cycle"], engine_df[col], linewidth=1.2)
        ax.set_ylabel(col, fontsize=9)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Cycle")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def plot_predicted_vs_actual(y_true: np.ndarray, y_pred: np.ndarray,
                             title: str = "Predicted vs Actual RUL"):
    """Scatter plot comparing predicted and actual RUL values.

    Returns a matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_true, y_pred, alpha=0.5, edgecolors="k", linewidths=0.3, s=30)
    lims = [0, max(y_true.max(), y_pred.max()) + 10]
    ax.plot(lims, lims, "r--", linewidth=1.5, label="Ideal")
    ax.set_xlabel("Actual RUL (cycles)")
    ax.set_ylabel("Predicted RUL (cycles)")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_rul_distribution(y_pred: np.ndarray, engine_ids: list):
    """Bar chart of predicted RUL per engine with colour-coded risk.

    Returns a matplotlib Figure.
    """
    colours = []
    for r in y_pred:
        if r <= 50:
            colours.append("#e74c3c")
        elif r <= 100:
            colours.append("#f39c12")
        else:
            colours.append("#2ecc71")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(len(engine_ids)), y_pred, color=colours, edgecolor="k",
           linewidth=0.3)
    ax.set_xlabel("Engine Index")
    ax.set_ylabel("Predicted RUL (cycles)")
    ax.set_title("Predicted RUL per Engine")
    ax.axhline(y=50, color="#e74c3c", linestyle="--", alpha=0.6, label="Critical (≤50)")
    ax.axhline(y=100, color="#f39c12", linestyle="--", alpha=0.6, label="Moderate (≤100)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


def plot_training_history(history):
    """Plot training and validation loss curves.

    Returns a matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(history.history["loss"], label="Training Loss")
    ax.plot(history.history["val_loss"], label="Validation Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss (MSE)")
    ax.set_title("Model Training History")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_risk_pie(risk_labels: list):
    """Donut chart of risk level distribution.

    Returns a matplotlib Figure.
    """
    from collections import Counter
    counts = Counter(risk_labels)
    labels = ["CRITICAL", "MODERATE", "LOW"]
    sizes = [counts.get(l, 0) for l in labels]
    colors = ["#e74c3c", "#f39c12", "#2ecc71"]

    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=140, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
    )
    for t in texts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    for t in autotexts:
        t.set_fontsize(9)
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Fleet Risk Distribution", fontsize=13, fontweight="bold", pad=15)
    fig.tight_layout()
    return fig
