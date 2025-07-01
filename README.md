# 📈 Stock Analyzer: AI-Powered Forecasting Platform

## Overview

Stock Analyzer is a full-stack production-ready web app that predicts stock prices using multiple machine learning models and provides visual insights into expected price changes. Designed for both investors and ML practitioners, it features a dashboard, model comparison tools, and an explore view powered by precomputed forecasts.

---

## 🚀 Features

* **Explore**: View top gainers/losers based on average model forecasts
* **Dashboard**: Get model-specific predictions with stock fundamentals
* **Compare**: See model-level forecasts side-by-side for any stock
* **Watchlist (planned)**: Save and monitor preferred tickers
* **API-first**: FastAPI backend with RESTful endpoints
* **Responsive Frontend**: Built using React + Chakra UI + Framer Motion

---

## Machine Learning Models

We train and deploy the following four models independently per S\&P 500 ticker:

| Model   | Purpose                                  | Strengths                                                        |
| ------- | ---------------------------------------- | ---------------------------------------------------------------- |
| Prophet | Time-series trend + seasonality modeling | Handles holidays, robust for business data                       |
| ARIMA   | Statistical forecasting                  | Simple, interpretable, good baseline                             |
| XGBoost | Gradient boosting regression             | Captures non-linearities, performs well with engineered features |
| LSTM    | Neural sequence model                    | Captures temporal dependencies in price history                  |

## Explore View Logic

* Each model forecasts the price N days ahead (e.g., 30-day return).
* For each stock, we **average predictions across all available models**.
* From these, we precompute and store in S3:

  * Top gainers: highest average % increase
  * Top losers: highest average % drop
* Data is fetched efficiently via `/explore/top-gainers` and `/explore/top-losers` endpoints.

---

## Tech Stack

### Frontend

* React + Vite
* Chakra UI for design system
* Framer Motion for animations
* Axios for API calls
* Hosted via CloudFront + S3

### Backend

* FastAPI + Uvicorn
* Joblib for ML models (Prophet, ARIMA, XGBoost)
* TensorFlow (for LSTM models)
* S3 used to store pre-trained models and explore summaries

### ML & Infra

* Python training pipelines in `ml/train_model.py`
* Models built as Docker images and run via AWS SageMaker
* Deployment using Terraform (ECS, ALB, CloudFront, ACM)

---

## How Predictions Work

* `/predict`: Accepts a `ticker` and `model`, returns predictions for 1–30 days
* `/metrics`: Returns fundamentals like P/E, EPS, volume
* `/compare`: Shows predictions across all 4 models for one ticker
* `/explore`: Aggregates top movers via precomputed S3 data

---

## CI/CD & Model Flow

* GitHub Actions triggers SageMaker jobs for model training
* Models uploaded to S3 as `.pkl` or `.keras`
* Backend loads models dynamically from local/S3 depending on env
* Explore batch jobs compute volatility & price delta → saved to `explore_data.json`

---

## Roadmap

* ✅ Core ML forecasting with Prophet, ARIMA, XGBoost, LSTM
* ✅ Explore page with filters (sector, days)
* ✅ Compare models visually
* 🔜 User auth + watchlists
* 🔜 Alert system when prediction delta > threshold
* 🔜 Model performance charts and drift monitoring

---

## License

MIT License. Contributions welcome!

---

For local development, model training, Docker usage, and deployment instructions, see [`developer.md`](developer.md).
