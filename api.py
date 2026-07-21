from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import os
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Spotify Popularity Predictor API", version="1.0")

# Allow CORS for UI interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pipeline safely
PIPELINE_PATH = "pipeline.pkl"
GENRES_PATH = "genres.pkl"

pipeline = None
genres_list = []

if os.path.exists(PIPELINE_PATH):
    pipeline = joblib.load(PIPELINE_PATH)
    print("Model pipeline loaded successfully!")
else:
    print("Warning: Pipeline not found. Run train_model.py first.")

if os.path.exists(GENRES_PATH):
    genres_list = joblib.load(GENRES_PATH)
else:
    genres_list = ["acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime"] # fallback

# Define request schema
class TrackFeatures(BaseModel):
    track_genre: str
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    time_signature: int
    explicit: int
    duration_min: float

@app.post("/predict")
def predict_popularity(features: TrackFeatures):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model Pipeline is not loaded. Train model first.")

    try:
        # Convert request body into DataFrame with a single row
        # (This is exactly what our pipeline expects as input)
        input_data = pd.DataFrame([features.model_dump()])

        # Predict
        prediction = pipeline.predict(input_data)[0]
        
        # Ensure prediction is bounded between 0 and 100
        pred_clamped = max(0.0, min(100.0, float(prediction)))
        
        return {"predicted_popularity": round(pred_clamped, 2)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata")
def get_metadata():
    return {"genres": genres_list}

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/")
    def serve_index():
        return {"message": "Frontend not found. Please create the frontend directory."}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
