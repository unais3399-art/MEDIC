"""MEDIC — SQLite database operations (CRUD)."""
import os
import sqlite3

from config import DB_PATH


def init_db():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT,
        symptoms_extracted TEXT,
        predicted_disease TEXT,
        confidence REAL,
        urgency TEXT,
        recommendations TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


def save_consultation(user_input, symptoms, disease, confidence, urgency, recommendations):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO consultations
        (user_input, symptoms_extracted, predicted_disease, confidence, urgency, recommendations)
        VALUES (?, ?, ?, ?, ?, ?)''',
                 (user_input, str(symptoms), disease, confidence, urgency, str(recommendations)))
    conn.commit()
    conn.close()


def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('''SELECT user_input, symptoms_extracted, predicted_disease,
                                  confidence, urgency, timestamp
                           FROM consultations
                           ORDER BY timestamp DESC, id DESC LIMIT ?''', (limit,)).fetchall()
    conn.close()
    return rows


def get_stats():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute('SELECT COUNT(*) FROM consultations').fetchone()[0]
    avg_conf = conn.execute('SELECT AVG(confidence) FROM consultations').fetchone()[0] or 0.0
    row = conn.execute('''SELECT predicted_disease, COUNT(*) AS c
                          FROM consultations GROUP BY predicted_disease
                          ORDER BY c DESC LIMIT 1''').fetchone()
    conn.close()
    return total, avg_conf, (row[0] if row else 'N/A')


def clear_history():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM consultations')
    conn.commit()
    conn.close()