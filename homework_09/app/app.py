from fastapi import FastAPI
from pydantic import BaseModel

from model.model import load_model

model = None
app = FastAPI()


class ToxicResponse(BaseModel):
    text: str
    sentiment_label: str
    sentiment_score: float


# route
@app.get("/")
def index():
    return {"text": "Toxicity Analysis"}


# Register function to run during startup
@app.on_event("startup")
def startup_event():
    global model
    model = load_model()


# FastAPI route handlers
@app.get("/predict")
def predict_toxicity(text: str):
    sentiment = model(text)

    response = ToxicResponse(
        text=text,
        sentiment_label=sentiment.label,
        sentiment_score=sentiment.score,
    )

    return response

# uvicorn app.app:app --host 127.0.0.1 --port 8080
