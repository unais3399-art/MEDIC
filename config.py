"""MEDIC — Global constants, keyword maps and configuration (no Streamlit calls)."""

# ---------------- Paths ----------------
DB_PATH = 'database/healthcare.db'
MODEL_DIR = 'generated_files'
CSV_PATH = 'disease_data.csv'

# ---------------- Symptoms ----------------
SYMPTOM_KEYS = ['fever', 'cough', 'headache', 'fatigue',
                'nausea', 'sore_throat', 'chest_pain', 'shortness_breath']

SYMPTOM_KEYWORDS = {
    'fever': ['fever', 'high temperature', 'hot', 'sweating', 'chills', 'temp'],
    'cough': ['cough', 'coughing', 'phlegm', 'mucus', 'chesty'],
    'headache': ['headache', 'head pain', 'migraine', 'throbbing', 'head hurts'],
    'fatigue': ['fatigue', 'tired', 'exhausted', 'weak', 'low energy', 'sleepy', 'worn out'],
    'nausea': ['nausea', 'nauseous', 'vomit', 'sick stomach', 'queasy', 'throwing up'],
    'sore_throat': ['sore throat', 'throat pain', 'scratchy throat', 'swallowing pain'],
    'chest_pain': ['chest pain', 'chest tightness', 'heart pain', 'pressure chest', 'chest hurts'],
    'shortness_breath': ['shortness of breath', 'breathing difficulty', 'out of breath',
                         'wheezing', 'cant breathe', "can't breathe"],
}

# ---------------- Visual constants ----------------
PLOT_BG = '#0d1117'

URGENCY_META = {
    'Critical': ('🔴', '#ff4d4d'),
    'High':     ('🟠', '#ff9f43'),
    'Medium':   ('🟡', '#f5c542'),
    'Low':      ('🟢', '#3fb950'),
}

QUICK_OPTIONS = [
    ("🤒 Fever & Cough", "I have fever and cough"),
    ("🤕 Headache & Fatigue", "I have headache and feel tired"),
    ("😷 Sore Throat", "I have a sore throat"),
    ("💔 Chest Pain", "I have chest pain"),
    ("😤 Breathing Difficulty", "I have shortness of breath"),
    ("🤢 Nausea & Vomiting", "I feel nauseous and have been vomiting"),
    ("🔥 High Fever", "I have a high fever and chills"),
    ("😴 Extreme Fatigue", "I feel extremely tired and weak"),
]

CHAT_EXAMPLES = [
    "I have fever and cough",
    "I feel tired and have a headache",
    "I have chest pain and shortness of breath",
    "I have a sore throat and nausea",
]

FALLBACK_MSG = """🤔 I couldn't identify any specific symptoms in your message.

Try describing them clearly, for example:
- "I have fever, cough and headache"
- "I feel tired with chest pain"
- "I have a sore throat and difficulty breathing"

Or tap a ⚡ **Quick Symptom** chip in the sidebar."""