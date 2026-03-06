# SheinPulse MLOps

SheinPulse is an end-to-end MLOps project built on the H&M retail dataset.  
The project demonstrates the full lifecycle of a machine learning system including data processing, model training, experiment tracking with MLflow, API deployment using FastAPI, and a React dashboard for predictions and recommendations.

The system supports two machine learning tasks:

- Demand prediction for fashion articles
- Customer product recommendation

---

# Project Overview

This project demonstrates a complete machine learning pipeline including:

- Data ingestion and preprocessing
- Feature engineering
- Model training and evaluation
- Experiment tracking using MLflow
- Model registry and versioning
- Model serving with FastAPI
- Frontend interface using React

The goal of the project is to simulate a real-world ML system used in fashion retail analytics.

---

# Features

## Demand Prediction

The demand prediction module estimates weekly product demand for a given article.

Key characteristics:

- Weekly demand aggregation
- Feature engineering using article metadata
- Regression model training
- Experiment comparison with MLflow
- Best model registered in MLflow Model Registry
- FastAPI inference endpoint

Models tested:

- RandomForestRegressor
- GradientBoostingRegressor

The best performing model is automatically registered as the production model.

---

## Product Recommendation

The recommendation module suggests products for a given customer.

Two recommendation strategies are implemented:

### Popularity-based baseline
Recommends the most purchased products excluding those already purchased by the customer.

### Collaborative filtering improvement
Finds customers with similar purchases and recommends items frequently bought by similar customers.

The recommendation API returns:

- article_id
- product name
- product type
- product group

---

# MLOps Components

The project demonstrates the following MLOps practices:

- Experiment tracking
- Parameter logging
- Metric logging
- Model artifact storage
- Model registry versioning
- Production model alias
- API-based inference
- Frontend integration

MLflow is used to manage the model lifecycle.

---

# Project Structure
mlops-main/
│
├── app/
│ ├── main.py
│ ├── model_loader.py
│ ├── recommender.py
│ └── schemas.py
│
├── data/
│ ├── raw/
│ └── processed/
│
├── frontend/
│ ├── src/
│ └── package.json
│
├── models/
│ ├── article_customers.parquet
│ ├── article_popularity.parquet
│ └── customer_history.parquet
│
├── reports/
│ └── figures/
│
├── src/
│ ├── features/
│ │ └── build_demand_dataset.py
│ ├── recommendation/
│ │ └── build_recommender.py
│ └── training/
│ └── train.py
│
├── mlruns/
├── README.md
├── requirements.txt
└── .gitignore

---

# Dataset

The project uses the H&M fashion retail dataset.

Files used:

- transactions.parquet
- articles.parquet
- customers.parquet

Transactions contain purchase history linking customers and articles.

Article metadata provides product attributes used for feature engineering.

---

# Machine Learning Pipeline

## 1 Data Processing

Demand dataset creation is handled by:
src/features/build_demand_dataset.py

This script:

- loads transaction data
- extracts year and week from transaction dates
- aggregates purchases per article per week
- merges article metadata
- saves the processed dataset

Output file:
data/processed/weekly_demand.parquet
---

## 2 Recommendation Data Preparation

Recommendation artifacts are created using:


src/recommendation/build_recommender.py


This script builds:

- customer purchase history
- article to customer mapping
- article popularity ranking

Output files:


models/customer_history.parquet
models/article_customers.parquet
models/article_popularity.parquet


---

## 3 Model Training

Training is handled by:


src/training/train.py


Steps performed:

- load processed dataset
- preprocess features using ColumnTransformer
- train regression models
- compare models using MLflow
- register best model

Metrics logged:

- MAE
- RMSE
- R²

The best model is registered as:


sheinpulse_model


---

# MLflow Experiment Tracking

MLflow tracks:

- experiments
- parameters
- metrics
- model artifacts
- model versions

To start MLflow UI:


mlflow ui


Open in browser:


http://127.0.0.1:5000


---

# FastAPI Model Serving

FastAPI provides the backend API for predictions and recommendations.

Run the API:


uvicorn app.main:app --reload


Open API documentation:


http://127.0.0.1:8000/docs


Available endpoints:

## Health Check


GET /health


## Model Info


GET /model-info


## Demand Prediction


POST /predict


Example request:

```json
{
  "article_id": 108775051,
  "year": 2018,
  "week": 38
}
Customer Recommendations

GET /recommend/{customer_id}?top_k=5


Returns recommended products for a given customer.

React Frontend

The frontend dashboard provides a visual interface for interacting with the system.

Features:

Demand prediction form

Recommendation form

API status display

Model information

Product recommendation cards

The frontend communicates with the FastAPI backend using Axios.

Installation
1 Clone the repository

git clone <repository_url>
cd sheinpulse-mlops-main

2 Create virtual environment

Windows:


python -m venv .venv
.venv\Scripts\activate

3 Install Python dependencies

pip install -r requirements.txt

4 Install frontend dependencies

cd frontend
npm install
cd ..

Running the Project
Step 1 Activate the virtual environment

.venv\Scripts\activate

Step 2 Build the demand dataset

python src/features/build_demand_dataset.py

Step 3 Build recommendation artifacts

python src/recommendation/build_recommender.py

Step 4 Train the model

python src/training/train.py

Step 5 Start MLflow

mlflow ui


Open:


http://127.0.0.1:5000

Step 6 Start FastAPI

uvicorn app.main:app --reload


API docs:


http://127.0.0.1:8000/docs

Step 7 Start React frontend

Open a second terminal:


cd frontend
npm run dev


Open:


http://localhost:5173

Demo Workflow
Demand Prediction

1 Open dashboard
2 Enter article_id
3 Enter year and week
4 Click Run Prediction
5 Predicted demand is displayed

Product Recommendation

1 Enter a customer_id
2 Select number of recommendations
3 Click Get Recommendations
4 The system returns recommended products

Technical Architecture

React Frontend
      |
      v
FastAPI Backend
      |
      v
MLflow Production Model
      |
      v
Prediction Response


Recommendation pipeline:


Customer ID
     |
     v
FastAPI /recommend
     |
     v
Collaborative Recommendation Logic
     |
     v
Recommended Products

Current Limitations

The available transaction snapshot covers a short time window

Temporal variation in the demand dataset is limited

Recommendation system is a baseline collaborative approach

Future improvements could include:

larger transaction history

advanced collaborative filtering

hybrid recommendation models

deployment with Docker

production cloud deployment

Technologies Used

Backend

Python

FastAPI

Pandas

Scikit-learn

MLflow

Frontend

React

Vite

Axios

Data

Parquet

H&M fashion dataset

Author

Rawen Beji
Engineering student in Data Science and AI focusing on building real-world machine learning systems.