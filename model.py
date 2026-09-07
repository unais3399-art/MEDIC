"""MEDIC — Model loading, NLP symptom extraction and prediction."""
import os
import pickle

import streamlit as st

import train_model as tm
from config import MODEL_DIR, SYMPTOM_KEYWORDS


@st.cache_resource(show_spinner='🧠 Loading MEDIC AI model…')
def get_model():
    """Load pickled model; auto-train if missing/corrupted (app never crashes)."""
    mp = os.path.join(MODEL_DIR, 'model.pkl')
    ep = os.path.join(MODEL_DIR, 'encoder.pkl')
    sp = os.path.join(MODEL_DIR, 'symptom_names.pkl')

    if all(os.path.exists(p) for p in (mp, ep, sp)):
        try:
            with open(mp, 'rb') as f:
                model = pickle.load(f)
            with open(ep, 'rb') as f:
                encoder = pickle.load(f)
            with open(sp, 'rb') as f:
                symptom_names = pickle.load(f)
            return model, encoder, symptom_names, 'Trained model (generated_files/)'
        except Exception:
            pass

    model, encoder, symptom_names = tm.train_and_save(force=False, verbose=False)
    return model, encoder, symptom_names, 'Auto-trained model (dataset fallback)'


def extract_symptoms(text):
    """Keyword-based NLP extraction from free text."""
    text = str(text).lower()
    found = [sym for sym, kws in SYMPTOM_KEYWORDS.items() if any(k in text for k in kws)]
    return sorted(set(found))


def symptoms_to_vector(extracted, symptom_names):
    return [1 if s in extracted else 0 for s in symptom_names]


def predict_disease(vector, model, encoder):
    pred = model.predict([vector])
    disease = str(encoder.inverse_transform(pred)[0])
    proba = model.predict_proba([vector])[0]
    confidence = float(max(proba)) * 100.0
    all_probs = {str(encoder.classes_[i]): float(proba[i]) * 100.0
                 for i in range(len(encoder.classes_))}
    return disease, confidence, all_probs