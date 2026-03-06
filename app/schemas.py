from pydantic import BaseModel


class PredictionInput(BaseModel):
    article_id: int
    year: int
    week: int


class PredictionResponse(BaseModel):
    prediction: float