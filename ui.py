"""MEDIC — UI components: CSS theme, HTML cards, headers, version-safe widgets."""
import streamlit as st

from config import URGENCY_META

CSS_STYLES = """
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.6rem; padding-bottom: 6rem;}
.brand {display:flex; align-items:center; gap:14px; margin-bottom:.4rem;}
.brand-logo {font-size:2.1rem; filter: drop-shadow(0 0 12px rgba(77,163,255,.55));}
.brand h1 {margin:0; font-size:1.9rem; font-weight:800;
  background: linear-gradient(90deg,#4da3ff,#7ee787 60%,#f5c542);
  -webkit-background-clip:text; background-clip:text; color:transparent;}
.brand p {margin:2px 0 0; color:#8b949e; font-size:.9rem;}
.status-dot {display:inline-block;width:8px;height:8px;border-radius:50%;
  background:#3fb950;margin-right:6px;animation:pulse 2s infinite;}
@keyframes pulse {0%,100%{opacity:1}50%{opacity:.25}}
.metric-card {background:#161b22;border:1px solid #30363d;border-radius:14px;
  padding:.9rem 1rem;height:100%;}
.metric-label {color:#8b949e;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;}
.metric-value {color:#e6edf3;font-size:1.7rem;font-weight:800;margin-top:.3rem;}
.resp-card {background:#161b22;border:1px solid #21262d;border-radius:16px;
  padding:1rem 1.1rem;margin:.3rem 0;}
.resp-head {display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;}
.resp-label {color:#8b949e;font-size:.7rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.08em;margin:0 0 4px 0;}
.resp-disease {color:#e6edf3;font-size:1.45rem;font-weight:800;margin:0;}
.urgency-pill {padding:.35rem .8rem;border-radius:999px;font-size:.72rem;font-weight:800;white-space:nowrap;}
.conf-track {background:#0d1117;border-radius:999px;height:8px;overflow:hidden;margin:4px 0 2px;}
.conf-fill {height:100%;border-radius:999px;transition:width .6s ease;}
.conf-val {color:#e6edf3;font-weight:700;font-size:.9rem;}
.symptom-pill {display:inline-block;background:rgba(77,163,255,.12);color:#93c5fd;
  border:1px solid rgba(77,163,255,.4);padding:.28rem .7rem;border-radius:999px;
  margin:0 .3rem .3rem 0;font-size:.75rem;}
.warn-box {border-left:4px solid #f5c542;background:rgba(245,197,66,.08);color:#f5d76e;
  border-radius:10px;padding:.7rem .9rem;margin:.5rem 0;font-size:.88rem;}
.danger-box {border-left:4px solid #ff4d4d;background:rgba(255,77,77,.08);color:#ffb3b3;
  border-radius:10px;padding:.7rem .9rem;margin:.5rem 0;font-size:.88rem;font-weight:600;}
.rec-grid {display:flex;gap:.7rem;flex-wrap:wrap;margin:.6rem 0;}
.rec-col {flex:1 1 180px;background:#0d1117;border:1px solid #21262d;border-radius:12px;
  padding:.7rem .8rem;font-size:.85rem;color:#c9d1d9;line-height:1.7;}
.doc-box {background:rgba(77,163,255,.08);border:1px solid rgba(77,163,255,.35);
  border-radius:12px;padding:.7rem .9rem;margin:.5rem 0;color:#93c5fd;font-size:.88rem;}
.disclaimer {color:#8b949e;font-size:.78rem;font-style:italic;margin-top:.6rem;}
.side-card {background:#161b22;border:1px solid #21262d;border-radius:14px;
  padding:.85rem .95rem;margin:.4rem 0;}
.history-item {background:#161b22;border:1px solid #21262d;border-radius:10px;
  padding:.45rem .6rem;margin:.3rem 0;}
.history-item .d {color:#e6edf3;font-weight:600;font-size:.85rem;}
.history-item .t {color:#8b949e;font-size:.7rem;}
.welcome {text-align:center;padding:2.6rem 1rem 1.4rem;}
.welcome h2 {font-size:2.1rem;font-weight:800;color:#e6edf3;margin:0 0 .4rem;}
.welcome p {color:#8b949e;font-size:1rem;}
div[data-testid="stChatMessage"] {background:#11161d;border:1px solid #21262d;border-radius:14px;}
</style>
"""


def load_css():
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


# ---------- Version-safe widgets (old & new Streamlit) ----------
def full_button(label, key=None, button_type='secondary'):
    try:
        return st.button(label, key=key, type=button_type, width='stretch')
    except TypeError:
        return st.button(label, key=key, type=button_type, use_container_width=True)


def full_dataframe(df):
    try:
        st.dataframe(df, width='stretch', hide_index=True)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ---------- HTML builders ----------
def _li(items):
    return '<br>'.join(f'• {i}' for i in items) if items else '—'


def build_assistant_html(result):
    disease = result['disease']
    confidence = result['confidence']
    recs = result['recommendations']
    symptoms = result['symptoms']

    urgency = recs.get('urgency', 'Medium')
    icon, color = URGENCY_META.get(urgency, ('🟡', '#f5c542'))
    bar_color = '#27AE60' if confidence > 80 else '#F39C12' if confidence > 60 else '#E74C3C'
    pills = ''.join(f'<span class="symptom-pill">{s.replace("_", " ").title()}</span>'
                    for s in symptoms)
    emergency_html = (f'<div class="danger-box">{recs["emergency"]}</div>'
                      if recs.get('emergency') else '')

    return f"""
<div class="resp-card">
  <div class="resp-head">
    <div>
      <p class="resp-label">Predicted condition</p>
      <p class="resp-disease">🩺 {disease}</p>
    </div>
    <span class="urgency-pill"
          style="background:{color}22;color:{color};border:1px solid {color}66;">
      {icon} {urgency.upper()} URGENCY</span>
  </div>
  <p class="resp-label" style="margin-top:10px;">Confidence</p>
  <div style="display:flex;align-items:center;gap:10px;">
    <div class="conf-track" style="flex:1;">
      <div class="conf-fill" style="width:{min(confidence, 100.0):.1f}%;background:{bar_color};"></div>
    </div>
    <span class="conf-val">{confidence:.1f}%</span>
  </div>
  <p class="resp-label" style="margin-top:12px;">🔍 Symptoms detected</p>
  <div style="margin:4px 0 2px;">{pills}</div>
  <div class="warn-box">{recs.get('warning', '')}</div>
  {emergency_html}
  <div class="rec-grid">
    <div class="rec-col"><p class="resp-label">💊 Medications</p>{_li(recs.get('medications', []))}</div>
    <div class="rec-col"><p class="resp-label">🥗 Diet & Nutrition</p>{_li(recs.get('diet', []))}</div>
    <div class="rec-col"><p class="resp-label">💡 Lifestyle</p>{_li(recs.get('lifestyle', []))}</div>
  </div>
  <div class="doc-box">{recs.get('doctor', '')}</div>
  <p class="disclaimer">{recs.get('disclaimer', '')}</p>
</div>"""


# ---------- Static blocks ----------
def render_header():
    st.markdown("""
<div class="brand">
  <div class="brand-logo">🩺</div>
  <div>
    <h1>MEDIC</h1>
    <p><span class="status-dot"></span>Machine-learning Enabled Diagnosis & Intelligent Care</p>
  </div>
</div>""", unsafe_allow_html=True)


def render_sidebar_brand():
    st.markdown("""
<div class="brand">
  <div class="brand-logo">🩺</div>
  <div>
    <h1 style="font-size:1.4rem;">MEDIC</h1>
    <p>AI Healthcare Assistant</p>
  </div>
</div>""", unsafe_allow_html=True)


def render_welcome():
    st.markdown("""
<div class="welcome">
  <h2>How are you feeling today?</h2>
  <p>Describe your symptoms and MEDIC will give you an instant AI triage recommendation.</p>
</div>""", unsafe_allow_html=True)