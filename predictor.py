import os
import requests
import joblib
import pandas as pd
import json

from dotenv import load_dotenv, find_dotenv


# Load environment variables reliably
load_dotenv(find_dotenv())

print("Groq key detected:", bool(os.getenv("GROQ_API_KEY")))


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model.pkl"
)

_local_model = None


def _load_local_model():
    global _local_model

    if _local_model is None:
        _local_model = joblib.load(MODEL_PATH)

    return _local_model


def _local_prediction(glucose, haemoglobin, cholesterol):

    model = _load_local_model()

    features = pd.DataFrame(
        [[glucose, haemoglobin, cholesterol]],
        columns=[
            "glucose",
            "haemoglobin",
            "cholesterol"
        ]
    )

    prediction = model.predict(features)[0]

    return prediction


def _try_groq_api(local_label, glucose, haemoglobin, cholesterol):

    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        return f"{local_label} [Groq API key missing]"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Patient Details

Glucose: {glucose}
Haemoglobin: {haemoglobin}
Cholesterol: {cholesterol}

Machine Learning Prediction:
{local_label}

Write exactly two short professional medical remarks.
Do not mention AI.
Do not mention confidence scores.
Do not prescribe medicines.
"""

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "system",
                "content": "You are a healthcare assistant. Reply with exactly two short professional medical remarks."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("Status:", response.status_code)

        response.raise_for_status()

        data = response.json()
        print(data)

        choices = data.get("choices", [])

        if choices:
            message = choices[0].get("message", {})
            content = message.get("content")

            if isinstance(content, str) and content.strip():
                return content.strip()

            # Some models return content as a list
            if isinstance(content, list):
                text = ""
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text += item.get("text", "")
                if text.strip():
                    return text.strip()

        return local_label

    except Exception as e:
        print(e)
        return local_label


def predict_remarks(
    glucose,
    haemoglobin,
    cholesterol
):

    local_label = _local_prediction(
        glucose,
        haemoglobin,
        cholesterol
    )

    return _try_groq_api(
        local_label,
        glucose,
        haemoglobin,
        cholesterol
    )
