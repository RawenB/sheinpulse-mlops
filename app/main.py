from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from app.schemas import PredictionInput, PredictionResponse
from app.model_loader import load_model
from app.recommender import recommend_for_customer


app = FastAPI(title="SheinPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = load_model()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model-info")
def model_info():
    return {"model_uri": "models:/sheinpulse_model@production"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionInput):
    df = pd.DataFrame([payload.dict()])
    prediction = model.predict(df)[0]
    return PredictionResponse(prediction=float(prediction))

@app.get("/recommend/{customer_id}")
def recommend(customer_id: str, top_k: int = 5):
    recommendations = recommend_for_customer(customer_id, top_k=top_k)
    return {
        "customer_id": customer_id,
        "recommendations": recommendations
    }