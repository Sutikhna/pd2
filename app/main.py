from fastapi import FastAPI
from app.utils.data_reader import get_latest_sensor_data
import pickle
import os

app = FastAPI()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

@app.get("/predict")
def predict():
    data = get_latest_sensor_data()
    if data is None:
        return {"error": "No valid sensor data found"}
    prediction = model.predict([data])[0]
    return {
        "sensor_data": {
            "Temperature": data[0],
            "Humidity": data[1],
            "Moisture": data[2],
            "Gas": data[3],
            "IR": data[4],
            "PIR": data[5],
            "Vibration": data[6]
        },
        "pest_detected": bool(prediction)
    }

