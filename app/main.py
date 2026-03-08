from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.dependencies import get_current_admin
from app.schemas import PredictionInput, PredictionResponse
from app.model_loader import load_model
from app.recommender import recommend_for_customer

app = FastAPI(title="SheinPulse API")

app.include_router(auth_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = load_model()


@app.get("/health")
def health(admin=Depends(get_current_admin)):
    return {"status": "ok"}


@app.get("/model-info")
def model_info(admin=Depends(get_current_admin)):
    return {"model_uri": "models:/sheinpulse_model@production"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionInput, admin=Depends(get_current_admin)):
    df = pd.DataFrame([payload.dict()])
    prediction = model.predict(df)[0]
    return PredictionResponse(prediction=float(prediction))


@app.get("/recommend/{customer_id}")
def recommend(customer_id: str, top_k: int = 5, admin=Depends(get_current_admin)):
    recommendations = recommend_for_customer(customer_id, top_k=top_k)
    return {
        "customer_id": customer_id,
        "recommendations": recommendations
    }


@app.get("/")
def root(admin=Depends(get_current_admin)):
    return {"message": "API is running"}