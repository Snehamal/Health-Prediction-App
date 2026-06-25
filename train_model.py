"""
train_model.py
---------------
Trains the local "custom ML model" used to generate health Remarks.

Why a synthetic dataset?
Public, labeled, patient-level blood-test datasets are sensitive and hard to
obtain legally for a take-home task. Instead, we generate a large synthetic
dataset where the label for each row is derived from well-established
clinical reference ranges (see `label_row`). A RandomForestClassifier is
then trained on this data, so the model learns the *boundaries and
interactions* between glucose, haemoglobin and cholesterol rather than us
hardcoding a long if/else chain in the app itself.

This script only needs to be run once (or whenever you want to retrain).
It saves the trained model to model.pkl, which app.py loads at runtime.

Run with:  python train_model.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

RANDOM_SEED = 42
N_SAMPLES = 6000


def label_row(glucose, haemoglobin, cholesterol):
    """
    Clinical reference ranges used to generate ground-truth labels:
      Glucose (fasting, mg/dL):   Normal <100 | Prediabetes 100-125 | Diabetic >125
      Haemoglobin (g/dL):         Low <12 (anaemia) | Normal 12-16.5 | High >16.5
      Cholesterol (mg/dL):        Normal <200 | Borderline 200-239 | High >=240

    Priority order below mirrors how a clinician would flag the most
    significant finding first when several values are abnormal.
    """
    if glucose >= 126 and cholesterol >= 240:
        return "High risk: Diabetes and high cholesterol indicators"
    if glucose >= 126:
        return "High risk: Possible diabetes (high glucose)"
    if cholesterol >= 240:
        return "High risk: High cholesterol (cardiovascular risk)"
    if haemoglobin < 10:
        return "High risk: Severe anaemia indicators"
    if glucose >= 100:
        return "Moderate risk: Prediabetes range glucose"
    if cholesterol >= 200:
        return "Moderate risk: Borderline high cholesterol"
    if haemoglobin < 12:
        return "Moderate risk: Possible anaemia (low haemoglobin)"
    if haemoglobin > 17.5:
        return "Moderate risk: Elevated haemoglobin"
    return "Low risk: All values within normal range"


def generate_dataset(n=N_SAMPLES, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)

    glucose = rng.uniform(60, 320, n)
    haemoglobin = rng.uniform(7, 19, n)
    cholesterol = rng.uniform(120, 320, n)

    df = pd.DataFrame({
        "glucose": glucose,
        "haemoglobin": haemoglobin,
        "cholesterol": cholesterol,
    })
    df["label"] = df.apply(
        lambda r: label_row(r["glucose"], r["haemoglobin"], r["cholesterol"]), axis=1
    )
    return df


def train_and_save(model_path="model.pkl"):
    df = generate_dataset()
    X = df[["glucose", "haemoglobin", "cholesterol"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=150, random_state=RANDOM_SEED)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print("Validation performance:\n")
    print(classification_report(y_test, preds))

    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")


if __name__ == "__main__":
    train_and_save()
