"""MEDIC — Train the Random Forest model and save artifacts to generated_files/.

Usage:
    python train_model.py          # retrain from disease_data.csv
If the CSV is missing/invalid, a built-in synthetic dataset is used so the
project always works.
"""
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from config import CSV_PATH, MODEL_DIR, SYMPTOM_KEYS

# Fallback profiles (used only if disease_data.csv is missing/invalid)
_PROFILES = {
    'Flu':           ['fever', 'cough', 'headache', 'fatigue'],
    'Malaria':       ['fever', 'headache', 'fatigue', 'nausea'],
    'Cold':          ['cough', 'sore_throat', 'headache'],
    'Diabetes':      ['fatigue', 'nausea', 'headache'],
    'Cancer':        ['fatigue', 'headache', 'nausea', 'cough'],
    'Pneumonia':     ['fever', 'cough', 'chest_pain', 'shortness_breath'],
    'Heart_Disease': ['chest_pain', 'shortness_breath', 'fatigue'],
}


def _synthetic_dataset(seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for disease, core in _PROFILES.items():
        for _ in range(60):
            vec = {s: 0 for s in SYMPTOM_KEYS}
            for s in core:
                vec[s] = int(rng.random() > 0.12)
            for s in SYMPTOM_KEYS:
                if not vec[s] and rng.random() < 0.05:
                    vec[s] = 1
            if sum(vec.values()) == 0:
                vec[core[0]] = 1
            vec['disease'] = disease
            rows.append(vec)
    return pd.DataFrame(rows)


def _load_csv(csv_path):
    if not os.path.exists(csv_path):
        return None
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None
    required = ['disease'] + SYMPTOM_KEYS
    if not all(c in df.columns for c in required):
        return None
    df = df[required].dropna()
    if df.empty or df['disease'].nunique() < 2:
        return None
    for k in SYMPTOM_KEYS:
        df[k] = pd.to_numeric(df[k], errors='coerce').fillna(0).clip(0, 1).astype(int)
    return df


def _load_artifacts():
    with open(os.path.join(MODEL_DIR, 'model.pkl'), 'rb') as f:
        model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'encoder.pkl'), 'rb') as f:
        enc = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'symptom_names.pkl'), 'rb') as f:
        names = pickle.load(f)
    return model, enc, names


def train_and_save(force=False, verbose=True, csv_path=CSV_PATH):
    os.makedirs(MODEL_DIR, exist_ok=True)
    mp = os.path.join(MODEL_DIR, 'model.pkl')
    ep = os.path.join(MODEL_DIR, 'encoder.pkl')
    sp = os.path.join(MODEL_DIR, 'symptom_names.pkl')

    if not force and all(os.path.exists(p) for p in (mp, ep, sp)):
        try:
            return _load_artifacts()
        except Exception:
            pass  # corrupted artifacts → retrain below

    df = _load_csv(csv_path)
    source = csv_path if df is not None else 'built-in synthetic dataset'
    if df is None:
        df = _synthetic_dataset()

    X = df[SYMPTOM_KEYS].astype(int)
    y = df['disease'].astype(str).str.strip().values

    enc = LabelEncoder()
    y_enc = enc.fit_transform(y)

    try:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X.values, y_enc, test_size=0.2, random_state=42, stratify=y_enc)
    except ValueError:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X.values, y_enc, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    clf.fit(X_tr, y_tr)

    if verbose:
        from sklearn.metrics import accuracy_score, classification_report
        pred = clf.predict(X_te)
        print(f'[MEDIC] Training source : {source}')
        print(f'[MEDIC] Samples         : {len(X)} | Symptoms: {X.shape[1]} | Classes: {len(enc.classes_)}')
        print(f'[MEDIC] Test accuracy   : {accuracy_score(y_te, pred):.3f}')
        print(classification_report(y_te, pred, target_names=enc.classes_, zero_division=0))

    with open(mp, 'wb') as f:
        pickle.dump(clf, f)
    with open(ep, 'wb') as f:
        pickle.dump(enc, f)
    with open(sp, 'wb') as f:
        pickle.dump(list(X.columns), f)
    if verbose:
        print(f'[MEDIC] ✅ Saved artifacts → {MODEL_DIR}/ (model.pkl, encoder.pkl, symptom_names.pkl)')
    return clf, enc, list(X.columns)


if __name__ == '__main__':
    train_and_save(force=True)