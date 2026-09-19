from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()
model = joblib.load("model.joblib")

class Message(BaseModel):
    text: str

@app.post("/predict")
def predict(message: Message):
    prediction = model.predict([message.text])[0]
    return {"label": prediction}

@app.get("/healthz")
def healthz():
    return "OK"
