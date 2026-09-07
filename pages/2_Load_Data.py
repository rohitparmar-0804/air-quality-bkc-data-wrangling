import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Load Data | BKC Air Quality", page_icon="📥", layout="wide")
st.title("📥 1. Load Data")
st.caption("Initial inspection of the Bandra Kurla Complex air-quality dataset before cleaning.")

DATA = Path(__file__).parents[1] / "data" / "BandraKurlaComplexMumbaiIITM_AQI.csv"
df = pd.read_csv(DATA)

# Parse dates for display only
for c in ["From Date", "To Date"]:
    df[c] = pd.to_datetime(df[c], dayfirst=True, errors="coerce")

st.subheader("What happens during the Load Data step?")
c1,c2,c3 = st.columns(3)
with c1:
    st.markdown("**1. Load**\n\nRead the CSV using `pandas.read_csv()`.")
with c2:
    st.markdown("**2. Inspect**\n\nCheck rows, columns, data types, missing values and duplicates.")
with c3:
    st.markdown("**3. Prepare**\n\nPass the raw data to the cleaning stage.")

st.subheader("Dataset Preview — First 15 Records")
st.dataframe(df.head(15), use_container_width=True, height=420)

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Rows", f"{df.shape[0]:,}")
c2.metric("Total Columns", df.shape[1])
c3.metric("Pollutant Fields", 7)
c4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

st.subheader("Column Names")
st.write(list(df.columns))

st.subheader("Missing Values")
missing = df.isna().sum().sort_values(ascending=False).to_frame("Missing Values")
st.dataframe(missing, use_container_width=True)

st.subheader("Data Types")
st.dataframe(df.dtypes.astype(str).to_frame("Data Type"), use_container_width=True)

st.subheader("Basic Statistics")
st.dataframe(df.describe().T, use_container_width=True)

st.success("Inspection completed. We'll Clean the Data to prepare the dataset for analysis.")
