from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import redis
import time

app = FastAPI()
model = joblib.load("model.joblib")

# Connect to Redis using the service name 'cache' as the hostname
r_cache = redis.Redis(host='cache', port=6379, db=0, decode_responses=True)

class Message(BaseModel):
    text: str

@app.post("/predict")
def predict(message: Message):
    start_time = time.time()
    
    # 1. Check the Redis cache for that exact input text
    cached_label = r_cache.get(message.text)
    
    if cached_label:
        # Cache HIT: return the cached label without recomputing
        prediction = cached_label
        source = "cache_hit"
    else:
        # Cache MISS: compute the prediction
        prediction = model.predict([message.text])[0]
        # Store it in Redis with a Time-To-Live (TTL) of 60 seconds
        r_cache.setex(message.text, 60, prediction)
        source = "cache_miss"
        
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    
    return {
        "label": prediction, 
        "source": source, 
        "time_ms": elapsed_ms
    }

@app.get("/healthz")
def healthz():
    return "OK"
