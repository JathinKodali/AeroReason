"""
Reasoning Engine – converts numerical RUL predictions into
actionable maintenance insights.

Responsibilities:
- Risk classification (LOW / MODERATE / CRITICAL)
- Degradation trend analysis
- Human-readable explanations
- Maintenance recommendations
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np

from reasoning.ollama_engine import (
    is_ollama_available,
    generate_llm_explanation,
    generate_llm_recommendation,
    generate_llm_trend_analysis,
)
import pandas as pd


# ──────────────────────────────────────────────
# Risk thresholds
# ──────────────────────────────────────────────
CRITICAL_THRESHOLD = 50
MODERATE_THRESHOLD = 100


@dataclass
class MaintenanceInsight:
    """Container for a single engine's maintenance assessment."""
    engine_id: int
    predicted_rul: float
    risk_level: str              # LOW, MODERATE, CRITICAL
    risk_color: str              # CSS-friendly colour
    explanation: str
    recommendation: str
    trend_summary: Optional[str] = None


# ──────────────────────────────────────────────
# Risk classification
# ──────────────────────────────────────────────
def classify_risk(rul: float) -> tuple:
    """Return (risk_level, colour) for a given RUL value."""
    if rul <= CRITICAL_THRESHOLD:
        return "CRITICAL", "#e74c3c"
    elif rul <= MODERATE_THRESHOLD:
        return "MODERATE", "#f39c12"
    else:
        return "LOW", "#2ecc71"


# ──────────────────────────────────────────────
# Explanation generation
# ──────────────────────────────────────────────
def generate_explanation(rul: float, risk_level: str) -> str:
    """Generate a human-readable explanation based on RUL and risk."""
    explanations = {
        "LOW": (
            f"Engine is operating within normal parameters. "
            f"Predicted remaining useful life is {rul:.0f} cycles. "
            f"No immediate degradation concerns detected."
        ),
        "MODERATE": (
            f"Engine shows signs of degradation. "
            f"Predicted remaining useful life is {rul:.0f} cycles. "
            f"Performance metrics indicate progressive wear that "
            f"requires monitoring."
        ),
        "CRITICAL": (
            f"⚠️ Engine is approaching failure. "
            f"Predicted remaining useful life is only {rul:.0f} cycles. "
            f"Significant degradation detected across multiple sensors."
        ),
    }
    return explanations.get(risk_level, "Unable to assess engine status.")


# ──────────────────────────────────────────────
# Recommendation generation
# ──────────────────────────────────────────────
def generate_recommendation(rul: float, risk_level: str) -> str:
    """Provide actionable maintenance recommendations."""
    recommendations = {
        "LOW": (
            "• Continue routine monitoring schedule.\n"
            "• Next inspection recommended in 50–100 cycles.\n"
            "• No component replacement needed at this time."
        ),
        "MODERATE": (
            "• Schedule detailed inspection within the next 20–30 cycles.\n"
            "• Increase sensor monitoring frequency.\n"
            "• Pre-order replacement parts as a precaution.\n"
            "• Review maintenance logs for recent anomalies."
        ),
        "CRITICAL": (
            "🔴 IMMEDIATE ACTION REQUIRED:\n"
            "• Ground the engine for emergency inspection.\n"
            "• Initiate replacement procedure immediately.\n"
            "• Notify maintenance crew and operations.\n"
            "• Do NOT operate beyond the next 10 cycles without inspection."
        ),
    }
    return recommendations.get(risk_level, "Consult maintenance manual.")


# ──────────────────────────────────────────────
# Trend analysis
# ──────────────────────────────────────────────
def analyse_degradation_trend(engine_df: pd.DataFrame,
                              sensor_cols: List[str]) -> str:
    """Summarise the degradation trend from sensor time-series."""
    if engine_df.empty or len(engine_df) < 10:
        return "Insufficient data for trend analysis."

    degrading, stable = [], []
    for col in sensor_cols:
        if col not in engine_df.columns:
            continue
        vals = engine_df[col].values
        # Simple linear trend via polyfit
        slope = np.polyfit(range(len(vals)), vals, 1)[0]
        if abs(slope) > 0.001:
            degrading.append(col)
        else:
            stable.append(col)

    if not degrading:
        return "All monitored sensors are stable — no degradation trend."
    return (
        f"{len(degrading)} sensor(s) show a degradation trend "
        f"({', '.join(degrading[:5])}{'…' if len(degrading) > 5 else ''}). "
        f"{len(stable)} sensor(s) remain stable."
    )


# ──────────────────────────────────────────────
# Main reasoning entry point
# ──────────────────────────────────────────────
def reason(engine_id: int,
           predicted_rul: float,
           engine_df: Optional[pd.DataFrame] = None,
           sensor_cols: Optional[List[str]] = None,
           use_llm: bool = False,
           llm_model: str = "llama3") -> MaintenanceInsight:
    """Run the full reasoning pipeline for one engine.

    Args:
        engine_id: Engine identifier.
        predicted_rul: The RUL value predicted by the LSTM model.
        engine_df: Optional DataFrame of the engine's time-series data
                   for trend analysis.
        sensor_cols: Sensor column names used for trend analysis.
        use_llm: If True, use Ollama LLM for explanation/recommendation.
        llm_model: Ollama model name to use.

    Returns:
        MaintenanceInsight dataclass with all assessment fields.
    """
    risk_level, risk_color = classify_risk(predicted_rul)

    # Trend analysis (needed before LLM call for context)
    trend_summary = None
    if engine_df is not None and sensor_cols is not None:
        trend_summary = analyse_degradation_trend(engine_df, sensor_cols)

    # Start with rule-based defaults
    explanation = generate_explanation(predicted_rul, risk_level)
    recommendation = generate_recommendation(predicted_rul, risk_level)

    # Attempt LLM-powered generation if requested
    if use_llm and is_ollama_available():
        llm_explanation = generate_llm_explanation(
            engine_id, predicted_rul, risk_level, trend_summary, model=llm_model
        )
        if llm_explanation:
            explanation = llm_explanation

        llm_recommendation = generate_llm_recommendation(
            engine_id, predicted_rul, risk_level, trend_summary, model=llm_model
        )
        if llm_recommendation:
            recommendation = llm_recommendation

        if trend_summary:
            llm_trend = generate_llm_trend_analysis(
                engine_id, predicted_rul, risk_level, trend_summary, model=llm_model
            )
            if llm_trend:
                trend_summary = llm_trend

    return MaintenanceInsight(
        engine_id=engine_id,
        predicted_rul=predicted_rul,
        risk_level=risk_level,
        risk_color=risk_color,
        explanation=explanation,
        recommendation=recommendation,
        trend_summary=trend_summary,
    )


def batch_reason(engine_ids: list,
                 predictions: list,
                 test_df: Optional[pd.DataFrame] = None,
                 sensor_cols: Optional[List[str]] = None,
                 use_llm: bool = False,
                 llm_model: str = "llama3") -> List[MaintenanceInsight]:
    """Run reasoning for multiple engines at once."""
    insights = []
    for eid, pred in zip(engine_ids, predictions):
        engine_data = None
        if test_df is not None:
            engine_data = test_df[test_df["engine_id"] == eid]
        insights.append(reason(eid, pred, engine_data, sensor_cols,
                               use_llm=use_llm, llm_model=llm_model))
    return insights
