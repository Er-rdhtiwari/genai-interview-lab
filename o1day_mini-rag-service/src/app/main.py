# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # (You can also avoid Pydantic and parse manually)
import logging

from .qa_service import answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    top_k: int = 3

class AskResponse(BaseModel):
    answer: str
    sources: list[dict]

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        result = answer_question(req.question, req.top_k)
        return result
    except Exception as e:
        logger.exception("Failed to answer question")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok"}