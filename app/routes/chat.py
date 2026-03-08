import os
from fastapi import APIRouter, Depends, HTTPException
from google import genai

from app.dependencies import get_current_admin
from app.chat_schemas import ChatExplainRequest, ChatExplainResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

client = genai.Client()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


@router.post("/explain", response_model=ChatExplainResponse)
def explain_chat(
    data: ChatExplainRequest,
    admin=Depends(get_current_admin),
):
    try:
        context_parts = []

        if data.prediction is not None:
            context_parts.append(f"Prediction value: {data.prediction}")

        if data.article_id is not None:
            context_parts.append(f"Article ID: {data.article_id}")

        if data.year is not None:
            context_parts.append(f"Year: {data.year}")

        if data.week is not None:
            context_parts.append(f"Week: {data.week}")

        if data.recommendations:
            trimmed_recommendations = data.recommendations[:3]
            context_parts.append(f"Recommendations: {trimmed_recommendations}")

        context_text = "\n".join(context_parts) if context_parts else "No extra context provided."

        prompt = f"""
You are a concise retail analytics assistant for the SheinPulse dashboard.

Rules:
- Explain predictions and recommendations in simple business language.
- Be short, practical, and easy to understand.
- Do not invent facts.
- If context is missing, say what is missing.
- If the user asks what to do next, give practical retailer-oriented suggestions.

User question:
{data.message}

Dashboard context:
{context_text}
""".strip()

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        reply = response.text if getattr(response, "text", None) else "Sorry, I could not generate a response."

        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")