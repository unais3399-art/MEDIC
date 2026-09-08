"""MEDIC — training pipeline (v4): binary CSV, Kaggle text CSV, or synthetic fallback."""
import os
import pickle
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from config import CSV_PATH, MODEL_DIR, SYMPTOM_KEYS

MAX_ROWS = 20000

_PROFILES = {
    'Flu':           ['fever', 'cough', 'headache', 'fatigue'],
    'Malaria':       ['fever', 'headache', 'fatigue', 'nausea'],
    'Cold':          ['cough', 'sore_throat', 'headache'],
    'Diabetes':      ['fatigue', 'nausea', 'headache'],
    'Cancer':        ['fatigue', 'headache', 'nausea', 'cough'],
    'Pneumonia':     ['fever', 'cough', 'chest_pain', 'shortness_breath'],
    'Heart_Disease': ['chest_pain', 'shortness_breath', 'fatigue'],
}

DISEASE_COLS = ('disease', 'diseases', 'prognosis', 'label', 'target')


def _normalize(name):
    return str(name).strip().lower().replace(' ', '_').replace('-', '_')


def _find_disease_col(df):
    cols = {str(c).strip().lower(): c for c in df.columns}
    dcol = next((cols[k] for k in DISEASE_COLS if k in cols), None)
    if dcol is None:
        dcol = next((c for c in df.columns if 'disease' in str(c).lower()), None)
    return dcol


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


def _load_binary_csv(path):
    try:
        df = pd.read_csv(path)
    except Exception:
        return None
    dcol = _find_disease_col(df)
    if dcol is None:
        return None
    feat = [c for c in df.columns if c != dcol]
    if not feat:
        return None
    num = df[feat].apply(pd.to_numeric, errors='coerce')
    if num.isna().any().any():
        return None
    X = num.clip(0, 1).astype(int)
    X.columns = [_normalize(c) for c in X.columns]
    X = X.loc[:, ~X.columns.duplicated()]
    X['disease'] = df[dcol].astype(str).str.strip().values
    X = X[X['disease'].str.lower() != 'nan']
    return X if X['disease'].nunique() >= 2 else None


def _load_text_symptom_csv(path):
    try:
        df = pd.read_csv(path)
    except Exception:
        return None
    dcol = _find_disease_col(df)
    if dcol is None:
        return None
    sym_cols = [c for c in df.columns if c != dcol and str(c).lower().startswith('symptom')]
    if not sym_cols:
        return None
    parsed, all_syms = [], set()
    for _, row in df.iterrows():
        disease = str(row[dcol]).strip()
        if not disease or disease.lower() == 'nan':
            continue
        present = set()
        for c in sym_cols:
            v = row[c]
            if pd.notna(v) and str(v).strip().lower() not in ('', 'nan'):
                present.add(_normalize(v))
        if present:
            parsed.append((disease, present))
            all_syms |= present
    if len(parsed) < 20 or len({d for d, _ in parsed}) < 2:
        return None
    all_syms = sorted(all_syms)
    rows = [{**{s: int(s in present) for s in all_syms}, 'disease': d}
            for d, present in parsed]
    return pd.DataFrame(rows)


def _load_artifacts():
    with open(os.path.join(MODEL_DIR, 'model.pkl'), 'rb') as f:
        model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'encoder.pkl'), 'rb') as f:
        enc = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'symptom_names.pkl'), 'rb') as f:
        names = pickle.load(f)
    return model, enc, names


def _cap_rows(df, min_count=2, max_rows=MAX_ROWS):
    """Drop too-rare diseases, then stratified-downsample huge datasets."""
    counts = df['disease'].value_counts()
    df = df[df['disease'].isin(counts[counts >= min_count].index)]
    if len(df) > max_rows:
        df, _ = train_test_split(df, train_size=max_rows, random_state=42,
                                 stratify=df['disease'])
    return df


def train_and_save(force=False, verbose=True, csv_path=CSV_PATH):
    os.makedirs(MODEL_DIR, exist_ok=True)
    mp = os.path.join(MODEL_DIR, 'model.pkl')
    ep = os.path.join(MODEL_DIR, 'encoder.pkl')
    sp = os.path.join(MODEL_DIR, 'symptom_names.pkl')

    if not force and all(os.path.exists(p) for p in (mp, ep, sp)):
        try:
            return _load_artifacts()
        except Exception:
            pass

    df = _load_binary_csv(csv_path)         
    if df is None:
        df = _load_text_symptom_csv(csv_path)
    source = csv_path if df is not None else 'built-in synthetic dataset'
    if df is None:
        df = _synthetic_dataset()

    df = _cap_rows(df)

    X = df.drop(columns=['disease']).astype(int)
    y = df['disease'].values

    enc = LabelEncoder()
    y_enc = enc.fit_transform(y)
    try:
        split = train_test_split(X.values, y_enc, test_size=0.2,
                                 random_state=42, stratify=y_enc)
    except ValueError:
        split = train_test_split(X.values, y_enc, test_size=0.2, random_state=42)
    X_tr, X_te, y_tr, y_te = split

    clf = RandomForestClassifier(n_estimators=150, max_depth=10,
                                 min_samples_split=5, min_samples_leaf=2,
                                 random_state=42, n_jobs=-1)
    clf.fit(X_tr, y_tr)

    if verbose:
        pred = clf.predict(X_te)
        print(f'[MEDIC] Source   : {source}')
        print(f'[MEDIC] Samples  : {len(X)} | Symptoms: {X.shape[1]} | Diseases: {len(enc.classes_)}')
        print(f'[MEDIC] Accuracy : {accuracy_score(y_te, pred):.3f}')
        labels = np.unique(y_te)
        names = [enc.classes_[i] for i in labels]
        print(classification_report(y_te, pred, labels=labels,
                                     target_names=names, zero_division=0))
    with open(mp, 'wb') as f:
        pickle.dump(clf, f)
    with open(ep, 'wb') as f:
        pickle.dump(enc, f)
    with open(sp, 'wb') as f:
        pickle.dump(list(X.columns), f)
    if verbose:
        print(f'[MEDIC] ✅ Saved artifacts → {MODEL_DIR}/')
    return clf, enc, list(X.columns)


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    train_and_save(force=True, csv_path=path)