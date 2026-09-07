import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="BKC Air Quality", page_icon="🌫️", layout="wide", initial_sidebar_state="expanded")

# ---------- Styling ----------
st.markdown("""
<style>
:root { --navy:#0e1b35; --navy2:#17264a; --red:#ff3f46; --muted:#68758d; --bg:#f4f7fb; }
.stApp { background:var(--bg); }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1730 0%,#172a57 100%); }
section[data-testid="stSidebar"] * { color:#f7f9ff !important; }
[data-testid="stSidebarNav"] {
    display: none;
}
.block-container { padding-top:1.2rem; padding-bottom:2rem; max-width:1500px; }
.hero { background:linear-gradient(110deg,#0c1832,#233f79); border-radius:22px; padding:28px 34px; color:white; margin-bottom:22px; box-shadow:0 8px 24px rgba(14,27,53,.12); }
.hero h1 { color:white; margin:0 0 8px 0; font-size:34px; }
.hero p { color:#dfe8ff; margin:0; font-size:16px; }
.section-title { font-size:25px; font-weight:800; color:#16213b; margin:12px 0 14px; }
.card {
    background: white;
    color: #18233d;
    border-radius: 18px;
    padding: 20px 22px;
    box-shadow: 0 4px 18px rgba(31,52,91,.07);
    border: 1px solid #e8edf5;
}
.card h1,
.card h2,
.card h3,
.card h4,
.card h5,
.card h6,
.card p,
.card li,
.card ol,
.card ul,
.card span,
.card div {
    color: #18233d !important;
}
.card .small {
    color: #68758d !important;
}
.card hr {
    border-color: #e5e9f1;
}
.small { color:#71809a; font-size:14px; }
.kpi-label { color:#71809a; font-size:14px; margin-bottom:5px; }
.kpi-value { color:#18233d; font-size:28px; font-weight:800; }
.badge { display:inline-block; padding:6px 12px; border-radius:999px; font-weight:700; font-size:13px; }
.footer { text-align:center; color:#71809a; font-size:13px; padding:24px 0 8px; }
</style>
""", unsafe_allow_html=True)

DATA = Path(__file__).parent / "data" / "BandraKurlaComplexMumbaiIITM_AQI.csv"

def load_data():
    df = pd.read_csv(DATA)
    df["From Date"] = pd.to_datetime(df["From Date"], dayfirst=True, errors="coerce")
    df["To Date"] = pd.to_datetime(df["To Date"], dayfirst=True, errors="coerce")
    return df

df = load_data()
aqi = df["aqi"].dropna()

def aqi_category(x):
    if pd.isna(x): return "Not Available"
    if x <= 50: return "Good"
    if x <= 100: return "Satisfactory"
    if x <= 200: return "Moderate"
    if x <= 300: return "Poor"
    if x <= 400: return "Very Poor"
    return "Severe"

# Sidebar branding and summary
with st.sidebar:
    st.markdown("# 🌫️ Air Quality Analysis — BKC Mumbai")
    st.caption("Data Wrangling")
    st.divider()
    st.markdown("**MAIN**")
    st.page_link("app.py", label="Dashboard", icon="🏠")
    st.markdown("**DATA WRANGLING**")
    st.page_link("pages/2_Load_Data.py", label="Load Data", icon="📥")
    st.page_link("pages/3_Clean_Data.py", label="Clean Data", icon="🧹")
    st.page_link("pages/4_Balance_Data.py", label="Balance Data", icon="⚖️")
    st.markdown("**ANALYTICS**")
    st.page_link("pages/5_Visualizations.py", label="Visualizations", icon="📊")
    st.divider()
    st.markdown("### DATASET SUMMARY")
    st.metric("Records", f"{len(df):,}")
    st.metric("AQI Records", f"{len(aqi):,}")
    st.metric("Avg AQI", f"{aqi.mean():.0f}" if len(aqi) else "—")
    st.metric("Max AQI", f"{aqi.max():.0f}" if len(aqi) else "—")

st.markdown("""
<div class="hero">
  <h1>🌫️ Air Quality Analysis — BKC Mumbai </h1>
  <p>From Raw Data to Meaningful Insights</p>
</div>
""", unsafe_allow_html=True)

# KPI cards
cols = st.columns(4)
metrics = [
    ("Monitoring Records", f"{len(df):,}"),
    ("AQI Records", f"{len(aqi):,}"),
    ("Average AQI", f"{aqi.mean():.0f}" if len(aqi) else "—"),
    ("Maximum AQI", f"{aqi.max():.0f}" if len(aqi) else "—")
]
for c,(label,value) in zip(cols,metrics):
    with c:
        st.markdown(f'<div class="card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Project Objectives</div>', unsafe_allow_html=True)
left,right = st.columns([1.7,1])
with left:
    st.markdown('''<div class="card">
    <ol>
      <li>Load and inspect the BKC air-quality dataset.</li>
      <li>Identify missing, duplicate and inconsistent values.</li>
      <li>Clean dates, numeric fields and missing sensor values.</li>
      <li>Work with the calculated CPCB-style AQI field.</li>
      <li>Examine AQI-category distribution and demonstrate oversampling.</li>
      <li>Create simple, presentation-friendly charts for interpretation.</li>
    </ol></div>''', unsafe_allow_html=True)

st.markdown('<div class="section-title">Project Workflow</div>', unsafe_allow_html=True)
steps = [("1. Load","Inspect rows, columns, types, missing values and duplicates."),("2. Clean","Remove duplicates, standardize dates and handle missing sensor values."),("3. Balance","Demonstrate random oversampling across observed AQI categories."),("4. Visualize","Use clear charts to explain AQI trends and pollutant patterns.")]
cols = st.columns(4)
for c,(title,desc) in zip(cols,steps):
    with c:
        st.markdown(f'<div class="card"><h4>{title}</h4><p class="small">{desc}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Python • Pandas • Matplotlib • Streamlit • Render</div>', unsafe_allow_html=True)
