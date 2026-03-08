from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatExplainRequest(BaseModel):
    message: str
    prediction: Optional[float] = None
    article_id: Optional[int] = None
    year: Optional[int] = None
    week: Optional[int] = None
    recommendations: Optional[List[Dict[str, Any]]] = None


class ChatExplainResponse(BaseModel):
    reply: str