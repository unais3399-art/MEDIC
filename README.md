<div align="center">

# 🩺 MEDIC

### Machine-learning Enabled Diagnosis & Intelligent Care

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://YOUR-USERNAME-medici.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-learn](https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)

An AI-powered conversational healthcare assistant that transforms natural-language
symptom descriptions into disease predictions with confidence scoring, urgency
triage, and personalized care guidance.

[Live Demo](https://YOUR-USERNAME-medici.streamlit.app) • [Features](#-key-features) • [Architecture](#-architecture) • [Getting Started](#-getting-started) • [License](#-license)

</div>

---

## 📖 Overview

MEDIC is a full-stack AI/ML web application that provides preliminary health
triage through a ChatGPT-style conversational interface. Users describe symptoms
in plain language; the system extracts clinical keywords, runs a Random Forest
classifier, and returns a ranked diagnosis with confidence metrics, color-coded
urgency levels, medication/diet/lifestyle guidance, and interactive visual
analytics. Every consultation is persisted locally for longitudinal review.

## ✨ Key Features

- **Conversational Triage** — ChatGPT-style chat interface with rich diagnostic response cards
- **ML Prediction** — Random Forest classifier over 8 symptoms and 7 disease classes
- **Confidence Analytics** — Confidence gauge, probability distribution, and historical trend charts
- **Urgency Triage** — Four-level color-coded urgency system with emergency escalation alerts
- **Care Guidance** — Disease-specific medications, diet, lifestyle, and physician-referral advice
- **Consultation History** — SQLite-backed history with urgency filtering and CSV export
- **Rapid Input** — One-tap quick-symptom chips alongside free-text entry
- **Premium UI** — Responsive dark theme with custom CSS design system

## 🧠 How It Works

```text
Natural Language Input
        │
        ▼
Symptom Extraction (keyword-based NLP)
        │
        ▼
Binary Feature Vector [1, 0, 1, ...]
        │
        ▼
Random Forest Classifier (300 estimators)
        │
        ▼
Disease Prediction + Class Probabilities
        │
        ▼
Medical Knowledge Base (urgency, medications, diet, lifestyle)
        │
        ├──▶ Chat Response Card
        ├──▶ Plotly Visualizations
        └──▶ SQLite Consultation Log