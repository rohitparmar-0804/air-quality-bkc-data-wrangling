import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Clean Data | BKC Air Quality",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 2. Clean Data")
st.caption(
    "Clean and prepare the historical BKC air-quality dataset "
    "before analysis."
)

DATA = (
    Path(__file__).parents[1]
    / "data"
    / "BandraKurlaComplexMumbaiIITM_AQI.csv"
)

df = pd.read_csv(DATA)

# ============================================================
# BEFORE CLEANING
# ============================================================

original_rows = len(df)
original_columns = df.shape[1]
original_dupes = int(df.duplicated().sum())

missing_before = df.isna().sum()

st.subheader("Before Cleaning")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Original Rows",
    f"{original_rows:,}"
)

c2.metric(
    "Original Columns",
    f"{original_columns:,}"
)

c3.metric(
    "Duplicate Rows",
    f"{original_dupes:,}"
)

c4.metric(
    "Missing AQI",
    f"{int(df['aqi'].isna().sum()):,}"
)

st.markdown(
    "**Missing Values Before Cleaning**"
)

st.dataframe(
    missing_before
    .sort_values(ascending=False)
    .to_frame("Missing Values"),
    use_container_width=True
)

# ============================================================
# STEP 1 — REMOVE UNNECESSARY INDEX
# ============================================================

st.subheader("Step 1 — Remove Unnecessary Index Column")

index_cols = [
    c for c in df.columns
    if c.lower().startswith("unnamed")
]

if index_cols:

    df = df.drop(columns=index_cols)

    st.success(
        f"Removed unnecessary column(s): "
        f"{', '.join(index_cols)}"
    )

else:

    st.info(
        "No unnecessary index column was found."
    )

# ============================================================
# STEP 2 — REMOVE DUPLICATES
# ============================================================

st.subheader("Step 2 — Remove Duplicate Records")

rows_before_duplicates = len(df)

df = df.drop_duplicates().copy()

duplicates_removed = (
    rows_before_duplicates - len(df)
)

if duplicates_removed > 0:

    st.success(
        f"Removed {duplicates_removed:,} duplicate row(s)."
    )

else:

    st.info(
        "No duplicate records were found."
    )

# ============================================================
# STEP 3 — STANDARDIZE DATES
# ============================================================

st.subheader("Step 3 — Standardize Date Columns")

invalid_dates = {}

for c in ["From Date", "To Date"]:

    if c in df.columns:

        original_date = df[c]

        df[c] = pd.to_datetime(
            df[c],
            dayfirst=True,
            errors="coerce"
        )

        invalid_dates[c] = int(
            df[c].isna().sum()
            - original_date.isna().sum()
        )

st.success(
    "Converted `From Date` and `To Date` "
    "to datetime format."
)

invalid_total = sum(
    max(v, 0) for v in invalid_dates.values()
)

st.write(
    f"Invalid date values created during conversion: "
    f"**{invalid_total:,}**"
)

# ============================================================
# STEP 4 — HANDLE COMPLETELY EMPTY COLUMNS
# ============================================================

st.subheader(
    "Step 4 — Identify Completely Empty Columns"
)

all_missing_cols = [
    c for c in df.columns
    if df[c].isna().all()
]

if all_missing_cols:

    df = df.drop(columns=all_missing_cols)

    st.warning(
        f"Removed completely empty column(s): "
        f"{', '.join(all_missing_cols)}"
    )

else:

    st.info(
        "No completely empty columns were found."
    )

# ============================================================
# STEP 5 — HANDLE MISSING NUMERIC VALUES
# ============================================================

st.subheader(
    "Step 5 — Handle Missing Numeric Sensor Values"
)

numeric_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

# AQI is intentionally excluded.
fill_cols = [
    c for c in numeric_cols
    if c != "aqi"
]

missing_before_imputation = (
    df[fill_cols].isna().sum().sum()
)

imputed_cells = 0

for c in fill_cols:

    missing_count = int(
        df[c].isna().sum()
    )

    if missing_count > 0:

        median_value = df[c].median()

        if pd.notna(median_value):

            df[c] = df[c].fillna(
                median_value
            )

            imputed_cells += missing_count

st.metric(
    "Numeric Values Imputed",
    f"{imputed_cells:,}"
)

st.info(
    "Partially missing numeric sensor values "
    "are filled using the median of each column."
)

# ============================================================
# STEP 6 — CHECK INVALID / NEGATIVE VALUES
# ============================================================

st.subheader(
    "Step 6 — Check Invalid Negative Values"
)

numeric_check_cols = df.select_dtypes(
    include=np.number
).columns

negative_counts = (
    (df[numeric_check_cols] < 0)
    .sum()
)

total_negative = int(
    negative_counts.sum()
)

if total_negative > 0:

    st.warning(
        f"Found {total_negative:,} negative numeric values."
    )

else:

    st.success(
        "No negative numeric values were found."
    )

# ============================================================
# AQI NOTE
# ============================================================

st.subheader(
    "AQI Handling"
)

aqi_missing = int(
    df["aqi"].isna().sum()
)

st.info(
    f"{aqi_missing:,} AQI records remain missing. "
    "AQI values are not artificially imputed because "
    "an unavailable AQI should not be invented."
)

# ============================================================
# AFTER CLEANING
# ============================================================

st.subheader("After Cleaning")

missing_after = (
    df.isna()
    .sum()
    .sort_values(ascending=False)
    .to_frame("Missing Values")
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Rows After Cleaning",
    f"{len(df):,}"
)

c2.metric(
    "Columns After Cleaning",
    f"{df.shape[1]:,}"
)

c3.metric(
    "Rows Removed",
    f"{original_rows - len(df):,}"
)

c4.metric(
    "Columns Removed",
    f"{original_columns - df.shape[1]:,}"
)

st.markdown(
    "**Missing Values After Cleaning**"
)

st.dataframe(
    missing_after,
    use_container_width=True
)

# ============================================================
# CLEANED DATA PREVIEW
# ============================================================

st.subheader("Cleaned Data Preview")

st.dataframe(
    df.head(20),
    use_container_width=True,
    height=420
)

# ============================================================
# DOWNLOAD
# ============================================================

df.to_csv(
    Path(__file__).parents[1]
    / "data"
    / "BKC_AQI_cleaned.csv",
    index=False
)
csv = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "⬇️ Download Cleaned Dataset",
    csv,
    "BKC_AQI_cleaned.csv",
    "text/csv"
)

# ============================================================
# SUMMARY
# ============================================================

st.success(
    "Data cleaning completed successfully!"
)