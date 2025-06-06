from fastapi import FastAPI
import pickle
import pandas as pd

app = FastAPI()
model = pickle.load(open("model.pkl", "rb"))

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: dict):
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]
    return {"prediction": int(prediction)}