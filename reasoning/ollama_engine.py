"""
Ollama LLM Engine – generates rich, context-aware maintenance
explanations and recommendations using a local Ollama model.

Falls back gracefully when Ollama is unavailable.
"""

import requests
from typing import Optional

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────
def is_ollama_available() -> bool:
    """Check if the Ollama server is running and reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def get_available_models() -> list:
    """Return list of model names available on the local Ollama server."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if resp.status_code == 200:
            return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass
    return []


# ──────────────────────────────────────────────
# Prompt builders
# ──────────────────────────────────────────────
_SYSTEM_PROMPT = (
    "You are an expert aerospace maintenance engineer AI assistant. "
    "You analyse turbofan engine health data and provide clear, "
    "actionable insights to maintenance crews. Be concise but thorough. "
    "Use professional language appropriate for aviation maintenance teams."
)


def _build_explanation_prompt(
    engine_id: int,
    rul: float,
    risk_level: str,
    trend_summary: Optional[str] = None,
) -> str:
    """Build the user prompt for generating an explanation."""
    prompt = (
        f"Engine ID: {engine_id}\n"
        f"Predicted Remaining Useful Life (RUL): {rul:.0f} cycles\n"
        f"Risk Classification: {risk_level}\n"
    )
    if trend_summary:
        prompt += f"Sensor Trend Analysis: {trend_summary}\n"

    prompt += (
        "\nProvide a clear, 2-3 sentence explanation of this engine's "
        "current health status. Mention the RUL, risk level, and any "
        "degradation trends. Do NOT use bullet points or markdown formatting."
    )
    return prompt


def _build_recommendation_prompt(
    engine_id: int,
    rul: float,
    risk_level: str,
    trend_summary: Optional[str] = None,
) -> str:
    """Build the user prompt for generating maintenance recommendations."""
    prompt = (
        f"Engine ID: {engine_id}\n"
        f"Predicted Remaining Useful Life (RUL): {rul:.0f} cycles\n"
        f"Risk Classification: {risk_level}\n"
    )
    if trend_summary:
        prompt += f"Sensor Trend Analysis: {trend_summary}\n"

    prompt += (
        "\nProvide 3-5 specific, actionable maintenance recommendations "
        "as bullet points (use • as the bullet character). "
        "Prioritise by urgency. Include inspection intervals, "
        "component checks, and crew notifications as appropriate. "
        "Keep each bullet to one line."
    )
    return prompt


def _build_trend_prompt(
    engine_id: int,
    rul: float,
    risk_level: str,
    trend_summary: str,
) -> str:
    """Build the user prompt for generating a detailed trend explanation."""
    return (
        f"Engine ID: {engine_id}\n"
        f"Predicted Remaining Useful Life (RUL): {rul:.0f} cycles\n"
        f"Risk Classification: {risk_level}\n"
        f"Raw Sensor Trend Data: {trend_summary}\n"
        f"\nProvide a concise 2-3 sentence expert analysis of the sensor "
        f"degradation trends. Explain what the degrading sensors likely "
        f"indicate about the engine's physical condition (e.g. compressor "
        f"wear, turbine erosion, bearing fatigue). "
        f"Do NOT use bullet points or markdown formatting."
    )


# ──────────────────────────────────────────────
# LLM call
# ──────────────────────────────────────────────
def _call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> Optional[str]:
    """Send a chat completion request to the local Ollama server.

    Returns the assistant's reply text, or None on failure.
    """
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 256,
            },
        }
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json()["message"]["content"].strip()
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────
def generate_llm_explanation(
    engine_id: int,
    rul: float,
    risk_level: str,
    trend_summary: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> Optional[str]:
    """Generate an LLM-powered explanation for an engine's health status.

    Returns None if the LLM call fails (caller should fall back to
    the rule-based explanation).
    """
    prompt = _build_explanation_prompt(engine_id, rul, risk_level, trend_summary)
    return _call_ollama(prompt, model)


def generate_llm_recommendation(
    engine_id: int,
    rul: float,
    risk_level: str,
    trend_summary: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> Optional[str]:
    """Generate LLM-powered maintenance recommendations.

    Returns None if the LLM call fails (caller should fall back to
    the rule-based recommendations).
    """
    prompt = _build_recommendation_prompt(engine_id, rul, risk_level, trend_summary)
    return _call_ollama(prompt, model)


def generate_llm_trend_analysis(
    engine_id: int,
    rul: float,
    risk_level: str,
    trend_summary: str,
    model: str = DEFAULT_MODEL,
) -> Optional[str]:
    """Generate an LLM-powered explanation of sensor degradation trends.

    Returns None if the LLM call fails (caller should fall back to
    the rule-based trend summary).
    """
    prompt = _build_trend_prompt(engine_id, rul, risk_level, trend_summary)
    return _call_ollama(prompt, model)
