# BKC Air Quality Data Wrangling Project

A beginner-friendly Data Wrangling mini project built with **Python, Pandas, Matplotlib and Streamlit**. It uses the Bandra Kurla Complex (Mumbai) air-quality dataset with a calculated `aqi` field.

## Project pages

1. **Dashboard** — project overview and key AQI metrics.
2. **Load Data** — inspect rows, columns, data types, missing values, statistics and duplicates.
3. **Clean Data** — remove an unnecessary index column, duplicates, standardize dates and handle partially missing numeric sensor values.
4. **Balance Data** — demonstrate random oversampling across observed AQI categories.
5. **Visualizations** — easy-to-explain bar, line, scatter and box charts.

## Run in VS Code

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Render

- Push this folder to a GitHub repository.
- Create a new **Web Service** on Render.
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Important AQI note

The original monitoring dataset did not contain a measured AQI field. The supplied `aqi` column is a calculated AQI field based on the available pollutant data and CPCB-style AQI methodology. Missing AQI values are intentionally kept missing rather than artificially filled.

## Charts chosen for easy viva explanation

- AQI category distribution
- Monthly average AQI trend
- Average pollutant concentration
- PM2.5 vs AQI scatter plot
- AQI box plot
