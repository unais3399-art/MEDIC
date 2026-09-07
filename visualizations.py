"""MEDIC — Plotly visualizations (gauge, probability bars, history trend)."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import PLOT_BG
from database import get_history


def _style(fig, height):
    fig.update_layout(
        height=height,
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font={'color': '#e6edf3'},
        margin=dict(t=45, b=25, l=25, r=25),
        xaxis_gridcolor='#21262d',
        yaxis_gridcolor='#21262d',
    )
    return fig


def show_chart(fig):
    """Version-safe chart rendering (new & old Streamlit)."""
    try:
        st.plotly_chart(fig, width='stretch')
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def create_confidence_gauge(confidence):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence,
        number={'suffix': '%'},
        title={'text': "Confidence Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4da3ff"},
            'steps': [
                {'range': [0, 40], 'color': '#3d1114'},
                {'range': [40, 70], 'color': '#3d2e0d'},
                {'range': [70, 100], 'color': '#0d3d21'},
            ],
            'threshold': {'line': {'color': "white", 'width': 3},
                          'thickness': 0.8, 'value': confidence},
        }))
    return _style(fig, 320)


def create_disease_distribution(probabilities):
    df = pd.DataFrame({
        'Disease': list(probabilities.keys()),
        'Probability': list(probabilities.values()),
    }).sort_values('Probability')
    fig = px.bar(df, x='Probability', y='Disease', orientation='h',
                 color='Probability',
                 color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                 text='Probability',
                 title='Disease Probability Distribution')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(coloraxis_showscale=False)
    return _style(fig, 320)


def create_history_chart():
    rows = get_history(limit=200)
    if len(rows) < 2:
        return None
    df = pd.DataFrame(rows, columns=['input', 'symptoms', 'disease',
                                     'confidence', 'urgency', 'timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    fig = px.line(df, x='timestamp', y='confidence', color='disease',
                  title='Consultation Confidence Over Time', markers=True)
    return _style(fig, 340)