"""MEDIC — model loading, scalable symptom extraction, prediction."""
import os
import pickle

import streamlit as st

import train_model as tm
from config import MODEL_DIR, SYMPTOM_KEYWORDS

# Synonyms mapped to the REAL dataset's symptom column names
EXTRA_SYNONYMS = {
    'palpitations': ['palpitation', 'heart racing', 'racing heart', 'pounding heart'],
    'insomnia': ["can't sleep", 'sleepless', 'trouble sleeping'],
    'anxiety_and_nervousness': ['anxious', 'anxiety', 'nervous', 'panic'],
    'depression': ['depressed', 'feeling low', 'hopeless'],
    'shortness_of_breath': ['breathless', 'difficulty breathing', "can't breathe"],
    'chest_tightness': ['tight chest', 'chest pressure'],
    'sharp_chest_pain': ['chest pain', 'chest hurts', 'heart pain'],
    'irregular_heartbeat': ['arrhythmia', 'skipped heartbeats'],
    'breathing_fast': ['rapid breathing', 'hyperventilating'],
    'sore_throat': ['throat pain', 'scratchy throat'],
    'dizziness': ['dizzy', 'lightheaded', 'vertigo'],
    'hoarse_voice': ['hoarse', 'raspy voice'],
    'fever': ['high temperature', 'chills', 'burning up'],
    'cough': ['coughing', 'phlegm'],
    'headache': ['head pain', 'head hurts', 'migraine'],
    'fatigue': ['tired', 'exhausted', 'weakness', 'low energy'],
    'nausea': ['nauseous', 'queasy', 'sick stomach'],
    'vomiting': ['throwing up', 'vomit'],
    'skin_rash': ['rash', 'red patches on skin'],
    'itching': ['itchy', 'itching all over'],
    'yellowish_skin': ['yellow skin', 'jaundice look'],
    'dark_urine': ['yellow urine', 'dark urine'],
    'abdominal_pain': ['stomach pain', 'belly pain', 'tummy pain'],
    'diarrhea': ['loose motions', 'loose stool'],
    'loss_of_appetite': ['no appetite', "can't eat"],
    'joint_pain': ['aching joints', 'joint ache'],
    'muscle_pain': ['body ache', 'muscle ache'],
    'weight_loss': ['losing weight'],
    'excessive_thirst': ['always thirsty'],
    'frequent_urination': ['peeing often', 'urinate often'],
    'runny_nose': ['stuffy nose', 'blocked nose'],
    'continuous_sneezing': ['sneezing'],
    'watering_from_eyes': ['watery eyes'],
}

_KEYWORD_CACHE = {}


def get_keyword_map(symptom_names):
    """Auto-build keywords: dataset symptom name + curated synonyms."""
    key = tuple(symptom_names)
    if key not in _KEYWORD_CACHE:
        kw = {}
        for s in key:
            kws = {s.replace('_', ' ')}
            kws.update(EXTRA_SYNONYMS.get(s, []))
            kws.update(SYMPTOM_KEYWORDS.get(s, []))
            kw[s] = sorted(kws)
        _KEYWORD_CACHE[key] = kw
    return _KEYWORD_CACHE[key]


@st.cache_resource(show_spinner='🧠 Loading MEDIC AI model…')
def get_model():
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


def extract_symptoms(text, symptom_names):
    text = str(text).lower()
    kw = get_keyword_map(symptom_names)
    return sorted({s for s in symptom_names if any(k in text for k in kw[s])})


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