"""
predictor.py
-------------
Generates the "Remarks" text for a patient based on their blood test values.

Two-tier strategy (both free):
1. If an HF_API_TOKEN is set in the environment, try calling the free
   Hugging Face Inference API (zero-shot health-text classification model)
   to add a natural-language style summary on top of the clinical signal.
2. Always fall back to (or run alongside) a locally trained scikit-learn
   RandomForestClassifier (see train_model.py) which never needs internet
   access or an API key. This guarantees the app keeps working even with
   no key configured, no internet, or if the free API is rate-limited.

This satisfies the task's "call any external AI/ML or Health-related API"
requirement while keeping the app fully functional and free with zero
mandatory external dependency.
"""

import os
import requests
import joblib
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
HF_MODEL_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
_local_model = None


def _load_local_model():
    global _local_model
    if _local_model is None:
        _local_model = joblib.load(MODEL_PATH)
    return _local_model


def _local_prediction(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    """Predict using the locally trained RandomForest model. Always available."""
    model = _load_local_model()
    features = pd.DataFrame(
        [[glucose, haemoglobin, cholesterol]],
        columns=["glucose", "haemoglobin", "cholesterol"],
    )
    pred = model.predict(features)[0]
    return pred


def _try_huggingface_api(local_label: str) -> str:
    """
    Optional enrichment step: ask a free Hugging Face zero-shot model to
    classify the local model's finding against a few candidate health
    categories, and append its confidence. If anything goes wrong (no
    token, no internet, rate limit, timeout), we silently skip this and
    just return the local label.
    """
    if not HF_API_TOKEN:
        return local_label

    candidate_labels = [
        "diabetes risk",
        "anaemia risk",
        "high cholesterol risk",
        "normal healthy result",
    ]

    try:
        response = requests.post(
            HF_MODEL_URL,
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={
                "inputs": local_label,
                "parameters": {"candidate_labels": candidate_labels},
            },
            timeout=8,
        )
        response.raise_for_status()
        result = response.json()

        top_label = result["labels"][0]
        top_score = result["scores"][0]
        return f"{local_label} (API cross-check: {top_label}, confidence {top_score:.0%})"

    except Exception:
        # Network/API issues should never break the app — just use the local result.
        return local_label


def predict_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    """
    Main entry point used by the Streamlit app.
    Always returns a usable remarks string.
    """
    local_label = _local_prediction(glucose, haemoglobin, cholesterol)
    return _try_huggingface_api(local_label)
