import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Balance Data | BKC Air Quality",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ 3. Balance Data")
st.caption(
    "Examine the distribution of historical AQI categories "
    "and demonstrate random oversampling."
)

DATA_DIR = Path(__file__).parents[1] / "data"

ORIGINAL_FILE = DATA_DIR / "BandraKurlaComplexMumbaiIITM_AQI.csv"
CLEANED_FILE = DATA_DIR / "BKC_AQI_cleaned.csv"
BALANCED_FILE = DATA_DIR / "BKC_AQI_balanced.csv"


# ============================================================
# LOAD CLEANED DATA
# ============================================================

if CLEANED_FILE.exists():

    df = pd.read_csv(CLEANED_FILE)

else:

    # Fallback: recreate the essential cleaning steps
    # if the cleaned file has not yet been downloaded/saved.

    df = pd.read_csv(ORIGINAL_FILE)

    # Remove unnecessary index columns
    index_cols = [
        c for c in df.columns
        if c.lower().startswith("unnamed")
    ]

    if index_cols:
        df = df.drop(columns=index_cols)

    # Remove duplicate rows
    df = df.drop_duplicates().copy()

    # Convert dates
    for c in ["From Date", "To Date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(
                df[c],
                dayfirst=True,
                errors="coerce"
            )

    # Remove completely empty columns
    empty_cols = [
        c for c in df.columns
        if df[c].isna().all()
    ]

    if empty_cols:
        df = df.drop(columns=empty_cols)

    # Median imputation for numeric sensor columns
    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    for c in numeric_cols:

        if c == "aqi":
            continue

        if df[c].isna().any():

            median_value = df[c].median()

            if pd.notna(median_value):
                df[c] = df[c].fillna(median_value)


# ============================================================
# AQI CATEGORIES
# ============================================================

def aqi_category(value):

    if pd.isna(value):
        return np.nan

    if value <= 50:
        return "Good"

    elif value <= 100:
        return "Satisfactory"

    elif value <= 200:
        return "Moderate"

    elif value <= 300:
        return "Poor"

    elif value <= 400:
        return "Very Poor"

    else:
        return "Severe"


# Make sure AQI is numeric
df["aqi"] = pd.to_numeric(
    df["aqi"],
    errors="coerce"
)

# Keep only records with calculated AQI
aqi_df = df.dropna(
    subset=["aqi"]
).copy()

aqi_df["AQI Category"] = aqi_df["aqi"].apply(
    aqi_category
)

# Remove any unexpected category
aqi_df = aqi_df.dropna(
    subset=["AQI Category"]
)

category_order = [
    "Good",
    "Satisfactory",
    "Moderate",
    "Poor",
    "Very Poor",
    "Severe"
]

observed_categories = [
    c for c in category_order
    if c in aqi_df["AQI Category"].unique()
]

category_counts = (
    aqi_df["AQI Category"]
    .value_counts()
    .reindex(observed_categories)
    .fillna(0)
    .astype(int)
)


# ============================================================
# STEP 1 — CHECK DISTRIBUTION
# ============================================================

st.subheader("Step 1 — Check AQI Category Distribution")

st.write(
    "Before balancing, we examine how historical AQI "
    "records are distributed across the observed categories."
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "AQI Records",
    f"{len(aqi_df):,}"
)

c2.metric(
    "AQI Categories",
    f"{len(observed_categories):,}"
)

c3.metric(
    "Largest Category",
    f"{category_counts.max():,}"
)

# Category table
distribution_table = pd.DataFrame({
    "AQI Category": category_counts.index,
    "Records": category_counts.values
})

st.dataframe(
    distribution_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# BEFORE BALANCING CHART
# ============================================================

st.subheader("AQI Category Distribution Before Balancing")

fig, ax = plt.subplots(figsize=(10, 4.5))

ax.bar(
    category_counts.index,
    category_counts.values
)

ax.set_title(
    "AQI Category Distribution Before Balancing"
)

ax.set_xlabel("AQI Category")
ax.set_ylabel("Number of Records")

ax.tick_params(axis="x", rotation=20)

for i, value in enumerate(category_counts.values):

    ax.text(
        i,
        value,
        f"{value:,}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ============================================================
# STEP 2 — RANDOM OVERSAMPLING
# ============================================================

st.subheader("Step 2 — Random Oversampling")

st.write(
    "Random oversampling increases the smaller AQI categories "
    "by randomly selecting existing records with replacement."
)

target_size = int(
    category_counts.max()
)

balanced_parts = []

for category in observed_categories:

    category_data = aqi_df[
        aqi_df["AQI Category"] == category
    ]

    current_size = len(category_data)

    if current_size < target_size:

        additional = category_data.sample(
            n=target_size - current_size,
            replace=True,
            random_state=42
        )

        category_balanced = pd.concat(
            [category_data, additional],
            ignore_index=True
        )

    else:

        category_balanced = category_data.copy()

    balanced_parts.append(
        category_balanced
    )

balanced_df = pd.concat(
    balanced_parts,
    ignore_index=True
)

# Shuffle the final balanced dataset
balanced_df = balanced_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# AFTER BALANCING
# ============================================================

balanced_counts = (
    balanced_df["AQI Category"]
    .value_counts()
    .reindex(observed_categories)
    .fillna(0)
    .astype(int)
)

st.subheader("Step 3 — Distribution After Balancing")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Records Before",
    f"{len(aqi_df):,}"
)

c2.metric(
    "Records After",
    f"{len(balanced_df):,}"
)

c3.metric(
    "Records per Category",
    f"{target_size:,}"
)


# ============================================================
# AFTER BALANCING CHART
# ============================================================

fig, ax = plt.subplots(figsize=(10, 4.5))

ax.bar(
    balanced_counts.index,
    balanced_counts.values
)

ax.set_title(
    "AQI Category Distribution After Random Oversampling"
)

ax.set_xlabel("AQI Category")
ax.set_ylabel("Number of Records")

ax.tick_params(axis="x", rotation=20)

for i, value in enumerate(balanced_counts.values):

    ax.text(
        i,
        value,
        f"{value:,}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ============================================================
# BEFORE VS AFTER TABLE
# ============================================================

st.subheader("Before vs After Balancing")

comparison = pd.DataFrame({
    "AQI Category": observed_categories,
    "Before Balancing": [
        category_counts[c]
        for c in observed_categories
    ],
    "After Balancing": [
        balanced_counts[c]
        for c in observed_categories
    ]
})

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EXPLANATION
# ============================================================

st.info(
    f"Random oversampling increases the smaller categories "
    f"to the size of the largest category ({target_size:,} records). "
    "Existing observations are reused rather than creating new "
    "AQI measurements."
)


# ============================================================
# BALANCED DATA PREVIEW
# ============================================================

st.subheader("Balanced Dataset Preview")

st.dataframe(
    balanced_df.head(20),
    use_container_width=True,
    height=420
)


# ============================================================
# SAVE BALANCED DATASET
# ============================================================

download_df = balanced_df.copy()

# Save the balanced dataset
download_df.to_csv(
    BALANCED_FILE,
    index=False
)

csv = download_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "⬇️ Download Balanced Dataset",
    csv,
    "BKC_AQI_balanced.csv",
    "text/csv"
)


# ============================================================
# SUMMARY
# ============================================================

st.success(
    "Data balancing completed successfully!"
)