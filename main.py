"""
main.py – CLI entry point for the Predictive Maintenance Framework.

Usage:
    python main.py                 # Train on FD001 and evaluate
    python main.py --dataset FD002 # Use a different sub-dataset
    python main.py --epochs 100    # Override training epochs
"""

import argparse
import os
import sys
import numpy as np

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from preprocessing.data_loader import prepare_data, FEATURES, SENSOR_COLS, RUL_CAP
from models.lstm_model import (
    build_lstm_model, train_model, evaluate_model,
    save_trained_model, load_trained_model,
)
from reasoning.reasoning_engine import batch_reason
from utils.helpers import (
    plot_predicted_vs_actual, plot_rul_distribution, plot_training_history,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Hybrid Predictive Maintenance Framework – Train & Evaluate"
    )
    parser.add_argument("--data-dir", type=str,
                        default=os.path.join(PROJECT_ROOT, "Research"),
                        help="Directory containing train/test/RUL .txt files")
    parser.add_argument("--dataset", type=str, default="FD001",
                        choices=["FD001", "FD002", "FD003", "FD004"],
                        help="C-MAPSS sub-dataset to use")
    parser.add_argument("--window", type=int, default=30,
                        help="Sliding window size")
    parser.add_argument("--epochs", type=int, default=50,
                        help="Max training epochs")
    parser.add_argument("--batch-size", type=int, default=256,
                        help="Training batch size")
    parser.add_argument("--model-path", type=str,
                        default=os.path.join(PROJECT_ROOT, "data",
                                             "trained_model.keras"),
                        help="Path to save/load the trained model")
    parser.add_argument("--load", action="store_true",
                        help="Load a pre‐trained model instead of training")
    return parser.parse_args()


def main():
    args = parse_args()

    # ── 1. Data preparation ──────────────────────
    print("=" * 60)
    print("  HYBRID PREDICTIVE MAINTENANCE FRAMEWORK")
    print("  NASA C-MAPSS Turbofan Engine Degradation")
    print("=" * 60)

    (X_train, y_train, X_test, y_test,
     test_engine_ids, scaler, train_df, test_df) = prepare_data(
        args.data_dir, args.dataset, args.window
    )

    # ── 2. Model ─────────────────────────────────
    if args.load and os.path.exists(args.model_path):
        model = load_trained_model(args.model_path)
    else:
        print("\n[Training] Building LSTM model …")
        model = build_lstm_model(
            input_shape=(X_train.shape[1], X_train.shape[2])
        )
        model.summary()

        history = train_model(
            model, X_train, y_train,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )

        # Save training curves
        fig = plot_training_history(history)
        os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)
        fig.savefig(os.path.join(PROJECT_ROOT, "data", "training_history.png"),
                    dpi=150)
        print("[Plot] Training history saved to data/training_history.png")

        save_trained_model(model, args.model_path)

    # ── 3. Evaluation ────────────────────────────
    print("\n[Evaluation]")
    rmse_norm, y_pred_norm = evaluate_model(model, X_test, y_test)

    # Denormalise back to real cycles
    y_pred = y_pred_norm * RUL_CAP
    y_test_real = y_test * RUL_CAP
    rmse = np.sqrt(np.mean((y_test_real - y_pred) ** 2))
    print(f"[Model] Denormalised RMSE: {rmse:.2f} cycles")

    # Save plots
    fig = plot_predicted_vs_actual(y_test_real, y_pred)
    fig.savefig(os.path.join(PROJECT_ROOT, "data", "pred_vs_actual.png"),
                dpi=150)
    print("[Plot] Predicted vs Actual saved to data/pred_vs_actual.png")

    fig = plot_rul_distribution(y_pred, test_engine_ids)
    fig.savefig(os.path.join(PROJECT_ROOT, "data", "rul_distribution.png"),
                dpi=150)
    print("[Plot] RUL distribution saved to data/rul_distribution.png")

    # ── 4. Reasoning ─────────────────────────────
    print("\n[Reasoning Engine]")
    sensor_features = [c for c in SENSOR_COLS if c in test_df.columns]
    insights = batch_reason(test_engine_ids, y_pred, test_df, sensor_features)

    print(f"\n{'Engine':<10}{'Pred RUL':<12}{'Actual RUL':<12}{'Risk':<12}")
    print("-" * 46)
    for insight, actual in zip(insights, y_test_real):
        print(f"{insight.engine_id:<10}"
              f"{insight.predicted_rul:<12.1f}"
              f"{actual:<12.1f}"
              f"{insight.risk_level:<12}")

    # Summary stats
    risk_counts = {"LOW": 0, "MODERATE": 0, "CRITICAL": 0}
    for i in insights:
        risk_counts[i.risk_level] += 1
    print(f"\nRisk Summary: {risk_counts}")
    print(f"Overall RMSE: {rmse:.2f}")
    print("\n✅ Pipeline complete. Run the Streamlit app for interactive analysis:")
    print(f"   streamlit run {os.path.join(PROJECT_ROOT, 'app', 'streamlit_app.py')}")


if __name__ == "__main__":
    main()
