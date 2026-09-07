import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Visualizations",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Visualizations")
st.caption(
    "Simple visual analysis of the historical BKC air-quality dataset."
)

DATA_DIR = Path(__file__).parents[1] / "data"

CLEANED_FILE = DATA_DIR / "BKC_AQI_cleaned.csv"
ORIGINAL_FILE = DATA_DIR / "BandraKurlaComplexMumbaiIITM_AQI.csv"


# ============================================================
# LOAD CLEANED DATA
# ============================================================

if CLEANED_FILE.exists():

    df = pd.read_csv(CLEANED_FILE)

else:

    df = pd.read_csv(ORIGINAL_FILE)

    # Remove unnecessary index columns
    index_cols = [
        c for c in df.columns
        if c.lower().startswith("unnamed")
    ]

    if index_cols:
        df = df.drop(columns=index_cols)

    # Remove duplicate records
    df = df.drop_duplicates().copy()

    # Convert date columns
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

    # Median imputation for numeric sensor fields
    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns

    for c in numeric_cols:

        if c == "aqi":
            continue

        if df[c].isna().any():

            median_value = df[c].median()

            if pd.notna(median_value):

                df[c] = df[c].fillna(
                    median_value
                )


# ============================================================
# PREPARE AQI DATA
# ============================================================

df["aqi"] = pd.to_numeric(
    df["aqi"],
    errors="coerce"
)

df["From Date"] = pd.to_datetime(
    df["From Date"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)

aqi_df = df.dropna(
    subset=["aqi"]
).copy()


# ============================================================
# AQI CATEGORY FUNCTION
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


aqi_df["AQI Category"] = aqi_df["aqi"].apply(
    aqi_category
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


# ============================================================
# OVERVIEW
# ============================================================

st.subheader("Historical AQI Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "AQI Records",
    f"{len(aqi_df):,}"
)

c2.metric(
    "Average AQI",
    f"{aqi_df['aqi'].mean():.0f}"
)

c3.metric(
    "Minimum AQI",
    f"{aqi_df['aqi'].min():.0f}"
)

c4.metric(
    "Maximum AQI",
    f"{aqi_df['aqi'].max():.0f}"
)


# ============================================================
# CHART 1 — AQI CATEGORY DISTRIBUTION
# ============================================================

st.subheader("1. AQI Category Distribution")

st.write(
    "This chart shows how many historical AQI records "
    "fall into each AQI category."
)

category_counts = (
    aqi_df["AQI Category"]
    .value_counts()
    .reindex(observed_categories)
    .fillna(0)
    .astype(int)
)

fig, ax = plt.subplots(figsize=(10, 5))

bars = ax.bar(
    category_counts.index,
    category_counts.values
)

ax.set_title(
    "Historical AQI Category Distribution"
)

ax.set_xlabel("AQI Category")
ax.set_ylabel("Number of Records")

ax.tick_params(
    axis="x",
    rotation=20
)

for bar, value in zip(
    bars,
    category_counts.values
):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:,}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ============================================================
# CHART 2 — MONTHLY AVERAGE AQI
# ============================================================

st.subheader("2. Monthly Average AQI")

st.write(
    "This chart shows the average AQI for each calendar month "
    "across the historical observation period."
)

aqi_df["Month Number"] = (
    aqi_df["From Date"].dt.month
)

aqi_df["Month"] = (
    aqi_df["From Date"].dt.strftime("%b")
)

month_order = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

monthly_aqi = (
    aqi_df
    .groupby("Month Number")["aqi"]
    .mean()
    .reindex(range(1, 13))
)

monthly_labels = [
    month_order[i - 1]
    for i in monthly_aqi.index
]

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    monthly_labels,
    monthly_aqi.values,
    marker="o",
    linewidth=2
)

ax.set_title(
    "Average AQI by Month"
)

ax.set_xlabel("Month")
ax.set_ylabel("Average AQI")

ax.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ============================================================
# CHART 3 — PM2.5 VS AQI
# ============================================================

st.subheader("3. PM2.5 vs AQI")

st.write(
    "This scatter plot shows the relationship between PM2.5 "
    "concentration and AQI across historical observations."
)

if "PM2.5" in df.columns:

    scatter_df = df[
        ["PM2.5", "aqi"]
    ].copy()

    scatter_df["PM2.5"] = pd.to_numeric(
        scatter_df["PM2.5"],
        errors="coerce"
    )

    scatter_df["aqi"] = pd.to_numeric(
        scatter_df["aqi"],
        errors="coerce"
    )

    scatter_df = scatter_df.dropna(
        subset=["PM2.5", "aqi"]
    )

    # Use a representative sample only for visualization
    if len(scatter_df) > 5000:

        scatter_df = scatter_df.sample(
            n=5000,
            random_state=42
        )

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    ax.scatter(
        scatter_df["PM2.5"],
        scatter_df["aqi"],
        alpha=0.35,
        s=14
    )

    ax.set_title(
        "PM2.5 Concentration vs AQI"
    )

    ax.set_xlabel(
        "PM2.5 Concentration"
    )

    ax.set_ylabel(
        "AQI"
    )

    ax.grid(
        alpha=0.3
    )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)

else:

    st.warning(
        "PM2.5 data is not available in the dataset."
    )

# ============================================================
# CHART 4 — MAJOR POLLUTANT CONCENTRATION
# ============================================================

st.subheader("4. Average Major Pollutant Concentration")

st.write(
    "This chart compares the average concentration of the "
    "major pollutants measured in the dataset. CO and Ozone "
    "are excluded from this comparison because their AQI "
    "averaging periods and concentration scales differ."
)

pollutant_columns = [
    "PM2.5",
    "PM10",
    "NO2",
    "SO2",
    "NH3"
]

available_pollutants = [
    c for c in pollutant_columns
    if c in df.columns
]

pollutant_means = (
    df[available_pollutants]
    .apply(pd.to_numeric, errors="coerce")
    .mean()
)

fig, ax = plt.subplots(figsize=(10, 5))

bars = ax.bar(
    pollutant_means.index,
    pollutant_means.values
)

ax.set_title(
    "Average Major Pollutant Concentration"
)

ax.set_xlabel("Pollutant")
ax.set_ylabel("Average Concentration")

for bar, value in zip(
    bars,
    pollutant_means.values
):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.1f}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ============================================================
# CHART 5 — AVERAGE AQI BY PM10 RANGE
# ============================================================

st.subheader("5. Average AQI by PM10 Concentration Range")

st.write(
    "This chart shows the average AQI across different "
    "PM10 concentration ranges."
)

if "PM10" in df.columns:

    pm10_df = df[["PM10", "aqi"]].copy()

    pm10_df["PM10"] = pd.to_numeric(
        pm10_df["PM10"],
        errors="coerce"
    )

    pm10_df["aqi"] = pd.to_numeric(
        pm10_df["aqi"],
        errors="coerce"
    )

    pm10_df = pm10_df.dropna(
        subset=["PM10", "aqi"]
    )

    # Create simple PM10 concentration ranges
    bins = [
        -np.inf,
        50,
        100,
        150,
        200,
        300,
        np.inf
    ]

    labels = [
        "≤50",
        "51–100",
        "101–150",
        "151–200",
        "201–300",
        ">300"
    ]

    pm10_df["PM10 Range"] = pd.cut(
        pm10_df["PM10"],
        bins=bins,
        labels=labels
    )

    pm10_range_aqi = (
        pm10_df
        .groupby(
            "PM10 Range",
            observed=False
        )["aqi"]
        .mean()
        .reindex(labels)
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(
        pm10_range_aqi.index.astype(str),
        pm10_range_aqi.values
    )

    ax.set_title(
        "Average AQI by PM10 Concentration Range"
    )

    ax.set_xlabel(
        "PM10 Concentration Range"
    )

    ax.set_ylabel(
        "Average AQI"
    )

    for bar, value in zip(
        bars,
        pm10_range_aqi.values
    ):

        if pd.notna(value):

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.0f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)

else:

    st.warning(
        "PM10 data is not available in the dataset."
    )
