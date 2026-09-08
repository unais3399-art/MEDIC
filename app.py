"""
🩺 MEDIC — Machine-learning Enabled Diagnosis & Intelligent Care
Main Streamlit application (entry point).
Run with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from config import CHAT_EXAMPLES, FALLBACK_MSG, QUICK_OPTIONS
from database import (clear_history, get_history, get_stats, init_db,
                      save_consultation)
from medical import get_recommendations
from model import (extract_symptoms, get_model, predict_disease,
                   symptoms_to_vector)
from ui import (build_assistant_html, full_button, full_dataframe, load_css,
                render_header, render_sidebar_brand, render_welcome)
from visualizations import (create_confidence_gauge,
                            create_disease_distribution, create_history_chart,
                            show_chart)

# ================= BOOTSTRAP =================
st.set_page_config(page_title="MEDIC • AI Healthcare Assistant",
                   page_icon="🩺",
                   layout="wide",
                   initial_sidebar_state="expanded")

init_db()
load_css()
model, encoder, symptom_names, MODEL_SOURCE = get_model()

if 'chat' not in st.session_state:
    st.session_state.chat = []


# ================= CHAT ENGINE =================
def push(role, content=None, html=None, result=None):
    st.session_state.chat.append({'role': role, 'content': content,
                                  'html': html, 'result': result})


def handle_input(text):
    push('user', content=text)
    extracted = extract_symptoms(text, symptom_names)
    if not extracted:
        push('assistant', content=FALLBACK_MSG)
        return

    disease, confidence, probs = predict_disease(
        symptoms_to_vector(extracted, symptom_names), model, encoder
    )
    recs = get_recommendations(disease, confidence)
    save_consultation(
        text,
        extracted,
        disease,
        confidence,
        recs.get('urgency', 'Medium'),
        str(recs),
    )
    push(
        'assistant',
        html=build_assistant_html(
            {
                'disease': disease,
                'confidence': confidence,
                'probabilities': probs,
                'recommendations': recs,
                'symptoms': extracted,
            }
        ),
        result={
            'disease': disease,
            'confidence': confidence,
            'probabilities': probs,
            'recommendations': recs,
            'symptoms': extracted,
        },
    )


def latest_result():
    for msg in reversed(st.session_state.chat):
        if msg.get('result'):
            return msg['result']
    return None


# ================= SIDEBAR =================
def render_sidebar():
    with st.sidebar:
        render_sidebar_brand()

        total, avg_conf, most_common = get_stats()
        st.markdown(f"""
<div class="side-card">
  <p class="resp-label">📊 Dashboard</p>
  <div style="display:flex;justify-content:space-between;color:#e6edf3;font-size:.88rem;">
    <span>Consultations</span><b>{total}</b></div>
  <div style="display:flex;justify-content:space-between;color:#e6edf3;font-size:.88rem;">
    <span>Avg confidence</span><b>{avg_conf:.1f}%</b></div>
  <div style="display:flex;justify-content:space-between;color:#e6edf3;font-size:.88rem;">
    <span>Most common</span><b>{most_common}</b></div>
  <div style="margin-top:6px;color:#8b949e;font-size:.72rem;">
    <span class="status-dot"></span>{MODEL_SOURCE}</div>
</div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<p class="resp-label">⚡ Quick Symptoms</p>', unsafe_allow_html=True)
        for (label1, text1), (label2, text2) in zip(QUICK_OPTIONS[::2], QUICK_OPTIONS[1::2]):
            c1, c2 = st.columns(2)
            if full_button(label1, key=f'q_{label1}'):
                st.session_state.quick_input = text1
                st.rerun()
            if full_button(label2, key=f'q_{label2}'):
                st.session_state.quick_input = text2
                st.rerun()

        st.divider()
        st.markdown('<p class="resp-label">📜 Recent History</p>', unsafe_allow_html=True)
        history = get_history(limit=5)
        if history:
            for entry in history:
                icon = {'Low': '🟢', 'Medium': '🟡', 'High': '🟠'}.get(entry[4], '🔴')
                st.markdown(f"""<div class="history-item">
  <div class="d">{icon} {entry[2]}</div>
  <div class="t">{entry[5][:16]} • {entry[3]:.0f}% conf</div>
</div>""", unsafe_allow_html=True)
        else:
            st.caption("No consultations yet.")

        st.divider()
        c1, c2 = st.columns(2)
        if full_button("🧹 Clear chat", key='clr_chat'):
            st.session_state.chat = []
            st.rerun()
        if full_button("🗑️ Clear DB", key='clr_db'):
            clear_history()
            st.rerun()

        st.markdown("""<p style="color:#8b949e;font-size:.7rem;text-align:center;margin-top:.8rem;">
⚕️ <b>Medical Disclaimer</b><br>MEDIC provides general information only —
it does not replace professional medical advice.</p>""", unsafe_allow_html=True)


# ================= TAB RENDERERS =================
def render_chat_tab():
    if not st.session_state.chat:
        render_welcome()
        cols = st.columns(len(CHAT_EXAMPLES))
        for col, ex in zip(cols, CHAT_EXAMPLES):
            if full_button(ex, key=f'ex_{ex}'):
                st.session_state.quick_input = ex
                st.rerun()
    else:
        for msg in st.session_state.chat:
            avatar = "🧑" if msg['role'] == 'user' else "🩺"
            with st.chat_message(msg['role'], avatar=avatar):
                if msg.get('html'):
                    st.markdown(msg['html'], unsafe_allow_html=True)
                else:
                    st.markdown(msg['content'])
        if latest_result():
            st.caption("📊 Full probability breakdown & trends are in the **Analytics** tab.")


def render_analytics_tab():
    total, avg_conf, most_common = get_stats()
    lr = latest_result()

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="metric-label">Consultations</div>'
                f'<div class="metric-value">{total}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-label">Avg Confidence</div>'
                f'<div class="metric-value">{avg_conf:.1f}%</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-label">Most Common</div>'
                f'<div class="metric-value" style="font-size:1.15rem;margin-top:.55rem;">{most_common}</div></div>',
                unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-label">Last Prediction</div>'
                f'<div class="metric-value" style="font-size:1.15rem;margin-top:.55rem;">{lr["disease"] if lr else "—"}</div></div>',
                unsafe_allow_html=True)

    if lr:
        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            show_chart(create_confidence_gauge(lr['confidence']))
        with g2:
            show_chart(create_disease_distribution(lr['probabilities']))
    else:
        st.info("No predictions yet — start a chat to see live analytics! 💬")

    trend = create_history_chart()
    if trend is not None:
        st.divider()
        show_chart(trend)


def render_history_tab():
    rows = get_history(limit=500)
    if not rows:
        st.info("No consultation history stored yet.")
        return
    df = pd.DataFrame(rows, columns=['User Input', 'Symptoms', 'Predicted Disease',
                                     'Confidence (%)', 'Urgency', 'Timestamp'])
    options = sorted(df['Urgency'].unique())
    urgency_filter = st.multiselect("Filter by urgency", options, default=options)
    df_show = df[df['Urgency'].isin(urgency_filter)]
    if df_show.empty:
        st.warning("No consultations match the selected filters.")
    else:
        full_dataframe(df_show)
        st.download_button("⬇️ Export history as CSV",
                           df_show.to_csv(index=False).encode(),
                           file_name="medic_consultations.csv",
                           mime="text/csv")


# ================= MAIN FLOW =================
pending = st.session_state.pop('quick_input', None)
user_text = st.chat_input("Describe your symptoms… e.g. 'I have fever and cough'")
incoming = pending or (user_text.strip() if user_text else None)
if incoming:
    handle_input(incoming)

render_sidebar()
render_header()

tab_chat, tab_analytics, tab_history = st.tabs(["💬 Chat", "📊 Analytics", "📜 History"])
with tab_chat:
    render_chat_tab()
with tab_analytics:
    render_analytics_tab()
with tab_history:
    render_history_tab()